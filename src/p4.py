# coding: utf-8
import SparkApi
import re
import os
import glob
import math
from pdfminer.high_level import extract_text

import time
#以下密钥信息从控制台获取   https://console.xfyun.cn/services/bm35
appid = "bfb43910"     #填写控制台中获取的 APPID 信息
api_secret = "ZjVmMGY1NTRkM2E5N2Y3YzBhNDVjY2Q2"   #填写控制台中获取的 APISecret 信息
api_key ="1dbd3761ebe3b15f501f9b9d6fd6661b"    #填写控制台中获取的 APIKey 信息

domain = "generalv3.5"    # v3.5版本

Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址

#初始上下文内容，当前可传system、user、assistant 等角色
text =[
    # {"role": "system", "content": "你现在扮演李白，你豪情万丈，狂放不羁；接下来请用李白的口吻和用户对话。"} , # 设置对话背景或者模型角色
    # {"role": "user", "content": "你是谁"},  # 用户的历史问题
    # {"role": "assistant", "content": "....."} , # AI的历史回答结果
    # # ....... 省略的历史对话
    # {"role": "user", "content": "你会做什么"}  # 最新的一条问题，如无需上下文，可只传最新一条问题
]


def getText(role,content):
    jsoncon = {}
    jsoncon["role"] = role
    jsoncon["content"] = content
    text.append(jsoncon)
    return text

def getlength(text):
    length = 0
    for content in text:
        temp = content["content"]
        leng = len(temp)
        length += leng
    return length

def evaluate(average):
    return math.sqrt(average)

def checklen(text):
    while (getlength(text) > 12000):
        del text[0]
    return text
    
def extract_pdf_text(pdf_path):
    return extract_text(pdf_path)
# 控制长度
def trim_string(s):
    if len(s) > 10000:
        return s[:10000]
    else:
        return s

# 指定要遍历的文件夹路径
folder_path = 'example'

if __name__ == '__main__':
    num = 0
    pdf_files = glob.glob(os.path.join(folder_path, '*.pdf'))
    # 遍历匹配到的 PDF 文件
    for pdf_file in pdf_files:
        num = num + 1
        Len = 0
        print(num, end="    ")
        while(Len == 0):
            text1 = extract_pdf_text(pdf_file)
            text1 = text1.replace("政", "")
            text1 = text1.replace("government", "")
            text1 = text1.replace("governance", "")
            text1 = trim_string(text1)
            text1 = text1 + '请给你对上述论文的连贯性、写作规范性、论文逻辑性进行综合评分，必须给出一个1-10之间的分数，不要解释理由'
            question = checklen(getText("user", text1))
            SparkApi.answer = ""
            print("星火:",end ="")
            SparkApi.main(appid, api_key, api_secret, Spark_url, domain, question)
            numbers = re.findall(r'\d+', SparkApi.answer)
            numbers_list = [int(num) for num in numbers]
            Len = len(numbers_list)
            if Len == 0:
                continue
            total = sum(numbers_list)
            average = total / Len
            while(average > 10):
                average = evaluate(average)
            print(average,end="\n")
            with open('output.txt', 'a', encoding='utf-8') as file:
                # 将内容写入文件
                file.write(str(average)+"\n")
            getText("assistant", SparkApi.answer)





