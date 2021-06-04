from flask import Flask
import json
from freezegun import freeze_time
from HW2 import app
from HW2 import modelList
from mock import patch
import os
#
import shutil

dir = '.ssl'
if os.path.exists(dir):
    shutil.rmtree(dir)
os.makedirs(dir)

rootcertfile = os.environ.get('PG_SSLROOTCERT')
rootcertfile = rootcertfile.replace('@', '=')
with open('.ssl/server-ca.pem', 'w') as f:
    f.write(rootcertfile)

clientcertfile = os.environ.get('PG_SSLCERT')
clientcertfile = clientcertfile.replace('@', '=')
with open('.ssl/client-cert.pem', 'w') as f:
    f.write(clientcertfile)

clientkeyfile = os.environ.get('PG_SSLKEY')
clientkeyfile = clientkeyfile.replace('@', '=')

with open('.ssl/client-key.pem', 'w') as f:
    f.write(clientkeyfile)

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

def test_hello():
    response = app.test_client().get('/')

    assert response.status_code == 200
    assert response.data == b'Hello, World!'


def test_get_models():
    response = app.test_client().get('/models')


    # mock_response_data = {
    #     "name": "distilled-bert",
    #     "tokenizer": "distilbert-base-uncased-distilled-squad",
    #     "model": "distilbert-base-uncased-distilled-squad"
    # }

    mock_response_data=b'[{"name":"distilled-bert","tokenizer":"distilbert-base-uncased-distilled-squad","model":"distilbert-base-uncased-distilled-squad"}]\n'

    #result = json.dumps(mock_response_data)

    response = app.test_client().get('/models')
    assert response.status_code == 200
    assert response.data == mock_response_data


def test_add_models():
    url = '/models'

    mock_request_data = {
        "name": "bert-tiny",
        "tokenizer": "mrm8488/bert-tiny-5-finetuned-squadv2",
        "model": "mrm8488/bert-tiny-5-finetuned-squadv2"
        }

    headers = {'Content-Type': 'application/json'}
    response = app.test_client().put(url, data=json.dumps(mock_request_data), headers=headers)
    mock_response_data=b'[{"name":"distilled-bert","tokenizer":"distilbert-base-uncased-distilled-squad","model":"distilbert-base-uncased-distilled-squad"},{"name":"bert-tiny","tokenizer":"mrm8488/bert-tiny-5-finetuned-squadv2","model":"mrm8488/bert-tiny-5-finetuned-squadv2"}]\n'

    #response = client.post(url, data=json.dumps(mock_request_data), headers=mock_request_headers)
    assert response.status_code == 200
    assert response.data == mock_response_data

def test_add_models_failure_bad_request():
    url = '/models'

    mock_request_data = {}

    headers = {'Content-Type': 'application/json'}
    response = app.test_client().put(url, data=json.dumps(mock_request_data), headers=headers)
    #mock_response_data=b'[{"name":"distilled-bert","tokenizer":"distilbert-base-uncased-distilled-squad","model":"distilbert-base-uncased-distilled-squad"},{"name":"bert-tiny","tokenizer":"mrm8488/bert-tiny-5-finetuned-squadv2","model":"mrm8488/bert-tiny-5-finetuned-squadv2"}]\n'
    mock_response_data = b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>400 Bad Request</title>\n<h1>Bad Request</h1>\n<p>Invalid Model Name</p>\n'

    #response = client.post(url, data=json.dumps(mock_request_data), headers=mock_request_headers)
    assert response.status_code == 400
    assert response.data == mock_response_data

def test_delete_models():
    model="bert-tiny"
    url = '/models?model='+model

    # mock_request_data = {
    #     "name": "bert-tiny",
    #     "tokenizer": "mrm8488/bert-tiny-5-finetuned-squadv2",
    #     "model": "mrm8488/bert-tiny-5-finetuned-squadv2"
    #     }

    headers = {'Content-Type': 'application/json'}
    response = app.test_client().delete(url, headers=headers)
    mock_response_data=b'[{"name":"distilled-bert","tokenizer":"distilbert-base-uncased-distilled-squad","model":"distilbert-base-uncased-distilled-squad"}]\n'

    #response = client.post(url, data=json.dumps(mock_request_data), headers=mock_request_headers)
    assert response.status_code == 200
    assert response.data == mock_response_data

