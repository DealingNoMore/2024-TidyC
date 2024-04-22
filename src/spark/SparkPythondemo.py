# coding: utf-8
import SparkApi
import time
#以下密钥信息从控制台获取   https://console.xfyun.cn/services/bm35
appid = "58a14477"     #填写控制台中获取的 APPID 信息
api_secret = "NzliNDE2Mjk2MThjYTkyMGNkMWM1ODA2"   #填写控制台中获取的 APISecret 信息
api_key ="8f3f91932c1a3cfc035b941754bbc076"    #填写控制台中获取的 APIKey 信息

domain = "generalv3.5"    # v3.0版本

Spark_url = "wss://spark-api.xf-yun.com/v3.5/chat"  # v3.5环服务地址

#初始上下文内容，当前可传system、user、assistant 等角色
text =[
    {"role": "system", "content": "你现在扮演竞赛论文评审老师，你对论文的结构、语言连贯性和论文中做的工作与题目是否相关很关注；接下来请用评审老师的口吻对用户上传的论文进行评分，满分10分，并附上理由。"} , # 设置对话背景或者模型角色
    {"role":"system","content":""}
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

def checklen(text):
    while (getlength(text) > 8000):
        del text[0]
    return text
    


if __name__ == '__main__':

    while(1):
        Input = input("\n" +"我:")
        question = checklen(getText("user",Input))
        SparkApi.answer =""
        print("星火:",end ="")
        SparkApi.main(appid,api_key,api_secret,Spark_url,domain,question)
        # print(SparkApi.answer)
        getText("assistant",SparkApi.answer)




