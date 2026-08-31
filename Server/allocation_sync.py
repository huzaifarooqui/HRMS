import os
import re
import json
import time
import hashlib
import logging
import subprocess
from datetime import datetime
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

KOOFR_ROOT = r"C:\Users\Lenovo\Koofr"
LEGACY_APPROVED_FOLDERS = ("Fazil", "Harshit Kumar", "Heena", "Lucky")
EMPLOYEE_FOLDER_EXCLUSIONS = {"huzaifa", "synctrash"}
VALID_EXTENSIONS = (".xlsb", ".xlsx", ".xlsm", ".xls")
SCAN_SECONDS = 45
STABLE_WAIT_SECONDS = 8
LOG_FILE = os.path.join(BASE_DIR, "allocation_sync.log")
PS_READER = os.path.join(BASE_DIR, "read_performance.ps1")
ADMIN_SOURCE = r"C:\Users\Lenovo\Koofr\Huzaifa\Master Allocation Aug'2026.xlsb"
ADMIN_PS_READER = os.path.join(BASE_DIR, "read_admin_performance.ps1")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

def db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "game_db"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        autocommit=False,
    )

def norm(value):
    return re.sub(r"[^a-z0-9]+", "", (value or "").lower())

def active_employees():
    cnx = db()
    cur = cnx.cursor(dictionary=True)
    try:
        cur.execute("""SELECT id,first_name,last_name
                       FROM employees
                       WHERE status='Active'
                       ORDER BY id""")
        return cur.fetchall()
    finally:
        cur.close()
        cnx.close()

def root_employee_folders():
    """Return only immediate Koofr root folders, excluding Huzaifa and SyncTrash."""
    if not os.path.isdir(KOOFR_ROOT):
        return []
    folders=[]
    for name in os.listdir(KOOFR_ROOT):
        path=os.path.join(KOOFR_ROOT,name)
        if not os.path.isdir(path):
            continue
        if name.strip().lower() in EMPLOYEE_FOLDER_EXCLUSIONS:
            continue
        folders.append(name)
    return folders

def discover_folder_for_employee(employee, folders=None):
    """
    Auto-map an active HRMS employee to a same-name Koofr folder.
    Priority:
      1) exact normalized full name
      2) exact normalized first name, only when unambiguous
    """
    folders = folders if folders is not None else root_employee_folders()
    full = f"{employee.get('first_name') or ''} {employee.get('last_name') or ''}".strip()
    full_key = norm(full)
    first_key = norm(employee.get('first_name') or '')

    exact_full=[f for f in folders if norm(f)==full_key]
    if len(exact_full)==1:
        return exact_full[0]

    exact_first=[f for f in folders if norm(f)==first_key]
    if len(exact_first)==1:
        return exact_first[0]

    return None

def resolve_employee(folder_name):
    cnx = db()
    cur = cnx.cursor(dictionary=True)
    try:
        cur.execute("""SELECT id,first_name,last_name
                       FROM employees
                       WHERE status='Active'
                       ORDER BY id""")
        employees = cur.fetchall()
    finally:
        cur.close()
        cnx.close()

    wanted = norm(folder_name)
    exact, first_only = [], []
    for e in employees:
        full = f"{e.get('first_name') or ''} {e.get('last_name') or ''}".strip()
        if norm(full) == wanted:
            exact.append(e)
        if norm(e.get("first_name") or "") == wanted:
            first_only.append(e)

    if len(exact) == 1:
        return exact[0]
    if len(first_only) == 1:
        return first_only[0]
    return None

def newest_master(folder_path):
    if not os.path.isdir(folder_path):
        return None
    matches = []
    for name in os.listdir(folder_path):
        p = os.path.join(folder_path, name)
        if not os.path.isfile(p):
            continue
        low = name.lower()
        if low.startswith("~$"):
            continue
        if os.path.splitext(low)[1] not in VALID_EXTENSIONS:
            continue
        if not low.startswith("master allocation"):
            continue
        matches.append(p)
    return max(matches, key=os.path.getmtime) if matches else None

def stable_file(path):
    try:
        first = (os.path.getsize(path), os.path.getmtime(path))
        time.sleep(STABLE_WAIT_SECONDS)
        second = (os.path.getsize(path), os.path.getmtime(path))
        return first == second and first[0] > 0
    except OSError:
        return False

