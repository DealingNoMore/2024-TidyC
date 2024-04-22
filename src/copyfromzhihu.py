import os
import re

import gensim
import jieba
import spacy
from pdfminer.high_level import extract_text

# 加载中文模块
nlp = spacy.load("zh_core_web_sm")


# 读取PDF文件内容
def extract_pdf_text(pdf_path):
    return extract_text(pdf_path)


def stopwordslist():
    stopwords = [
        line.strip() for line in
        open("D:/Code/Python/2024-TidyC/stopwords-master/hit_stopwords.txt", "r", encoding="utf-8").readlines()
    ]
    return stopwords


def keyPointParagraphSegmentation(text):
    problems = re.findall(r"问题 .：.*", text)
    return problems


# 将文本分成段落或句子
def segment_text(text):
    paragraphs = re.split("[\n]", text)

    segments = [item for item in paragraphs if item.strip()]
    main_segments = segments[segments.index('二、解决问题 ') + 1:segments.index('\x0c附录： ')]
    print(main_segments)
    alltext = "".join(main_segments)
    alltext = re.sub(r'\d+', "", alltext)
    alltext = re.sub(r'[（）“”()：:、‘’-]', "", alltext)
    alltext = re.sub(r'\\\\', "", alltext)
    alltext = re.sub(r'\\/', "", alltext)
    alltext = re.sub(r'[\\.]*', "", alltext)
    alltext = re.sub(r'[a-zA-Z]', "", alltext)
    alltext = re.sub(r'\.', '', alltext)
    alltext = re.sub(r' ', '', alltext)
    # print(alltext)
    return alltext

def clean_paper(text):
    text = re.sub(r'\d+', "", text)
    text = re.sub(r'[（）“”()：:、‘’-]', "", text)
    text = re.sub(r'\\\\', "", text)
    text = re.sub(r'\\/', "", text)
    text = re.sub(r'[\\.]*', "", text)
    text = re.sub(r'[a-zA-Z]', "", text)
    text = re.sub(r'\.', '', text)
    text = re.sub(r' ', '', text)
    # print(alltext)
    return text

# 从文本中提取赛题相关的关键词
def extract_keywords(segments, stop_keywords):
    # segments = re.sub(r"[\.]", "", segments)
    # segments = re.sub(r"[\\]", "", segments)
    # segments = re.sub(r"[_*]", "", segments)
    # segments = re.sub(r"[^a-zA-Z]", "", segments)
    # segments = re.sub(r"[^0-9]+", "", segments)
    keywords = [word for word in jieba.cut(segments) if word not in stop_keywords and word.strip()]
    print(keywords)

    return keywords


def extractKeyWordsFromTheQuestion(paper_text):
    problems = re.findall(r"问题 .：.*", paper_text)
    paragraphs = re.split("[\n]", paper_text)
    mainPoints_paragraphs = [item for item in paragraphs if item.strip()]
    keys = []
    for i in range(0, len(problems)):
        if i == len(problems) - 1:
            section = mainPoints_paragraphs[
                      mainPoints_paragraphs.index(problems[i]) + 1::
                      ]
        else:
            section = mainPoints_paragraphs[
                      mainPoints_paragraphs.index(problems[i])
                      + 1: mainPoints_paragraphs.index(problems[i + 1])
                      ]
        paragraph = "".join(section)
        paragraph = re.sub(r"[\.]", "", paragraph)
        paragraph = re.sub(r"[\\]", "", paragraph)
        paragraph = re.sub(r"[_*]", "", paragraph)
        filtered_paragraph = [word for word in jieba.cut(paragraph) if word not in stopwordslist() and word.strip()]
    return list(set(filtered_paragraph))


# 从文本中识别与赛题相关的主题或话题
def evaluate_problem_statement(topics, keywords):
    # 输出每个主题的关键词
    topic_words = []
    for topic in topics:
        topic_num = topic[0]
        topic_keywords = [word[0] for word in topic[1]]
        topic_words.extend(topic_keywords)
        print(f"主题{topic_num + 1}的关键词：{topic_keywords}")

    topic_coverage = len(set(keywords) & set(topic_words)) / len(keywords)
    return round(topic_coverage, 2)


problem_pdf_path = "D:/Code/Python/2024-TidyC/data/C题-示例数据/赛题数据/附件2/C题 - “智慧政务”中的文本挖掘应用.pdf"  # 赛题题目"  # 赛题题目

# 读取文件内容
problem_text = extract_pdf_text(problem_pdf_path)

# 将文本分成段落或句子
problem_segments = segment_text(problem_text)

# 使用哈工大中文停用词库
chinese_stopwords = stopwordslist()
# 从文本中提取赛题相关的关键词
problem_keywords = extract_keywords(problem_segments, chinese_stopwords)
dict_file = 'D:/Code/Python/2024-TidyC/src/data/custom_dict.txt'
if not os.path.exists(dict_file):
    # 将自定义词典列表写入文件
    with open(dict_file, 'w', encoding='utf-8') as f:
        for word in problem_keywords:
            f.write(word + ' 10 n' + '\n')

        # 把题目中的关键词，加入自定义词典
jieba.load_userdict(dict_file)
for path in range(1, 2000):
    paper_pdf_path = "D:/Code/Python/2024-TidyC/data/C题-示例数据/赛题数据/附件1/C" + "{:03}".format(
        path) + ".pdf"  # 论文
    if not os.path.exists(paper_pdf_path):
        break
    paper_text = extract_pdf_text(paper_pdf_path)
    paper_text = clean_paper(paper_text)
    # 去除中文停用词和符号
    filtered_paper_text = [word for word in jieba.cut(paper_text) if word not in chinese_stopwords and word.strip()]
    # filtered_paper_text = []
    # fp = open('D:/Code/Python/2024-TidyC/src/data/text_processed.txt', "r", encoding="utf-8")
    # for line in fp:
    #     new_line = []
    #     if len(line) > 1:
    #         line = line.strip().split(" ")
    #         for w in line:
    #             w.encode(encoding="utf-8")
    #             new_line.append(w)
    #     if len(new_line) > 1:
    #         filtered_paper_text.append(new_line)

    # 创建并训练LDA主题模型
    num_topic = 8
    paper_dictionary = gensim.corpora.Dictionary(
        [paper_segment.lower().split() for paper_segment in filtered_paper_text])
    paper_bow_corpus = [paper_dictionary.doc2bow(segment.lower().split()) for segment in filtered_paper_text]
    lda_model = gensim.models.LdaModel(paper_bow_corpus, id2word=paper_dictionary, num_topics=num_topic, passes=10)

    # 获取主题关键词
    topics = lda_model.show_topics(num_topics=num_topic, num_words=20, formatted=False)
    # 从文本中识别与赛题相关的主题或话题
    # 0到1之间，如果要十分制，乘以10即可
    problem_statement_score = evaluate_problem_statement(topics, list(set(problem_keywords)))
    print(f"论文相关性得分: {problem_statement_score}")
