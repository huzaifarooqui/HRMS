import os, shutil, subprocess, zipfile
from datetime import datetime
from dotenv import load_dotenv

BASE=os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE,".env"))
PROJECT=os.path.dirname(BASE)
DATA_ROOT=os.getenv("HRMS_DATA_ROOT",os.path.join(os.path.dirname(PROJECT),"GRSJ-HRMS_DATA"))
BACKUP=os.path.join(DATA_ROOT,"backups")
UPLOADS=os.path.join(DATA_ROOT,"uploads")
os.makedirs(BACKUP,exist_ok=True)
stamp=datetime.now().strftime("%Y%m%d_%H%M%S")
sql=os.path.join(BACKUP,f"game_db_{stamp}.sql")
zip_path=os.path.join(BACKUP,f"GRSJ_HRMS_Backup_{stamp}.zip")

db=os.getenv("DB_NAME","game_db")
user=os.getenv("DB_USER","root")
host=os.getenv("DB_HOST","localhost")
password=os.getenv("DB_PASSWORD","")

dump=shutil.which("mysqldump")
if dump:
    cmd=[dump,"-h",host,"-u",user,f"-p{password}",db,"--routines","--events","--single-transaction"]
    with open(sql,"wb") as f:
        subprocess.run(cmd,stdout=f,stderr=subprocess.PIPE,check=True)

with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
    if os.path.isfile(sql): z.write(sql,os.path.basename(sql))
    if os.path.isdir(UPLOADS):
        for root,_,files in os.walk(UPLOADS):
            for name in files:
                p=os.path.join(root,name)
                z.write(p,os.path.join("uploads",os.path.relpath(p,UPLOADS)))
if os.path.isfile(sql):
    try: os.remove(sql)
    except OSError: pass
print(zip_path)
