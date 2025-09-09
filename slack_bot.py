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
        # 使用 slack_sdk 封装好的 v2 方法，它会自动处理所有步骤
        response = client.files_upload_v2(
            channel=CHANNEL_ID,
            file=file_path,
            title=title,
            initial_comment=f"Here is the file: {title}",
        )
        print("files_upload_v2 response:", response)
        if not response.get("ok"):
            raise Exception(f"files_upload_v2 failed: {response.get('error')}")

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