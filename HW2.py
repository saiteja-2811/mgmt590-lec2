#------------------------------#
# Question Answering REST -API #
#------------------------------#

#-----------------------#
# Import the Libraries  #
#-----------------------#
import time #Time
from flask import Flask,request,jsonify,abort,render_template,Response #Flask
from transformers.pipelines import pipeline #NLP
import os #OS
import pg8000
import datetime
import logging
import sqlalchemy #Cloud SQL
import shutil #SSL Files
import psycopg2 #Cloud SQL

#-------------------#
# Global Variables  #
#-------------------#
global modelList
global default_model
global db

logger = logging.getLogger()

#------------------------------#
# Connecting to Google SQL DB  #
#------------------------------#
# Make a directory within the code
dir = 'ssl'
if os.path.exists(dir):
    shutil.rmtree(dir)
os.makedirs(dir)

# Pass the SSL certificate of the root.
rootcertfile = os.environ.get('PG_SSLROOTCERT')
rootcertfile = rootcertfile.replace('@', '=')
with open('ssl/server-ca.pem', 'w') as f:
    f.write(rootcertfile)

# Pass the SSL certificate of the client.
clientcertfile = os.environ.get('PG_SSLCERT')
clientcertfile = clientcertfile.replace('@', '=')
with open('ssl/client-cert.pem', 'w') as f:
    f.write(clientcertfile)

# Pass the SSL key of the client.
clientkeyfile = os.environ.get('PG_SSLKEY')
with open('ssl/client-key.pem', 'w') as f:
    f.write(clientkeyfile)

# Making the private files as public
os.chmod("ssl/client-key.pem", 0o600)
os.chmod("ssl/client-cert.pem", 0o600)
os.chmod("ssl/server-ca.pem", 0o600)

# Database inputs
sslmode = "sslmode=verify-ca"
sslrootcert = "sslrootcert={}".format("ssl/server-ca.pem")
sslcert = "sslcert={}".format("ssl/client-cert.pem")
sslkey = "sslkey={}".format("ssl/client-key.pem")

hostaddr = "hostaddr={}".format(os.environ.get('PG_HOST'))
user = "user=postgres"
password = "password={}".format(os.environ.get('PG_PASSWORD'))
dbname = "dbname=mgmt590"

# Construct database connect string using the
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
app = Flask(__name__)

# This global variable is declared with a value of `None`, instead of calling
# `init_connection_engine()` immediately, to simplify testing. In general, it
# is safe to initialize your database connection pool when your script starts
# -- there is no need to wait for the first request.

#---------------------------------#
# Function to create tables in DB #
#---------------------------------#
def create_tables():
    # Make the DB connection
    conn = psycopg2.connect(db_connect_string)
    cur = conn.cursor()
    # Create tables (if they don't already exist)
    cur.execute(
        "CREATE TABLE IF NOT EXISTS prodscale (timestamp INT, model VARCHAR, answer VARCHAR, question VARCHAR, context VARCHAR);")
    conn.commit()

# Default models list
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

#---------------------------------------------#
# Function to insert values into tables in DB #
#---------------------------------------------#

def insert_db(timestamp, model, answer, question, context):
    conn = psycopg2.connect(db_connect_string)
    # Open a cursor to perform database operations
    cur = conn.cursor()
    # Creating tables
    postgres_insert_query = "INSERT INTO prodscale (timestamp, model, answer,question,context) VALUES (%s,%s,%s,%s,%s)"
    record_to_insert = (timestamp, model, answer, question, context)
    cur.execute(postgres_insert_query, record_to_insert)
    conn.commit()

#--------------------------------#
# Function to get default values #
#--------------------------------#
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

#-------------------------------#
# Function to get custom values #
#-------------------------------#
def get_recent_custom(start, end, model):
    conn = psycopg2.connect(db_connect_string)
    # Open a cursor to perform database operations
    cur = conn.cursor()
    postgres_insert_query = "SELECT timestamp, model, answer, question,context FROM prodscale WHERE timestamp BETWEEN %s AND %s model= %s"
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

# Check for an error
def my_funct(text):
    abort(400, text)

#-----------------------------#
# Route to POST & GET answers #
#-----------------------------#
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

#-----------------------------------------#
# Route to DELETE PUT & GET Model Details #
#-----------------------------------------#
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

#-----------------------------------------#
# Default Commands to run in the file     #
#-----------------------------------------#
# Run if running "python answer.py"
if __name__ == '__main__':
    # Run our Flask app and start listening for requests!
    default_model = modelList[0]
    create_tables()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)), threaded=True)
