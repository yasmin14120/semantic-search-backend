# helper skript to download gensims pretrained model (will be deleted later)
import gensim.downloader as api
import json
from gensim import models
from gensim.downloader import base_dir
import os

model_dict = {
    "w2v": {
        "file_path": os.path.join(base_dir, 'word2vec-google-news-subwords-300', 'word2vec-google-news-subwords-300.gz'),
        "binary": True
    },
    "glove": {
        "file_path": os.path.join(base_dir, 'glove-wiki-gigaword-300', 'glove-wiki-gigaword-300.gz'),
        "binary": False
    },
    "fasttext": {
        "file_path": os.path.join(base_dir, 'fasttext-wiki-news-subwords-300', 'fasttext-wiki-news-subwords-300.gz'),
        "binary": False
    }
}


def gensim_info():
    # To get all pre-trained models and corpora provided in gensim
    info = api.info()
    print(json.dumps(info, indent=4))


def download_models():
    # Download word embeddings:
    w2v = api.load('word2vec-google-news-300', return_path="./models")
    glove = api.load("glove-wiki-gigaword-300", return_path="./models")
    fasttext = api.load("fasttext-wiki-news-subwords-300", return_path="./models")


def load_model(model_name):
    global model_dict
    if model_name in ["w2v", "glove", "fasttext"]:
        model = models.KeyedVectors.load_word2vec_format(model_dict[model_name]["file_path"], binary=model_dict[model_name]["binary"])
        print("Model loaded successfully")
        return model



