import os
import openai
from config import BOT_TOKEN, OPENAI_API_KEY, adminId, groupId, groupId2, testGroupId

TELEGRAM_BOT_TOKEN = os.getenv("BOT_TOKEN", BOT_TOKEN)
OPENAI_API = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)
ADMIN_ID = os.getenv("adminId", adminId)
GROUP_ID = os.getenv("groupId", groupId)
GROUP_ID2 = os.getenv("groupId2", groupId2)
TEST_GROUP_ID = os.getenv("testGroupId", testGroupId)