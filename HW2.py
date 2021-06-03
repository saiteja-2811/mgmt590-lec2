import time
from flask import Flask
from flask import Flask, request
from flask import jsonify
from flask import request
from transformers.pipelines import pipeline
import os
import pg8000
global modelList
global default_model
import sqlite3
from flask import abort
import datetime
import logging
import os
from flask import Flask, render_template, request, Response
import sqlalchemy

global db

logger = logging.getLogger()
# importing the psycopg2 module
import psycopg2 

import os

import psycopg2

# Format DB connection information

rootcertfile = os.environ.get('PG_SSLROOTCERT')

os.mkdir('.ssl')

with open('.ssl/server-ca.pem','w') as f:
	f.write(rootcertfile)
	
clientcertfile = os.environ.get('PG_SSLCERT')

with open('.ssl/client-cert.pem','w') as f:
	f.write(clientcertfile)
	
clientkeyfile = os.environ.get('PG_SSLKEY')

with open('.ssl/client-key.pem','w') as f:
      f.write(clientkeyfile)

sslmode = "sslmode=verify-ca"
sslrootcert = "sslrootcert={}".format(".ssl/server-ca.pem")
sslcert = "sslclientcert={}".format(".ssl/client-cert.pem")
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
# # storing all the information
# database = 'mgmt590'
# user = 'postgres'
# password = 'prodscale'
# # connecting to the database
# connection = psycopg2.connect(database=database, user=user, password=password)
# # instantiating the cursor
# cursor = connection.cursor()
#
#
#
# def init_connection_engine():
#     db_config = {
#         # [START cloud_sql_postgres_sqlalchemy_limit]
#         # Pool size is the maximum number of permanent connections to keep.
#         "pool_size": 5,
#         # Temporarily exceeds the set pool_size if no connections are available.
#         "max_overflow": 2,
#         # The total number of concurrent connections for your application will be
#         # a total of pool_size and max_overflow.
#         # [END cloud_sql_postgres_sqlalchemy_limit]
#
#         # [START cloud_sql_postgres_sqlalchemy_backoff]
#         # SQLAlchemy automatically uses delays between failed connection attempts,
#         # but provides no arguments for configuration.
#         # [END cloud_sql_postgres_sqlalchemy_backoff]
#
#         # [START cloud_sql_postgres_sqlalchemy_timeout]
#         # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
#         # new connection from the pool. After the specified amount of time, an
#         # exception will be thrown.
#         "pool_timeout": 30,  # 30 seconds
#         # [END cloud_sql_postgres_sqlalchemy_timeout]
#
#         # [START cloud_sql_postgres_sqlalchemy_lifetime]
#         # 'pool_recycle' is the maximum number of seconds a connection can persist.
#         # Connections that live longer than the specified amount of time will be
#         # reestablished
#         "pool_recycle": 1800,  # 30 minutes
#         # [END cloud_sql_postgres_sqlalchemy_lifetime]
#     }
#
#     if os.environ.get("DB_HOST"):
#         return init_tcp_connection_engine(db_config)
#     else:
#         return init_unix_connection_engine(db_config)
#
#
# def init_tcp_connection_engine(db_config):
#     # [START cloud_sql_postgres_sqlalchemy_create_tcp]
#     # Remember - storing secrets in plaintext is potentially unsafe. Consider using
#     # something like https://cloud.google.com/secret-manager/docs/overview to help keep
#     # secrets secret.
#     # db_user = os.environ["DB_USER"]
#     # db_pass = os.environ["DB_PASS"]
#     # db_name = os.environ["DB_NAME"]
#     # db_host = os.environ["DB_HOST"]
#
#     db_user = os.environ.get('DB_USER')
#     db_pass = os.environ.get('DB_PASS')
#     db_name = os.environ.get('DB_NAME')
#     db_host = os.environ.get('DB_HOST')
#
#
#     # Extract host and port from db_host
#     host_args = db_host.split(":")
#     db_hostname, db_port = host_args[0], int(host_args[1])
#
#     pool = sqlalchemy.create_engine(
#         # Equivalent URL:
#         # postgresql+pg8000://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
#         sqlalchemy.engine.url.URL.create(
#             drivername="postgresql+pg8000",
#             username=db_user,  # e.g. "my-database-user"
#             password=db_pass,  # e.g. "my-database-password"
#             host=db_hostname,  # e.g. "127.0.0.1"
#             port=db_port,  # e.g. 5432
#             database=db_name  # e.g. "my-database-name"
#         ),
#         **db_config
#     )
#     # [END cloud_sql_postgres_sqlalchemy_create_tcp]
#     pool.dialect.description_encoding = None
#     return pool
#
#
# def init_unix_connection_engine(db_config):
#     # [START cloud_sql_postgres_sqlalchemy_create_socket]
#     # Remember - storing secrets in plaintext is potentially unsafe. Consider using
#     # something like https://cloud.google.com/secret-manager/docs/overview to help keep
#     # secrets secret.
#     # db_user = os.environ["DB_USER"]
#     # db_pass = os.environ["DB_PASS"]
#     # db_name = os.environ["DB_NAME"]
#
#     db_user = os.environ.get('DB_USER')
#     db_pass = os.environ.get('DB_PASS')
#     db_name = os.environ.get('DB_NAME')
#     db_host = os.environ.get('DB_HOST')
#
#     db_socket_dir = os.environ.get("DB_SOCKET_DIR", "/cloudsql")
#     cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")
#
#     pool = sqlalchemy.create_engine(
#
#         # Equivalent URL:
#         # postgresql+pg8000://<db_user>:<db_pass>@/<db_name>
#         #                         ?unix_sock=<socket_path>/<cloud_sql_instance_name>/.s.PGSQL.5432
#         sqlalchemy.engine.url.URL.create(
#             drivername="postgresql+pg8000",
#             username=db_user,  # e.g. "my-database-user"
#             password=db_pass,  # e.g. "my-database-password"
#             database=db_name,  # e.g. "my-database-name"
#             query={
#                 "unix_sock": "{}/{}/.s.PGSQL.5432".format(
#                     db_socket_dir,  # e.g. "/cloudsql"
#                     cloud_sql_connection_name)  # i.e "<PROJECT-NAME>:<INSTANCE-REGION>:<INSTANCE-NAME>"
#             }
#         ),
#         **db_config
#     )
#     # [END cloud_sql_postgres_sqlalchemy_create_socket]
#     pool.dialect.description_encoding = None
#     return pool

