
import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify


import lark_oapi as lark
import json
from dotenv import load_dotenv
import os

load_dotenv()

# 从环境变量读取飞书配置
FEISHU_APP_ID = os.getenv('FEISHU_APP_ID')
FEISHU_APP_SECRET = os.getenv('FEISHU_APP_SECRET')

# 创建 LarkClient 对象
client = lark.Client.builder().app_id(FEISHU_APP_ID).app_secret(FEISHU_APP_SECRET).build()

def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    # 解析消息内容
    if data.event.message.message_type == "text":
        try:
            msg_text = json.loads(data.event.message.content)["text"]
        except Exception:
            msg_text = "解析消息失败，请发送文本消息\nparse message failed, please send text message"
    else:
        msg_text = "解析消息失败，请发送文本消息\nparse message failed, please send text message"

    reply_content = json.dumps({
        "text": f"收到你发送的消息：{msg_text}\nReceived message: {msg_text}"
    })

    if data.event.message.chat_type == "p2p":
        # 单聊，直接发送消息
        request = lark.im.v1.CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(
                lark.im.v1.CreateMessageRequestBody.builder()
                .receive_id(data.event.message.chat_id)
                .msg_type("text")
                .content(reply_content)
                .build()
            ).build()
        response = client.im.v1.message.create(request)
        if not response.success():
            print(f"发送消息失败: {response.code}, {response.msg}, log_id: {response.get_log_id()}")
    else:
        # 群聊，回复消息
        request = lark.im.v1.ReplyMessageRequest.builder() \
            .message_id(data.event.message.message_id) \
            .request_body(
                lark.im.v1.ReplyMessageRequestBody.builder()
                .content(reply_content)
                .msg_type("text")
                .build()
            ).build()
        response = client.im.v1.message.reply(request)
        if not response.success():
            print(f"回复消息失败: {response.code}, {response.msg}, log_id: {response.get_log_id()}")

# 注册事件回调
event_handler = (
    lark.EventDispatcherHandler.builder("", "")
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1)
    .build()
)

def main():
    wsClient = lark.ws.Client(
        FEISHU_APP_ID,
        FEISHU_APP_SECRET,
        event_handler=event_handler,
        log_level=lark.LogLevel.DEBUG,
    )
    wsClient.start()

if __name__ == "__main__":
    main()


