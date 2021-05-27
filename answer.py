from transformers.pipelines import pipeline
from flask import Flask
from flask import request
from flask import jsonify

# Create my flask app
app = Flask(__name__)


# Define a handler for the /answer path, which
# processes a JSON payload with a question and
# context and returns an answer using a Hugging
# Face model.
@app.route("/answer", methods=['POST'])
def answer():
    # Get the request body data
    data = request.json

    # Import Hugging face model
    hg_comp = pipeline('question-answering', model="deepset/roberta-base-squad2",
                       tokenizer="deepset/roberta-base-squad2")

    # Answer the answer
    answer = hg_comp({'question': data['question'], 'context': data['context']})['answer']

    # Create the response body.
    out = {
        "question": data['question'],
        "context": data['context'],
        "answer": answer
    }

    return jsonify(out)


# Run if running "python answer.py"
if __name__ == '__main__':
    # Run our Flask app and start listening for requests!
    app.run(host='0.0.0.0', port=8000, threaded=True)
