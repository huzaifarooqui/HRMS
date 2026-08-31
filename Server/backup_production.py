import os, shutil, subprocess, zipfile
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

ROOT=Path(__file__).resolve().parents[1]
SERVER=ROOT/'Server'
BACKUPS=ROOT/'Backups'
BACKUPS.mkdir(exist_ok=True)
load_dotenv(SERVER/'.env')

def find_mysqldump():
    found=shutil.which('mysqldump')
    if found:return Path(found)
    candidates=[
        Path(r'C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqldump.exe'),
        Path(r'C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe'),
    ]
    for p in candidates:
        if p.exists():return p
    raise FileNotFoundError('mysqldump.exe was not found. Add MySQL bin folder to PATH.')

def prune(pattern,keep):
    files=sorted(BACKUPS.glob(pattern),key=lambda p:p.stat().st_mtime,reverse=True)
    for p in files[keep:]:
        try:p.unlink()
        except OSError:pass

def database_backup(stamp):
    exe=find_mysqldump()
    host=os.getenv('DB_HOST','127.0.0.1'); port=os.getenv('DB_PORT','3306'); user=os.getenv('DB_USER','root'); password=os.getenv('DB_PASSWORD',''); db=os.getenv('DB_NAME','game_db')
    out=BACKUPS/f'grsj_db_{stamp}.sql'
    cmd=[str(exe),f'--host={host}',f'--port={port}',f'--user={user}',f'--password={password}','--single-transaction','--routines','--triggers','--events','--default-character-set=utf8mb4',db]
    with out.open('wb') as f:
        subprocess.run(cmd,stdout=f,stderr=subprocess.PIPE,check=True)
    return out

def project_backup(stamp):
    out=BACKUPS/f'GRSJ-HRMS_project_{stamp}.zip'
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for p in ROOT.rglob('*'):
            if not p.is_file():continue
            rel=p.relative_to(ROOT)
            if rel.parts and rel.parts[0] in {'Backups','.venv'}:continue
            if p.name in {'waitress.log'} or '__pycache__' in rel.parts:continue
            z.write(p,rel)
    return out

def main():
    now=datetime.now();stamp=now.strftime('%Y-%m-%d_%H%M%S')
    db=database_backup(stamp);print(f'Database backup: {db}')
    # Project ZIP once a week on Sunday; database still backs up every day.
    if now.weekday()==6:
        project=project_backup(stamp);print(f'Project backup: {project}')
    prune('grsj_db_*.sql',30);prune('GRSJ-HRMS_project_*.zip',10)

if __name__=='__main__':main()
