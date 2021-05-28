# Assignment 2 : MGMT 590, Production Scale Data Products, Summer 2021

## Application Overview

In this assignment we are asked to perform two major tasks:
1. Build a REST API which uses NLP techniques and answers the questions given with a context.
2. Deploy this API using Google Cloud. It is deployed at https://mgmt590-assignment2-ykof2ki2ga-uc.a.run.app

## Learnings

I have learnt the below processes.

- Understood how to commit to github with git bash.
- Understood how REST API works.
- Fimiliarized with Python Flask App.
- Have Created a service in Google Cloud
- Build an API accessible on the public Internet
- Version control the code in github
- Using a SQLite database to log all answered questions

## Outline

- A - Question Answering using Hugging Face Transformers 

- B - Getting to know the Python Flask framework

- C - Dependencies

- D - REST API endpoints

- E - Building and running the API locally

## A - Question Answering using Hugging Face Transformers
These are NLP models used to answer the questions when given a context to the question. A default model "distilbert-base-uncased-distilled-squad" has been used to answer questions. But you can use the "POST" method with "models" handler to input a model type. 

## B - Getting to know the Python Flask framework
I have used `Flask` client to make the application and have used postman to test the all the specified requests. This project is created with `python` and for the database utility I have used `sqlite3`.


## C - Dependencies
All the `Dependencies` have been listed in the `requirements.txt`. These below ones are the required modules to be installed additionally to run this application.
- transformers == 4.5.1
- flask == 1.1.2
- torch == 1.8.1

## D - REST API endpoints

- GET  `/models`: This route gets the list of the models currently loaded into the server.

Sample Response:

  ```
[
    {
        "name": "distilled-bert",
        "tokenizer": "distilbert-base-uncased-distilled-squad",
        "model": "distilbert-base-uncased-distilled-squad"
    },
    {
        "name": "deepset-roberta",
        "tokenizer": "deepset/roberta-base-squad2",
        "model": "deepset/roberta-base-squad2"
    }
]
  ```

## Adding a Model
- PUT  `/models`: This route is used to add a new model into the server.

Sample Response:
  ```
    {
        "name": "distilled-bert",
        "tokenizer": "distilbert-base-uncased-distilled-squad",
        "model": "distilbert-base-uncased-distilled-squad"
    }
  ```

## Delete a Model

- DELETE   `/models?model=<model name>`: This route is used to delete an existing model on the server.

Query Parameters:
`<model name> (required) - The name of the model to be deleted`

Sample Response : The models available after deleting the above model.

  ```
[
    {
        "name": "distilled-bert",
        "tokenizer": "distilbert-base-uncased-distilled-squad",
        "model": "distilbert-base-uncased-distilled-squad"
    },
    {
        "name": "deepset-roberta",
        "tokenizer": "deepset/roberta-base-squad2",
        "model": "deepset/roberta-base-squad2"
    }
]
  ```

## Answer a Question

- POST  `/answer?model=<model name>`: This route uses one of the available models to answer a question, given the context.
- The constraint here is we can only send one `question` & `context` in a request.

Query Parameters:
`<model name> (optional) - The name of the model to be used in answering the
question. If no model name is provided use a default model.`

Sample Input :

  ```
{
  "question": "who did holly matthews play in waterloo rd?",
  "context": "She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC's Doctors, playing Connie Whitfield; in ITV's The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack."
}
  ```

Sample Response :

  ```
{
  "timestamp": 1621602784,
  "model": "deepset-roberta",
  "answer": "Leigh-Ann Galloway",
  "question": "who did holly matthews play in waterloo rd?",
  "context": "She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC's Doctors, playing Connie Whitfield; in ITV's The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack."
}
  ```
##List Recently Answered Questions

- GET  `/answer?model=<model name>&start=<start timestamp>&end=<end
timestamp>`: This route gets the list recently answered questions within a timeline.
  
Query Parameters:

`<model name> (optional) - Filter the results by providing a certain model name, such
that the results only include answered questions that were answered using the provided
model.`

`<start timestamp> (required) - The starting timestamp, such that answers to questions
prior to this timestamp won't be returned. This should be a Unix timestamp.`

`<end timestamp> (required) - The ending timestamp, such that answers to questions
after this timestamp won't be returned. This should be a Unix timestamp.`

Expected Response Format :

  ```
[
    {
        "timestamp": 1622100672,
        "model": "distilled-bert",
        "answer": "Leigh-Ann Galloway",
        "question": "who did holly matthews play in waterloo rd?",
        "context": "She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC's Doctors, playing Connie Whitfield; in ITV's The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack."
    },
    {
        "timestamp": 1622100683,
        "model": "distilled-bert",
        "answer": "Leigh-Ann Galloway",
        "question": "who did holly matthews play in waterloo rd?",
        "context": "She attended the British drama school East 15 in 2005,and left after winning a high-profile role in the BBC drama Waterloo Road, playing the bully Leigh-Ann Galloway.[6] Since that role, Matthews has continued to act in BBC's Doctors, playing Connie Whitfield; in ITV's The Bill playing drug addict Josie Clarke; and she was back in the BBC soap Doctors in 2009, playing Tansy Flack."
    }
]
 ```
## E - Building and running the API locally

### a)Running Locally with Python and Flask

To run this application on your local operating system, you will need to have
[Python installed](https://www.python.org/downloads/).

Step 1. Install required dependencies using the Python package installer (`pip`):

   ```
   $ pip install -r requirements.txt
   ```

Step 2. Run the app:

   ```
   $ FLASK_APP=answers.py flask run
   ```

1. Navigate to `http://localhost:8080` in your web browser to access the running
   application

### b)Running Locally with Docker

This application may be run locally using
[Docker](https://docs.docker.com/get-docker/).

Step 1. Build the Docker image:

   ```
   $ docker build -t mgmt590-assignment-2
   ```

1. Run the docker container:
   ```
   $ docker run --env PORT=8080 -p 8080:8080 mgmt590-assignment-2
   ```

1. Navigate to `http://localhost:8080` in your web browser to access the running
   application

### c)Deploying with Google Cloud Run

This application can be deployed to Google Cloud Run. This requires a Google
account.

Step 1. Select or create a Google Cloud project using the
[Google Cloud Console](https://console.cloud.google.com/projectselector2/home/dashboard)

Step 2. Install and initialize the [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)

Step 3. Build and deploy the application to Google Cloud Run.

1. When complete, the last command execute in the previous step will display the
   URL of deployed application; navigate to that URL in your web browser to
   access the application.