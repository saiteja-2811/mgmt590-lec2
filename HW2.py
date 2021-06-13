# Importing Libraries
import time
import datetime

# Flask
from flask import Flask, request
from flask import jsonify
from flask import request
from flask import Flask, render_template, request, Response

# NLP
from transformers.pipelines import pipeline
import os
import pg8000
import pandas as pd

# Global
global modelList
global default_model
import sqlite3
from flask import abort

# Database
import logging
import sqlalchemy
from werkzeug.utils import secure_filename
from google.cloud import storage
import base64
import logging
global db

logger = logging.getLogger()
# importing the psycopg2 module
import psycopg2
import shutil

# SSL Connections
dir = '.ssl'
if os.path.exists(dir):
    shutil.rmtree(dir)
os.makedirs(dir)

# setting gcs creds for access to bucket
filecontents = os.environ.get('GCS_CREDS')
decoded_creds = base64.b64decode(filecontents)
with open('creds.json', 'wb') as f1:
    f1.write(decoded_creds)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'creds.json'

# getting bucket details
storage_client = storage.Client()
bucket = storage_client.get_bucket('mgmt590-pst')

# SSL Certificates

# serverca
rootcertfile = os.environ.get('PG_SSLROOTCERT')
rootcertfile = rootcertfile.replace('@', '=')
with open('.ssl/server-ca.pem', 'w') as f:
    f.write(rootcertfile)
# clientcert
clientcertfile = os.environ.get('PG_SSLCERT')
clientcertfile = clientcertfile.replace('@', '=')
with open('.ssl/client-cert.pem', 'w') as f:
    f.write(clientcertfile)
# clientkey
clientkeyfile = os.environ.get('PG_SSLKEY')
with open('.ssl/client-key.pem', 'w') as f:
    f.write(clientkeyfile)

# File permissions in local
os.chmod(".ssl/client-key.pem", 0o600)
os.chmod(".ssl/client-cert.pem", 0o600)
os.chmod(".ssl/server-ca.pem", 0o600)

sslmode = "sslmode=verify-ca"
sslrootcert = "sslrootcert={}".format(".ssl/server-ca.pem")
sslcert = "sslcert={}".format(".ssl/client-cert.pem")
sslkey = "sslkey={}".format(".ssl/client-key.pem")

hostaddr = "hostaddr={}".format(os.environ.get('PG_HOST'))
user = "user=postgres"
password = "password={}".format(os.environ.get('PG_PASSWORD'))
dbname = "dbname=mgmt590"

# Construct database connect string
db_connect_string = " ".join([
    sslmode,
    sslrootcert,
    sslcert,
    sslkey,
    hostaddr,
    user,
    password,
    dbname
])

# Create the table structure in the database
def create_tables():
    conn = psycopg2.connect(db_connect_string)
    # Create tables (if they don't already exist)
    cur = conn.cursor()
    # Creating tables
    cur.execute(
        "CREATE TABLE IF NOT EXISTS prodscale (timestamp INT, model VARCHAR, answer VARCHAR, question VARCHAR, context VARCHAR);")
    conn.commit()
create_tables()

app = Flask(__name__)

modelList = [
    {
        'name': "distilled-bert",
        'tokenizer': "distilbert-base-uncased-distilled-squad",
        'model': "distilbert-base-uncased-distilled-squad"
    }
]
default_model = modelList[0]

# Create my flask app
app.config['JSON_SORT_KEYS'] = False

# Define a handler for the / path, which
# returns "Hello World"
@app.route("/")
def hello_world():
    return 'Hello, World!'

# Insert data into the database
def insert_db(timestamp, model, answer, question, context):
    conn = psycopg2.connect(db_connect_string)
    # Open a cursor to perform database operations
    cur = conn.cursor()
    # Creating tables
    postgres_insert_query = "INSERT INTO prodscale (timestamp, model, answer,question,context) VALUES (%s,%s,%s,%s,%s)"
    record_to_insert = (timestamp, model, answer, question, context)
    cur.execute(postgres_insert_query, record_to_insert)
    conn.commit()

# Get Answers between start and end date
def get_recent_default(start, end):
    conn = psycopg2.connect(db_connect_string)
    # Open a cursor to perform database operations
    cur = conn.cursor()
    postgres_insert_query = "SELECT timestamp, model, answer, question,context FROM prodscale WHERE timestamp BETWEEN %s AND %s"
    record_to_insert = (start, end)
    cur.execute(postgres_insert_query, record_to_insert)
    result = cur.fetchall()
    out = []
    for index, tuple in enumerate(result):
        dict = {
            "timestamp": tuple[0],
            "model": tuple[1],
            "answer": tuple[2],
            "question": tuple[3],
            "context": tuple[4]}
        out.append(dict)
    return jsonify(out)