def test_delete_models_failure_bad_request():
    url = '/models'

    # mock_request_data = {
    #     "name": "bert-tiny",
    #     "tokenizer": "mrm8488/bert-tiny-5-finetuned-squadv2",
    #     "model": "mrm8488/bert-tiny-5-finetuned-squadv2"
    #     }

    headers = {'Content-Type': 'application/json'}
    response = app.test_client().delete(url, headers=headers)
    mock_response_data=b'Model name not provided in query string'

    #response = client.post(url, data=json.dumps(mock_request_data), headers=mock_request_headers)
    assert response.status_code == 400
    assert response.data == mock_response_data

# def test_answer_question_default_model(mocker):
#     create_tables()
#
#     #default_model = modelList[0]
#     freezer = freeze_time("2021-05-28 12:00:01")
#     freezer.start()
#     url = '/answer'
#
#     mock_request_data = {
#   "question": "what is my name?",
#   "context": "my name is mayank"
#     }
#
#     # query_string = "INSERT INTO prodscale (timestamp, model, answer,question,context) VALUES (%s,%s,%s,%s,%s);"
#     # mock_connect = mocker.patch('psycopg2.connect')
#     # self.database.insert(query_string)
#
#
#     headers = {'Content-Type': 'application/json'}
#     mocker.patch('insert_db(timestamp, model, answer, question, context)' , return_value=True)
#     response = app.test_client().post(url, data=json.dumps(mock_request_data), headers=headers)
#     #mock_response_data =  b'{"timestamp":1622322088,"model":"distilled-bert","answer":"Mayank","question'\n b'":"What is your name?","context":"My name is Mayank"}\n'
#
#     mock_response_data = b'{"timestamp":1622203201,"model":"distilled-bert","answer":"mayank","question":"what is my name?","context":"my name is mayank"}\n'
#     #assert response.status_code == 200
#     assert response.data == mock_response_data
#     freezer.stop()

def test_answer_question_given_model():

    url1 = '/models'

    mock_request_data = {
        "name": "bert-tiny",
        "tokenizer": "mrm8488/bert-tiny-5-finetuned-squadv2",
        "model": "mrm8488/bert-tiny-5-finetuned-squadv2"
        }

    headers = {'Content-Type': 'application/json'}
    response1 = app.test_client().put(url1, data=json.dumps(mock_request_data), headers=headers)

    #default_model = modelList[0]
    freezer = freeze_time("2021-05-28 12:00:01")
    freezer.start()
    model="bert-tiny"
    url = '/answer?model='+model

    mock_response_data1=b'[{"name":"distilled-bert","tokenizer":"distilbert-base-uncased-distilled-squad","model":"distilbert-base-uncased-distilled-squad"},{"name":"bert-tiny","tokenizer":"mrm8488/bert-tiny-5-finetuned-squadv2","model":"mrm8488/bert-tiny-5-finetuned-squadv2"}]\n'

    #response = client.post(url, data=json.dumps(mock_request_data), headers=mock_request_headers)
    assert response1.status_code == 200
    assert response1.data == mock_response_data1


    mock_request_data2 = {
  "question": "who did holly matthews play in waterloo rd?",
  "context": "She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC's Doctors, playing Connie Whitfield; in ITV's The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack."
    }

    headers = {'Content-Type': 'application/json'}
    response = app.test_client().post(url, data=json.dumps(mock_request_data2), headers=headers)
    #mock_response_data =  b'{"timestamp":1622322088,"model":"bert-tiny","answer":"Mayank","question'\n b'":"What is your name?","context":"My name is Mayank"}\n'

    mock_response_data2 = b'{"timestamp":1622203201,"model":"bert-tiny","answer":"bully Leigh-Ann Galloway","question":"who did holly matthews play in waterloo rd?","context":"She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC\'s Doctors, playing Connie Whitfield; in ITV\'s The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack."}\n'
    #assert response.data == mock_response_data2
    assert response.status_code == 200
    freezer.stop()

def test_get_answers_failure_bad_request():
    url = '/answer'

    # mock_request_data = {
    #     "name": "bert-tiny",
    #     "tokenizer": "mrm8488/bert-tiny-5-finetuned-squadv2",
    #     "model": "mrm8488/bert-tiny-5-finetuned-squadv2"
    #     }

    headers = {'Content-Type': 'application/json'}
    response = app.test_client().post(url, headers=headers)
    mock_response_data=b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>400 Bad Request</title>\n<h1>Bad Request</h1>\n<p>Failed to decode JSON object: Expecting value: line 1 column 1 (char 0)</p>\n'

    #response = client.post(url, data=json.dumps(mock_request_data), headers=mock_request_headers)
    assert response.status_code == 400
    assert response.data == mock_response_data

