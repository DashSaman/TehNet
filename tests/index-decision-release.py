"""Index runtime/activation exercised only inside the existing disposable cloud fixture."""
import importlib.util,json,os,subprocess,sys
from pathlib import Path
spec=importlib.util.spec_from_file_location("tn_release","ops/release-growth-content.py");op=importlib.util.module_from_spec(spec);spec.loader.exec_module(op)
lab=Path(sys.argv[1]);phase=sys.argv[2];source=os.environ["GITHUB_SHA"];baseline="6d54fe885e33f37540e8143630ff93af5c63e6b5"
if os.environ.get("RUNNER_ENVIRONMENT")!="github-hosted" or os.environ.get("GITHUB_REPOSITORY")!="DashSaman/TehNet":raise RuntimeError("Managed synthetic runner required")
scopes=[op.INDEX_RUNTIME_SCOPE,op.INDEX_ACTIVATION_SCOPE]
def cfg(scope):return lab/("index-runtime" if scope==scopes[0] else "index-activation")
def run(scope,mode):
 root=cfg(scope);release=op.Release(root/"config.json",root/"bundle")
 try:
  result=release.execute(mode)
  print("TN_INDEX_PUBLISHER "+json.dumps({"scope":scope,"mode":mode,"result":result,"production_mutations":0}))
  return result
 except BaseException:
  release.log.flush();log=(root/"private-release/commands-private.log").read_text(errors="replace");print("TN_INDEX_SYNTHETIC_DIAGNOSTIC\n"+log.replace(os.environ.get("TN_FIXTURE_PASSWORD","NEVER_EMPTY"),"[MASKED]")[-6500:]);raise
if phase=="prepare":
 for scope in scopes:
  root=cfg(scope);root.mkdir(mode=0o700);op.build_bundle(Path.cwd(),root/"bundle",source,baseline,scope)
  base=json.loads((lab/"config.json").read_text());base.update(bundle_manifest_sha256=op.file_digest(root/"bundle/bundle.json"),release_dir=str(root/"private-release"));(root/"config.json").write_text(json.dumps(base));(root/"config.json").chmod(0o600)
  if scope==scopes[0]:
   m=json.loads((root/"bundle/bundle.json").read_text())
   for rel,row in m["files"].items():
    dst=lab/"web/wp-content"/rel.removeprefix("site/")
    if row["old"] is None:
     if dst.is_file():dst.unlink()
    else:dst.write_bytes(subprocess.check_output(["git","show",baseline+":"+rel]))
elif phase=="runtime":
 r=run(scopes[0],"check");assert r["status"]=="READY";r=run(scopes[0],"apply");assert r["status"]=="APPLIED" and r["content"]["option_writes"]==0
 r=run(scopes[0],"apply");assert r["files_changed"]==0
elif phase=="activate":
 r=run(scopes[1],"check");assert r["content"]["approved_paths"]==16
 r=run(scopes[1],"apply");assert r["files_changed"]==0 and r["content"]["option_writes"]==1
 r=run(scopes[1],"apply");assert r["files_changed"]==0 and r["content"]["option_writes"]==0
elif phase=="rollback":
 r=run(scopes[1],"rollback");assert r["content"]["option_restored"]
 r=run(scopes[0],"rollback");assert r["status"]=="ROLLED_BACK"
else:raise RuntimeError("Unknown index fixture phase")
