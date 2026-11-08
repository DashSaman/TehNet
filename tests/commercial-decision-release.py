"""Cloud-only integration of the existing immutable bundle publisher; no production config."""
import importlib.util,json,os,subprocess,sys
from pathlib import Path
spec=importlib.util.spec_from_file_location("tn_release", "ops/release-growth-content.py")
op=importlib.util.module_from_spec(spec);spec.loader.exec_module(op)
lab=Path(sys.argv[1]);phase=sys.argv[2];repo=Path.cwd();source=os.environ["GITHUB_SHA"];baseline="6d54fe885e33f37540e8143630ff93af5c63e6b5"
app,db=os.environ["TN_STAGE_APP"],os.environ["TN_STAGE_DB"]
if os.environ.get("RUNNER_ENVIRONMENT")!="github-hosted" or os.environ.get("GITHUB_REPOSITORY")!="DashSaman/TehNet":raise RuntimeError("Managed synthetic runner required")
if phase=="prepare":
 op.build_bundle(repo,lab/"bundle",source,baseline,op.DECISION_SCOPE)
 m=json.loads((lab/"bundle/bundle.json").read_text())
 for rel,row in m["files"].items():
  dst=lab/"web/wp-content"/rel.removeprefix("site/")
  if row["old"] is None:
   if dst.is_file():dst.unlink()
  else:dst.write_bytes(subprocess.check_output(["git","show",baseline+":"+rel]))
 config={"environment":"staging","app":app,"db":db,"app_id":op.Release.inspect if False else json.loads(subprocess.check_output(["docker","inspect",app]))[0]["Id"],"db_id":json.loads(subprocess.check_output(["docker","inspect",db]))[0]["Id"],"network":os.environ["TN_STAGE_NET"],"staging_app_bindings":{},"source_commit":source,"baseline_commit":baseline,"bundle_manifest_sha256":op.file_digest(lab/"bundle/bundle.json"),"release_dir":str(lab/"private-release"),"wp_cli":"/lab/wp","wp_user":"1"}
 (lab/"config.json").write_text(json.dumps(config));(lab/"config.json").chmod(0o600)
elif phase in ("apply","rollback"):
 release=op.Release(lab/"config.json",lab/"bundle")
 try:
  if phase=="apply":
   check=release.execute("check");assert check["status"]=="READY" and check["content"]["pages_pending"]==5 and check["content"]["hubs_pending"]==5
   result=release.execute("apply");assert result["content"]["pages_created"]==5 and result["content"]["hubs_updated"]==5
   repeated=release.execute("apply");assert repeated["files_changed"]==0 and repeated["content"]["pages_created"]==0
   print("TN_DECISION_PUBLISHER "+json.dumps({"status":"PASS","scope":op.DECISION_SCOPE,"check":check,"apply":result,"repeat":repeated,"production_mutations":0}))
  else:
   result=release.execute("rollback");assert result["status"]=="ROLLED_BACK" and result["content"]["hubs_restored"]==5 and result["content"]["pages_drafted"]==5
   again=release.execute("rollback");assert again["content"]["hubs_restored"]==0
   print("TN_DECISION_PUBLISHER "+json.dumps({"status":"PASS","rollback":result,"repeat_rollback":again,"new_pages_retained_as_drafts":True,"production_mutations":0}))
 except BaseException:
  release.log.flush()
  # Only failure diagnostics from this disposable synthetic fixture; password masked.
  log=(lab/"private-release/commands-private.log").read_text(errors="replace")
  safe=log.replace(os.environ.get("TN_FIXTURE_PASSWORD","NEVER_EMPTY"),"[MASKED]")
  print("TN_DECISION_SYNTHETIC_DIAGNOSTIC\n"+safe[-6000:]);raise
else:raise RuntimeError("Unknown fixture operation")
