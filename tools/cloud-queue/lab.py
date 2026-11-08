"""Actual disposable CHR/WinBox capture, only on a GitHub-hosted Linux runner.
No local workstation, production credential, inbound listener or paid storage.
"""
from pathlib import Path
import base64, datetime, hashlib, json, logging, os, re, secrets, select
import shutil, socket, struct, subprocess, tempfile, time, urllib.request, zipfile
import paramiko
from PIL import Image
from prompt_state import select_prompt
from queue_values import exact_queue_limits

ROOT = Path(tempfile.mkdtemp(prefix="tn-queue-cloud-"))
os.umask(0o077)
logging.basicConfig(filename=ROOT / "ssh-private.log", level=logging.WARNING)
PASSWORD = secrets.token_urlsafe(26)
print("::add-mask::" + PASSWORD, flush=True)
PROCESSES = []
phase = "preflight"
CAPTURES = []
RESULT = {"schema": 1, "status": "STARTED", "production_mutations": 0,
          "local_workstation_access": False, "historical_private_deny_scan": "NOT_RUN_OWNER_APPROVED_BRANCH_EXCEPTION",
          "runtime": "standard GitHub-hosted ubuntu-24.04", "actual_new_videos": 0}

def run(args, timeout=30, env=None):
    p = subprocess.run([str(x) for x in args], capture_output=True, timeout=timeout, env=env)
    if p.returncode:
        (ROOT / ("command-" + secrets.token_hex(4) + ".log")).write_bytes(p.stdout + p.stderr)
        raise RuntimeError("Command failed in " + phase + "; raw diagnostics not exported")
    return p.stdout

def download(url, name, expected=None):
    assert url.startswith("https://download.mikrotik.com/"), "Only pinned vendor HTTPS downloads"
    p = ROOT / name
    with urllib.request.urlopen(url, timeout=90) as response, p.open("xb") as out:
        shutil.copyfileobj(response, out)
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    if expected: assert digest == expected, "Vendor asset differs from pinned accepted source"
    return p, digest

def extract(archive, directory):
    directory.mkdir()
    with zipfile.ZipFile(archive) as z:
        assert sum(i.file_size for i in z.infolist()) < 700 * 1024 * 1024
        for info in z.infolist():
            p = directory / info.filename
            assert p.resolve().is_relative_to(directory.resolve())
            assert not ((info.external_attr >> 16) & 0o170000) == 0o120000
        z.extractall(directory)

def start(args, label, env=None):
    out = (ROOT / (label + "-stdout.log")).open("wb")
    err = (ROOT / (label + "-stderr.log")).open("wb")
    p = subprocess.Popen([str(x) for x in args], stdout=out, stderr=err, env=env)
    PROCESSES.append((p, out, err))
    return p

def clean(data):
    return re.sub(rb"\x1b\[[0-?]*[ -/]*[@-~]", b"", data).replace(b"\r", b"")

def serial_wait(s, patterns, timeout=50):
    end = time.monotonic() + timeout
    data = b""
    while time.monotonic() < end:
        try: data += s.recv(65536)
        except socket.timeout: pass
        text = clean(data)
        choice = select_prompt(text, patterns)
        if choice:
            return choice, text
    raise RuntimeError("Fresh guest console not ready in " + phase)

def bootstrap(node):
    sequence = {"node": node["name"], "steps": []}
    RESULT.setdefault("boot_sequences", []).append(sequence)
    port = node["serial"]
    end = time.monotonic() + 100
    while True:
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=3)
            break
        except OSError:
            assert time.monotonic() < end, "Fresh console socket unavailable"
            time.sleep(.5)
    with s:
        s.settimeout(.5)
        s.sendall(b"\r")
        serial_wait(s, {"login": rb"Login:"}, 110)
        s.sendall(b"admin\r")
        serial_wait(s, {"password": rb"Password:"})
        s.sendall(b"\r")
        patterns = {"license": rb"Do you want to see.*license",
                    "repeat": rb"repeat new password\s*>",
                    "new": rb"(?:new password|New Password)\s*>",
                    "prompt": rb"\[[^\n]+\]\s*>"}
        for _ in range(8):
            key, _ = serial_wait(s, patterns, 60)
            sequence["steps"].append(key)
            if key == "license":
                s.sendall(b"n\r")
            elif key in ("new", "repeat"):
                s.sendall(PASSWORD.encode() + b"\r")
            else:
                break
        else: raise RuntimeError("Fresh login sequence did not complete")
        command = '/user set [find name=admin] password="' + PASSWORD + '"; /system identity set name=' + node["identity"] + '; :if ([:len [/ip dhcp-client find interface=ether1]]=0) do={/ip dhcp-client add interface=ether1 disabled=no}; :put "TN_BOOTSTRAP_DONE"'
        s.sendall(command.encode() + b"\r")
        serial_wait(s, {"prompt": rb"\[[^\n]+\]\s*>"}, 30)