# Get Answers between start and end date for a model
def get_recent_custom(start, end, model):
    conn = psycopg2.connect(db_connect_string)
    # Open a cursor to perform database operations
    cur = conn.cursor()
    postgres_insert_query = "SELECT timestamp, model, answer, question,context FROM prodscale WHERE timestamp BETWEEN %s AND %s AND model= %s"
    record_to_insert = (start, end, model)
    cur.execute(postgres_insert_query, record_to_insert)
    result = cur.fetchall()
    out = []
    for index, tuple in enumerate(result):
        dict = {
            "timestamp": tuple[0],
            "model": tuple[1],
            "answer": tuple[2],
            "question": tuple[3],
            "context": tuple[4]}
        out.append(dict)
    return jsonify(out)

def my_funct(text):
    abort(400, text)

# 9. function to check the file extension
ALLOWED_EXTENSIONS = {'csv'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# 10. function to upload file
def uploadOneFile(bucket, filename):
    logging.info('Inside File Uploads')

    try:
        blob = bucket.blob(filename)
        response = blob.upload_from_filename(filename)

    except Exception as ex:
        logging.error("Exception occurred while trying to upload files ", ex)
    return response

# Route to upload file
@app.route("/upload", methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return ('No file Provided')
    file = request.files['file']
    if file and allowed_file(file.filename):
        dataFrame = pd.read_csv(file)
        timestamp = int(time.time())
        fileName = 'question_context' + '_' + str(timestamp) + '.csv'
        csvFile = dataFrame.to_csv(fileName, index=False)
        response = uploadOneFile(bucket, fileName)
        return jsonify({"status": "File Uploaded Successfully", "status code": 200})

# Route to answer questions
@app.route("/answer", methods=['POST', 'GET'])
def answers():
    if request.method == 'POST':
        # Get the request body data
        model = request.args.get('model')
        data = request.json

        if (model == None):
            model = default_model['name']
            try:
                hg_comp = pipeline('question-answering', model='distilbert-base-uncased-distilled-squad',
                                   tokenizer='distilbert-base-uncased-distilled-squad')
            except:
                my_funct("Invalid Model Name")
            # Answer the answer
            answer = hg_comp({'question': data['question'], 'context': data['context']})['answer']
            timestamp = int(time.time())
            # Create the response body.
            out = {
                "timestamp": timestamp,
                "model": model,
                "answer": answer,
                "question": data['question'],
                "context": data['context']

            }

            insert_db(timestamp, model, answer, data['question'], data['context'])
            return jsonify(out)
        else:
            model_name = ""
            tokenizer = ""

            for i in range(len(modelList)):
                if modelList[i]['name'] == model:
                    model_name = modelList[i]['model']
                    tokenizer = modelList[i]['tokenizer']
                    break

            try:
                hg_comp = pipeline('question-answering', model=model_name,
                                   tokenizer=tokenizer)
            except:
                my_funct("Invalid")
            # Answer the answer
            answer = hg_comp({'question': data['question'], 'context': data['context']})['answer']

            timestamp = int(time.time())

            # Create the response body.
            out = {
                "timestamp": timestamp,
                "model": model,
                "answer": answer,
                "question": data['question'],
                "context": data['context']

            }
            insert_db(timestamp, model, answer, data['question'], data['context'])
            return jsonify(out)
    else:

        if request.args.get('start') == None or request.args.get('end') == None:
            return "Query timestamps not provided", 400
        model = request.args.get('model')
        start = request.args.get('start')
        end = request.args.get('end')

        if (model == None):
            return get_recent_default(start, end)

        else:

            return get_recent_custom(start, end, model)

# Route to get list of models
@app.route("/models", methods=['GET', 'PUT', 'DELETE'])
def getModels(modelList=modelList):
    if request.method == 'PUT':
        data = request.json
        try:
            hg_comp = pipeline('question-answering', model=data['model'],
                               tokenizer=data['tokenizer'])
            modelList.append({
                'name': data['name'],
                'tokenizer': data['tokenizer'],
                'model': data['model']
            })
        except:
            my_funct("Invalid Model Name")
        seen = set()
        new_l = []
        for d in modelList:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)
        modelList = new_l
        return jsonify(modelList)

    elif request.method == 'DELETE':
        if request.args.get('model') == None:
            return "Model name not provided in query string", 400
        model = request.args.get('model')
        for i in range(len(modelList)):
            if modelList[i]['name'] == model:
                del modelList[i]
                break
        seen = set()
        new_l = []
        for d in modelList:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)

        modelList = new_l
        return jsonify(modelList)

    else:
        seen = set()
        new_l = []
        for d in modelList:
            t = tuple(d.items())
            if t not in seen:
                seen.add(t)
                new_l.append(d)

        modelList = new_l
        return jsonify(modelList)

# Run if running "python answer.py"
if __name__ == '__main__':
    default_model = modelList[0]
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)), threaded=True)