def signature(path):
    st = os.stat(path)
    raw = f"{os.path.abspath(path)}|{st.st_size}|{st.st_mtime_ns}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def content_signature(headers, rows):
    payload = json.dumps(
        {"headers": headers, "rows": rows},
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def latest_content_matches(employee_id, headers, rows):
    cnx = db()
    cur = cnx.cursor(dictionary=True)
    try:
        cur.execute("""SELECT headers_json,rows_json
                       FROM allocation_snapshots
                       WHERE employee_id=%s
                       ORDER BY imported_at DESC,id DESC LIMIT 1""",
                    (employee_id,))
        latest = cur.fetchone()
        if not latest:
            return False
        try:
            old_headers = json.loads(latest.get("headers_json") or "[]")
            old_rows = json.loads(latest.get("rows_json") or "[]")
        except Exception:
            return False
        return content_signature(old_headers, old_rows) == content_signature(headers, rows)
    finally:
        cur.close()
        cnx.close()

def already_imported(employee_id, sig):
    cnx = db()
    cur = cnx.cursor()
    try:
        cur.execute("SELECT 1 FROM allocation_snapshots WHERE employee_id=%s AND source_signature=%s LIMIT 1",
                    (employee_id, sig))
        return cur.fetchone() is not None
    finally:
        cur.close()
        cnx.close()

def read_performance(path):
    proc = subprocess.run(
        ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", PS_READER, "-WorkbookPath", path],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout or "Excel reader failed").strip())
    payload = proc.stdout.strip()
    if not payload:
        raise RuntimeError("Performance sheet returned no data.")
    data = json.loads(payload)
    if not isinstance(data, dict) or "rows" not in data:
        raise RuntimeError("Unexpected Performance Pivot reader response.")
    return data["rows"]

def trim(v):
    return (str(v) if v is not None else "").strip()

def extract_pivot(matrix):
    """
    Extract an employee's visible Performance Pivot.

    Employee workbooks are not all identical:
      - some use RO + State
      - some use RO + Code
      - future workbooks may use another second dimension

    The second visible column immediately after RO is therefore preserved
    dynamically. Metric columns remain validated.
    """
    header_index = start_col = end_col = None

    canonical = {
        "RO": "RO",
        "STATE": "State",
        "CODE": "Code",
        "CALLER": "Caller",
        "FRESHSTAB": "Fresh / Stab",
        "COUNT": "COUNT",
        "POS": "POS",
        "TGT": "TGT",
        "COLLECTED": "Collected",
        "BTC": "BTC",
        "ROR": "ROR",
        "PTPAMT": "PTP Amt",
        "DRR": "DRR",
    }

    def key(value):
        return re.sub(r"[^A-Z0-9]+", "", trim(value).upper())

    required_metrics = {"RO", "COUNT", "POS", "TGT", "COLLECTED", "BTC", "ROR", "PTPAMT"}

    for ri, row in enumerate(matrix):
        keys = [key(x) for x in row]
        found = set(keys)
        if not required_metrics.issubset(found):
            continue

        ro = keys.index("RO")
        # The employee dimension must be the next visible column after RO,
        # but its label may be State, Code, Caller, Fresh/Stab, etc.
        if ro + 1 >= len(keys) or not keys[ro + 1]:
            continue

        header_index = ri
        start_col = ro

        # Keep DRR when it is exposed beside the Pivot.
        if "DRR" in keys and keys.index("DRR") > ro:
            end_col = keys.index("DRR")
        else:
            end_col = keys.index("PTPAMT")
        break

    if header_index is None:
        preview = " | ".join(
            " ; ".join(trim(x) for x in row[:15]) for row in matrix[:8]
        )
        raise RuntimeError(
            "Pivot header was not found on Performance sheet. Preview: " + preview[:1200]
        )

    raw_headers = matrix[header_index][start_col:end_col + 1]
    headers = []
    for raw in raw_headers:
        k=key(raw)
        headers.append(canonical.get(k, trim(raw)))

    rows = []
    width=end_col-start_col+1
    for raw in matrix[header_index + 1:]:
        row = [trim(x) for x in raw[start_col:end_col + 1]]
        if not any(row):
            continue
        # Ensure every row matches header width.
        if len(row)<width:
            row += [""]*(width-len(row))
        rows.append(row)

    if not rows:
        raise RuntimeError("Performance Pivot contains no data rows.")

    return headers, rows

def save_snapshot(employee_id, folder_name, path, sig, headers, rows):
    """
    Insert a new snapshot, or UPDATE the existing employee+signature snapshot.
    This makes a manual force-refresh safe even when the file signature has not
    changed and prevents MySQL 1062 duplicate-key errors.
    """
    cnx = db()
    cur = cnx.cursor()
    try:
        modified = datetime.fromtimestamp(os.path.getmtime(path))
        headers_json=json.dumps(headers, ensure_ascii=False)
        rows_json=json.dumps(rows, ensure_ascii=False)

        cur.execute(
            """INSERT INTO allocation_snapshots
               (employee_id,source_folder,source_file,source_modified,source_signature,headers_json,rows_json)
               VALUES(%s,%s,%s,%s,%s,%s,%s)
               ON DUPLICATE KEY UPDATE
                 source_folder=VALUES(source_folder),
                 source_file=VALUES(source_file),
                 source_modified=VALUES(source_modified),
                 headers_json=VALUES(headers_json),
                 rows_json=VALUES(rows_json),
                 imported_at=CURRENT_TIMESTAMP""",
            (employee_id, folder_name, os.path.basename(path), modified, sig,
             headers_json, rows_json),
        )

        # Keep latest 20 successful snapshots for this employee.
        cur.execute("""DELETE FROM allocation_snapshots
                       WHERE employee_id=%s AND id NOT IN
                       (SELECT id FROM
                         (SELECT id FROM allocation_snapshots
                          WHERE employee_id=%s ORDER BY imported_at DESC,id DESC LIMIT 20) k)""",
                    (employee_id, employee_id))
        cnx.commit()
    except Exception:
        cnx.rollback()
        raise
    finally:
        cur.close()
        cnx.close()

def sync_folder(folder_name, force=False, employee=None):
    folder_path = os.path.join(KOOFR_ROOT, folder_name)
    employee = employee or resolve_employee(folder_name)
    if not employee:
        logging.info("Skipping Koofr folder without a unique active HRMS employee: %s", folder_name)
        return False

    source = newest_master(folder_path)
    if not source:
        logging.warning("No Master Allocation workbook found in: %s", folder_path)
        return False

    if not stable_file(source):
        logging.info("File is still syncing/changing; retrying later: %s", source)
        return False

    sig = signature(source)
    if already_imported(employee["id"], sig) and not force:
        return True

    matrix = read_performance(source)
    headers, rows = extract_pivot(matrix)

    # Skip duplicate history, but force refresh still re-reads the workbook.
    if latest_content_matches(employee["id"], headers, rows):
        logging.info("No visible Performance change for %s; duplicate snapshot skipped.", folder_name)
        return True

    save_snapshot(employee["id"], folder_name, source, sig, headers, rows)
    logging.info("Updated %s from %s (%s rows)", folder_name, os.path.basename(source), len(rows))
    return True

def sync_employee(employee_id, force=False):
    """Sync one active employee by automatically finding the matching Koofr folder."""
    cnx=db()
    cur=cnx.cursor(dictionary=True)
    try:
        cur.execute("""SELECT id,first_name,last_name
                       FROM employees
                       WHERE id=%s AND status='Active'""",(employee_id,))
        employee=cur.fetchone()
    finally:
        cur.close()
        cnx.close()

    if not employee:
        raise RuntimeError("Active employee not found.")

    folder=discover_folder_for_employee(employee)
    if not folder:
        full=f"{employee.get('first_name') or ''} {employee.get('last_name') or ''}".strip()
        raise RuntimeError(f'No same-name Koofr folder found for "{full}".')

    return sync_folder(folder, force=force, employee=employee)

def sync_all_employees(force=False):
    """
    Automatically discovers every active HRMS employee.
    New employees are included without code changes as soon as a matching
    root-level Koofr folder exists.
    """
    employees=active_employees()
    folders=root_employee_folders()
    matched=0

    for employee in employees:
        folder=discover_folder_for_employee(employee, folders)
        full=f"{employee.get('first_name') or ''} {employee.get('last_name') or ''}".strip()

        if not folder:
            logging.info("No matching Koofr Performance folder yet for active employee: %s", full)
            continue

        try:
            if sync_folder(folder, force=force, employee=employee):
                matched += 1
        except Exception as exc:
            logging.exception("Performance sync failed for employee %s / folder %s: %s", full, folder, exc)

    return matched

def normalize_admin_table(raw, index):
    matrix = raw.get("rows") or []
    header_i = None
    for i,row in enumerate(matrix):
        keys=[re.sub(r"[^A-Z0-9/]+","",trim(x).upper()) for x in row]
        if "RO" in keys:
            header_i=i; break
    if header_i is None:
        raise RuntimeError("RO header not found in admin Performance Pivot %s" % index)
    headers=[trim(x) for x in matrix[header_i]]
    while headers and not headers[-1]: headers.pop()
    width=len(headers)
    rows=[]
    for rawrow in matrix[header_i+1:]:
        row=[trim(x) for x in rawrow[:width]]
        if any(row): rows.append(row)
    titles={1:"Main Allocation",2:"Caller-wise Allocation",3:"Fresh / Stab Allocation"}
    return {"index":index,"title":titles.get(index,"Performance Pivot %s"%index),"headers":headers,"rows":rows}

def read_admin_performance(path):
    proc=subprocess.run(["powershell.exe","-NoProfile","-ExecutionPolicy","Bypass","-File",ADMIN_PS_READER,"-WorkbookPath",path],capture_output=True,text=True,timeout=150)
    if proc.returncode != 0: raise RuntimeError((proc.stderr or proc.stdout or "Admin Excel reader failed").strip())
    data=json.loads(proc.stdout.strip())
    tables=data.get("tables") or []
    if len(tables) != 3: raise RuntimeError("Admin Performance must contain exactly 3 PivotTables.")
    return [normalize_admin_table(t,i+1) for i,t in enumerate(tables)]

def sync_admin_allocation(force=False):
    path=ADMIN_SOURCE
    if not os.path.isfile(path):
        logging.warning("Admin Allocation exact source file not found: %s",path);return
    if not stable_file(path):
        logging.info("Admin Allocation file is still syncing/changing; retrying later.");return
    sig=signature(path)
    cnx=db();cur=cnx.cursor(dictionary=True)
    try:
        cur.execute("SELECT 1 FROM admin_allocation_snapshots WHERE source_signature=%s LIMIT 1",(sig,))
        if cur.fetchone() and not force: return
    finally: cur.close();cnx.close()
    tables=read_admin_performance(path)
    payload=json.dumps(tables,ensure_ascii=False,separators=(",",":"))
    content_sig=hashlib.sha256(payload.encode("utf-8")).hexdigest()
    cnx=db();cur=cnx.cursor(dictionary=True)
    try:
        cur.execute("SELECT tables_json FROM admin_allocation_snapshots ORDER BY imported_at DESC,id DESC LIMIT 1")
        latest=cur.fetchone()
        if latest:
            old=latest.get("tables_json") or ""
            try: old_sig=hashlib.sha256(json.dumps(json.loads(old),ensure_ascii=False,separators=(",",":")).encode("utf-8")).hexdigest()
            except Exception: old_sig=""
            if old_sig == content_sig:
                logging.info("No visible Admin Allocation change; duplicate snapshot skipped.");return
        cur.execute("INSERT INTO admin_allocation_snapshots(source_file,source_modified,source_signature,tables_json) VALUES(%s,%s,%s,%s)",(os.path.basename(path),datetime.fromtimestamp(os.path.getmtime(path)),sig,payload))
        cur.execute("DELETE FROM admin_allocation_snapshots WHERE id NOT IN (SELECT id FROM (SELECT id FROM admin_allocation_snapshots ORDER BY imported_at DESC,id DESC LIMIT 20) x)")
        cnx.commit();logging.info("Admin Allocation updated from exact Huzaifa workbook: %s",os.path.basename(path))
    except Exception: cnx.rollback();raise
    finally: cur.close();cnx.close()

def sync_all():
    try:
        sync_admin_allocation()
    except Exception as exc:
        logging.exception("Admin Performance sync failed: %s", exc)
    sync_all_employees()

def main():
    logging.info("GRSJ Performance Sync started. Employee folders are auto-mapped from active HRMS names; Huzaifa and SyncTrash are excluded.")
    while True:
        sync_all()
        time.sleep(SCAN_SECONDS)

if __name__ == "__main__":
    main()
