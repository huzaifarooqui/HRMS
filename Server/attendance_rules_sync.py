import time
import logging
import os
from app import app, sync_company_attendance_rules

LOG=os.path.join(os.path.dirname(__file__),"attendance_rules.log")
logging.basicConfig(filename=LOG,level=logging.INFO,format="%(asctime)s | %(levelname)s | %(message)s")

def main():
    logging.info("GRSJ automatic attendance rules service started.")
    while True:
        try:
            with app.app_context():
                sync_company_attendance_rules()
        except Exception as exc:
            logging.exception("Automatic attendance rule cycle failed: %s",exc)
        time.sleep(300)

if __name__=="__main__":
    main()
