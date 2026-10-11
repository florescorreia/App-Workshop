"""Prepare reviewable Quadlets only. Never contacts or mutates the VPS."""
import argparse,re,json
from pathlib import Path
import yaml
p=argparse.ArgumentParser();p.add_argument('--compose',required=True);p.add_argument('--output',required=True);p.add_argument('--account',required=True);p.add_argument('--images',required=True);a=p.parse_args()
if not re.fullmatch(r'governed-dd(?:-[a-f0-9]{24})?',a.account):raise ValueError('Dedicated governed-dd account required')
c=yaml.safe_load(Path(a.compose).read_text());pins=json.loads(Path(a.images).read_text());out=Path(a.output)
if out.exists():raise ValueError('Fresh review output directory required')
out.mkdir(parents=True);project=c['name'];target='app-'+project+'.target';members=[]
def write(name,lines): (out/name).write_text('\n'.join(lines)+'\n')
for name,n in c['networks'].items():
 lines=['[Network]','NetworkName='+n['name']]
 if n.get('internal'):lines.append('Internal=true')
 for ipam in n.get('ipam',{}).get('config',[]):lines.append('Subnet='+ipam['subnet'])
 write(project+'-'+name+'.network',lines)
for name,v in c['volumes'].items():write(project+'-'+name+'.volume',['[Volume]','VolumeName='+v['name']])
for name,s in c['services'].items():
 unit=project+'-'+name;members.append(unit+'.service')
 image=pins.get(s['image'],s['image'])
 if '@sha256:' not in image and not re.fullmatch('sha256:[a-f0-9]{64}',image):raise ValueError('Missing immutable image pin for '+s['image'])
 dependencies=list(s.get('depends_on',{}));depunits=' '.join(project+'-'+d+'.service' for d in dependencies)
 lines=['[Unit]','Description=Governed DD '+name,'PartOf='+target]
 if depunits:lines+=['After='+depunits,'Requires='+depunits]
 lines+=['[Container]','Image='+image,'ContainerName='+unit,'EnvironmentFile=%h/.config/governed-dd/'+name+'.env']
 nets=s.get('networks',[]);nets={n:{} for n in nets} if isinstance(nets,list) else nets
 for net,options in nets.items():
  lines.append('Network='+project+'-'+net+'.network')
  for alias in (options or {}).get('aliases',[]):lines.append('NetworkAlias='+alias)
 for mount in s.get('volumes',[]):
  src,dest,*options=mount.split(':');src=project+'-'+src+'.volume' if src in c['volumes'] else '%h/.config/governed-dd/assets/'+Path(src).name
  lines.append('Volume='+':'.join([src,dest]+options))
 for secret in s.get('secrets',[]):
  source=secret if isinstance(secret,str) else secret['source'];dest=source if isinstance(secret,str) else secret.get('target',source)
  lines.append('Volume=%h/.config/governed-dd/secrets/'+source+':/run/secrets/'+dest+':ro')
 if name=='gateway':lines.append('PublishPort=127.0.0.1:18082:8080')
 if s.get('command'):lines.append('Exec='+' '.join(s['command']))
 if s.get('cap_drop'):lines+=['DropCapability='+cap for cap in s['cap_drop']]
 if s.get('user'):lines.append('User='+str(s['user']))
 for mount in s.get('tmpfs',[]):lines.append('Tmpfs='+mount)
 health=s.get('healthcheck',{});test=health.get('test',[])
 if test:
  import shlex
  command=test[1] if test[0]=='CMD-SHELL' else ' '.join(shlex.quote(str(v)) for v in test[1:])
  lines+=['HealthCmd='+command,'HealthInterval='+health.get('interval','10s'),'HealthRetries='+str(health.get('retries',30))]
 memory=s.get('mem_limit','512m');cpu=s.get('cpus',1)
 lines+=['PodmanArgs=--memory='+str(memory)+' --cpus='+str(cpu)+' --pids-limit='+str(s.get('pids_limit',256))+' --security-opt=no-new-privileges','[Service]']
 for dep in dependencies:
  if isinstance(s.get('depends_on'),dict) and s['depends_on'][dep].get('condition')=='service_healthy':
   lines.append('ExecStartPre=%h/.config/governed-dd/wait-healthy.sh '+project+'-'+dep)
 lines+=['Restart=on-failure','TimeoutStartSec=600','TimeoutStopSec=120','[Install]','WantedBy='+target]
 write(unit+'.container',lines)
write(target,['[Unit]','Description=Governed DD '+project,'Requires='+' '.join(members),'After='+' '.join(members),'[Install]','WantedBy=default.target'])
write('wait-healthy.sh',['#!/bin/sh','set -eu','case "$1" in governed-dd-*) ;; *) exit 2;; esac','attempt=0','while [ "$attempt" -lt 120 ]; do',' status=$(podman inspect --format "{{.State.Health.Status}}" "$1")',' [ "$status" = healthy ] && exit 0',' attempt=$((attempt+1)); sleep 2','done','echo "Dependency readiness timed out" >&2; exit 1'])
write('REVIEW_REQUIRED.md',['# Prepared release; not deployed','Account: '+a.account,'Review private ingress between rootless accounts, network isolation, readiness health gates, DNS/TLS and environment files before installation.','Keycloak start-dev must be replaced with a production build/start command.','Do not expose model keys to Paperclip or inject host SSH credentials.'])
print('Reviewable app-specific Quadlet inventory prepared; no deployment performed.')
