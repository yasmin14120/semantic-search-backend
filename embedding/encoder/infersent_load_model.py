# 1. Download infersent trained with GloVe/ Fasttext
# curl -Lo infersent1.pkl https://dl.fbaipublicfiles.com/infersent/infersent1.pkl
# curl -Lo infersent2.pkl https://dl.fbaipublicfiles.com/infersent/infersent2.pkl
# v1 is trained with Glove, v2 with fasttext

from encoder.models import InferSent
import torch


def load_model(path_infersent, path_word_vector):
    params_model = {'bsize': 64, 'word_emb_dim': 300, 'enc_lstm_dim': 2048,
                    'pool_type': 'max', 'dpout_model': 0.0, 'version': 2}
    infersent_ = InferSent(params_model)
    infersent_.load_state_dict(torch.load(path_infersent))
    infersent_.set_w2v_path(path_word_vector)
    infersent_.build_vocab_k_words(K=500000)  # add the most common k english words (optimisation with direct sentence input?)
    print("Model has been loaded successfully.")
    return infersent_


if __name__ == "__main__":
    # Example how to load and use infersent model
    # For a detailed description see https://github.com/facebookresearch/InferSent

    # before start use the gensim_load_models.py script to download and unpack the word embeddings glove & fasttext
    path_glove = "/home/user/gensim-data/glove-wiki-gigaword-300/glove-wiki-gigaword-300.txt"
    path_fasttext = "/home/user/gensim-data/fasttext-wiki-news-subwords-300/fasttext-wiki-news-subwords-300.vec"
    path_infersent_v1 = "infersent1.pkl"
    path_infersent_v2 = "infersent2.pkl"

    infersent = load_model(path_infersent_v1, path_glove)

    sentences = ["Hello fresh is a good start in the day.",
                 "This morning I feel great.",
                 "The Cat is sleeping every morning.",
                 "Be grateful today."]

    embeddings = infersent.encode(sentences, tokenize=True)

    print("EMBEDDINGS: ", embeddings)
    print(len(embeddings[0]))

    # results in an error, I wasn't interested in debugging facebook code, so I stopped trying
    # infersent.visualize('A man plays an instrument.', tokenize=True)


