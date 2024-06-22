#!/usr/bin/env python3
# -*-coding:utf-8 -*-
import base64
import ssl
import uuid
import _thread as thread
import json
from functools import partial
import logging

import jsonpath
import websocket

from suntone_ise_cn_python.sample import ne_utils, aipass_client
from suntone_ise_cn_python.data import *

logger = logging.getLogger(__name__)
print("jsonpath module location:", jsonpath.__file__)
print("jsonpath.jsonpath exists:", hasattr(jsonpath, 'jsonpath'))


# 收到websocket连接建立的处理
def on_open(ws):
    def run():
        # 清除文件
        # ne_utils.del_file('server/suntone_ise_cn_python/resource/output')
        # 判断是否是多模请求
        # json_data = json.loads(request_data)
        print(request_data)
        exist_audio = jsonpath.jsonpath(request_data, "$.payload.*.audio")
        exist_video = jsonpath.jsonpath(request_data, "$.payload.*.video")
        multi_mode = True if exist_audio and exist_video else False

        # 获取frame，用于设置发送数据的频率
        frame_rate = None
        if jsonpath.jsonpath(request_data, "$.payload.*.frame_rate"):
            frame_rate = jsonpath.jsonpath(request_data, "$.payload.*.frame_rate")[0]
        time_interval = 40
        if frame_rate:
            time_interval = round((1 / frame_rate) * 1000)

        # 获取待发送的数据
        media_path2data = aipass_client.prepare_req_data(request_data)
        # 发送数据
        aipass_client.send_ws_stream(ws, request_data, media_path2data, multi_mode, time_interval)

    thread.start_new_thread(run, ())



# 收到websocket消息的处理
def on_message(ws, message, key='', result={}):
    # aipass_client.deal_message(ws, message)
    message = eval(message)
    logger.info(f"on_message1: {message}")
    print(f"on_message2: {message}")
    if message["header"]["status"] == 2:
        text = message["payload"]["result"]["text"]
        text_de = base64.b64decode(text)
        result[key] = json.loads(text_de)
        ws.close()
    else:
        result[key] = message



# 收到websocket错误的处理
def on_error(ws, error):
    logger.error("### error:", error)


# 收到websocket关闭的处理
def on_close(ws, a, b):
    print("*** 执行结束，连接自动关闭 ***")


def recognize_audio(file_path, ref_text):
    request_data['header']['app_id'] = APPId
    request_data['payload']['data']['audio'] = file_path
    request_data['parameter']['st']['refText'] = ref_text
    auth_request_url = ne_utils.build_auth_request_url(request_url, "GET", APIKey, APISecret)
    websocket.enableTrace(False)
    u_key = str(uuid.uuid4())
    result = {}
    on_message_with_param = partial(on_message, key=u_key, result=result)
    ws = websocket.WebSocketApp(auth_request_url, on_message=on_message_with_param, on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    return result.get(u_key)


if __name__ == '__main__':
    # 程序启动的时候设置APPID
    request_data['header']['app_id'] = APPId
    request_data['parameter']['st']['refText'] = "test"
    auth_request_url = ne_utils.build_auth_request_url(request_url, "GET", APIKey, APISecret)
    websocket.enableTrace(False)
    u_key = str(uuid.uuid4())
    result = {}
    on_message_with_param = partial(on_message, key=u_key, result=result)
    ws = websocket.WebSocketApp(auth_request_url, on_message=on_message_with_param, on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
    print(result)
