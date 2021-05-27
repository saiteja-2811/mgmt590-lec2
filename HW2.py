from transformers.pipelines import pipeline
from flask import Flask
from flask import request
from flask import jsonify
import time

# Create my flask app
app = Flask(__name__)

model_list = []
rm_ind = int()

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
        if (model_list[i]['model']  == request.args.get('model')):
            cnt = i
    # Get the request body data
    data = request.json
    # Import Hugging face model
    hg_comp = pipeline('question-answering',
                       model=model_list[i]['model'],
                       tokenizer=model_list[i]['tokenizer'])
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
    return jsonify(out)

if __name__ == '__main__':
    # Run our Flask app and start listening for requests!
    app.run(host='0.0.0.0', port=8000, threaded=True)