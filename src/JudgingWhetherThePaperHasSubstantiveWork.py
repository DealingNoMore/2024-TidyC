import os
import re

import jieba
import matplotlib.pyplot as plt
import pyLDAvis
from gensim import corpora, models
from gensim.models import CoherenceModel
from gensim.models import LdaModel
from pdfminer.high_level import extract_text
from multiprocessing import Process, freeze_support


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
    paper_text = re.sub(r"[\.]", "", paper_text)
    paper_text = re.sub(r"[\\]", "", paper_text)
    paper_text = re.sub(r"[_*]", "", paper_text)
    return [
        word
        for word in jieba.cut(paper_text)
        if word not in cn_stopwordslist and word.strip()
    ]


# 提取题目关键词
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
        filtered_paragraph = [
        word
        for word in jieba.cut(paragraph)
        if word not in stopwordslist(stopwordslist_path) and word.strip()
    ]
        keys.append(list(set(filtered_paragraph)))
    return keys


# 评价函数
def evaluateTheRelevanceOfPapersAndCompetitionQuestions(topics, keywords):
    topic_words = []
    for topic in topics:
        topic_num = topic[0]
        topic_keywords = [word[0] for word in topic[1]]
        topic_words.extend(topic_keywords)
        print(f"问题{topic_num + 1}的关键词：{topic_words}")
    topic_coverage = len(set(keywords) & set(topic_words)) / len(keywords)
    return round(topic_coverage, 2)


def infile(fliepath):
    # 输入分词好的TXT，返回train
    train = []
    fp = open(fliepath, "r", encoding="utf-8")
    for line in fp:
        new_line = []
        if len(line) > 1:
            print("正确进入分支")
            line = line.strip().split(" ")
            print(line)
            for w in line:
                w.encode(encoding="utf-8")
                new_line.append(w)
        print(new_line)
        if len(new_line) > 1:
            train.append(new_line)
    return train


def deal(train):
    # 输入train，输出词典,texts和向量
    id2word = corpora.Dictionary(train)  # Create Dictionary
    texts = train  # Create Corpus
    corpus = [id2word.doc2bow(text) for text in texts]  # Term Document Frequency

    # 使用tfidf
    tfidf = models.TfidfModel(corpus)
    corpus = tfidf[corpus]

    id2word.save("D:/Code/Python/2024-TidyC/src/tmp/deerwester.dict")  # 保存词典
    corpora.MmCorpus.serialize("D:/Code/Python/2024-TidyC/src/tmp/deerwester.mm", corpus)  # 保存corpus

    return id2word, texts, corpus


def run(corpus_1, id2word_1, num, texts):
    # 标准LDA算法
    lda_model = LdaModel(
        corpus=corpus_1,
        id2word=id2word_1,
        num_topics=num,
        passes=60,
        alpha=(50 / num),
        eta=0.01,
        random_state=42,
    )
    # num_topics：主题数目
    # passes：训练伦次
    # num：每个主题下输出的term的数目
    # 输出主题
    # topic_list = lda_model.print_topics()
    # for topic in topic_list:
    # print(topic)
    # 困惑度
    perplex = lda_model.log_perplexity(
        corpus_1
    )  # a measure of how good the model is. lower the better.
    # 一致性
    coherence_model_lda = CoherenceModel(
        model=lda_model, texts=texts, dictionary=id2word_1, coherence="c_v"
    )
    coherence_lda = coherence_model_lda.get_coherence()
    # print('\n一致性指数: ', coherence_lda)   # 越高越好
    return lda_model, coherence_lda, perplex


def save_visual(lda, corpus, id2word, name):
    # 保存为HTML
    d = pyLDAvis.gensim.prepare(lda, corpus, id2word)
    pyLDAvis.save_html(d, name + ".html")  # 可视化


def compute_coherence_values(dictionary, corpus, texts, start, limit, step):
    coherence_values = []
    perplexs = []
    model_list = []
    for num_topic in range(start, limit, step):
        # 模型
        lda_model, coherence_lda, perplex = run(corpus, dictionary, num_topic, texts)
        # lda_model = LdaModel(corpus=corpus,num_topics=num_topic,id2word=dictionary,passes=50)
        model_list.append(lda_model)
        perplexs.append(perplex)  # 困惑度
        # 一致性
        # coherence_model_lda = CoherenceModel(model=lda_model, texts=texts, dictionary=dictionary, coherence='c_v')
        # coherence_lda = coherence_model_lda.get_coherence()
        coherence_values.append(coherence_lda)

    return model_list, coherence_values, perplexs


