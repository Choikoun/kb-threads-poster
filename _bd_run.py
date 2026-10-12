import subprocess, sys
for k in ['퇴직연금디폴트옵션','증여세율표']:
    r=subprocess.run([sys.executable,'_bd.py',k],capture_output=True,text=True,encoding='utf-8')
    open(f'_bd_{k}.log','w',encoding='utf-8').write(r.stdout+r.stderr)
print('ALL DONE')
