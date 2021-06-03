from flask import Flask
import json
from freezegun import freeze_time
from testscript import app
from gcloud import modelList
from gcloud import insert_db
import gcloud
from mock import patch
from gcloud import create_tables
# import os
#
# os.environ["DB_USER"] = "postgres"
# os.environ["DB_NAME"] = "postgres-prodscale"
# os.environ["DB_PASS"] = "prodscale"
# os.environ["DB_HOST"] = "35.232.200.40:5432"

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

def test_answer_question_default_model():

    #default_model = modelList[0]
    freezer = freeze_time("2021-05-28 12:00:01")
    freezer.start()
    url = '/answer'

    mock_request_data = {
  "question": "who did holly matthews play in waterloo rd?",
  "context": "She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC's Doctors, playing Connie Whitfield; in ITV's The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack."
    }

    headers = {'Content-Type': 'application/json'}
    response = app.test_client().post(url, data=json.dumps(mock_request_data), headers=headers)
    #mock_response_data =  b'{"timestamp":1622322088,"model":"distilled-bert","answer":"Mayank","question'\n b'":"What is your name?","context":"My name is Mayank"}\n'

    mock_response_data = b'{"timestamp":1622203201,"model":"distilled-bert","answer":"Leigh-Ann Galloway","question":"who did holly matthews play in waterloo rd?","context":"She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC\'s Doctors, playing Connie Whitfield; in ITV\'s The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack."}\n'
    assert response.status_code == 200
    assert response.data == mock_response_data
    freezer.stop()

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
    assert response.data == mock_response_data2
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
    mock_response_data=b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>400 Bad Request</title>\n<h1>Bad Request</h1>\n<p>The browser (or proxy) sent a request that this server could not understand.</p>\n'

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
    assert response1.data == mock_response_data1


    mock_request_data2 = {
  "question": "who did holly matthews play in waterloo rd?",
  "context": "She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC's Doctors, playing Connie Whitfield; in ITV's The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack."
    }

    headers = {'Content-Type': 'application/json'}
    response = app.test_client().post(url, data=json.dumps(mock_request_data2), headers=headers)
    #mock_response_data =  b'{"timestamp":1622322088,"model":"bert-tiny","answer":"Mayank","question'\n b'":"What is your name?","context":"My name is Mayank"}\n'

    mock_response_data2 = b'{"timestamp":1622203201,"model":"bert-tiny","answer":"bully Leigh-Ann Galloway","question":"who did holly matthews play in waterloo rd?","context":"She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC\'s Doctors, playing Connie Whitfield; in ITV\'s The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack."}\n'
    assert response.data == mock_response_data2
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
    assert response.data == mock_response_data3
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