def compute_coherence_values(dictionary, corpus, texts, start, limit, step):
    """
    Compute c_v coherence for various number of topics

    Parameters:
    ----------
    dictionary : Gensim dictionary
    corpus : Gensim corpus
    texts : List of input texts
    limit : Max num of topics

    Returns:
    -------
    model_list : List of LDA topic models
    coherence_values : Coherence values corresponding to the LDA model with respective number of topics
    """
    coherence_values = []
    perplexs = []
    model_list = []
    for num_topic in range(start, limit, step):
        # 模型
        lda_model, coherence_lda, perplex = run(corpus, dictionary, num_topic, texts)
        # lda_model = LdaModel(corpus=corpus,num_topics=num_topic,id2word=dictionary,passes=50)
        model_list.append(lda_model)
        perplexs.append(perplex)  # 困惑度
        # 一致性
        # coherence_model_lda = CoherenceModel(model=lda_model, texts=texts, dictionary=dictionary, coherence='c_v')
        # coherence_lda = coherence_model_lda.get_coherence()
        coherence_values.append(coherence_lda)

    return model_list, coherence_values, perplexs


def show_1(dictionary, corpus, texts, start, limit, step):
    # 从 5 个主题到 30 个主题，步长为 5 逐次计算一致性，识别最佳主题数
    model_list, coherence_values, perplexs = compute_coherence_values(
        dictionary, corpus, texts, start, limit, step
    )
    # 输出一致性结果
    n = 0
    for m, cv in zip(perplexs, coherence_values):
        print(
            "主题模型序号数",
            n,
            "主题数目",
            (n + 4),
            "困惑度",
            round(m, 4),
            " 主题一致性",
            round(cv, 4),
        )
        n = n + 1
    # 打印折线图
    x = list(range(start, limit, step))
    # 困惑度
    plt.plot(x, perplexs)
    plt.xlabel("Num Topics")
    plt.ylabel("perplex  score")
    plt.legend(("perplexs"), loc="best")
    plt.show()
    # 一致性
    plt.plot(x, coherence_values)
    plt.xlabel("Num Topics")
    plt.ylabel("Coherence score")
    plt.legend(("coherence_values"), loc="best")
    plt.show()

    return model_list


# 文件地址
problem_pdf_path = "D:/Code/Python/2024-TidyC/data/C题-示例数据/赛题数据/附件2/C题 - “智慧政务”中的文本挖掘应用.pdf"
mainPoints_pdf_path = "D:/Code/Python/2024-TidyC/data/C题-示例数据/赛题数据/附件2/C题 - “智慧政务”中的文本挖掘应用评阅要点.pdf"
paper_text_path = "D:/Code/Python/2024-TidyC/data/C题-示例数据/赛题数据/附件1/C001.pdf"
stopwordslist_path = "D:/Code/Python/2024-TidyC/stopwords-master/hit_stopwords.txt"
# 中文停止词列表
cn_stopwordslist = stopwordslist(stopwordslist_path)
# 读取文件内容
problem_text = extract_pdf_text(problem_pdf_path)
mainPoints_text = extract_pdf_text(mainPoints_pdf_path)
paper_text = extract_pdf_text(paper_text_path)
cleaned_papers = paragraphs_text(paper_text)
essay = "".join(cleaned_papers)
cleaned_paper = removeChineseStopWords(essay)

keys = extractKeyWordsFromTheQuestion(mainPoints_text)
# print(keys)
dict_file = "D:/Code/Python/2024-TidyC/src/data/C001.txt"
if not os.path.exists(dict_file):
    with open(dict_file, "w", encoding="utf-8") as f:
        for word in cleaned_paper:
            f.write(word + "\n")
# jieba.load_userdict(dict_file)
# print(keys)

# 创建和训练LAD主题模型
# num_topic = 10
# paper_dictionary = gensim.corpora.Dictionary(
#     [paper_segment.lower().split() for paper_segment in cleaned_papers]
# )
# paper_bow_corpus = [
#     paper_dictionary.doc2bow(segment.lower().split()) for segment in cleaned_papers
# ]
# lda_model = gensim.models.LdaModel(
#     paper_bow_corpus, id2word=paper_dictionary, num_topics=num_topic, passes=10
# )

# # 获取问题关键词
# topics = lda_model.show_topics(num_topics=num_topic, num_words=20, formatted=False)

# score = evaluateTheRelevanceOfPapersAndCompetitionQuestions(topics, keys)


if __name__ == '__main__':
    train = []
    train.append(cleaned_paper)
    # print(train)
    name = "C001.txt"  # 后续结果文件名
    id2word, texts, corpus = deal(train)
    model_list = show_1(id2word, corpus, texts, 4, 16, 1)
