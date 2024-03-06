import re
import subprocess
import sys
import spacy
from spacy.matcher import PhraseMatcher
import docx2txt
from googletrans import Translator
from pdfminer.high_level import extract_text
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
from resume_parser import resumeparse
from PIL import Image
import cv2
import pytesseract
import img2pdf
import os
import json
import pymysql
import mysql.connector
from mysql.connector import errorcode


def extract_text_from_pdf(pdf_path):
    return extract_text(pdf_path)


def extract_text_from_docx(docx_path):
    txt = docx2txt.process(docx_path)
    if txt:
        return txt.replace('\t', ' ')
    return None


def doc_to_text_catdoc(file_path):
    try:
        process = subprocess.Popen(
            ['catdoc', '-w', file_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )
    except (
            FileNotFoundError,
            ValueError,
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
    ) as err:
        return (None, str(err))
    else:
        stdout, stderr = process.communicate()
    return (stdout.strip(), stderr.strip())


def img_to_text(file_path):
    # path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    # img = Image.open(file_path)
    # pytesseract.tesseract_cmd = path_to_tesseract
    # txt = pytesseract.image_to_string(img)
    # return txt
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    img = cv2.imread(file_path)
    txt = pytesseract.image_to_string(img)
    return txt


def extract_skills(txt):
    nlp = spacy.load("en_core_web_lg")

    skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)

    # extract skills from job_description

    annotations = skill_extractor.annotate(txt)

    return annotations['results']


def extract_linkedin(txt):
    LINKEDIN_REG = re.compile(r'linkedin.com/+[a-z0-9]+/+[a-z0-9\.\-+_]+[a-z0-9\.\-+_]+[a-z0-9\.\-+_]+-*')
    return re.findall(LINKEDIN_REG, txt)


def translate_text(txt):
    file_translate = Translator()
    result = file_translate.translate(txt, dest='en')
    # print(result.text)
    with open('translation.txt', 'w') as f:
        f.write(result.text)
    return result.text

def int_32_removal(dict2):
    for e in dict2:
        e.update({'score': float(e['score'])})
        e.update({'len': int(e['len'])})
    return dict2


def add_to_db(data, skills):
    try:
        con = pymysql.connect(user='root',
                              password='',
                              database='resumes')
        print("Connected to db")
        cursor = con.cursor()

        sql = "INSERT INTO resume(`name`, `email`, `phone`, `university`, `degree`, `designition`, `companies`, `exp`)" \
              " VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
        val = (data['name'], data['email'], data['phone'], str(data['university']),
               str(data['degree']), str(data['designition']), str(data['Companies worked at']), data['total_exp'])
        cursor.execute(sql, val)
        con.commit()
        num = cursor.lastrowid
        print(num)
        for item in skills['full_matches']:
            sql2 = "INSERT INTO skills (`resume_id`, `doc_node_id`, `value`, `type`, `score`) " \
                   "VALUES ( %s, %s, %s, %s, %s)"
            val2 = (num,  str(item['doc_node_id']), item['doc_node_value'], SKILL_DB[item['skill_id']]['skill_type'], item['score'])
            cursor.execute(sql2, val2)
            con.commit()
        print("full matches added")

        for item in int_32_removal(skills['ngram_scored']):
            sql3 = "INSERT INTO skills (`resume_id`, `doc_node_id`, `value`, `type`, `score`) " \
                   "VALUES ( %s, %s, %s, %s, %s)"
            val3 = (num,  str(item['doc_node_id']), item['doc_node_value'], SKILL_DB[item['skill_id']]['skill_type'], item['score'])
            cursor.execute(sql3, val3)
            con.commit()
        print("Sub-matches added")


    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        con.close()


def generate_Json(data, skills):
    dictionary = {
        "name": data['name'],
        "email": data['email'],
        "phone": data['phone'],
        "university": data['university'],
        "degree": data['degree'],
        "designition": data['designition'],
        "Companies worked at": data['Companies worked at'],
        "total_exp": data['total_exp'],
        "full_matches": skills['full_matches'],
        "ngram_scored": int_32_removal(skills['ngram_scored'])
    }

    # print(dictionary)
    json_object = json.dumps(dictionary, indent=4)
    with open("data.json", "w") as outfile:
        outfile.write(json_object)
    return json_object

#
# file_path = r"C:\Users\nadaa\OneDrive\Pictures\resume.png"
# file_name, file_extension = os.path.splitext(file_path)
#
# if file_extension == ".pdf":
#     text = extract_text_from_pdf(file_path)
#
# elif file_extension == ".docx":
#     text = extract_text_from_docx(file_path)
#
# elif file_extension == ".doc":
#     text, err = doc_to_text_catdoc(file_path)
#
#     if err:
#         print(err)
#         sys.exit(2)
# else:
#     text = img_to_text(file_path)
#
#
# translation = translate_text(text)
# data = resumeparse.read_file('translation.txt')
# # print(data)
# # print(data['name'])
# # print(data['email'])
# # print(data['phone'])
# # print(str(extract_linkedin(text)))
# # print(data['university'])
# # print(data['degree'])
# # print(data['designition'])
# # print(data['Companies worked at'])
# # print(data['total_exp'])
# #
# #
# # skills = extract_skills(translation)
# # print("Skills:")
# # print(skills)
# skills = extract_skills(translation)
#
# add_to_db(data, skills)
# generate_Json(data, skills)

from docx2pdf import convert
file_path = r"C:\Users\nadaa\Downloads\98-modele-cv-aide-soignant_1.docx"
directory = r"C:\Users\nadaa\OneDrive\Desktop\resumes uploaded"
def doc_to_pdf():
    filename = os.path.basename(file_path)
    filename_without_ext = os.path.splitext(filename)[0]
    print(file_path)
    print(os.path.join(directory, (filename_without_ext + '.pdf')))
    convert(file_path, os.path.join(directory, (filename_without_ext + '.pdf')))
    return filename_without_ext + '.pdf'


def fetchSkillsDB():
    list = []
    for key in SKILL_DB:
        list.append({
            'value': SKILL_DB[key]['skill_name'],
            'type': SKILL_DB[key]['skill_type'],
        })
    return list

print (doc_to_pdf())