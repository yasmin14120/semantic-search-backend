# 1. Download infersent trained with GloVe/ Fasttext
# curl -Lo infersent1.pkl https://dl.fbaipublicfiles.com/infersent/infersent1.pkl
# curl -Lo infersent2.pkl https://dl.fbaipublicfiles.com/infersent/infersent2.pkl
# v1 is trained with Glove, v2 with fasttext

from backend.utils.encoder.models import InferSent
import torch

# before start use the gensim_load_models.py script to download and unpack the word embeddings glove & fasttext
path_glove = "/home/user/gensim-data/glove-wiki-gigaword-300/glove-wiki-gigaword-300.txt"
path_fasttext = "/home/user/gensim-data/fasttext-wiki-news-subwords-300/fasttext-wiki-news-subwords-300.vec"
path_infersent_v1 = "backend/utils/encoder/infersent1.pkl"
path_infersent_v2 = "backend/utils/encoder/infersent2.pkl"


def load_model_v1(string=""):
    print("loading...")
    params_model = {'bsize': 64, 'word_emb_dim': 300, 'enc_lstm_dim': 2048,
                    'pool_type': 'max', 'dpout_model': 0.0, 'version': 2}
    infersent_ = InferSent(params_model)
    infersent_.load_state_dict(torch.load(path_infersent_v1))
    infersent_.set_w2v_path(path_glove)
    infersent_.build_vocab_k_words(K=500000)  # add the most common k english words (optimisation with direct sentence input?)
    print("Model has been loaded successfully.")
    return infersent_


def load_model_v2(string=""):
    params_model = {'bsize': 64, 'word_emb_dim': 300, 'enc_lstm_dim': 2048,
                    'pool_type': 'max', 'dpout_model': 0.0, 'version': 2}
    infersent_ = InferSent(params_model)
    infersent_.load_state_dict(torch.load(path_infersent_v2))
    infersent_.set_w2v_path(path_fasttext)
    infersent_.build_vocab_k_words(
        K=500000)  # add the most common k english words (only 500000 because I only use the small package)
    print("Model has been loaded successfully.")
    return infersent_


if __name__ == "__main__":
    # Example how to load and use infersent model
    # For a detailed description see https://github.com/facebookresearch/InferSent

    infersent = load_model_v1()

    sentences = ["Hello fresh is a good start in the day.",
                 "This morning I feel great.",
                 "The Cat is sleeping every morning.",
                 "Be grateful today."]

    embeddings = infersent.encode(sentences, tokenize=True)

    print("EMBEDDINGS: ", embeddings)


