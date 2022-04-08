import requests
from flask import Flask, request, jsonify
from backend.utils import search as s
from backend.settings import Handler
from backend.config import es_url
from backend.utils.elasticsearch import es_request
import json

app = Flask('app')
app.model_handler = Handler
model_dict = {"glove": "word_embedding_2",
              "fasttext": "word_embedding_3",
              "use": "sentence_embedding_2",
              "infersent": "sentence_embedding_1"}
counter = 0


@app.route('/search', methods=['POST'])
def search():  # put application's code here
    body = request.get_json()

    term, model, dataset, size = body['term'], body['model'], body['dataset'], body['size']

    print("Load model: ", model)
    app.model_handler.load_model(body['model'])

    try:
        is_word_embedding = True if body["model"] in ["glove", "w2v", "fasttext"] else False
        vector = s.calc_vector(term, app.model_handler.get(body['model']), is_word_embedding)
    except Exception as e:
        print(e)
        return {"message": "No vector embeddings possible with the search term '{}'".format(term)}, 400

    try:
        resp = s.search(vector, size, es_url, dataset, model_dict[model], term)
        global counter
        counter += 1
        return resp
    except Exception as e:
        print(e)
        return {"message": "Error from elasticsearch! "}, 500


@app.route('/stats', methods=['POST'])
def stats():
    body = dict(request.get_json())
    url = es_url + "test_stats" + "/doc_"
    r = es_request("POST", url, body)
    return r.text, r.status_code


@app.route('/get_counter', methods=['GET'])
def get_counter():
    global counter
    return {"counter": counter}, 200
