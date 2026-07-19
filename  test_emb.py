import requests
import json

key = "sk-ws-H.EDPIRDD.UGwJ.MEUCIGByeMPc78LWHknFTUmoZ1VeBqSvi87E3sMoyzEqScB4AiEA10Izm3TmwQB1w49nKV0uGsVWiAXCWSL-6cokDI85fZM"
url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

headers = {
    "Authorization": f"Bearer {key}",
    "Content-Type": "application/json"
}
body = {
    "model":"qwen-turbo",
    "input":{"prompt":"你好"},
    "parameters":{"result_format":"message"}
}
res = requests.post(url,json=body,headers=headers)
print(res.text)