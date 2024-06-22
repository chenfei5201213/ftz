APPId = "bf5794b5"
APIKey = "d450c29f9db543f91f945dc000d61573"
APISecret = "Y2RhZjk5MmU1YWU0NDE2NWViNzMyNThm"
# audio_path = "./resource/input/audio/您好，欢迎来到科大讯飞.mp3"
audio_path = "../../server/media/Lf9kjiMwojSBfde91345f9a758e5dd5c39aac68666fc.durationTime3338.aac"

# 请求数据
request_data = {
    "header": {
        "app_id": "123456",
        "status": 0
    },
    "parameter": {
        "st": {
            "lang": "jp",
            "core": "sent",
            "refText": "",
            "result": {
                "encoding": "utf8",
                "compress": "raw",
                "format": "plain"
            }
            # "getParam":0,
            # "attachAudioUrl":0,
            # "vad":0,
            # "seek":0,
            # "ref_length":0,
            # "phoneme_output":0,
            # "slack":0,
            # "scale":0,
            # "precision":0,
            # "refPinyin":"",
            # "serverTimeout":0,
            # "output_rawtext":0,
            # "realtime_feedback":0,
            # "customized_lexicon":"",
            # "phoneme_diagnosis":0,
            # "dict_type":"",
            # "paragraph_need_word_score":0,
        }
    },
    "payload": {
        "data": {
            "encoding": "lame",
            "sample_rate": 16000,
            "channels": 1,
            "bit_depth": 16,
            "status": 0,
            "seq": 0,
            "audio": audio_path,
            "frame_size": 0
        }
    }
}

# 请求地址
# request_url = "wss://cn-east-1.ws-api.xf-yun.com/v1/private/s8e098720"
request_url = "wss://cn-east-1.ws-api.xf-yun.com/v1/private/sffc17cdb"

# 用于快速定位响应值

response_path_list = ['$..payload.result', ]
