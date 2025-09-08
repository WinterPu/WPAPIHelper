from dotenv import load_dotenv
import os

## Load .env file
load_dotenv()

app_id = os.getenv('FEISHU_APP_ID')
app_secret = os.getenv('FEISHU_APP_SECRET')

print(f"FEISHU_APP_ID: {app_id}")
print(f"FEISHU_APP_SECRET: {app_secret}")
