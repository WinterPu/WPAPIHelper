import os
import requests
from dotenv import load_dotenv
from requests_toolbelt.multipart.encoder import MultipartEncoder

load_dotenv()

FEISHU_WEBHOOK_URL = os.getenv("FEISHU_BOT_WEBHOOK_URL")

# 发送文本消息到群机器人 webhook
# 参考: https://open.feishu.cn/document/faq/bot

def send_webhook_text(text):
    url = FEISHU_WEBHOOK_URL
    payload = {
        "msg_type": "text",
        "content": {
            "text": text
        }
    }
    resp = requests.post(url, json=payload)
    return resp.json()

# 发送富文本消息到群机器人 webhook
# content_blocks 示例: [[{"tag": "text", "text": "富文本内容"}]]

def send_webhook_post(title, content_blocks):
    url = FEISHU_WEBHOOK_URL
    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": content_blocks
                }
            }
        }
    }
    resp = requests.post(url, json=payload)
    return resp.json()

# 发送图片消息到群机器人 webhook
# 需要先上传图片到飞书开放平台，获取 image_key
# 参考: https://open.feishu.cn/document/server-docs/im-v1/image/create
def send_webhook_image(image_key):
    url = FEISHU_WEBHOOK_URL
    payload = {
        "msg_type": "image",
        "content": {
            "image_key": image_key
        }
    }
    print(f"[LOG] 发送图片到 webhook, image_key: {image_key}")
    resp = requests.post(url, json=payload)
    print(f"[LOG] webhook response: {resp.text}")
    return resp.json()

# 图片上传说明：
# webhook 机器人无法直接上传图片，只能使用开放平台接口（需 app_id/app_secret）上传图片，获取 image_key 后再用 webhook 发送。

# 使用开放平台接口上传图片，获取 image_key
def upload_image(image_path):
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    print(f"[LOG] 上传图片: {image_path}")
    # 获取 tenant_access_token
    token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/"
    payload = {"app_id": app_id, "app_secret": app_secret}
    resp = requests.post(token_url, json=payload)
    print(f"[LOG] tenant_access_token response: {resp.text}")
    tenant_access_token = resp.json().get("tenant_access_token")
    if not tenant_access_token:
        raise Exception("获取 tenant_access_token 失败")
    # 上传图片，使用 MultipartEncoder
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    with open(image_path, "rb") as f:
        multi_form = MultipartEncoder(
            fields={
                "image_type": "message",
                "image": (image_path, f, "image/jpeg")
            }
        )
        headers = {
            "Authorization": f"Bearer {tenant_access_token}",
            "Content-Type": multi_form.content_type
        }
        resp = requests.post(url, headers=headers, data=multi_form)
    print(f"[LOG] 图片上传 response: {resp.text}")
    image_key = resp.json().get("data", {}).get("image_key")
    if not image_key:
        raise Exception(f"图片上传失败: {resp.text}")
    print(f"[LOG] 获取到 image_key: {image_key}")
    return image_key

# 示例用法
if __name__ == "__main__":
    print(send_webhook_text("Hello from Feishu Webhook!"))
    post_content = [
        [
            {"tag": "text", "text": "富文本内容"},
            {"tag": "a", "text": "链接", "href": "https://www.feishu.cn"}
        ]
    ]
    print(send_webhook_post("富文本标题", post_content))
    # 上传并发送图片
    image_key = upload_image("SampleImage.jpg")
    print(send_webhook_image(image_key))
