import json
import os
import re
import subprocess
import sys
import time
import cv2
import docx2txt
import mysql.connector
import pymysql
import pytesseract
import pywintypes
import spacy
from docx2pdf import convert
from flask import Flask, jsonify, request
from flask_cors import CORS
from googletrans import Translator
from mysql.connector import errorcode
from pdfminer.high_level import extract_text
from resume_parser import resumeparse
from skillNer.general_params import SKILL_DB
from skillNer.skill_extractor_class import SkillExtractor
from spacy.matcher import PhraseMatcher
from werkzeug.utils import secure_filename
import pythoncom

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


def doc_to_pdf(file_path, directory):
    filename = os.path.basename(file_path)
    filename_without_ext = os.path.splitext(filename)[0]
    print(filename, filename_without_ext)
    outputFile = os.path.join(directory, (filename_without_ext + '.pdf'))
    print(outputFile)
    convert(file_path, outputFile, pythoncom.CoInitialize())
    print('converted')
    os.remove(file_path)
    return filename_without_ext + '.pdf'


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
    if re.findall(LINKEDIN_REG, txt)!=[]:
        return re.findall(LINKEDIN_REG, txt)
    else:
        return ''


def translate_text(txt):
    file_translate = Translator()
    result = file_translate.translate(txt, dest='en')
    #print(result.text)
    with open('translation.txt', 'w' , encoding='utf-8') as f:
        f.write(result.text)
    return result.text


def int_32_removal(dict2):
    for e in dict2:
        e.update({'score': float(e['score'])})
        e.update({'len': int(e['len'])})
    return dict2


# For testing
# def generate_Json(data, skills):
#     dictionary = {
#         "name": data['name'],
#         "email": data['email'],
#         "phone": data['phone'],
#         "university": data['university'],
#         "degree": data['degree'],
#         "designition": data['designition'],
#         "Companies worked at": data['Companies worked at'],
#         "total_exp": data['total_exp'],
#         "full_matches": skills['full_matches'],
#         "ngram_scored": int_32_removal(skills['ngram_scored'])
#     }
#
#     # print(dictionary)
#     json_object = json.dumps(dictionary, indent=4)
#     with open("data.json", "w") as outfile:
#         outfile.write(json_object)
#     return json_object

def add_to_db(data, skills, linkedin, file_path):
    num = 0
    try:
        con = pymysql.connect(user='root',
                              password='',
                              database='resumes')
        print("Connected to db")
        cursor = con.cursor()

        sql = "INSERT INTO resume(`name`, `email`, `phone`, `linkedin`, `university`, `degree`, `designition`, `companies`, `exp`, `file_path`, `checked`)" \
              " VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (data['name'], data['email'], data['phone'], linkedin, str(data['university']),
               str(data['degree']), str(data['designition']), str(data['Companies worked at']),
               data['total_exp'], file_path, False)
        print(val)
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
    return num


def fetchResumes():
    try:
        con = pymysql.connect(user='root',
                              password='',
                              database='resumes')
        print("Connected to db")
        cursor = con.cursor()

        sql = "select * from resume"
        cursor.execute(sql)
        r = [dict((cursor.description[i][0], value) \
                  for i, value in enumerate(row)) for row in cursor.fetchall()]
        return r
        # return cursor.fetchall()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        con.close()


def fetchSkills(id):
    try:
        con = pymysql.connect(user='root',
                              password='',
                              database='resumes')
        print("Connected to db")
        cursor = con.cursor()

        sql = """select * from skills where resume_id = %s"""
        cursor.execute(sql, (id,))
        r = [dict((cursor.description[i][0], value) \
                  for i, value in enumerate(row)) for row in cursor.fetchall()]
        return r
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        con.close()


def fetchDetails(id):
    try:
        con = pymysql.connect(user='root',
                              password='',
                              database='resumes')
        print("Connected to db")
        cursor = con.cursor()

        sql = """select * from resume where id = %s"""
        cursor.execute(sql, (id,))
        r = [dict((cursor.description[i][0], value) \
                  for i, value in enumerate(row)) for row in cursor.fetchall()]
        return r
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        con.close()


def extractData(file_path):
    # file_path = r"C:\Users\nadaa\OneDrive\Pictures\resume.png"
    file_name, file_extension = os.path.splitext(file_path)

    if file_extension == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif file_extension == ".docx":
        text = extract_text_from_docx(file_path)
    elif file_extension == ".doc":
        text, err = doc_to_text_catdoc(file_path)

        if err:
            print(err)
            sys.exit(2)
    else:
        text = img_to_text(file_path)

    translation = translate_text(text)
    #data = resumeparse.read_file('translation.txt')
    #
    # skills = extract_skills(translation)
    return resumeparse.read_file('translation.txt'), extract_skills(translation), extract_linkedin(translation)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def delete_resume(id):
    try:
        con = pymysql.connect(user='root',
                              password='',
                              database='resumes')
        print("Connected to db")
        cursor = con.cursor()
        sql1 = """select file_path from resume where id = %s"""
        cursor.execute(sql1, (id,))
        file_path = cursor.fetchall()
        sql2 = """delete from resume where id = %s"""
        cursor.execute(sql2, (id,))
        con.commit()
        cursor.execute(sql1, (id,))
        return cursor.fetchall(), file_path
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        con.close()


def update_resume(resume_id, data):
    try:
        con = pymysql.connect(user='root',
                              password='',
                              database='resumes')
        print("Connected to db")
        cursor = con.cursor()
        sql = """UPDATE resume SET name=%s, email=%s, phone=%s, linkedin=%s, university=%s, degree=%s, designition=%s, companies=%s, exp=%s, checked=%s WHERE id = %s"""
        val = (
            data['name'], data['email'], data['phone'], data['linkedin'], str(data['university']), str(data['degree']),
            str(data['designition']), str(data['companies']), data['exp'], data['checked'], resume_id)
        cursor.execute(sql, val)
        con.commit()
        return cursor.rowcount
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        con.close()


