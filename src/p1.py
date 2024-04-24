import re

from pdfminer.high_level import extract_text


# 读取PDF文件内容
def extract_pdf_text(pdf_path):
    return extract_text(pdf_path)


# 识别标题结构
def recognize_structure(text, titles):
    recognized_titles = [
        title for title in titles if re.search(title, text, re.IGNORECASE)
    ]

    return recognized_titles


# 评估结构的逻辑完整性和条理性
def evaluate_structure(recognized_titles, expected_titles):
    if recognized_titles == expected_titles:
        logic_score = 1
    else:
        logic_score = round(len(recognized_titles) / len(expected_titles), 1)

    return logic_score


for path in range(1, 21):
    pdf_path = (
            "2024泰迪杯c/C题-示例数据/赛题数据/附件1/C" + "{:03}".format(path) + ".pdf"
    )
    expected_titles = [
        "摘要",
        "目录",
        "问题重述",
        "假设条件",
        "符号说明",
        "模型建立",
        "模型求解",
        "模型检验",
        "结果分析",
        "结论",
        "参考文献",
        "附录",
    ]
    text = extract_pdf_text(pdf_path)
    recognized_titles = recognize_structure(text, expected_titles)
    # 0到1之间，如果要十分制，乘以10即可
    score = evaluate_structure(recognized_titles, expected_titles)
    print(f"论文结构的逻辑完整性和条理性得分: {score:.2f}")
