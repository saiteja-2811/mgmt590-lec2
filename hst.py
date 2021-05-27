# Importing libraries
from transformers.pipelines import pipeline
from flask import Flask,request,jsonify
import time
import sqlite3

# Create flask app
# Try to handle a error model also
app = Flask(__name__)

# Define a handler for / path
@app.route("/")
def hello_world():
    return "<p>Hello,world</p>"

models_list = []

@app.route("/models", methods =['GET'])
def modelslist_output():
    global models_list
    # Returning the dictionary as response
    return jsonify(models_list)

@app.route("/models", methods =['PUT'])
def models_input():
    data = request.json
    global models_list
    output = {
        "name": data['name'],
        "tokenizer": data['tokenizer'],
        "model": data['model']
    }
    models_list.append(output)

    # Returning the dictionary as response
    return jsonify(models_list)

@app.route("/models", methods =['DELETE'])
def models_delete():
    global models_list
    model_name = request.args.get('model')
    newlist_models = [i for i in models_list if not (i['model'] == model_name)]
    models_list = newlist_models
    # Returning the dictionary as response
    return jsonify(models_list)

# Define a handler for /answer path which processes a json payload with question and context and return an answer
@app.route("/answer", methods =['POST'])
def answer():
    global models_list
    model_name =''
    model_name = request.args.get('model')
    if model_name=='':
        model_name="distilbert-base-uncased-distilled-squad"
    data = request.json
    required_model = [i for i in models_list if (i['model'] == model_name)]
    if len(required_model) ==0:
        return print("The selected model is not a part of the model list in API")
    # Importing the model for question answering
    hg_comp = pipeline('question-answering', model=required_model[0]['model'],
                       tokenizer=required_model[0]['tokenizer'])
    answer = hg_comp({'question': data['question'], 'context': data['context']})['answer']

    # Create the response body
    output = {
        "timestamp": int(time.time()),
        "model": model_name,
        "answer": answer,
        "question": data['question'],
        "context": data['context']
    }
    try:
        sqliteConnection = sqlite3.connect('SQLite_Hasit1.db')
        cursor = sqliteConnection.cursor()
        cursor.execute('''insert into answers (timestamp,question,answer,context,model) values(?,?,?,?,?);'''
        ,(int(time.time()), data['question'], answer, data['context'], model_name))
        sqliteConnection.commit()
        cursor.close()

    except sqlite3.Error as error:
        return print("Error while querying the database", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()

    return jsonify(output)

@app.route("/answer", methods =['GET'])
def answer_fromdb():
    global models_list
    model_name = ''
    model_name = request.args.get('model')
    if model_name=='':
        model_name="distilbert-base-uncased-distilled-squad"
    start_time = request.args.get('start')
    end_time = request.args.get('end')

    try:
        sqliteConnection = sqlite3.connect('SQLite_Hasit1.db')
        cursor = sqliteConnection.cursor()
        cursor.execute('''select * from answers where timestamp>=? and timestamp<=?  and model=?;'''
        ,(start_time, end_time, model_name))
        rows = cursor.fetchall()
        outputlist=[]
        for row in rows:
            output = {
                "timestamp": row[0],
                "model": row[4],
                "answer": row[2],
                "question": row[1],
                "context": row[3]
            }
            outputlist.append(output)
        sqliteConnection.commit()
        cursor.close()

    except sqlite3.Error as error:
        return print("Error while querying the database", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()

    return jsonify(outputlist)

# Run if running "pyhton answer.py"
if _name=='main_':
    # For Running API
    app.run(host='0.0.0.0',port=8000, threaded=True)

# One time code for creating the table for storing the answers in SQLLite database
# try:
#     sqliteConnection = sqlite3.connect('SQLite_Hasit1.db')
#     sqlite_create_table_query = '''CREATE TABLE answers (
#                                 timestamp INTEGER PRIMARY KEY,
#                                 question TEXT NOT NULL,
#                                 answer TEXT NOT NULL,
#                                 context TEXT NOT NULL,
#                                 model TEXT NOT NULL);'''
#
#     cursor = sqliteConnection.cursor()
#     cursor.execute(sqlite_create_table_query)
#     sqliteConnection.commit()
#     cursor.close()
#
# except sqlite3.Error as error:
#     print("Error while querying the database", error)
# finally:
#     if sqliteConnection:
#         sqliteConnection.close()
#         print("sqlite connection is closed")