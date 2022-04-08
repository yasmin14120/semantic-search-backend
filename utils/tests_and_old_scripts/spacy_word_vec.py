import numpy as np
import spacy
from sense2vec import Sense2Vec
from spacy.lang.en.stop_words import STOP_WORDS
from scipy.cluster.vq import kmeans, kmeans2

nlp = spacy.load("en_core_web_md")  # make sure to use larger package!
s2v = nlp.add_pipe("sense2vec")
s2v.from_disk("s2v_reddit_2015_md/s2v_old")

doc1 = nlp("Huawei is a good mobile phone. Mobile phones are important in our time.")
doc2 = nlp("Mobile phones are important in our time.")
doc3 = nlp("A mobile phone, cellular phone, cell phone, cellphone, handphone, or hand phone, sometimes "
           "shortened to simply mobile, cell or just phone, is a portable telephone that can make and "
           "receive calls over a radio frequency link while the user is moving within a telephone service "
           "area. The radio frequency link establishes a connection to the switching systems of a mobile "
           "phone operator, which provides access to the public switched telephone network (PSTN). "
           "Modern mobile telephone services use a cellular network architecture and, therefore, mobile "
           "telephones are called cellular telephones or cell phones in North America. In addition to "
           "telephony, digital mobile phones (2G) support a variety of other services, such as text messaging,"
           " MMS, email, Internet access, short-range wireless communications (infrared, Bluetooth), "
           "business applications, video games and digital photography. Mobile phones offering only "
           "those capabilities are known as feature phones; mobile phones which offer greatly advanced "
           "computing capabilities are referred to as smartphones.[1]The development of "
           "metal-oxide-semiconductor (MOS) large-scale integration (LSI) technology, information theory "
           "and cellular networking led to the development of affordable mobile communications."
           "The first handheld mobile phone was demonstrated by John F. Mitchell[2][3] and Martin Cooper of "
           "Motorola in 1973, using a handset weighing c. 2 kilograms (4.4 lbs).[4] In 1979, Nippon Telegraph "
           "and Telephone (NTT) launched the world's first cellular network in Japan.[citation needed] "
           "In 1983, the DynaTAC 8000x was the first commercially available handheld mobile phone. "
           "From 1983 to 2014, worldwide mobile phone subscriptions grew to over seven billion; enough "
           "to provide one for every person on Earth.[5] In the first quarter of 2016, the top smartphone "
           "developers worldwide were Samsung, Apple and Huawei; smartphone sales represented 78 percent of "
           "total mobile phone sales.[6] For feature phones (slang: 'dumbphones') as of 2016, the top-selling "
           "brands were Samsung, Nokia and Alcatel.")


# Similarity of two documents
# print(doc1[0], "<->", doc2[0], doc1.similarity(doc2))
# print(doc1[0], "<->", doc2[1], doc1.similarity(doc2))
# print(doc1[-1], "<->", doc2[1], doc1.similarity(doc2))
# print(doc2[1].pos_)


def clean_text(doc):
    filtered_words = []
    vectors = []
    unknown = []
    for token in range(len(doc)):
        if doc[token].pos_ not in ["NUM", "SYM", "PUNCT"] and not doc[token].is_stop:
            if doc[token]._.s2v_vec is None:
                unknown.append(token)
            else:
                filtered_words.append(token)
                vectors.append(doc[token]._.s2v_vec)
    return filtered_words, np.array(vectors)


def create_doc(filename):
    with open(filename, "r") as file:
        text = file.read()
    global nlp
    doc = nlp(text)
    return doc


def cluster(vectors, doc, indices):
    synonyms = []
    #clusters, prec = kmeans(vectors, len(indices) // 2)
    centroid, label = kmeans2(vectors, 3, minit='points')
    print("Cluster_1: ", vectors[label == 0])
    print("Cluster_2: ", vectors[label == 1])
    print("Cluster_3: ", vectors[label == 2])
    # temp = []
    # for cluster in clusters:
    #     temp_cluster = []
    #     for vector in cluster:
    #         temp_cluster.append(doc[indices[np.ndarray.tolist(vectors).index(vector)]])
    #     temp.append(temp_cluster)
    # return temp

#    return save_synonyms(synonyms, "synonyms.csv")

index, vector = clean_text(doc1)
print(vector)
cluster(vector, doc1, index)


# print(cluster(vector, doc1, index))

def find_synonyms_knn():
    pass


def save_synonyms(synonyms, filename):
    with open(filename, "w+") as file:
        file.write("{}, {}\n".format("FROM TEXT", "FROM MODEL"))
        for synonym in synonyms:
            file.write("{}, {}\n".format(synonym[0], synonym[1]))
