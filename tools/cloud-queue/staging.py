"""Disposable WordPress qualification on GitHub-hosted Linux only; never a deployer."""
import os
assert os.environ.get("RUNNER_ENVIRONMENT")=="github-hosted", "Cloud executor required before filesystem access"
assert os.environ.get("GITHUB_REPOSITORY")=="DashSaman/TehNet" and os.uname().sysname=="Linux"
from pathlib import Path
import base64, datetime, hashlib, json, re, secrets, shutil, subprocess, tempfile, time

REPO=Path.cwd().resolve()
ROOT=Path(tempfile.mkdtemp(prefix="tn-queue-cloud-stage-")).resolve()
os.umask(0o077)
assert ROOT.parent==Path("/tmp") and ROOT.name.startswith("tn-queue-cloud-stage-") and not REPO.is_relative_to(ROOT)
os.environ.update(GIT_CONFIG_COUNT="1",GIT_CONFIG_KEY_0="safe.directory",GIT_CONFIG_VALUE_0=str(REPO))
SOURCE=subprocess.check_output(["git","rev-parse","HEAD"],cwd=REPO).decode().strip()
BASE="04c2af953b6676306b702933aecc412a76d67730"
SCOPE="tehnet-winbox-queue-cloud-20261108-v1"
DIRECTORY="content/queue-winbox-cloud-2026-11-08"
MEDIA="mu-plugins/tehnet-technical-resources/learning-media/queue-cloud-20261108"
JOB=os.environ["GITHUB_RUN_ID"]
assert re.fullmatch(r"\d+",JOB) and re.fullmatch(r"[a-f0-9]{40}",SOURCE)
APP="tn-queue-stage-app-"+JOB
DB="tn-queue-stage-db-"+JOB
NET="tn-queue-stage-net-"+JOB
CLI="tn-queue-stage-cli-"+JOB
CONTAINERS=[]
NETWORK_CREATED=False
PHASE="preflight"
RESULT={"schema":1,"status":"STARTED","source_commit":SOURCE,"baseline_commit":BASE,
        "synthetic_fixture_only":True,"local_workstation_access":False,"production_mutations":0,
        "historical_private_deny_scan":"NOT_RUN_OWNER_APPROVED_BRANCH_EXCEPTION",
        "wordpress_runtime_compatibility":"Fresh declared fixture; production runtime match is not claimed"}
for _ in range(3):
    value=secrets.token_urlsafe(26)
    print("::add-mask::"+value,flush=True)
    if _==0: DB_PASSWORD=value
    elif _==1: DB_ROOT_PASSWORD=value
    else: ADMIN_PASSWORD=value

def run(args,timeout=180,env=None,allow_failure=False):
    RESULT["last_safe_command"]=[Path(str(a)).name for a in args[:2]]
    result=subprocess.run([str(a) for a in args],cwd=REPO,capture_output=True,timeout=timeout,env=env)
    (ROOT/("private-"+secrets.token_hex(5)+".log")).write_bytes(result.stdout+result.stderr)
    if result.returncode and not allow_failure:
        text=(result.stdout+result.stderr).decode(errors="replace")
        known=("manifest unknown","pull access denied","toomanyrequests","Could not resolve","Connection refused",
               "Permission denied","Block serialization mismatch","Page sanitization mismatch",
               "Unapproved existing-page scope","Exact Queue manifest fields and owner required",
               "Only scope-approved original captures with descriptive alt are approved",
               "Original full-size link and matching callout class required","Exact Queue figure class required",
               "Protected runtime drift","Managed-file drift","Bundle checksum mismatch","Parse error")
        RESULT["safe_command_categories"]=[value for value in known if value.lower() in text.lower()]
        missing=re.findall(r"Call to undefined function ([A-Za-z0-9_\\]+)\(",text)
        if missing:RESULT["missing_php_functions"]=missing
        categories=re.findall(rb"(?:RuntimeException: (FAIL: [^\r\n]+|Closed [^\r\n]+|Exact [^\r\n]+)|AssertionError: ([^\r\n]+))",result.stdout+result.stderr)
        if categories:
            RESULT.setdefault("safe_failure_labels",[]).extend((a or b).decode(errors="replace")[:180] for a,b in categories)
        raise RuntimeError("Cloud staging command failed in "+PHASE+"; raw diagnostics not exported")
    return result

def out(args,**kwargs):
    return run(args,**kwargs).stdout

def inspect(name):
    return json.loads(out(["docker","inspect",name]))[0]