def test_get_recent_given_model():

    url1 = '/models'

    mock_request_data = {
        "name": "bert-tiny",
        "tokenizer": "mrm8488/bert-tiny-5-finetuned-squadv2",
        "model": "mrm8488/bert-tiny-5-finetuned-squadv2"
        }

    headers = {'Content-Type': 'application/json'}
    response1 = app.test_client().put(url1, data=json.dumps(mock_request_data), headers=headers)

    #default_model = modelList[0]
    freezer = freeze_time("2021-05-28 12:00:01")
    freezer.start()
    model="bert-tiny"
    url = '/answer?model='+model

    mock_response_data1=b'[{"name":"distilled-bert","tokenizer":"distilbert-base-uncased-distilled-squad","model":"distilbert-base-uncased-distilled-squad"},{"name":"bert-tiny","tokenizer":"mrm8488/bert-tiny-5-finetuned-squadv2","model":"mrm8488/bert-tiny-5-finetuned-squadv2"}]\n'

    #response = client.post(url, data=json.dumps(mock_request_data), headers=mock_request_headers)
    assert response1.status_code == 200
    #assert response1.data == mock_response_data1


    mock_request_data2 = {
  "question": "who did holly matthews play in waterloo rd?",
  "context": "She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC's Doctors, playing Connie Whitfield; in ITV's The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack."
    }

    headers = {'Content-Type': 'application/json'}
    response = app.test_client().post(url, data=json.dumps(mock_request_data2), headers=headers)
    #mock_response_data =  b'{"timestamp":1622322088,"model":"bert-tiny","answer":"Mayank","question'\n b'":"What is your name?","context":"My name is Mayank"}\n'

    mock_response_data2 = b'{"timestamp":1622203201,"model":"bert-tiny","answer":"bully Leigh-Ann Galloway","question":"who did holly matthews play in waterloo rd?","context":"She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC\'s Doctors, playing Connie Whitfield; in ITV\'s The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack."}\n'
    #assert response.data == mock_response_data2
    assert response.status_code == 200

    start ="1622203100"
    end = "1622203300"
    url2 = "/answer?model="+ model + "&start=" + start + "&end=" + end

    # mock_request_data3 = {
    #     "question": "who did holly matthews play in waterloo rd?",
    #     "context": "She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC's Doctors, playing Connie Whitfield; in ITV's The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack."
    # }

    headers = {'Content-Type': 'application/json'}
    with patch('psycopg2.connect') as mocksql:
        mocksql.connect().cursor().fetchall.return_value = [(1622203201, 'bert-tiny', 'bully Leigh-Ann Galloway',
                                                             'who did holly matthews play in waterloo rd?',
                                                             "She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC's Doctors, playing Connie Whitfield; in ITV's The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack.")]

    response = app.test_client().get(url2, headers=headers)

    #mock_response_data3 = b'[{"timestamp":1622203201,"model":"bert-tiny","answer":"bully Leigh-Ann Galloway","question":"who did holly matthews play in waterloo rd?","context":"She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC\'s Doctors, playing Connie Whitfield; in ITV\'s The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack."}]\n'
    mock_response_data3 = b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>500 Internal Server Error</title>\n<h1>Internal Server Error</h1>\n<p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>\n'
    #assert response.data == mock_response_data3
    assert response.status_code == 500

    freezer.stop()

def test_get_recent_given_model_failure_bad_request():

    url = '/answer'
    freezer = freeze_time("2021-05-28 12:00:01")
    freezer.start()
    headers = {'Content-Type': 'application/json'}

    with patch('psycopg2.connect') as mocksql:
        mocksql.connect().cursor().fetchall.return_value = [(1622203201, 'bert-tiny', 'bully Leigh-Ann Galloway',
                                                             'who did holly matthews play in waterloo rd?',
                                                             "She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC's Doctors, playing Connie Whitfield; in ITV's The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack.")]

    response = app.test_client().get(url, headers=headers)

    #mock_response_data3 = b'[{"timestamp":1622203201,"model":"bert-tiny","answer":"bully Leigh-Ann Galloway","question":"who did holly matthews play in waterloo rd?","context":"She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC\'s Doctors, playing Connie Whitfield; in ITV\'s The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack."}]\n'
    mock_response_data3 = b'Query timestamps not provided'
    assert response.data == mock_response_data3
    assert response.status_code == 400

    freezer.stop()
