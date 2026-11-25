#!/usr/bin/env python3
"""Resumable sequential Inkling 2 Mini run over p01-p15. One llama-server (-np 1), one request at a time."""
import json,os,re,subprocess,sys,time,urllib.request
sys.path.insert(0,os.environ.get('DBENCH','.'))
from bench import run as R, grade
A='/content/inkling'; O=os.environ.get('INKLING_OUT',os.path.expanduser('~/research-artifacts/inkling-full-20261122'))
PORT=18431; N_PREDICT=int(os.environ.get('INKLING_NPREDICT','12288'))
PIDS=sorted(f[:-3] for f in os.listdir(os.path.join(os.environ.get('DBENCH','.'),'bench','problems')) if re.match(r'p\d\d_',f))
def memavail(): return int([l for l in open('/proc/meminfo') if l.startswith('MemAvailable')][0].split()[1])/1048576
def rss(pid):
    d={}
    for l in open(f'/proc/{pid}/status'):
        if l.startswith(('VmRSS','RssAnon','RssFile','VmHWM')): k,v=l.split(':'); d[k]=int(v.split()[0])
    return d
def start():
    env=dict(os.environ,LD_LIBRARY_PATH=A+'/llama-b12600:/usr/lib64-nvidia')
    p=subprocess.Popen([A+'/llama-b12600/llama-server','-m',A+'/Inkling-2-Mini-IQ4_NL.gguf','--jinja','-c','32768','-t','6','-tb','6','-np','1','-ngl','99',
      '--temp','1.0','--top-k','50','--top-p','1.0','--min-p','0','--port',str(PORT),'--host','127.0.0.1'],env=env,stdout=open(O+'/server.log','a'),stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL)
    for _ in range(600):
        try: urllib.request.urlopen(f'http://127.0.0.1:{PORT}/health',timeout=2); return p
        except Exception: time.sleep(2)
    raise SystemExit('server did not start')
def main():
    srv=None; todo=[x for x in PIDS if not os.path.exists(f'{O}/{x}.result.json') and (not os.environ.get('INKLING_ONLY') or x[:3] in os.environ['INKLING_ONLY'].split(','))]
    for pid in todo:
        if memavail()<10: json.dump({'pid':pid,'aborted':'MemAvailable<10GiB','memavail_gib':memavail()},open(f'{O}/{pid}.result.json','w')); continue
        if srv is None: srv=start()
        prompt=R.prompt_for(pid); la=open('/proc/loadavg').read().split()[:3]
        EFF=os.environ.get('INKLING_EFFORT')
        req={'messages':[{'role':'user','content':prompt}],'max_tokens':N_PREDICT,'temperature':1.0,'top_k':50,'top_p':1.0,'min_p':0,'stream':False}
        if EFF: req['chat_template_kwargs']={'reasoning_effort':EFF}
        body=json.dumps(req).encode()
        t0=time.monotonic(); peak=0; err=None; resp={}
        import threading
        stop=threading.Event(); pk=[0]
        def mon():
            pass
            while not stop.is_set():
                pk[0]=max(pk[0],rss(srv.pid).get('VmHWM',0)); time.sleep(5)
        th=threading.Thread(target=mon,daemon=True); th.start()
        try: resp=json.load(urllib.request.urlopen(urllib.request.Request(f'http://127.0.0.1:{PORT}/v1/chat/completions',body,{'Content-Type':'application/json'}),timeout=4*3600))
        except Exception as e: err=repr(e)
        stop.set(); wall=time.monotonic()-t0
        m=(resp.get('choices') or [{}])[0]; msg=m.get('message',{}); content=msg.get('content') or ''; think=msg.get('reasoning_content') or ''
        tm=resp.get('timings',{}); us=resp.get('usage',{})
        blocks=re.findall(r'```(?:python)?\s*\n(.*?)```',content,re.S|re.I); code=blocks[-1].strip() if blocks else ''
        v=grade.grade_text(pid,code) if code else {'outcome':'no_code','detail':'no final fenced python block; finish_reason=%s'%m.get('finish_reason')}
        open(f'{O}/{pid}.raw.txt','w').write('=== REASONING ===\n'+think+'\n=== CONTENT ===\n'+content)
        json.dump({'pid':pid,'effort':EFF or 'default','max_tokens':N_PREDICT,'wall_s':wall,'loadavg_start':la,'finish_reason':m.get('finish_reason'),'prompt_tok':us.get('prompt_tokens'),'out_tok':us.get('completion_tokens'),
          'gen_tps':tm.get('predicted_per_second'),'prompt_tps':tm.get('prompt_per_second'),'peak_rss_kib':pk[0],'rss_end':rss(srv.pid),'memavail_gib_end':memavail(),
          'reasoning_chars':len(think),'verdict':v,'error':err,'code_lines':len(code.splitlines())},open(f'{O}/{pid}.result.json','w'),indent=1)
        print(pid,v.get('outcome'),round(wall),flush=True)
    if srv: srv.terminate()
main()