def wp(*args,env=None,allow_failure=False,as_admin=True):
    command=["docker","exec"]
    for key,value in (env or {}).items():
        command+=["-e",key+"="+str(value)]
    command += [APP,"php","/tmp/wp-cli.phar","--allow-root","--path=/var/www/html"]
    if as_admin:command+=["--user=1"]
    command+=list(args)
    return run(command,allow_failure=allow_failure).stdout

def private_file(name,text):
    target=ROOT/name
    target.write_text(text,encoding="utf-8")
    target.chmod(0o600)
    return target

def copy_private(source,destination):
    out(["docker","cp",source,APP+":"+destination])

def file_state(root):
    state={}
    for p in sorted(root.rglob("*")):
        if p.is_symlink():raise RuntimeError("Unexpected fixture link")
        state[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else "DIRECTORY"
    return state

def release(mode,config):
    result=json.loads(out(["python3",str(ROOT/"bundle/release-growth-content.py"),
                            "--mode",mode,"--bundle",str(ROOT/"bundle"),"--config",str(config)]))
    assert result["status"]!="FAILED", "Release operator did not qualify"
    return result

try:
    assert SOURCE==os.environ.get("TN_SOURCE_SHA"), "Exact PR source checkout required"
    PHASE="public-assets"
    captures=json.loads((REPO/DIRECTORY/"captures.json").read_text())
    for shot in captures["captures"]:
        f=REPO/"site"/MEDIA/(shot["name"]+".png")
        assert hashlib.sha256(f.read_bytes()).hexdigest()==shot["sha256"]
    PHASE="preflight-downloads"
    images=["wordpress:7.1.4-php8.3-apache","wordpress:cli-2.12.0-php8.3","mariadb:11.4.13-noble"]
    RESULT["image_digests"]={}
    for image in images:
        out(["docker","pull",image],timeout=360)
        data=json.loads(out(["docker","image","inspect",image]))[0]
        RESULT["image_digests"][image]=data["RepoDigests"]
    pkg=ROOT/"node";browsers=ROOT/"browsers"
    node_env={**os.environ,"NODE_PATH":str(pkg/"node_modules"),"PLAYWRIGHT_BROWSERS_PATH":str(browsers)}
    out(["npm","install","--prefix",pkg,"--ignore-scripts","--no-audit","--no-fund","playwright@1.56.1"],timeout=300)
    out(["node",pkg/"node_modules/playwright/cli.js","install","--with-deps","chromium"],timeout=480,env=node_env)
    RESULT["playwright"]=out(["node","-e","process.stdout.write(require('playwright/package.json').version)"],env=node_env).decode()
    wp_root=ROOT/"wordpress";wp_root.mkdir(mode=0o755)
    content=wp_root/"wp-content"
    assert not any(p.is_symlink() for p in (REPO/"site").rglob("*")), "Source links refused"
    shutil.copytree(REPO/"site",content)
    css=content/"themes/tehnet/assets/css/visual-refresh.css"
    marker="\n/* Queue cloud: scoped callouts only; original screenshot bytes remain unchanged. */\n"
    assert css.read_text().count(marker)==1
    css.write_text(css.read_text().split(marker)[0],encoding="utf-8")
    assert hashlib.sha256(css.read_bytes()).hexdigest()==os.environ["TN_BASE_CSS_SHA256"]
    queue_dir=content/MEDIA
    for shot in captures["captures"]:
        p=queue_dir/(shot["name"]+".png")
        assert p.resolve().is_relative_to(content.resolve())
        p.unlink()
    queue_dir.rmdir()
    isolation=content/"mu-plugins/tn-cloud-isolation.php"
    assert not isolation.exists()
    isolation.write_text("""<?php
add_filter('pre_wp_mail','__return_false',PHP_INT_MIN);
add_filter('pre_http_request',static fn()=>new WP_Error('tn_cloud_blocked','Cloud fixture blocks outbound HTTP'),PHP_INT_MIN,3);
add_filter('woocommerce_available_payment_gateways','__return_empty_array',PHP_INT_MAX);
add_action('init',static function(){if(!post_type_exists('product'))register_post_type('product',['public'=>false,'label'=>'Synthetic cloud fixture only']);});
""")
    db_env=private_file("db.env","MARIADB_DATABASE=wordpress\nMARIADB_USER=wordpress\nMARIADB_PASSWORD="+DB_PASSWORD+"\nMARIADB_ROOT_PASSWORD="+DB_ROOT_PASSWORD+"\n")
    extra="define('WP_ENVIRONMENT_TYPE','staging'); define('WP_HTTP_BLOCK_EXTERNAL',true); define('DISABLE_WP_CRON',true); define('WP_HOME','http://localhost:18085'); define('WP_SITEURL','http://localhost:18085');"
    app_env=private_file("app.env","WORDPRESS_DB_HOST=db:3306\nWORDPRESS_DB_USER=wordpress\nWORDPRESS_DB_NAME=wordpress\nWORDPRESS_DB_PASSWORD="+DB_PASSWORD+"\nWORDPRESS_CONFIG_EXTRA="+extra+"\n")
    PHASE="internal-fixture-start"
    out(["docker","network","create","--internal",NET]);NETWORK_CREATED=True
    out(["docker","run","-d","--name",DB,"--network",NET,"--network-alias","db","--memory","1g","--cpus","1","--env-file",db_env,images[2]]);CONTAINERS.append(DB)
    ready=False
    for _ in range(40):
        if run(["docker","exec",DB,"healthcheck.sh","--connect","--innodb_initialized"],allow_failure=True).returncode==0:
            ready=True;break
        time.sleep(1)
    assert ready,"Fresh database readiness timeout"
    out(["docker","run","-d","--name",APP,"--network",NET,"--network-alias","wp","--memory","1g","--cpus","1",
         "--env-file",app_env,"-p","127.0.0.1:18085:80","-v",str(wp_root)+":/var/www/html",
         "-v",str(REPO)+":/srv/tehnet:ro",images[0]]);CONTAINERS.append(APP)
    for _ in range(40):
        if (wp_root/"wp-config.php").exists() and (wp_root/"wp-includes/version.php").exists():break
        time.sleep(1)
    assert (wp_root/"wp-config.php").exists(),"Fresh WordPress initialization timeout"
    out(["docker","create","--name",CLI,images[1]]);CONTAINERS.append(CLI)
    out(["docker","cp",CLI+":/usr/local/bin/wp",str(ROOT/"wp-cli.phar")])
    copy_private(str(ROOT/"wp-cli.phar"),"/tmp/wp-cli.phar")
    PHASE="synthetic-install"
    # Exactly one install attempt; no production dump or old credentials.
    wp("core","install","--url=http://localhost:18085","--title=TehNet — لاب ابری ساختگی",
       "--admin_user=tn_cloud_editor","--admin_password="+ADMIN_PASSWORD,"--admin_email=cloud-admin@example.invalid","--skip-email",as_admin=False)
    RESULT["wordpress"]=wp("core","version").decode().strip()
    assert RESULT["wordpress"]=="7.1.4"
    wp("theme","activate","tehnet")
    fixture=private_file("seed.php","""<?php
$repo='/srv/tehnet';
$body=file_get_contents($repo.'/content/educational-integrity-2026-11-04/queues-troubleshooting.html');
$items=[
[5,'home','خانه',0],[7,'lab','آزمایشگاه',0],[8,'services','خدمات',0],[9,'shop','فروشگاه',0],
[10,'learn','آموزش',0],[11,'mikrotik','میکروتیک',10],[12,'blog','مجله شبکه',0],[13,'contact','تماس با ما',0],
[40,'mtcna','MTCNA',11],[67,'queues-troubleshooting','Simple Queue و عیب‌یابی؛ راهنمای تکمیلی مستقل',40]];
foreach($items as[$id,$slug,$title,$parent]){
 $result=wp_insert_post(wp_slash(['import_id'=>$id,'post_type'=>'page','post_status'=>'publish','post_name'=>$slug,
 'post_title'=>$title,'post_parent'=>$parent,'post_content'=>$id===67?$body:'<!-- wp:paragraph --><p>TN synthetic cloud fixture</p><!-- /wp:paragraph -->',
 'post_excerpt'=>$id===67?'Simple Queue و عیب‌یابی در RouterOS؛ راهنمای نوشتاری تکمیلی مستقل، خارج از جلسات ضبط‌شدهٔ MTCNA.':'Synthetic fixture only']),true);
 if(is_wp_error($result)||$result!==$id)throw new RuntimeException('Exact synthetic page fixture failed');
 update_post_meta($id,'_tn_cloud_fixture','synthetic-only');
}
update_option('show_on_front','page');update_option('page_on_front',5);update_option('page_for_posts',12);update_option('woocommerce_shop_page_id',9);
update_option('blog_public',0);update_option('WPLANG','fa_IR');update_option('permalink_structure','/%postname%/');
$menu=wp_create_nav_menu('Cloud synthetic primary');
foreach([5,8,10,7,9]as$id)wp_update_nav_menu_item($menu,0,['menu-item-object-id'=>$id,'menu-item-object'=>'page','menu-item-type'=>'post_type','menu-item-status'=>'publish']);
set_theme_mod('nav_menu_locations',['primary'=>$menu]);
for($i=0;$i<25;$i++){$id=wp_insert_post(['post_type'=>'product','post_status'=>'draft','post_title'=>'TN synthetic product '.($i+1)]);if(!$id)throw new RuntimeException('Synthetic product fixture failed');update_post_meta($id,'_stock',100+$i);update_post_meta($id,'_tn_cloud_fixture','synthetic-only');}
if(!wp_save_post_revision(67))throw new RuntimeException('Synthetic revision fixture required');
echo 'CLOUD_FIXTURE_READY';
""")
    copy_private(str(fixture),"/tmp/tn-cloud-seed.php");wp("eval-file","/tmp/tn-cloud-seed.php")
    wp("rewrite","flush","--hard")
    (wp_root/".htaccess").write_text("<IfModule mod_rewrite.c>\nRewriteEngine On\nRewriteBase /\nRewriteRule ^index\\.php$ - [L]\nRewriteCond %{REQUEST_FILENAME} !-f\nRewriteCond %{REQUEST_FILENAME} !-d\nRewriteRule . /index.php [L]\n</IfModule>\n")
    snapshot=private_file("snapshot.php","""<?php
global$wpdb;$state=[];foreach(['posts','postmeta','users','usermeta']as$t){$key=$t==='postmeta'?'meta_id':($t==='usermeta'?'umeta_id':'ID');$state[$t]=$wpdb->get_results("SELECT * FROM {$wpdb->$t} ORDER BY $key",ARRAY_A);}
foreach(['blog_public','page_on_front','page_for_posts','woocommerce_shop_page_id','template','stylesheet']as$k)$state['options'][$k]=get_option($k);
echo hash('sha256',wp_json_encode($state));
""")
    copy_private(str(snapshot),"/tmp/tn-cloud-snapshot.php")
    baseline_rows=wp("eval-file","/tmp/tn-cloud-snapshot.php").decode().strip()
    PHASE="native-positive-negative"
    testroot="/tmp/tn-queue-cloud-native-"+JOB
    out(["docker","exec",APP,"mkdir","-m","700",testroot])
    out(["docker","exec",APP,"mkdir","-m","700",testroot+"/evidence"])
    env={"TN_TEST_MANIFEST":"/srv/tehnet/"+DIRECTORY+"/manifest.json",
         "TN_TEST_MIGRATION":"/srv/tehnet/ops/migrate-growth-content.php","TN_TEST_DIRECTORY":testroot+"/evidence"}
    result=wp("eval-file","/srv/tehnet/tests/cloud-queue-migration-native.php",env=env).decode()
    found=re.search(r"QUEUE_CLOUD_NATIVE=PASS checks=(\d+)",result)
    assert found,"Native test result missing"
    RESULT["native_checks"]=int(found[1])
    assert wp("eval-file","/tmp/tn-cloud-snapshot.php").decode().strip()==baseline_rows,"Native tests must restore original fixture rows"
    PHASE="before-browser"
    before=ROOT/"before-browser"
    out(["node","tests/cloud-queue-site-readonly.cjs",before],timeout=240,
        env={**node_env,"TN_SERVICE_ORIGIN":"http://localhost:18085","TN_SERVICE_BEFORE":"1"})
    RESULT["before_browser_checks"]=json.loads((before/"before-browser.json").read_text())["passed"]
    PHASE="immutable-bundle"
    out(["git","fetch","--no-tags","--depth=1","origin",BASE],timeout=90)
    out(["python3","ops/release-growth-content.py","--mode","bundle","--repo",REPO,"--bundle",ROOT/"bundle",
         "--source-commit",SOURCE,"--baseline-commit",BASE,"--scope",SCOPE])
    bundle=json.loads((ROOT/"bundle/bundle.json").read_text())
    app=inspect(APP);db=inspect(DB)
    config={"environment":"staging","app":APP,"db":DB,"app_id":app["Id"],"db_id":db["Id"],"network":NET,
            "staging_app_bindings":app["HostConfig"]["PortBindings"],"source_commit":SOURCE,"baseline_commit":BASE,
            "bundle_manifest_sha256":hashlib.sha256((ROOT/"bundle/bundle.json").read_bytes()).hexdigest(),
            "release_dir":str(ROOT/"release"),"wp_cli":"/tmp/wp-cli.phar","wp_user":"1"}
    configpath=private_file("config.json",json.dumps(config))
    files_before=file_state(content)
    rows_before=wp("eval-file","/tmp/tn-cloud-snapshot.php").decode().strip()
    PHASE="canonical-release"
    checked=release("check",configpath);assert checked["status"]=="READY"
    applied=release("apply",configpath);assert applied["status"]=="APPLIED" and applied["files_changed"]==13
    repeated=release("apply",configpath);assert repeated["files_changed"]==0
    result=wp("eval-file","/srv/tehnet/tests/cloud-queue-renderer-native.php").decode()
    found=re.search(r"QUEUE_CLOUD_RENDERER=PASS checks=(\d+)",result)
    assert found,"Native renderer result missing"
    RESULT["renderer_checks"]=int(found[1])
    PHASE="after-browser"
    after=ROOT/"after-browser"
    out(["node","tests/cloud-queue-site-readonly.cjs",after],timeout=300,
        env={**node_env,"TN_SERVICE_ORIGIN":"http://localhost:18085","TN_SERVICE_BEFORE":"0"})
    browser=json.loads((after/"browser.json").read_text())
    RESULT["browser_checks"]=browser["passed"]
    assert browser["status"]=="PASS" and browser["submissions"]==0
    PHASE="canonical-rollback"
    rolled=release("rollback",configpath);assert rolled["status"]=="ROLLED_BACK"
    again=release("rollback",configpath);assert again["status"]=="ROLLED_BACK"
    assert file_state(content)==files_before,"All original fixture files and directories must restore"
    assert wp("eval-file","/tmp/tn-cloud-snapshot.php").decode().strip()==rows_before,"All original fixture data rows must restore"
    ledger=json.loads((ROOT/"release/release-private.json").read_text())
    assert ledger["backup_checksum_verified"] is True
    RESULT.update(status="VERIFIED_SYNTHETIC_CLOUD_STAGING_NOT_DEPLOYED",files_applied=13,repeat_files=0,
                  original_fixture_rows_restored=True,original_fixture_files_restored=True,
                  fresh_private_backup_checksum_verified=True,submissions=0,
                  isolation={"docker_internal_network":True,"loopback_http_only":True,"mail_http_cron_payments_blocked":True},
                  limits=["Synthetic fixture only; no production database or customer data used.",
                          "Exact production runtime match is not established; live release remains separately gated.",
                          "This is not a complete SQL disaster-recovery exercise or commercial/SEO parity proof."])
    RESULT["screenshots"]={}
    for folder in (before,after):
        for p in sorted(folder.glob("*.png")):
            key=p.name
            RESULT["screenshots"][key]=hashlib.sha256(p.read_bytes()).hexdigest()
            # Only synthetic cloud WordPress rendering of public lesson source and approved original lab images.
            if key in ("after-67-375-light.png","callout-67-375-light.png","after-67-1440-light.png"):
                assert p.stat().st_size<2*1024*1024
                print("TN_STAGE_IMAGE "+json.dumps({"name":key,"sha256":RESULT["screenshots"][key],
                      "synthetic_cloud_fixture_only":True,"base64":base64.b64encode(p.read_bytes()).decode()}),flush=True)
except BaseException as error:
    RESULT.update(status="FAILED",failed_phase=PHASE,error_type=type(error).__name__,
                  error_message=str(error)[:200] if isinstance(error,(AssertionError,RuntimeError)) else "See safe phase classification",
                  raw_diagnostics_exported=False)
finally:
    for name in reversed(CONTAINERS):
        run(["docker","rm","--force","--volumes",name],allow_failure=True)
    if NETWORK_CREATED:run(["docker","network","rm",NET],allow_failure=True)
    RESULT["task_containers_removed"]=all(run(["docker","inspect",name],allow_failure=True).returncode!=0 for name in CONTAINERS)
    RESULT["task_network_removed"]=(not NETWORK_CREATED or run(["docker","network","inspect",NET],allow_failure=True).returncode!=0)
    if not RESULT["task_containers_removed"] or not RESULT["task_network_removed"]:
        RESULT.update(status="FAILED",failed_phase="cleanup")
    RESULT["private_diagnostics_lifetime"]="Ephemeral job only; raw logs are not exported and are deleted at teardown"
    RESULT["completed_utc"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
    print("TN_STAGE_RECEIPT "+json.dumps(RESULT),flush=True)
    assert ROOT.parent==Path("/tmp") and ROOT.name.startswith("tn-queue-cloud-stage-")
    shutil.rmtree(ROOT)
if RESULT["status"]=="FAILED":raise SystemExit(1)
