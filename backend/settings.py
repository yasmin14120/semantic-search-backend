from backend.utils.model import Model, ModelHandler
from backend.utils.gensim_load_models import load_model
from backend.utils.encoder.infersent_load_model import load_model_v1
import tensorflow_hub as hub


def load_use(path=""):
    path = "backend/utils/universal-sentence-encoder_4"
    return hub.load(path)


Glove = Model("glove", load_model)
W2V = Model("w2v", load_model)
Fasttext = Model("fasttext", load_model)
InferSent = Model("infersent", load_model_v1)
USE = Model("use", load_use)
Handler = ModelHandler({"glove": Glove,
                        "w2v": W2V,
                        "fasttext": Fasttext,
                        "infersent": InferSent,
                        "use": USE})
