import p1
import p2
import p3
import p4
import os
import jieba
import math
import re
import openpyxl as op


if __name__ == '__main__':
    spark = p3.ChatSparkLLM(
        spark_api_url=p3.SPARKAI_URL,
        spark_app_id=p3.SPARKAI_APP_ID,
        spark_api_key=p3.SPARKAI_API_KEY,
        spark_api_secret=p3.SPARKAI_API_SECRET,
        spark_llm_domain=p3.SPARKAI_DOMAIN,
        streaming=False,
    )
    if not os.path.exists('result.xlsx'):
        file = open("result.xlsx", "w")
        file.close()
    title = ["论文编号", "完整性", "实质性", "摘要", "写作水平", "综合评分"]
    wb = op.Workbook() # 创建工作簿对象
    ws = wb['Sheet'] # 创建子表
    ws.append(title) # 添加表头    
    num = 0
    for path in range(1, 31):
        # ---------------------------------------------------------------------p1
        pdf_path = (
            "./data/C题-示例数据/赛题数据/附件1/C" + "{:03}".format(path) + ".pdf"
        )

        text = p1.extract_pdf_text(pdf_path)
        recognized_titles = p1.recognize_structure(text, p1.expected_titles)
        # 0到1之间，如果要十分制，乘以10即可
        p1_score = p1.evaluate_structure(recognized_titles, p1.expected_titles)
        p1_score = round(p1_score*10, 0)
        # print(p1_score)
        # ---------------------------------------------------------------------p1

        # ---------------------------------------------------------------------p2
        paper_pdf_path = "./data/C题-示例数据/赛题数据/附件1/C" + "{:03}".format(
            path) + ".pdf"  # 论文
        if not os.path.exists(paper_pdf_path):
            break
        paper_text = p2.extract_pdf_text(paper_pdf_path)
        paper_text = p2.clean_paper(paper_text)
        paper_text = p2.remove_non_chinese(paper_text)
        # 去除中文停用词和符号
        filtered_paper_text = [word for word in jieba.cut(
            paper_text) if word not in p2.chinese_stopwords and word.strip()]

        # 创建并训练LDA主题模型
        num_topic = 8
        paper_dictionary = p2.gensim.corpora.Dictionary(
            [paper_segment.lower().split() for paper_segment in filtered_paper_text])
        paper_bow_corpus = [paper_dictionary.doc2bow(
            segment.lower().split()) for segment in filtered_paper_text]
        lda_model = p2.gensim.models.LdaModel(
            paper_bow_corpus, id2word=paper_dictionary, num_topics=num_topic, passes=10)

        # 获取主题关键词
        topics = lda_model.show_topics(
            num_topics=num_topic, num_words=50, formatted=False)
        # 从文本中识别与赛题相关的主题或话题
        problem_statement_score = p2.evaluate_problem_statement(
            topics, list(set(p2.problem_keywords)))
        problem_statement_score *= 100
        p2_score = round(math.sqrt(problem_statement_score), 0)
        # print(f"论文相关性得分: {round(problem_statement_score, 0)}")
        # ---------------------------------------------------------------------p2

        # ---------------------------------------------------------------------p3
        abstract, body = p3.extract_abstract_and_body(pdf_path)

        result = p3.get_consistency_and_relevance_score(spark, abstract, body)
        first_generation_list = result.generations[0] if result.generations else [
        ]
        first_generation = first_generation_list[0]

        str_numbers = re.findall(r'\d+', first_generation.text)

        scores = float(str_numbers[0])
        p3_score = p3.get_numbers(scores)
        # print(pdf_path + ": ", scores)
        # ---------------------------------------------------------------------p3

        # ---------------------------------------------------------------------p4
        num = num + 1
        Len = 0
        # print(num, end="    ")
        while (Len == 0):
            text1 = p4.extract_pdf_text(pdf_path)
            text1 = text1.replace("政", "")
            text1 = text1.replace("government", "")
            text1 = text1.replace("governance", "")
            text1 = p4.trim_string(text1)
            text1 = text1 + '请给你对上述论文的连贯性、写作规范性、论文逻辑性进行综合评分，必须给出一个1-10之间的分数，不要解释理由'
            question = p4.checklen(p4.getText("user", text1))
            p4.SparkApi.answer = ""
            # print("星火:",end ="")
            p4.SparkApi.main(p4.appid, p4.api_key, p4.api_secret,
                             p4.Spark_url, p4.domain, question)
            numbers = re.findall(r'\d+', p4.SparkApi.answer)
            numbers_list = [int(num) for num in numbers]
            Len = len(numbers_list)
            if Len == 0:
                continue
            total = sum(numbers_list)
            average = total / Len
            while (average > 10):
                average = p4.evaluate(average)
            p4_score = round(average, 0)
            # print(average,end="\n")
            with open('output.txt', 'a', encoding='utf-8') as file:
                # 将内容写入文件
                file.write(str(average)+"\n")
            p4.getText("assistant", p4.SparkApi.answer)
        # ---------------------------------------------------------------------p4
        print(pdf_path+":评分完成！")
        comprehensiveScore = round(
            (p1_score + p2_score+p3_score+p4_score)/4, 0)
        result = ["C"+"{:03}".format(path), p1_score,
                  p2_score, p3_score, p4_score, comprehensiveScore]
        ws.append(result) # 每次写入一行
        wb.save("result.xlsx")