def update_skills(resume_id, skills):
    try:
        con = pymysql.connect(user='root',
                              password='',
                              database='resumes')
        print("Connected to db")
        cursor = con.cursor()
        sql = "delete from skills where resume_id = %s"
        val = resume_id
        cursor.execute(sql, val)
        con.commit()
        print("skills deleted")
        for item in skills:
            sql2 = "INSERT INTO skills (`resume_id`, `doc_node_id`, `value`, `type`, `score`) " \
                   "VALUES ( %s, %s, %s, %s, %s)"
            val2 = (resume_id, item['doc_node_id'], item['value'], item['type'], str(item['score']))
            cursor.execute(sql2, val2)
            con.commit()
        return cursor.rowcount
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Access denied")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        con.close()


def fetchSkillsDB():
    list = []
    for key in SKILL_DB:
        list.append({
            'value': SKILL_DB[key]['skill_name'],
            'type': SKILL_DB[key]['skill_type'],
            'doc_node_id': '[]',
            'score': '2'
        })
    return list


DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
path = os.getcwd()
UPLOAD_FOLDER = r'C:\Users\dell\Desktop\tmp'
directory = r'C:\Users\dell\Desktop\resumes_uploaded'
if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = set(['doc', 'docx', 'txt', 'pdf', 'png', 'jpg', 'jpeg'])
CORS(app, resources={r'/*': {'origins': '*'}})
CORS_ALLOW_ALL_ORIGINS = True


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    file = request.files.get('file')
    if file:
        if file.filename == "":
            return {"message": "No file found", "status": "error"}

        elif allowed_file(file.filename) is True:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            return {
                "filename": filename,
                "message": "file uploaded",
                "status": "success",
            }


@app.route('/removeFile', methods=['GET', 'DELETE'])
def remove_file():
    file_upload_args = request.get_json()
    filename = file_upload_args["cancel_file"]
    filename_no_extension = filename.rsplit(".", 1)[0]
    try:
        os.remove(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        return jsonify({
            'status': 'success',
            'message': 'upload cancelled'
        })
    except FileNotFoundError:
        return jsonify({
            'status': 'failed',
            'message': 'file not found'
        })


@app.route('/Re-extract/<resume_id>/<path:file_name>', methods=['GET', 'POST'])
def Re_extract(resume_id, file_name):
    print(file_name)
    try:

        delete_resume(resume_id)
        data, skills, linkedin = extractData(os.path.join(directory, file_name))
        num = add_to_db(data, skills, linkedin, os.path.join(directory, file_name))

    except Exception as e:
        return jsonify({
            'status': 'failed',
            'message': str(e)})

    return jsonify({
        'status': 'success',
        'new_id': num,
        'message': 'file extracted'
    })


@app.route('/extract', methods=['GET', 'POST'])
def parseToJson():
    try:
        for filename in os.listdir(app.config["UPLOAD_FOLDER"]):
            file_extension = os.path.splitext(filename)[1]
            if file_extension == '.docx':
                filename = doc_to_pdf(os.path.join(app.config["UPLOAD_FOLDER"], filename), directory)
                print('file:', filename)

            else:
                os.rename(os.path.join(app.config["UPLOAD_FOLDER"], filename), os.path.join(directory, filename))

            data, skills, linkedin = extractData(os.path.join(directory, filename))
            add_to_db(data, skills, linkedin, os.path.join(directory, filename))
    except Exception as e:
        for file_name in os.listdir(UPLOAD_FOLDER):
            # construct full file path
            file = UPLOAD_FOLDER + file_name
            if os.path.isfile(file):
                print('Deleting file:', file)
                os.remove(file)
        print(e)
        return jsonify({
            'status': 'failed',
            'message': 'parsing failed'})

    return jsonify({
        'status': 'success',
        'message': str(os.listdir(app.config["UPLOAD_FOLDER"]))
    })


@app.route('/fetchAll', methods=['GET'])
def fetchAll():
    return jsonify({
        'status': 'success',
        'resumes': fetchResumes()
    })


@app.route('/fetchResume/<resume_id>', methods=['GET'])
def fetchResume(resume_id):
    return jsonify({
        'status': 'success',
        'data': fetchDetails(resume_id),
        'skills': fetchSkills(resume_id)
    })


@app.route('/DeleteResume/<resume_id>', methods=['DELETE'])
def DeleteResume(resume_id):
    record = delete_resume(resume_id)
    if not record[0]:
        print(record[1])
        os.remove(record[1][0][0])
        return jsonify({
            'status': 'success',
            'message': 'deleted'
        })

    else:
        return jsonify({
            'status': 'failed',
            'message': 'error deleting resume'
        })


@app.route('/UpdateResume/<resume_id>', methods=['PUT'])
def UpdateResume(resume_id):
    try:
        data = request.get_json()
        json_object = json.dumps(data, indent=4)
        with open("response.json", "w") as outfile:
            outfile.write(json_object)
        record1 = update_resume(resume_id, data['data'])
        record2 = update_skills(resume_id, data['skills']['skills'])

        return jsonify({
            'status': 'success',
            'resume update message': 'updated'.join(str(record1)),
            'skills update message': 'updated'.join(str(record2)),
        })
    except Exception as e:
        print(e)
        return jsonify({
            'status': 'failed',
            'message': 'exception occured'
        })


@app.route('/fetchAllSkills', methods=['GET'])
def FetchSKILLS_DB():
    return jsonify({
        'statuts': 'success',
        'data': fetchSkillsDB()
    })


if __name__ == '__main__':
    app.run()
