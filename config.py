import os
from os import getenv
from dotenv import load_dotenv
from OWNER import BOT_TOKEN, OWNER, OWNER_NAME, DATABASE, CHANNEL, GROUP, LOGS, VIDEO, API_ID, API_HASH

if os.path.exists("local.env"):
    load_dotenv("local.env")

load_dotenv()
admins = {}
user = {}
call = {}
dev = {}
logger = {}
logger_mode = {}
botname = {}
appp = {}
helper = {}

API_ID = API_ID
API_HASH = API_HASH
BOT_TOKEN = BOT_TOKEN
MONGO_DB_URL = DATABASE
OWNER = OWNER
OWNER_NAME = OWNER_NAME
CHANNEL = CHANNEL
GROUP = GROUP
LOGS = LOGS
VIDEO = VIDEO