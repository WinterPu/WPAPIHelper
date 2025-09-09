import os
import requests
from dotenv import load_dotenv

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
