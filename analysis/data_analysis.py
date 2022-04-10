# Skript to analyse used dataset
# Idea was to analyse the unique words count, the len of inverted index

import json

import requests
import spacy

from elasticsearch import es_request

nlp = spacy.load("en_core_web_md")


def count_unique_words(batch_size, index, fields):
    word_index = "inverse-index"
    url = "http://localhost:9200/" + index + "/_pit?keep_alive=60m"
    pit_id = requests.post(url=url).json().get("id")
    hits = int(requests.get("http://localhost:9200/{}/_count".format(index)).json().get("count"))
    search_after = None
    while hits > 0:
        words, search_after, size_ = search_after_query(fields, pit_id, search_after)
        words = list(words)
        words = [words[i] for i in range(len(words)) if not check_for_doc(words[i], word_index)]

        bulk = prepare_bulk_index(words, word_index=word_index)
        r = requests.post("http://localhost:9200/" + word_index + "/_bulk?refresh=wait_on",
                          headers={"content-type": "application/json"},
                          data=bulk)
        print(r.text)
        print(hits)
        print(search_after)
        hits -= size_


def check_for_doc(word, index):
    query = {
        "query": {
            "match": {
                "word": word
            }
        }
    }
    url = "http://localhost:9200/" + index + "/_search"
    res = es_request("GET", url, data=query).json()
    if res.get("hits", {}).get("total", []).get("value", 0) > 0:
        return True
    return False


def search_after_query(fields, pit_id, search_after=None):
    query = {
        "_source": fields,
        "size": 10000,
        "query": {
            "match_all": {}
        },
        "pit": {
            "id": pit_id,
            "keep_alive": "60m"
        },
        "sort": [
            {"_id": {"order": "asc"}}
        ]
    }
    if search_after is not None:
        query["search_after"] = search_after

    url = "http://localhost:9200/_search"
    r = es_request("GET", url, data=query)
    res = r.json().get("hits", {}).get("hits", [])
    if len(res) == 0:
        print("ERROR: ", r.text)
        return res, 0, 0
    strings = []
    for item in res:
        for field in fields:
            # noinspection PyBroadException
            try:
                if isinstance(item['_source'][field], list):
                    temp = ""
                    for _str in item['_source'][field]:
                        temp += _str
                    strings.append(temp)
                else:
                    strings.append(item['_source'][field])
            except Exception:
                strings.append("")

    return filter_words(strings), res[-1]["sort"], len(res)


def filter_words(strings):
    """
    Function takes an Array of string, filters them for nouns, verbs and adjectives and returns an array of words.
    :param strings: Array of string, from which the relevant words should be retrieved.
    :return: Array of words.
    """
    # Step 2: Prepare words to lookup
    counter_list = []
    words = set()
    for _str in strings:
        doc = nlp(_str.lower())
        temp = 0
        for token in doc:
            if token.pos_ not in ["SYM", "PUNCT"]:
                temp += 1
            if token.pos_ not in ["NUM", "SYM", "PUNCT"] and not token.is_stop:
                words.add(token.lemma_)
        counter_list.append(temp)

    # Return counter_list to calculate the avg word per doc value
    return words


def prepare_bulk_index(word_list, word_index):
    bulk = ""
    for word in word_list:
        bulk_data = {"doc": {"word": word}}
        bulk_action = {"index": {"_index": word_index, "_type": "_doc"}}
        bulk += json.dumps(bulk_action) + "\n"
        bulk += json.dumps(bulk_data) + "\n"
    return bulk


if __name__ == "__main__":
    count_unique_words(100, "data_books", ["title", "description"])
