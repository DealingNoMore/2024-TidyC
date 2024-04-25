from sparkai.llm.llm import ChatSparkLLM, ChunkPrintHandler
from sparkai.core.messages import ChatMessage
from pdfminer.high_level import extract_text
import os
import glob
import re
import random

# 读取PDF文件内容
# 使用正则表达式提取摘要部分和正文部分
def extract_abstract_and_body(pdf_path):
    full_text = extract_text(pdf_path)
    # 去除文本中的空格和空行
    full_text = full_text.replace(' ','').replace('\n','')

    # 修复可能的分页导致关键词被割断的问题
    repaired_text = full_text.replace('-\n','').replace('\n',' ')

    # 找到‘摘要’和‘关键词’之间的文本
    abstract_start_index = repaired_text.find('摘要')
    keywords_start_index = repaired_text.find('关键词')
    abstract_text = repaired_text[abstract_start_index+len('摘要'):keywords_start_index]

    # 找到正文起始关键词后的所有文本作为正文
    body_start_index = repaired_text.find('目录')
    body_end_index = min(body_start_index + len('目录') + 5000, len(repaired_text))
    body_text = repaired_text[body_start_index + len('目录'):body_end_index]
    
    body_text = body_text.replace('政', '') 
    # 清除摘要与正文之间可能多余的标题等内容
    return abstract_text.strip(), body_text.strip()

# 构造请求给AI的函数  
def get_consistency_and_relevance_score(spark, abstract, body):  
    # 构造请求消息  
    request_message = [ChatMessage(  
        role="user",  
        content=f"请给出以下摘要和正文之间的相关性分数（1-10）\n摘要: {abstract}\n正文: {body}\n"  
    )]  
      
    # 发送请求给AI  
    handler = ChunkPrintHandler()  
    response = spark.generate([request_message], callbacks=[handler])

    return response

def get_numbers(scores):
    if not 0 <= scores <= 10:
       scores = 1.0 + random.random() * 9.0
    return scores




SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.5/chat'
#星火认知大模型调用秘钥信息，请前往讯飞开放平台控制台（https://console.xfyun.cn/services/bm35）查看
SPARKAI_APP_ID = 'bfb43910'
SPARKAI_API_SECRET = 'ZjVmMGY1NTRkM2E5N2Y3YzBhNDVjY2Q2'
SPARKAI_API_KEY = '1dbd3761ebe3b15f501f9b9d6fd6661b'
#星火认知大模型v3.5的domain值，其他版本大模型domain值请前往文档（https://www.xfyun.cn/doc/spark/Web.html）查看
SPARKAI_DOMAIN = 'generalv3.5'

# if __name__ == '__main__':
#     spark = ChatSparkLLM(
#         spark_api_url=SPARKAI_URL,
#         spark_app_id=SPARKAI_APP_ID,
#         spark_api_key=SPARKAI_API_KEY,
#         spark_api_secret=SPARKAI_API_SECRET,
#         spark_llm_domain=SPARKAI_DOMAIN,
#         streaming=False,
#     )
    
#     # 指定要遍历的目录  
#     directory = 'data'  
      
#     # 使用glob库查找所有PDF文件  
#     pdf_files = glob.glob(os.path.join(directory, '**', '*.pdf'), recursive=True)  
      
#     # 遍历每一个PDF文件  
#     for pdf_file in pdf_files:   
#         #pdf_path = 'data/C001.pdf'  # 替换为你的PDF文件路径  
#         abstract, body = extract_abstract_and_body(pdf_file)
        
#         result = get_consistency_and_relevance_score(spark, abstract, body)
#         first_generation_list = result.generations[0] if result.generations else []
#         first_generation = first_generation_list[0]
        
#         str_numbers = re.findall(r'\d+', first_generation.text)
        
#         scores = float(str_numbers[0])
#         scores = get_numbers(scores)
#         print(pdf_file + ": ", scores)