def ssh(node):
    end = time.monotonic() + 45
    while True:
        client = paramiko.SSHClient()
        keyfile = ROOT / (node["name"] + "-known-hosts")
        if keyfile.exists():
            client.load_host_keys(str(keyfile))
            client.set_missing_host_key_policy(paramiko.RejectPolicy())
        else:
            # Fresh task-owned loopback guest only; next connections pin this exact key.
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect("127.0.0.1", port=node["ssh"], username="admin", password=PASSWORD,
                           allow_agent=False, look_for_keys=False, timeout=4,
                           banner_timeout=5, auth_timeout=5)
            if not keyfile.exists(): client.save_host_keys(str(keyfile))
            return client
        except (OSError, paramiko.SSHException):
            client.close()
            assert time.monotonic() < end, "Fresh isolated guest SSH unavailable"
            time.sleep(1)

def ros(node, command, pty=False, timeout=60):
    c = ssh(node)
    try:
        _, out, err = c.exec_command(command, timeout=timeout, get_pty=pty)
        text = (out.read() + err.read()).decode(errors="replace")
        (ROOT / ("ros-" + secrets.token_hex(4) + ".log")).write_text(text)
        assert not any(x in text.lower() for x in ["syntax error", "bad command", "failure:", "expected end of command"]), "RouterOS command failed in " + phase
        return text
    finally:
        c.close()

def measure_ping(node, destination, label):
    assert destination in ("192.0.2.10","203.0.113.1")
    source = "192.0.2.10" if node["name"]=="client" else "203.0.113.1"
    assert (source,destination) in (("192.0.2.10","203.0.113.1"),("203.0.113.1","192.0.2.10"))
    output = ros(node, "/ping " + destination + " src-address=" + source + " count=20 size=1000 interval=100ms")
    counts = re.search(r"sent=(\d+)\s+received=(\d+)\s+packet-loss=(\d+)%", output)
    average = re.search(r"avg-rtt=([^\s]+)", output)
    assert counts and average, "Finite ICMP count/latency observation required"
    parts = list(re.finditer(r"(\d+(?:\.\d+)?)(ns|us|µs|ms|s)",average[1]))
    assert parts and "".join(p[0] for p in parts)==average[1], "Unrecognized RouterOS latency unit"
    factors = {"ns":.000001,"us":.001,"µs":.001,"ms":1,"s":1000}
    delay = sum(float(p[1])*factors[p[2]] for p in parts)
    observed = {"source":source,"destination":destination,"sent":int(counts[1]),"received":int(counts[2]),
                "packet_loss_percent":int(counts[3]),"average_rtt_ms":round(delay,3)}
    RESULT.setdefault("icmp_observations",{})[label]=observed
    assert observed["sent"]==20 and 0<observed["received"]<=20, "Finite ICMP probe must retain observable replies"
    return delay

