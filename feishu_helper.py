
import os
from dotenv import load_dotenv

import requests
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import CreateAppRequest, ReqApp, CreateAppTableRecordRequest, ListAppTableRequest, AppTableRecord

load_dotenv()

APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")

# OAuth2 配置
REDIRECT_URI = os.getenv("FEISHU_REDIRECT_URI", "http://localhost:8000/callback")
if not REDIRECT_URI:
    raise ValueError("请在 .env 文件中配置 FEISHU_REDIRECT_URI，并确保与开放平台后台设置完全一致！")
AUTH_URL = f"https://open.feishu.cn/open-apis/authen/v1/index?app_id={APP_ID}&redirect_uri={REDIRECT_URI}&state=state"
TOKEN_URL = "https://open.feishu.cn/open-apis/authen/v1/access_token"


# 1. 在飞书开放平台应用后台 > 安全设置 > 重定向URL，填写一个你能访问的网页地址
# （如 http://localhost:8000/callback 或你的服务器地址）。
# 2. 在 .env 文件中，FEISHU_REDIRECT_URI 必须和后台填写的完全一致。

def exchange_code_for_token(code):
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "app_id": APP_ID,
        "app_secret": APP_SECRET,
        "redirect_uri": REDIRECT_URI
    }
    resp = requests.post(TOKEN_URL, json=payload)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("code") == 0:
            print("user_access_token 获取成功:", data["data"]["access_token"])
            return data["data"]["access_token"]
        else:
            print("获取失败:", data)
    else:
        print("HTTP 错误:", resp.status_code, resp.text)
    return None


# 自动本地回调服务获取 code
## 授权之后Code 是在浏览器地址里面，通过这个本地服务获取
def get_code_via_local_server():
    code_holder = {}
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(self.path).query)
            code = qs.get('code', [None])[0]
            code_holder['code'] = code
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write('<h1>授权成功，可关闭此页面</h1>'.encode('utf-8'))
    server = HTTPServer(('localhost', 8000), Handler)
    def run_server():
        server.handle_request()
    t = threading.Thread(target=run_server)
    t.start()
    print("请在浏览器打开以下链接进行授权:")
    print(AUTH_URL)
    webbrowser.open(AUTH_URL)
    t.join()
    server.server_close()
    return code_holder.get('code')

def get_user_access_token():
    code = get_code_via_local_server()
    if not code:
        print("未获取到 code，授权失败")
        return None
    return exchange_code_for_token(code)

def main():
    # 获取 user_access_token（自动本地回调获取 code，无需 .env 粘贴）
    user_access_token = get_user_access_token()
    if not user_access_token:
        print("无法获取 user_access_token，流程终止。")
        return
    # 用 user_access_token 创建多维表格（Base）
    ## 多维表格名称
    base_name = "HelloWorldBase"
    create_base_url = "https://open.feishu.cn/open-apis/bitable/v1/apps"
    headers = {
        "Authorization": f"Bearer {user_access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "name": base_name
    }
    resp = requests.post(create_base_url, headers=headers, json=payload)
    print("创建表格返回:", resp.text)  # 增加完整返回内容输出
    if resp.status_code == 200:
        data = resp.json()
        if data.get("code") == 0 and "data" in data and "app" in data["data"]:
            app_id = data["data"]["app"]["app_token"]
            print(f"{base_name} app_token: {app_id}")
            # 优先用默认表格ID
            table_id = data["data"]["app"].get("default_table_id")
            if table_id:
                print(f"{base_name} default_table_id: {table_id}")
            else:
                # 没有默认表格ID时再查表格列表
                list_table_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_id}/tables"
                resp = requests.get(list_table_url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    if data.get("code") == 0 and data["data"].get("items"):
                        table_id = data["data"]["items"][0]["table_id"]
                        print(f"{base_name} table_id: {table_id}")
                    else:
                        print("未找到表格:", data)
                        return
                else:
                    print("HTTP 错误:", resp.status_code, resp.text)
                    return
        else:
            print("创建表格失败，返回内容:", data)
            return
    else:
        print("HTTP 错误:", resp.status_code, resp.text)
        return

    # 获取表格列表
    list_table_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_id}/tables"
    resp = requests.get(list_table_url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("code") == 0 and data["data"].get("items"):
            table_id = data["data"]["items"][0]["table_id"]
            print(f"{base_name} table_id: {table_id}")
        else:
            print("未找到表格:", data)
            return
    else:
        print("HTTP 错误:", resp.status_code, resp.text)
        return

    # 获取表格字段名
    list_field_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_id}/tables/{table_id}/fields"
    resp = requests.get(list_field_url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("code") == 0:
            print("表格字段如下：")
            for field in data["data"]["items"]:
                print(f"字段名: {field['field_name']}, 字段ID: {field['field_id']}")
        else:
            print("获取字段失败:", data)
            return
    else:
        print("HTTP 错误:", resp.status_code, resp.text)
        return

    # 一键上传 images.png 到多维表格
    file_path = "images.png"
    # 修正 URL，应该是 medias (复数)
    upload_url = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all"
    
    # 让 requests 自动处理 multipart/form-data 的 Content-Type 和 boundary
    upload_headers = headers.copy()
    if 'Content-Type' in upload_headers:
        del upload_headers['Content-Type']

    with open(file_path, "rb") as f:
        file_size = os.path.getsize(file_path)
        # 修正 form-data 的字段名和值
        form_data = {
            'file_name': os.path.basename(file_path),
            'parent_type': 'bitable_image',  # 修正为 bitable_image
            'parent_node': app_id,
            'size': str(file_size)
        }
        files = {
            'file': (os.path.basename(file_path), f, 'image/png') # 修正 key 为 file
        }
        resp = requests.post(upload_url, headers=upload_headers, data=form_data, files=files)
    file_token = None
    print("上传接口响应:", resp.status_code, resp.text)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("code") == 0:
            file_token = data["data"].get("file_token")
            print("附件上传成功，file_token:", file_token)
        else:
            print("附件上传失败:", data)
    else:
        print("附件上传 HTTP 错误:", resp.status_code, resp.text)

    # 插入数据（请将字段名替换为实际字段名）
    insert_url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_id}/tables/{table_id}/records"
    record_payload = {
        "fields": {
            "文本": "测试Value",
            "单选": "测试Value2",
            "日期": 1757280000,
            "附件": [{"file_token": file_token}] if file_token else None
        }
    }
    resp = requests.post(insert_url, headers=headers, json=record_payload)
    if resp.status_code == 200:
        data = resp.json()
        if data.get("code") == 0:
            print("插入成功:", data["data"])
        else:
            print("插入数据失败:", data)
    else:
        print("HTTP 错误:", resp.status_code, resp.text)

if __name__ == "__main__":
	main()


