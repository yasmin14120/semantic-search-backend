# helper skript to download gensims pretrained model (will be deleted later)
import gensim.downloader as api
import json
from gensim import models
from gensim.downloader import base_dir
import os

model_dict = {
    "w2v": {
        "file_path": "/models/word_embeddings/word2vec-google-news-subwords-300/word2vec-google-news-subwords-300.gz",
        "es_field": "word_embedding_1",
        "path": os.path.join(base_dir, 'word2vec-google-news-300', 'word2vec-google-news-300.gz'),
        "binary": True
    },
    "glove": {
        "file_path": "./models/word_embeddings/glove-wiki-gigaword-300/glove-wiki-gigaword-300.gz",
        "es_field": "word_embedding_2",
        "path": os.path.join(base_dir, 'glove-wiki-gigaword-300', 'glove-wiki-gigaword-300.gz'),
        "binary": False
    },
    "fasttext": {
        "file_path": "/models/word_embeddings/fasttext-wiki-news-subwords-300/fasttext-wiki-news-subwords-300.gz",
        "es_field": "word_embedding_3",
        "path": os.path.join(base_dir, 'fasttext-wiki-news-subwords-300', 'fasttext-wiki-news-subwords-300.gz'),
        "binary": False
    }
}


def gensim_info():
    # To get all pre-trained models and corpora provided in gensim
    info = api.info()
    print(json.dumps(info, indent=4))


def download_models():
    # Download word embeddings:
    # Download path is always home/<user>/gensim-data
    w2v = api.load('word2vec-google-news-300')
    glove = api.load("glove-wiki-gigaword-300")
    fasttext = api.load("fasttext-wiki-news-subwords-300")


def load_model(model_name):
    global model_dict
    return models.KeyedVectors.load_word2vec_format(model_dict[model_name]["path"], binary=model_dict[model_name]["binary"])


if __name__ == "__main__":
    # Example how to get and use the model
    # Only Glove, Fasttext and W2V possible
    #download_models()
    #model = load_model("glove")
    #vec = model.get_vector("memory")
    print(gensim_info())