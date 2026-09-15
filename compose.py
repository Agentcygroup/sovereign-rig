#!/usr/bin/env python3
import json,glob,os,sys,subprocess
def dm(a,b):
    o=dict(a)
    for k,v in b.items():
        if k=="attributes" and isinstance(v,dict):
            o[k]=dm(o.get(k,{}),v)
        else:
            o[k]=v
    return o
layers=(["layers/base.machine.json"]+sorted(glob.glob("layers/models/*.json"))
        +["layers/rig.json","layers/session.metadusa.json"])
idx,sel={},{}
for lf in layers:
    d=json.load(open(lf))
    for p,pr in d.get("prims",{}).items():
        if "variantSets" in pr: idx.setdefault(p,{})["variantSets"]=pr["variantSets"]
        else: idx[p] =dm(idx.get(p,{}),pr)
    sel.update(d.get("variantSelection",{}))
    for p,a in d.get("overrides",{}).items(): idx[p] =dm(idx.get(p,{}),{"attributes":a})
for p,sets in sel.items():
    vs=idx.get(p,{}).get("variantSets",{}); ch={}
    for sn,vn in sets.items():
        vp=vs.get(sn,{}).get(vn) or sys.exit(f"unknown variant {sn}={vn}")
        ch=dm(ch,vp)
    idx[p] =dm({k:v for k,v in idx.get(p, {}).items() if k!="variantSets"},ch)
def res(p,seen=frozenset()):
    if p in seen: sys.exit(f"cycle at {p}")
    pr=json.loads(json.dumps(idx.get(p, {}))); m={}
    for r in pr.pop("references",[]): m=dm(m,res(r,seen|{p}))
    m=dm(m,{k:v for k,v in pr.items() if k!="payload"})
    if "payload" in pr: m["payload"]=pr["payload"]
    return m
for p in sorted(glob.glob("layers/models/*.json")):
    r=subprocess.run(["python3",os.path.expanduser("~/hf-harness/harness.py"),p],capture_output=True,text=True)
    if r.returncode: sys.exit(f"harness rejected {p}:\n{r.stdout}")
machine,server,rig=res("/machine"),res("/server"),res("/rig")
active=[res(x) for x in rig.get("references", [])]
total=sum(m["attributes"]["sizeGB"] for m in active); budget=machine["attributes"]["memoryBudgetGB"]
print(f"composed: {[m['attributes']['task'] for m in active]} ({total}GB/{budget}GB {'ok' if total<=budget else 'OVER BUDGET'})")
blocks=[]
for m in active:
    a,pay=m["attributes"],os.path.expanduser(m.get("payload",""))
    if a["server"]=="llama":
        blocks.append(f'nohup llama-server -t 12 -fa on --models-dir "$HOME/.llama/models" --host {server["attributes"]["host"]} --port {server["attributes"]["port"]} --ctx-size {server["attributes"]["ctxSize"]} --n-gpu-layers {server["attributes"]["gpuLayers"]} --models-max {server["attributes"]["modelsMax"]} > "$HOME/.llama/router.log" 2>&1 &')
    elif a["server"]=="whisper":
        blocks.append(f'nohup whisper-server --model {pay} --host {server["attributes"]["host"]} --port {a["port"]} > "$HOME/.whisper/server.log" 2>&1 &')
    elif a["server"]=="sd":
        blocks.append(f'command -v sd-server >/dev/null && nohup sd-server --model {pay} --host {server["attributes"]["host"]} --port {a["port"]} > "$HOME/.sd/server.log" 2>&1 &')
open("composed-server.sh","w").write("#!/usr/bin/env bash\nset -euo pipefail\npkill -f 'llama-server|whisper-server|sd-server' 2>/dev/null || true\nsleep 1\n"+"\n".join(blocks)+'\nfor i in $(seq 1 120); do curl -sf http://127.0.0.1:8080/health >/dev/null 2>&1 && break; sleep 1; done\necho "[ok] stage up"\n')
prim=next((m for m in active if m.get("attributes", {}).get("server")=="llama"), {})
print("wrote: composed-server.sh, ~/.pi/agent/llama.json")
