from transformers.pipelines import pipeline
from flask import Flask
from flask import request
from flask import jsonify
import time
import sqlite3

# Create my flask app
app = Flask(__name__)

model_list = []
rm_ind = int()
result = []
# Face model.
@app.route("/models", methods=['PUT'])
def putmodels():
    global model_list
    # Get the request body data
    data = request.json

    # Create the response body.
    out = {
        "name": data['name'],
        "tokenizer": data['tokenizer'],
        "model": data['model']
    }
    model_list.append(out)
    return jsonify(model_list)

#POST request
@app.route("/models", methods=['GET'])
def getmodels():
    global model_list
    return jsonify(model_list)

# DELETE Request
@app.route("/models", methods=['DELETE'])
def delmodels():
    global model_list
    for i in range(0,len(model_list)):
        if (model_list[i]['model']  == request.args.get('model')):
            cnt = i
    model_list.pop(cnt)
    return jsonify(model_list)

@app.route("/answer",methods=['POST'])
def postmodels():
    global model_list
    for i in range(0,len(model_list)):
        if (model_list[i]['name']  == request.args.get('model')):
            cnt = i
    # Get the request body data
    data = request.json

    # Import Hugging face model
    try:
        hg_comp = pipeline('question-answering',
                           model=model_list[i]['model'],
                           tokenizer=model_list[i]['tokenizer'])
    except:
        print("Error")
    # Answer the answer
    answer = hg_comp({'question': data['question'], 'context': data['context']})['answer']

    # Create the response body.
    out = {
        "timestamp" : int(time.time()),
        "model" : model_list[i]['model'],
        "answer": answer,
        "question": data['question'],
        "context": data['context']
        }

    # Creating the database
    try:
        sqliteConnection = sqlite3.connect('SQLite_Python.db')
        cursor = sqliteConnection.cursor()

        print("Database created and Successfully Connected to SQLite")
        #
        # sqlite_drop_query = """drop table if exists answers"""
        #
        # sqlite_create_Query = """ create table answers(
        #                                 timestamp int primary key not null,
        #                                 model text,
        #                                 answer text,
        #                                 question text,
        #                                 context text
        #                             );
        #                                 """
        sqlite_insert_Query = """
                                  insert into answers VALUES (?,?,?,?,?);
                                    """
        # cursor.execute(sqlite_drop_query)
        # cursor.execute(sqlite_create_Query)
        cursor.execute(sqlite_insert_Query, (int(time.time()), model_list[i]['model'], answer, data['question'],data['context']))
        sqliteConnection.commit()

    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")
    return jsonify(out)

@app.route("/answer",methods=['GET'])
def getanswer():
    global model_list
    try:
        model = request.args.get('model')
        start_ut = request.args.get('start')
        end_ut = request.args.get('end')
        sqliteConnection = sqlite3.connect('SQLite_Python.db')
        cursor = sqliteConnection.cursor()
        sqlite_select_Query = """select * from answers where timestamp between ? and ?;"""
        cursor.execute(sqlite_select_Query,(start_ut,end_ut))
        sqliteConnection.commit()
        global result
        result = cursor.fetchall()
        out_list = []
        for row in result:
            out = {
                "timestamp": row[0],
                "model": row[1],
                "answer": row[2],
                "question": row[3],
                "context": row[4]
            }
            out_list.append(out)
        cursor.close()
    except sqlite3.Error as error:
        print("Error while getting data from sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

    return jsonify(out_list)

if __name__ == '__main__':
    # Run our Flask app and start listening for requests!
    app.run(host='10.186.42.218', port=8000, threaded=True)