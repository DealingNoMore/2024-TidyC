import re
from pdfminer.high_level import extract_text
import numpy as np
import os


def extract_pdf_text(pdf_path):
    return extract_text(pdf_path)


problem_pdf_path = (
    'data/C题-示例数据/赛题数据/附件2/C题 - "智慧政务"中的文本挖掘应用.pdf'
)
paper_pdf_path = "2024泰迪杯c/C题-示例数据/赛题数据/附件1/"

# 读取文件内容
problem_text = extract_pdf_text(problem_pdf_path)
paper_text = extract_pdf_text(paper_pdf_path)

print(problem_text)
