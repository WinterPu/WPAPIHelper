from dotenv import load_dotenv
import os

import requests

## Load .env file
load_dotenv()

app_id = os.getenv('FEISHU_APP_ID')
app_secret = os.getenv('FEISHU_APP_SECRET')

print(f"FEISHU_APP_ID: {app_id}")
print(f"FEISHU_APP_SECRET: {app_secret}")


url= "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/" 
#应用凭证里的 app id 和 app secret  
post_data = {"app_id": app_id, "app_secret": app_secret}
r = requests.post(url, data=post_data)
tat = r.json()["tenant_access_token"] 
print(f"TAT: {tat}")


