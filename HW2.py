# Import all the dependecies
from transformers.pipelines import pipeline
from flask import Flask
from flask import request
from flask import jsonify
import time
import sqlite3
import os
import torch

# Initialize my flask app
app = Flask(__name__)

# Create a Database table
def create_table():
    # Create Connection
    sqliteConnection = sqlite3.connect('SQLite_Python.db')
    # Open the cursor
    cursor = sqliteConnection.cursor()
    print("Database created and Successfully Connected to SQLite")

    # Create the table structure
    sqlite_create_Query = """ create table if not exists answers(
                                    timestamp int primary key not null,
                                    model text not null,
                                    answer text not null,
                                    question text not null,
                                    context text not null
                                );
                                    """
    # Execute the select query
    cursor.execute(sqlite_create_Query)
    # Save the changes
    sqliteConnection.commit()
    # Close the cursor
    cursor.close()
    # Close the connection
    sqliteConnection.close()

# Default model details
df_model_details = {
                "name": "distilled-bert",
                "tokenizer": "distilbert-base-uncased-distilled-squad",
                "model": "distilbert-base-uncased-distilled-squad"
                }

# Empty model list
model_list = []
# Count
rm_ind = int()
# Empty answer list
result = []

# Define a handler for / path
@app.route("/")
def hello_world():
    return "<p>Hello,world</p>"

# PUT models to input the list of models
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
    # Append to the empty list
    model_list.append(out)
    model_list = set(model_list)
    return jsonify(model_list)

#GET models - to get the list of available models
@app.route("/models", methods=['GET'])
def getmodels():
    global model_list
    if len(model_list) == 0:
        return jsonify(df_model_details)
    else:
        return jsonify(model_list)

# DELETE models - to delete some models from the model list
@app.route("/models", methods=['DELETE'])
def delmodels():
    global model_list
    cnt = None
    del_mod = request.args.get('model')
    for i in range(0,len(model_list)):
        if (model_list[i]['name']  == del_mod):
            cnt = i
            model_list.pop(cnt)
    return jsonify(model_list)

# POST Answer - To get the answers for the question & context input and store the data in SQLite DB
@app.route("/answer",methods=['POST'])
def postmodels():
    # Get the request body data
    data = request.json
    # Get the model name
    model_name = request.args.get('model')
    # define empty list to store models
    model_param1 = ''
    model_param2 = ''
    global model_list
    # Check for parameter
    if request.args.get('model') == None:
        model_name = df_model_details['name']
        model_param1 = df_model_details['model']
        model_param2 = df_model_details['tokenizer']

    else:
        # start looping through models
        for i in range(0,len(model_list)):
            if (model_list[i]['name']  == model_name):
                model_param1 = model_list[i]['model']
                model_param2 = model_list[i]['tokenizer']
            else:
                return "The model you have requested is not available in the API"
    # Run the model now
    hg_comp = pipeline('question-answering',
                   model=model_param1,
                   tokenizer=model_param2)

    # Get the answer
    answer = hg_comp({'question': data['question'], 'context': data['context']})['answer']

    # Create the response body.
    out = {
        "timestamp" : int(time.time()),
        "model" : model_name,
        "answer": answer,
        "question": data['question'],
        "context": data['context']
        }

    # Creating the database
    try:
        # Open connection
        sqliteConnection = sqlite3.connect('SQLite_Python.db')
        # Initialize Cursor
        cursor = sqliteConnection.cursor()
        # Insert Query
        sqlite_insert_Query = """
                                  insert into answers VALUES (?,?,?,?,?);
                                    """
        # Execute the query
        cursor.execute(sqlite_insert_Query, (int(time.time()), model_name, answer, data['question'],data['context']))
        #Save changes to the database
        sqliteConnection.commit()
        #Close the cursor
        cursor.close()

    # Exception 1
    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)

    #Close the connection
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")
    return jsonify(out)

# GET recently answered question details
@app.route("/answer",methods=['GET'])
def getanswer():
    global model_list
    try:

        # Parameter 1
        model = request.args.get('model')
        # Parameter 2
        start_ut = request.args.get('start')
        # Parameter 3
        end_ut = request.args.get('end')
        # Open the connection
        sqliteConnection = sqlite3.connect('SQLite_Python.db')
        # Initialize the cursor
        cursor = sqliteConnection.cursor()
        #Get the data from the database
        sqlite_select_Query = """select * from answers where timestamp between ? and ? and model=?;"""
        # Execute the query
        cursor.execute(sqlite_select_Query,(start_ut,end_ut,model))
        # Save changes
        sqliteConnection.commit()

        # Stroing the results into JSON
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
        # Close the cursor
        cursor.close()
    except sqlite3.Error as error:
        print("Error while getting data from sqlite", error)
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print("The SQLite connection is closed")

    return jsonify(out_list)

# Run the Application
if __name__ == '__main__':
    # Call the create table function
    create_table()
    # Run our Flask app and start listening for requests!
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)), threaded=True)