app = Flask(__name__)

# This global variable is declared with a value of `None`, instead of calling
# `init_connection_engine()` immediately, to simplify testing. In general, it
# is safe to initialize your database connection pool when your script starts
# -- there is no need to wait for the first request.


def create_tables():
    conn = psycopg2.connect(db_connect_string)

    # Create tables (if they don't already exist)
    cur = conn.cursor()
    # conn = sqlite3.connect('database.db')
    # Creating tables
    cur.execute(
        "CREATE TABLE IF NOT EXISTS prodscale (timestamp INT, model VARCHAR, answer VARCHAR, question VARCHAR, context VARCHAR);")
    conn.commit()


# DATABASE_NAME = "prodscale.db"
#
#
# def get_db():
#     conn = sqlite3.connect(DATABASE_NAME)
#     return conn



# def create_tables():
#     tables = [
#         """CREATE TABLE IF NOT EXISTS prodscale(
#                 timestamp INTEGER PRIMARY KEY,
#                 model TEXT NOT NULL,
#                 answer TEXT NOT NULL,
#                 question TEXT NOT NULL,
# 				context TEXT NOT NULL)
#             """
#     ]
#     db = get_db()
#     cursor = db.cursor()
#     for table in tables:
#         cursor.execute(table)


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


def insert_db(timestamp, model, answer, question, context):

    conn = psycopg2.connect(db_connect_string)
    # Open a cursor to perform database operations
    cur = conn.cursor()
    # conn = sqlite3.connect('database.db')
    #Creating tables

    postgres_insert_query = "INSERT INTO prodscale (timestamp, model, answer,question,context) VALUES (%s,%s,%s,%s,%s)"

    record_to_insert = (timestamp,model,answer,question,context)
    cur.execute(postgres_insert_query, record_to_insert)
    conn.commit()


    # stmt = sqlalchemy.text(
    #     "INSERT INTO prodscale (timestamp, model, answer,question,context)"
    #     " VALUES (:timestamp, :model, :answer,:question,:context)"
    # )
    # try:
    #     # Using a with statement ensures that the connection is always released
    #     # back into the pool at the end of statement (even if an error occurs)
    #     with db.connect() as conn:
    #         conn.execute(stmt, timestamp=timestamp, model=model,answer=answer,question=question,context=context)
    # except Exception as e:
    #     # If something goes wrong, handle the error in this section. This might
    #     # involve retrying or adjusting parameters depending on the situation.
    #     # [START_EXCLUDE]
    #     logger.exception(e)
    #     return Response(
    #         status=500,
    #         response="Unable to successfully insert values in databse! Please check the "
    #                  "application logs for more details."
    #     )


def get_recent_default(start,end):
        conn = psycopg2.connect(db_connect_string)
        # Open a cursor to perform database operations
        cur = conn.cursor()
        postgres_insert_query ="SELECT timestamp, model, answer, question,context FROM prodscale WHERE timestamp BETWEEN %s AND %s"
        record_to_insert = (start,end)
        cur.execute(postgres_insert_query, record_to_insert)
        result = cur.fetchall()

        #result = conn.execute(stmt, start=start, end=end).fetchall()
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

def get_recent_custom(start,end,model):
    conn = psycopg2.connect(db_connect_string)
    # Open a cursor to perform database operations
    cur = conn.cursor()
    postgres_insert_query = "SELECT timestamp, model, answer, question,context FROM prodscale WHERE timestamp BETWEEN %s AND %s model= %s"
    record_to_insert = (start, end,model)
    cur.execute(postgres_insert_query, record_to_insert)
    result =cur.fetchall()

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
                return get_recent_default(start,end)

        else:

            return get_recent_custom(start,end,model)


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
    # Run our Flask app and start listening for requests!

    # with db.connect() as conn:
    #     conn.execute(
    #         "CREATE TABLE IF NOT EXISTS prodscale(timestamp INT PRIMARY KEY,model TEXT NOT NULL,answer TEXT NOT NULL,question TEXT NOT NULL,context TEXT NOT NULL);")

    # os.environ["DB_USER"] = "postgres"
    # os.environ["DB_NAME"] = "postgres-prodscale"
    # os.environ["DB_PASS"] = "prodscale"
    # os.environ["DB_HOST"] = "35.232.200.40:5432"
    default_model = modelList[0]
    create_tables()
    # with db.connect() as conn:
    #     conn.execute(
    #         "CREATE TABLE IF NOT EXISTS prodscale(timestamp INT PRIMARY KEY,model TEXT NOT NULL,answer TEXT NOT NULL,question TEXT NOT NULL,context TEXT NOT NULL);")

    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)), threaded=True)
