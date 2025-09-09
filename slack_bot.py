## pip install slack_sdk
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests
import json

from dotenv import load_dotenv
load_dotenv()

# 替换为你的 Bot Token
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
# 替换为你要发送消息的频道 ID
CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

client = WebClient(token=SLACK_BOT_TOKEN)

def send_text(text):
    try:
        client.chat_postMessage(channel=CHANNEL_ID, text=text)
    except SlackApiError as e:
        print(f"Error sending text: {e.response['error']}")

def send_rich_text(blocks):
    try:
        # 提供 text fallback，避免 invalid_blocks 错误
        fallback_text = "Rich text message"
        if blocks and isinstance(blocks, list):
            for block in blocks:
                if block.get("type") == "section" and "text" in block:
                    fallback_text = block["text"].get("text", fallback_text)
        response = client.chat_postMessage(channel=CHANNEL_ID, blocks=blocks, text=fallback_text)
        print(f"Response: {response}")
    except SlackApiError as e:
        print(f"Error sending rich text: {e.response['error']}")

# 发送图片文件到频道（本地文件路径或网络图片下载后保存本地）
# https://docs.slack.dev/reference/methods/files.upload/ 已废弃，详见内部

def send_file_external(file_path, title="Image"):
    try:
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        mimetype = "image/jpeg" if file_path.lower().endswith(".jpg") or file_path.lower().endswith(".jpeg") else "application/octet-stream"

        # Step 1: 使用 requests 手动调用 getUploadURLExternal
        get_url_payload = {
            "filename": file_name,
            "length": file_size,
        }
        headers = {
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        get_url_resp = requests.post("https://slack.com/api/files.getUploadURLExternal", headers=headers, data=get_url_payload).json()
        
        print("getUploadURLExternal response:", get_url_resp)
        if not get_url_resp.get("ok"):
            raise Exception(f"getUploadURLExternal failed: {get_url_resp.get('error')}")
            
        upload_url = get_url_resp["upload_url"]
        file_id = get_url_resp["file_id"]

        # Step 2: 上传文件内容
        with open(file_path, "rb") as f:
            file_data = f.read()
        # For PUT request to the upload_url, we don't need special headers
        put_resp = requests.put(upload_url, data=file_data)
        print("PUT response status:", put_resp.status_code)
        if put_resp.status_code != 200:
            raise Exception(f"File content upload failed with status {put_resp.status_code}")

        # Step 3: 使用 requests 手动调用 completeUploadExternal
        complete_payload = {
            "files": json.dumps([{"id": file_id, "title": title}]),
            "channel_id": CHANNEL_ID,
            "initial_comment": "Here is the uploaded image."
        }
        complete_resp = requests.post("https://slack.com/api/files.completeUploadExternal", headers=headers, data=complete_payload).json()
        
        print("completeUploadExternal response:", complete_resp)
        if not complete_resp.get("ok"):
             raise Exception(f"completeUploadExternal failed: {complete_resp.get('error')}")

    except Exception as e:
        print(f"Error in external file upload: {e}")

# 示例用法
send_text("Hello, this is a plain text message.")

rich_blocks = [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "*This* is a _rich_ text message with *Markdown*!"
        }
    }
]
send_rich_text(rich_blocks)

send_file_external("SampleImage.jpg", "Sample Image")