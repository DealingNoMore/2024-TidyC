import os.path

from JudgingWhetherThePaperHasSubstantiveWork import extract_pdf_text, paragraphs_text, removeChineseStopWords

train_text = []
for path in range(1, 21):
    pdf_path = (
            "D:/Code/Python/2024-TidyC/data/C题-示例数据/赛题数据/附件1/C" + "{:03}".format(path) + ".pdf"
    )
    pdf_text = extract_pdf_text(pdf_path)
    cleaned_pdf_text = paragraphs_text(pdf_text)
    pdf_text_list = removeChineseStopWords("".join(cleaned_pdf_text))
    train_text.append(pdf_text_list)

filepath = 'data/text_processed.txt'
if not os.path.exists(filepath):
    with open(filepath, 'w',encoding="utf-8") as file:
        for item in train_text:
            file.write(f'{item}'+'\n')

