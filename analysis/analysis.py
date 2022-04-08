# Analysis Tool of the Semantic Search user study
from elasticsearch import Elasticsearch
from scipy.stats import fisher_exact, barnard_exact, boschloo_exact, chi2_contingency
import numpy as np


# Configurations:
es_url = "http://localhost:9200"
es_index = "data_books"


def get_ratings(model):
    res = Elasticsearch(es_url).search(
        index="test_stats",
        body={
            "size": 10000,
            "query": {
                "bool": {
                    "must": [
                        {"term": {
                            "model": model
                        }}
                    ]
                }}
        }
    )
    hits = res["hits"]["total"]['value']
    count_true = count_ratings(res["hits"]["hits"], "rating", True)
    count_false = count_ratings(res["hits"]["hits"], "rating", False)
    return {"model": model, "hits": hits, "good_rating": count_true, "bad_rating": count_false, "ratio_good": count_true/hits*100, "ratio_bad": count_false/hits*100}


def count_ratings(res, field, value):
    counter = 0
    for result in res:
        if result["_source"][field] == value:
            counter += 1
    return counter


def run_tests(table):
    results_fisher_pvalues = []
    results_barnard_pvalues = []
    results_boschloo_pvalues = []

    for model in range(len(table[0])):
        fisher_, barnard_, boschloo_ = [], [], []
        for model_2 in range(len(table[0])):
            temp_table = [[table[0][model], table[0][model_2]], [table[1][model], table[1][model_2]]]
            # calc fisher
            #_, temp_pvalue = fisher(temp_table)
            #fisher_.append(temp_pvalue)
            # calc barnard
            #temp_pvalue = barnard(temp_table)
            #barnard_.append(temp_pvalue)
            # calc boschloo
            temp_pvalue = boschloo(temp_table)
            boschloo_.append(temp_pvalue)
            print(boschloo_)

        results_fisher_pvalues.append(fisher_)
        results_barnard_pvalues.append(barnard_)
        results_boschloo_pvalues.append(boschloo_)
        print(results_boschloo_pvalues)

    results = {"fisher": {"pvalue": results_fisher_pvalues},
               "barnard": {"pvalue": results_barnard_pvalues},
               "boschloo": {"pvalue": results_boschloo_pvalues},
               }
    return results


def fisher(table):
    oddsratio, pvalue = fisher_exact(table)
    return oddsratio, pvalue


def barnard(table):
    pvalue = barnard_exact(table)
    return pvalue.pvalue


def boschloo(table):
    pvalue = boschloo_exact(table)
    return pvalue.pvalue


def chi_2(table):
    stat, p, dof, expected = chi2_contingency(table)
    alpha = 0.05
    print(p)
    if p <= alpha:
        print('Dependent (reject H0)')
    else:
        print('Independent (fail to reject H0)')


if __name__ == "__main__":
    glove = get_ratings("glove")
    use = get_ratings("use")
    fasttext = get_ratings("fasttext")
    infersent = get_ratings("infersent")
    print(glove)
    print(use)
    print(fasttext)
    print(infersent)
    table = [[glove["good_rating"], glove["bad_rating"]],
              [use["good_rating"], use["bad_rating"]],
              [fasttext["good_rating"], fasttext["bad_rating"]],
              [infersent["good_rating"], infersent["bad_rating"]]]
    table_t = [[glove["good_rating"], use["good_rating"], fasttext["good_rating"], infersent["good_rating"]],
               [glove["bad_rating"], use["bad_rating"], fasttext["bad_rating"], infersent["bad_rating"]]]
    # Run FISHER test
    r = run_tests(table_t)
    print("FISHER:")
    print(np.asarray(r["fisher"]["pvalue"]))
    print("BARNARD:")
    print(np.asarray(r["barnard"]["pvalue"]))
    print("BOSCHLOO:")
    print(np.asarray(r["boschloo"]["pvalue"]))
    chi_2(table_t)

# Results:
# {'model': 'glove', 'hits': 731, 'good_rating': 495, 'bad_rating': 236, 'ratio_good': 67.72, 'ratio_bad': 32.28}
# {'model': 'use', 'hits': 681, 'good_rating': 443, 'bad_rating': 238, 'ratio_good': 65.05, 'ratio_bad': 34.95}
# {'model': 'fasttext', 'hits': 807, 'good_rating': 489, 'bad_rating': 318, 'ratio_good': 60.59, 'ratio_bad': 39.41}
# {'model': 'infersent', 'hits': 714, 'good_rating': 143, 'bad_rating': 571, 'ratio_good': 20.03, 'ratio_bad': 79.97}

# TESTS:
# Fisher Test:
# [  [1.0, 0.31013152080736944, 0.004068544719306542, 1.8568803950096902e-77],
#   [0.31013152080736944, 1.0, 0.08521773161863308, 2.738970756143432e-67],
#   [0.004068544719306542, 0.08521773161863308, 1.0, 6.556974001375678e-60],
#   [1.8568803950096906e-77, 2.738970756143432e-67, 6.556974001375677e-60, 1.0]]
#
# BARNARD:
# [[1.00000000e+00 2.99134619e-01 3.70707359e-03 1.74443277e-77]
#  [2.99134619e-01 1.00000000e+00 7.75685227e-02 2.47740810e-67]
#  [3.70707359e-03 7.75685227e-02 1.00000000e+00 1.99735665e-59]
#  [1.74443277e-77 2.47740810e-67 1.99735665e-59 1.00000000e+00]]
# BOSCHLOO:

# Pearson Chi Test (ohne InferSent weil nicht bewertbar)
# p = 0.012845776688492998
