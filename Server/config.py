import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY=os.getenv("SECRET_KEY","GAME-HRMS-CHANGE-ME")
    DB_HOST=os.getenv("DB_HOST","localhost")
    DB_PORT=int(os.getenv("DB_PORT","3306"))
    DB_NAME=os.getenv("DB_NAME","game_db")
    DB_USER=os.getenv("DB_USER","root")
    DB_PASSWORD=os.getenv("DB_PASSWORD","")
    MAX_CONTENT_LENGTH=4*1024*1024

    # Persistent runtime data lives OUTSIDE the replaceable application folder.
    # Default on this installation:
    # D:\\GRSJ\\GRSJ-HRMS_DATA\\uploads\\...
    _GRSJ_ROOT=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATA_ROOT=os.getenv("HRMS_DATA_ROOT",os.path.join(_GRSJ_ROOT,"GRSJ-HRMS_DATA"))
    UPLOAD_ROOT=os.path.join(DATA_ROOT,"uploads")
    UPLOAD_FOLDER=os.path.join(UPLOAD_ROOT,"employees")
