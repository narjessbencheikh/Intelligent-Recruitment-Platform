import io
import json
import os
import re
import subprocess
import cv2
import docx2txt
import fitz
import mysql.connector
import pymysql
import pytesseract
import spacy
from PIL import Image
from googletrans import Translator
from mysql.connector import errorcode
from pdfminer.high_level import extract_text
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
from spacy.matcher import PhraseMatcher
import glob
import shutil

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
            val2 = (num, str(item['doc_node_id']), item['doc_node_value'], SKILL_DB[item['skill_id']]['skill_type'],
                    item['score'])
            cursor.execute(sql2, val2)
            con.commit()
        print("full matches added")

        for item in int_32_removal(skills['ngram_scored']):
            sql3 = "INSERT INTO skills (`resume_id`, `doc_node_id`, `value`, `type`, `score`) " \
                   "VALUES ( %s, %s, %s, %s, %s)"
            val3 = (num, str(item['doc_node_id']), item['doc_node_value'], SKILL_DB[item['skill_id']]['skill_type'],
                    item['score'])
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


img_directory = r'C:\Users\nadaa\OneDrive\Desktop\profile pictures'
img_tmp = r'C:\Users\nadaa\OneDrive\Desktop\pictures tmp'
haarcascade_frontalface_default = r'C:\Users\nadaa\PycharmProjects\ResumeParser.v1.0\venv\Lib\site-packages\cv2\data\haarcascade_frontalface_default.xml'
default_img = r'C:\Users\nadaa\OneDrive\Pictures\Profile-Icon2.png'


def detect_photo(file_path):
    pdf_file = fitz.open(file_path)
    for page_index in range(len(pdf_file)):

        # get the page
        page = pdf_file[page_index]
        image_list = page.get_images()

        # printing number of images found in this page
        if image_list:
            print(f"[+] Found a total of {len(image_list)} images in page {page_index}")
        else:
            print("[!] No images found on page", page_index)
        for image_index, img in enumerate(image_list, start=1):
            # get the XREF of the image
            xref = img[0]
            # extract the image bytes
            base_image = pdf_file.extract_image(xref)
            image_bytes = base_image["image"]
            # get the image extension
            image_ext = base_image["ext"]
            # load it to PIL
            image = Image.open(io.BytesIO(image_bytes))
            # save it
            image.save(open(f"{img_tmp}\image{page_index + 1}_{image_index}.{image_ext}", "wb"))
            print("image saved")


def save_photo(file_path, id):
    print(file_path)
    face_cascade = cv2.CascadeClassifier(haarcascade_frontalface_default)
    if ".pdf" in file_path:
        detect_photo(file_path)
        for filename in os.listdir(img_tmp):
            img = cv2.imread(os.path.join(img_tmp, filename))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            if len(faces) != 0:
                cv2.imwrite(os.path.join(img_directory, str(id)) + ".jpg", img)
                print("photo added")
        for filename in os.listdir(img_tmp):
            file = os.path.join(img_tmp, filename)
            if os.path.isfile(file):
                print('Deleting file:', file)
                os.remove(file)
    else:
        img = cv2.imread(file_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        if len(faces) != 0:
            for (x, y, w, h) in faces:
                crop_img = img[y: y + h + 20, x: x + w]  # Crop from x, y, w, h -> 100, 200, 300, 400
                cv2.imwrite(os.path.join(img_directory, str(id)) + ".jpg", crop_img)
                print("photo added")
    if not os.path.isfile(os.path.join(img_directory, str(id)) + ".jpg"):
        for jpgfile in glob.iglob(default_img):
            shutil.copy(jpgfile, os.path.join(img_directory, str(id)) + ".jpg")
        print("profile photo set as default")

file_path = r'C:/Users/nadaa/OneDrive/Desktop/Testing CVs/Mohammed_Ali.png'
save_photo(file_path, 1)
