"""Run the unchanged native offline lab with one candidate's fixed transport.

Requires the outer bounded systemd unit and a private mount namespace. All
package/index/rootfs bytes remain in the existing noswap RAM laboratory.
"""
from pathlib import Path
import os,subprocess

OLD='''if os.environ.get('SOFTWARE_REFRESH_BUDGET_FILE'):
 from tools.refresh_transport import install_budget_hook
 install_budget_hook(os.environ['SOFTWARE_REFRESH_BUDGET_FILE'])
start=time.monotonic();result=prepare(profile,root/'kit',require_accepted=False)'''
NEW='''from app.provider_kit import selected_transport
observations=[];start=time.monotonic()
try:
 with selected_transport(profile,os.environ['PROVIDER_ID'],allow_candidate=True,observations=observations):
  if os.environ.get('SOFTWARE_REFRESH_BUDGET_FILE'):
   from tools.refresh_transport import install_budget_hook
   install_budget_hook(os.environ['SOFTWARE_REFRESH_BUDGET_FILE'])
  result=prepare(profile,root/'kit',require_accepted=False)
finally:
 (ops/'metadata/provider-downloads.json').write_text(json.dumps({'provider':os.environ['PROVIDER_ID'],'observations':observations},indent=2)+'\\n')'''

def render_lab(source):
    if source.count(OLD)!=1:raise ValueError('Reviewed native lab preparation seam changed')
    result=source.replace(OLD,NEW)
    result=result.replace("'baseline_and_kit_source':'official signed Ubuntu Base + original approved Arvan Ubuntu main/universe'","'baseline_and_kit_source':'official signed Ubuntu Base; exact signed profile bytes from selected '+os.environ['PROVIDER_ID']")
    return result

def main():
    if os.environ['PROVIDER_ID'] not in {'arvan','linuxmirrors','liara','hamravesh'}:raise ValueError('Fixed candidate required')
    source=(Path(__file__).resolve().parents[1]/'deployment/qualification/run-devtools-lab.sh').read_text()
    result=subprocess.run(['bash'],input=render_lab(source),text=True)
    raise SystemExit(result.returncode)

if __name__=='__main__':main()
