import re
from pdfminer.high_level import extract_text
import numpy as np
import os
import jieba
# import spacy
import gensim
import gensim.parsing.preprocessing

# nlp=spacy.load("zh_core_web_sm")


# 读取PDF文件内容
def extract_pdf_text(pdf_path):
    return extract_text(pdf_path)


# 分割段和清理空白文本
def paragraphs_text(text):
    paragraphs = re.split("[\n]", text)
    cleaned_data = [item for item in paragraphs if item.strip()]
    return cleaned_data


# 创建停用词列表
def stopwordslist(filepath):
    stopwords = [
        line.strip() for line in open(filepath, "r", encoding="utf-8").readlines()
    ]
    # strip() 方法用于移除字符串头尾指定的字符（默认为空格或换行符）或字符序列。
    # readlines()读取所有行并返回列表
    return stopwords


# 提取问题词
def keyPointParagraphSegmentation(text):
    problems = re.findall(r"问题 .：.*", text)
    return problems


# 去除中文停止词和符号
def removeChineseStopWords(paper_text):
    return [
        word
        for word in jieba.cut(paper_text)
        if word not in cn_stopwordslist and word.strip()
    ]


# 提取题目关键词
def extractKeyWordsFromTheQuestion(paper_text):
    problems = keyPointParagraphSegmentation(paper_text)
    mainPoints_paragraphs = paragraphs_text(paper_text)
    keys = []
    for i in range(0, len(problems)):
        if i == len(problems) - 1:
            section = mainPoints_paragraphs[
                mainPoints_paragraphs.index(problems[i]) + 1 : :
            ]
        else:
            section = mainPoints_paragraphs[
                mainPoints_paragraphs.index(problems[i])
                + 1 : mainPoints_paragraphs.index(problems[i + 1])
            ]
        paragraph = "".join(section)
        print(paragraph)
        filtered_paragraph = removeChineseStopWords(paragraph)
        keys.append(list(set(filtered_paragraph)))
    return keys

# 评价函数
def evaluateTheRelevanceOfPapersAndCompetitionQuestions(topics,keywords):
    topic_words=[]
    for topic in topics:
        topic_num = topic[0]
        topic_keywords=[word[0] for word in topic[1]]
        topic_words.extend(topic_keywords)
        print(f"问题{topic_num+1}的关键词：{topic_words}")
    topic_coverage=len(set(keywords)&set(topic_words))/len(keywords)
    return round(topic_coverage,2)

# 文件地址
problem_pdf_path = "D:/Code/Python/2024-TidyC/data/C题-示例数据/赛题数据/附件2/C题 - “智慧政务”中的文本挖掘应用.pdf"
mainPoints_pdf_path = "D:/Code/Python/2024-TidyC/data/C题-示例数据/赛题数据/附件2/C题 - “智慧政务”中的文本挖掘应用评阅要点.pdf"
paper_text_path = "D:/Code/Python/2024-TidyC/data/C题-示例数据/赛题数据/附件1/C001.pdf"
stopwordslist_path = "D:/Code/Python/2024-TidyC/stopwords-master/cn_stopwords.txt"
# 中文停止词列表
cn_stopwordslist = stopwordslist(stopwordslist_path)
# 读取文件内容
problem_text = extract_pdf_text(problem_pdf_path)
mainPoints_text = extract_pdf_text(mainPoints_pdf_path)
paper_text = extract_pdf_text(paper_text_path)
cleaned_papers = removeChineseStopWords(paragraphs_text(paper_text))
print(cleaned_papers)

keys = extractKeyWordsFromTheQuestion(mainPoints_text)
dict_file = 'data/custom_dict.txt'
if not os.path.exits(dict_file):
    with open(dict_file,'w',encoding='utf-8')as f:
        for word in keys:
            f.write(word+' 10 n'+'\n')
jieba.load_userdict(dict_file)
# print(keys)

#创建和训练LAD主题模型
num_topic = 10
paper_dictionary = gensim.corpora.Dictionary([paper_segment.lower().split() for paper_segment in cleaned_papers])
paper_bow_corpus = [paper_dictionary.doc2bow(segment.lower().split()) for segment in cleaned_papers]
lda_model = gensim.models.LdaModel(paper_bow_corpus, id2word=paper_dictionary, num_topics=num_topic, passes=10)

#获取问题关键词
topics = lda_model.show_topics(num_topics=num_topic, num_words=20, formatted=False)

score = evaluateTheRelevanceOfPapersAndCompetitionQuestions(topics,keys)