def queue_state(node):
    output = ros(node, ':local q [/queue simple find where name="tn-cloud-cap"]; ' +
                 ':put ("COUNT=" . [:len $q]); ' +
                 ':if ([:len $q]=1) do={:put ("TARGET=" . [/queue simple get $q target]); ' +
                 ':put ("LIMIT=" . [/queue simple get $q max-limit]); ' +
                 ':put ("DISABLED=" . [/queue simple get $q disabled]); ' +
                 ':put ("BYTES=" . [/queue simple get $q bytes]); ' +
                 ':put ("DROPPED=" . [/queue simple get $q dropped])}')
    fields = {}
    for key in ("COUNT", "TARGET", "LIMIT", "DISABLED", "BYTES", "DROPPED"):
        match = re.search(r"(?:^|[\r\n])" + key + r"=([^\r\n]*)", output)
        assert match, "Missing exact queue readback field: " + key
        fields[key] = match[1].strip()
    RESULT["latest_queue_readback"] = fields
    assert fields["COUNT"] == "1" and fields["TARGET"] == "192.0.2.10/32"
    exact_queue_limits(fields["LIMIT"])
    assert fields["DISABLED"] in ("true", "false", "yes", "no")
    assert all(re.fullmatch(r"\d+/\d+",fields[k]) for k in ("BYTES","DROPPED"))
    return fields

def xdo(*args):
    return run(["xdotool", *args], env={**os.environ, "DISPLAY": ":99"}).decode().strip()

def shot(name):
    data = (ROOT / "frames/Xvfb_screen0").read_bytes()
    h = struct.unpack(">25I", data[:100])
    assert h[1] == 7 and h[11] == 32 and h[7] == 0
    offset = h[0] + h[19] * 12
    im = Image.frombytes("RGB", (h[4], h[5]), data[offset:offset+h[12]*h[5]], "raw", "BGRX", h[12], 1)
    p = ROOT / (name + ".png")
    im.save(p, optimize=True)
    CAPTURES.append({"name": name, "width": im.width, "height": im.height,
                     "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                     "observed_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                     "original_ui_pixels": True})
    # Owner explicitly approved only fresh synthetic cloud screenshots in public logs.
    assert p.stat().st_size < 2 * 1024 * 1024, "Bounded screenshot export only"
    print("TN_CLOUD_IMAGE " + json.dumps({**CAPTURES[-1],
          "base64": base64.b64encode(p.read_bytes()).decode("ascii")}), flush=True)

def safe_display_diagnostics(process, env):
    # Fixed labels/flags only: never print stderr, argv, OCR text or screenshot pixels.
    stderr = (ROOT / "winbox-stderr.log").read_text(errors="replace")
    known = ["could not connect to display", "could not load the qt platform plugin",
             "xcb-cursor", "cannot open shared object file", "no qt platform plugin",
             "segmentation fault", "connection refused", "invalid password", "authentication failed"]
    names = subprocess.run(["xdotool", "search", "--onlyvisible", "--name", "."],
                           capture_output=True, env=env).stdout.decode().split()
    flags = {"window_count": len(names), "process_exit": process.poll(),
             "stderr_categories": [x for x in known if x in stderr.lower()]}
    RESULT["display_diagnostics"] = flags

def click(x, y):
    xdo("mousemove", str(x), str(y), "click", "1")
    time.sleep(.8)

