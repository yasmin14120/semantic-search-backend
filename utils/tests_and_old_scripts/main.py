# Import keras, tensorflow and word2vec
from gensim.models import KeyedVectors
import spacy
import pandas as pd
import json

# configurations
nlp = spacy.load("en_core_web_md")
GENSIM_SKIP_GRAM = 'en_wiki_dump_2017/model.bin'


def find_synonyms_knn(model, word, top_n):
    try:
        result = model.most_similar(positive=[word], topn=top_n)
        return result
    except KeyError as e:
        print("ERROR: ",e)
        return ""


def create_doc(filename):
    with open(filename, "r") as file:
        text = file.read()
    global nlp
    doc = nlp(text)
    return doc


def start_extracting_synonyms(model, filename):
    doc = create_doc(filename)
    synonyms = []
    for sent in doc.sents:
        for token in sent:
            print(token)
            target = find_synonyms_knn(model, str(token), 1)
            synonyms.append((token, target))
    return save_synonyms(synonyms, "synonyms.csv")


def read_database(filename, boundary=None):
    data = []
    with open(filename) as f:
        i = 0
        for line in f:
            if boundary is not None and i >= boundary:
                return data, pd.DataFrame.from_dict({})
            data.append(json.loads(line.strip()))
            i += 1

    df = pd.DataFrame.from_dict({})

    return data, df


# Todo: Replace with panda variant
def filter_database_slow(data, keywords):
    """
    Remove all attributes from data except that in the keywords array
    :param data: array of dicts, every dict has same keys and shape
    :param keywords: array of strings
    :return: data filtered
    """
    for i in range(len(data)):
        temp = {}
        for keyword in keywords:
            temp[keyword] = data[i][keyword]
        data[i] = temp
    return data


def save_synonyms(synonyms, filename):
    with open(filename, "w+") as file:
        file.write("{}, {}\n".format("FROM TEXT", "FROM MODEL"))
        for synonym in synonyms:
            file.write("{}, {}\n".format(synonym[0], synonym[1]))


def save_database(data, filename, keywords):
    with open(filename, "w+") as file:
        file.write("{}, {}\n".format("FROM TEXT", "FROM MODEL"))
        for row in data:
            temp = ""
            for keyword in keywords:
                temp += "{}, ".format(row[keyword])
            file.write(temp[:-2] + "\n")


def prepare_database(filename, filter_keywords, boundary):
    data = read_database(filename, boundary)[0]
    if filter_keywords is not None:
        data = filter_database_slow(data, filter_keywords)
    save_database(data, "../data/database", filter_keywords)


if __name__ == "__main__":
    model_ = KeyedVectors.load_word2vec_format(GENSIM_SKIP_GRAM, binary=True)
    print("Model is loaded to memory")
    start_extracting_synonyms(model_, "../data/database")
