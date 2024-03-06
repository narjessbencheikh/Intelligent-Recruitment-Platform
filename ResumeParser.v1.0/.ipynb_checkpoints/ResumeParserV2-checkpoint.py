import json
import os
import subprocess
import sys
import nlp as nlp
import spacy
from spacy.matcher import Matcher
from spacy.matcher import PhraseMatcher
import docx2txt
import nltk
import requests
from pdfminer.high_level import extract_text
import re
from nltk.corpus import stopwords
from skillNer.general_params import SKILL_DB
# import skill extractor
from skillNer.skill_extractor_class import SkillExtractor

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


nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('stopwords')
nltk.download('words')

nlp = spacy.load('en_core_web_sm')

# initialize matcher with a vocab
matcher = Matcher(nlp.vocab)


def extract_names(txt):

    nlp_text = nlp(txt)

    # First name and Last name are always Proper Nouns
    pattern = [{'POS': 'PROPN'}, {'POS': 'PROPN'}]

    matcher.add('NAME', [pattern])

    matches = matcher(nlp_text)

    for match_id, start, end in matches:
        span = nlp_text[start:end]
        return span.text


def extract_phone_number(resume_text):

    phone = re.findall(re.compile(r'(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?'),text)

    if phone:
        number = ''.join(phone[0])
        if len(number) > 10:
            return '+' + number
        else:
            return number


EMAIL_REG = re.compile(r'[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+')


def extract_emails(resume_text):
    return re.findall(EMAIL_REG, resume_text)


# def skill_exists(skill):
#     url = f'https://api.apilayer.com/skills?q={skill}&amp;count=1'
#     headers = {'apikey': 'wG2Qu01yBgFzBHQO7cTl6xYoEIWu6i0T'}
#     response = requests.request('GET', url, headers=headers)
#     result = response.json()
#
#     if response.status_code == 200:
#         return len(result) > 0 and result[0].lower() == skill.lower()
#     raise Exception(result.get('message'))
#
#
# def extract_skills(input_text):
#     stop_words = set(nltk.corpus.stopwords.words('english'))
#     word_tokens = nltk.tokenize.word_tokenize(input_text)
#
#     # remove the stop words
#     filtered_tokens = [w for w in word_tokens if w not in stop_words]
#
#     # remove the punctuation
#     filtered_tokens = [w for w in word_tokens if w.isalpha()]
#
#     # generate bigrams and trigrams (such as artificial intelligence)
#     bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))
#
#     # we create a set to keep the results in.
#     found_skills = set()
#
#     # we search for each token in our skills database
#     for token in filtered_tokens:
#         if skill_exists(token.lower()):
#             found_skills.add(token)
#
#     # we search for each bigram and trigram in our skills database
#     for ngram in bigrams_trigrams:
#         if skill_exists(ngram.lower()):
#             found_skills.add(ngram)
#
#     return found_skills
def extract_skills(txt):
    nlp = spacy.load("en_core_web_lg")
    skill_extractor = SkillExtractor(nlp, SKILL_DB, PhraseMatcher)

    # extract skills from job_description

    annotations = skill_extractor.annotate(txt)
    return annotations

RESERVED_WORDS = [
    'school',
    'college',
    'university',
    'academy',
    'faculty',
    'institute',
    'faculté',
    'ecole',
    'école',
    'lycée',
    'lycee',
    'polytechnique',
    'collège',
    'institut'
    'université'

]
STOPWORDS = set(stopwords.words('english'))

# Education Degrees
EDUCATION = [
    'BE', 'B.E.', 'B.E', 'BS', 'B.S',
    'ME', 'M.E', 'M.E.', 'M.B.A', 'MBA', 'MS', 'M.S',
    'BTECH', 'B.TECH', 'M.TECH', 'MTECH',
    'SSLC', 'SSC' 'HSC', 'CBSE', 'ICSE', 'X', 'XII',
    'Licence', 'Diplome', 'Doctorat', 'Ecole'
]


def extract_education(input_text):

    nlp_text = nlp(input_text)

    # Sentence Tokenizer
    nlp_text = [sent.text.strip() for sent in nlp_text.sents]

    edu = {}
    # Extract education degree
    for index, text in enumerate(nlp_text):
        for tex in text.split():
            # Replace all special symbols
            tex = re.sub(r'[?|$|.|!|,]', r'', tex)
            if tex.upper() in EDUCATION and tex not in STOPWORDS:
                edu[tex] = text + nlp_text[index + 1]

    # Extract year
    education = []
    for key in edu.keys():
        year = re.search(re.compile(r'(((20|19)(\d{})))'), edu[key])
        if year:
            education.append((key, ''.join(year[0])))
        else:
            education.append(key)
    return education

# def extract_education(input_text):
#     organizations = []
#
#     # first get all the organization names using nltk
#     for sent in nltk.sent_tokenize(input_text):
#         for chunk in nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent))):
#             if hasattr(chunk, 'label') and chunk.label() == 'ORGANIZATION':
#                 organizations.append(' '.join(c[0] for c in chunk.leaves()))
#
#     # we search for each bigram and trigram for reserved words
#     # (college, university etc...)
#     education = set()
#     for org in organizations:
#         for word in RESERVED_WORDS:
#             if org.lower().find(word) >= 0:
#                 education.add(org)
#     return education


file_path = "C:/Users/nadaa/Downloads/CV.pdf"
file_name, file_extension = os.path.splitext(file_path)

if file_extension == ".pdf":
    text = extract_text_from_pdf(file_path)

if file_extension == ".docx":
    text = extract_text_from_docx(file_path)

if file_extension == ".doc":
    text, err = doc_to_text_catdoc(file_path)

    if err:
        print(err)
        sys.exit(2)

names = extract_names(text)
if names:
    print(names)

print("-------------------------------------------------")

phone_number = extract_phone_number(text)
if phone_number:
    print("Phone:" + phone_number)

print("-------------------------------------------------")

emails = extract_emails(text)
if emails:
    print("Email: " + emails[0])

print("-------------------------------------------------")

education_information = extract_education(text)
print("Education:" + str(education_information))

print("-------------------------------------------------")

skills = extract_skills(text)
print("Skills:")
print(skills)