try:
    assert os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted"
    assert os.environ.get("GITHUB_REPOSITORY") == "DashSaman/TehNet"
    assert os.environ.get("GITHUB_REF", "").startswith(("refs/heads/lab/cloud-queue-", "refs/pull/"))
    assert os.uname().sysname == "Linux"
    phase = "download"
    imagezip, ziphash = download("https://download.mikrotik.com/routeros/7.25.1/chr-7.25.1.img.zip", "chr.zip")
    extract(imagezip, ROOT / "chr")
    raw = ROOT / "chr/chr-7.25.1.img"
    assert hashlib.sha256(raw.read_bytes()).hexdigest() == "42ce7e8bbcd07d3054bc1c7309540ef621e4bbead90b19defab34fccbba123af"
    wbzip, wbhash = download("https://download.mikrotik.com/routeros/winbox/4.5/WinBox_Linux.zip", "winbox.zip",
                            "5192817089eb91ac5d03edc68661b2603ef81f8098627ab4fd9425b6cc7546a2")
    extract(wbzip, ROOT / "winbox")
    wb = next(p for p in (ROOT / "winbox").rglob("WinBox") if p.is_file())
    wb.chmod(0o700)
    phase = "winbox-runtime-preflight"
    linkage = subprocess.run(["ldd", str(wb)], capture_output=True, timeout=20)
    missing = re.findall(r"^\s*(lib[\w.+-]+)\s+=>\s+not found\s*$",
                         linkage.stdout.decode(errors="replace"), re.M)
    RESULT["missing_winbox_libraries"] = sorted(set(missing))
    assert linkage.returncode == 0 and not missing, "WinBox runtime has unresolved shared libraries"
    RESULT.update(routeros="7.25.1", winbox="4.5", chr_raw_sha256=hashlib.sha256(raw.read_bytes()).hexdigest(),
                  winbox_zip_sha256=wbhash, qemu=run(["qemu-system-x86_64", "--version"]).decode().splitlines()[0])
    phase = "boot"
    nodes = [
        {"name":"r1", "identity":"TN-LAB-R1", "ssh":18222, "wb":18291, "serial":19401, "mac":"11", "peer":None},
        {"name":"client", "identity":"TN-LAB-CLIENT", "ssh":18223, "wb":18292, "serial":19402, "mac":"22", "peer":19321},
        {"name":"r2", "identity":"TN-LAB-R2", "ssh":18224, "wb":18293, "serial":19403, "mac":"33", "peer":19322}]
    for i, n in enumerate(nodes):
        disk = ROOT / (n["name"] + ".qcow2")
        run(["qemu-img", "create", "-f", "qcow2", "-F", "raw", "-b", raw, disk])
        args = ["qemu-system-x86_64", "-name", n["identity"], "-accel", "tcg,thread=single",
                "-cpu", "qemu64", "-smp", "1", "-m", "1024", "-drive", "file="+str(disk)+",if=virtio,format=qcow2",
                "-netdev", "user,id=mgmt,restrict=on,ipv6=off,net=10.61."+str(i+1)+".0/24,hostfwd=tcp:127.0.0.1:"+str(n["ssh"])+"-:22,hostfwd=tcp:127.0.0.1:"+str(n["wb"])+"-:8291",
                "-device", "virtio-net-pci,netdev=mgmt,mac=52:54:00:"+n["mac"]+":00:01"]
        links = [("lan", "listen=127.0.0.1:19321", "02"), ("transit", "listen=127.0.0.1:19322", "03")] if i==0 else [("lan", "connect=127.0.0.1:"+str(n["peer"]), "02")]
        for label, target, macend in links:
            args += ["-netdev", "socket,id="+label+","+target, "-device", "virtio-net-pci,netdev="+label+",mac=52:54:00:"+n["mac"]+":00:"+macend]
        args += ["-display", "none", "-monitor", "none", "-serial", "tcp:127.0.0.1:"+str(n["serial"])+",server=on,wait=off"]
        start(args, n["name"])
    for n in nodes: bootstrap(n)
    r1, client, r2 = nodes
    phase = "network-baseline"
    ros(r1, "/ip address add address=192.0.2.1/24 interface=ether2; /ip address add address=198.51.100.1/24 interface=ether3; /ip route add dst-address=203.0.113.0/24 gateway=198.51.100.2")
    ros(client, "/ip address add address=192.0.2.10/24 interface=ether2; /ip route add dst-address=203.0.113.0/24 gateway=192.0.2.1")
    ros(r2, "/ip address add address=198.51.100.2/24 interface=ether2; /interface bridge add name=target-net protocol-mode=none; /ip address add address=203.0.113.1/24 interface=target-net; /ip route add dst-address=192.0.2.0/24 gateway=198.51.100.1")
    for n in nodes:
        version = ros(n, ':put ("VERSION=" . [/system resource get version]); :put ("IDENTITY=" . [/system identity get name])')
        assert "VERSION=7.25.1" in version and "IDENTITY="+n["identity"] in version
    # Allow cold ARP/route adjacency to settle; the measured five-packet test is separate.
    ros(client, "/ping 203.0.113.1 src-address=192.0.2.10 count=3 size=500 interval=300ms")
    before = ros(client, "/ping 203.0.113.1 src-address=192.0.2.10 count=5 size=500 interval=100ms")
    observed = re.search(r"sent=(\d+)\s+received=(\d+)\s+packet-loss=(\d+)%", before)
    RESULT["baseline_ping_observed"] = [int(x) for x in observed.groups()] if observed else None
    assert re.search(r"sent=5\s+received=5\s+packet-loss=0%", before), "Five real internal pings required"
    empty = ros(r1, ':put ("QUEUES=" . [/queue simple print count-only]); :put ("FASTTRACK=" . [/ip firewall filter print count-only where action=fasttrack-connection])')
    assert "QUEUES=0" in empty and "FASTTRACK=0" in empty
    RESULT["baseline"] = {"ping_5_of_5": True, "queue_empty": True, "fasttrack_absent": True, "nat_required": False,
                           "documentation_address_topology": True, "all_three_identities_versions_verified": True}
    phase = "icmp-baseline"
    # No bandwidth-test endpoint is used; the rate-tool attempts remain unqualified.
    for endpoint in (client,r2):
        ros(endpoint,"/tool bandwidth-server set enabled=no")
    base_up = measure_ping(client,"203.0.113.1","baseline_client_initiated")
    base_down = measure_ping(r2,"192.0.2.10","baseline_r2_initiated")
    assert all(RESULT["icmp_observations"][k]["packet_loss_percent"]==0 for k in
               ("baseline_client_initiated","baseline_r2_initiated")), "Both baseline flows must be lossless"
    phase = "display"
    (ROOT / "frames").mkdir()
    start(["Xvfb", ":99", "-screen", "0", "1536x960x24", "-nolisten", "tcp", "-fbdir", ROOT / "frames"], "xvfb")
    for _ in range(30):
        if (ROOT / "frames/Xvfb_screen0").exists(): break
        time.sleep(.2)
    profile = ROOT / "profile"; profile.mkdir()
    env = {**os.environ, "DISPLAY":":99", "HOME":str(profile), "XDG_CONFIG_HOME":str(profile),
           "QT_QUICK_BACKEND":"software", "QT_XCB_GL_INTEGRATION":"none"}
    wb_process = start([wb, "127.0.0.1:18291", "admin", PASSWORD], "winbox", env)
    wid = None
    for _ in range(45):
        p = subprocess.run(["xdotool","search","--onlyvisible","--name","TN-LAB-R1"], capture_output=True, env=env)
        ids = p.stdout.decode().split()
        if len(ids)==1:
            wid=ids[0];break
        time.sleep(1)
    if not wid:
        safe_display_diagnostics(wb_process, env)
        shot("q00-startup-diagnostic")
    assert wid, "Connected actual WinBox window required"
    xdo("windowsize",wid,"1536","960"); xdo("windowmove",wid,"0","0")
    time.sleep(2)
    phase = "queue-gui-probe"
    shot("q01-connected-baseline")
    click(50,366)
    shot("q02-queues-window")
    click(400,294)
    shot("q03-new-dialog")
    phase = "gui-create-queue"
    def field(x, y, value):
        click(x,y)
        xdo("key","--clearmodifiers","ctrl+a")
        xdo("type","--clearmodifiers","--delay","20",value)
    field(820,409,"tn-cloud-cap")
    field(810,434,"192.0.2.10/32")
    field(820,365,"TN-CLOUD-QUEUE-LAB")
    shot("q04-name-target")
    field(760,525,"64k")
    field(925,525,"128k")
    shot("q05-upload-download-limits")
    click(1048,689)
    time.sleep(1)
    first = queue_state(r1)
    assert first["DISABLED"] in ("false","no"), "New GUI queue must be enabled"
    shot("q06-applied-general")
    phase = "active-queue-measurement"
    active_up = measure_ping(client,"203.0.113.1","active_client_initiated")
    active_down = measure_ping(r2,"192.0.2.10","active_r2_initiated")
    active = queue_state(r1)
    assert all(int(n)>0 for n in active["BYTES"].split("/")), "Both actual Queue byte counters must increase"
    assert active_up>base_up+5 and active_down>base_down+5, "Both controlled flows must show an actual latency increase"
    # Ping missing replies are recorded separately; never equate them with Queue drops.
    click(703,304)
    shot("q07-active-statistics")
    phase = "gui-disable-recovery"
    click(563,304)
    click(691,340)
    click(1048,689)
    disabled = queue_state(r1)
    assert disabled["DISABLED"] in ("true","yes"), "GUI Disable must read back true"
    shot("q08-disabled-general")
    disabled_up = measure_ping(client,"203.0.113.1","disabled_client_initiated")
    disabled_down = measure_ping(r2,"192.0.2.10","disabled_r2_initiated")
    assert all(RESULT["icmp_observations"][k]["packet_loss_percent"]==0 for k in
               ("disabled_client_initiated","disabled_r2_initiated")), "Disabling the queue must restore lossless delivery"
    assert disabled_up+5<active_up and disabled_down+5<active_down, "Disable must reverse the measured latency increase"
    disabled_after=queue_state(r1)
    assert all(disabled_after[k]==disabled[k] for k in ("BYTES","DROPPED")), "Disabled Queue byte/drop counters must remain unchanged under the same traffic"
    phase = "gui-reenable"
    click(691,340)
    click(1048,689)
    reenabled = queue_state(r1)
    assert reenabled["DISABLED"] in ("false","no"), "GUI Enable must read back false"
    shot("q09-reenabled-general")
    again_up = measure_ping(client,"203.0.113.1","reenabled_client_initiated")
    again_down = measure_ping(r2,"192.0.2.10","reenabled_r2_initiated")
    assert again_up>disabled_up+5 and again_down>disabled_down+5, "Re-enable must restore the measured latency effect"
    final_state=queue_state(r1)
    assert all(int(new)>int(old) for new,old in zip(final_state["BYTES"].split("/"),active["BYTES"].split("/"))), "Both queue byte counters must increase again after GUI re-enable"
    click(703,304)
    shot("q10-reenabled-statistics")
    phase = "owned-rule-cleanup"
    click(563,304)
    click(1120,689)
    shot("q11-final-queue-row")
    ros(r1, '/queue simple remove [find where name="tn-cloud-cap" comment="TN-CLOUD-QUEUE-LAB"]')
    assert "QUEUES=0" in ros(r1, ':put ("QUEUES=" . [/queue simple print count-only])')
    for endpoint in (client,r2):
        ros(endpoint,"/tool bandwidth-server set enabled=no")
    time.sleep(1)
    shot("q12-owned-rule-removed")
    after = ros(client,"/ping 203.0.113.1 src-address=192.0.2.10 count=5 size=500 interval=100ms")
    assert re.search(r"sent=5\s+received=5\s+packet-loss=0%",after), "Cleanup must retain the original data path"
    assert "TN-LAB-R1" in ros(r1,":put [/system identity get name]"), "Management must survive all Queue changes"
    RESULT.update(status="LAB_FLOW_VERIFIED_PENDING_MEDIA_REVIEW", captures=CAPTURES,
                  queue_created_by="Actual WinBox GUI; command-line readback only",
                  active_counters=active, disable_enable_actual=True, receive_rate_effect_verified=False,
                  traffic_latency_effect_verified=True, queue_readbacks={"active":active,"disabled":disabled_after,"reenabled":final_state},
                  cleanup={"only_owned_rule_removed":True,"servers_disabled":True,"queue_empty":True,
                           "ping_5_of_5":True,"management_retained":True},
                  limits=["Controlled20x1000-byte ICMP overload at100ms; averages cover received replies only. CHR/TCG evidence, not internet/hardware/customer capacity.",
                          "ICMP latency and Queue byte counters are verified; missing ICMP replies are not equated with Queue drops. Receive-rate/throughput is NOT qualified.",
                          "All new screenshots still require visual acceptance; website/native staging not qualified.",
                          "No new production body or image was published."])
except BaseException as e:
    RESULT.update(status="FAILED", failed_phase=phase, error_type=type(e).__name__, error_message=(str(e).replace(PASSWORD, "<REDACTED>")[:220] if isinstance(e, (AssertionError, RuntimeError)) else "See safe phase classification"),
                  captures=CAPTURES, raw_diagnostics_exported=False)
finally:
    for p,out,err in reversed(PROCESSES):
        if p.poll() is None:
            p.terminate()
            try:p.wait(timeout=8)
            except subprocess.TimeoutExpired:p.kill();p.wait()
        out.close();err.close()
    RESULT["all_task_processes_stopped"] = all(p.poll() is not None for p,_,_ in PROCESSES)
    print("TN_CLOUD_RECEIPT "+json.dumps(RESULT),flush=True)
    shutil.rmtree(ROOT)
if RESULT["status"]=="FAILED":raise SystemExit(1)
