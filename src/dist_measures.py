# coding=utf-8

import re
import nltk
from takelab_features import fix_compounds, get_lemmatized_words, weighted_word_match, get_locase_words, stopwords, ngram_match, wn_sim_match, dist_sim, nyt_sim, weighted_dist_sim, wiki_sim, relative_len_difference, relative_ic_difference
from tools import flatten

def takelab_preprocess(sents):
    text = " ".join(flatten([sent.words() for sent in sents]))

    r1 = re.compile(r'\<([^ ]+)\>')
    r2 = re.compile(r'\$US(\d)')

    text = text.replace(u'’', "'")
    text = text.replace(u'``', '"')
    text = text.replace(u"''", '"')
    text = text.replace(u"—", '--')
    text = text.replace(u"–", '--')
    text = text.replace(u"´", "'")
    text = text.replace(u"-", " ")
    text = text.replace(u"/", " ")
    text = r1.sub(r'\1', text)
    text = r2.sub(r'$\1', text)
    s = nltk.word_tokenize(text)

    s = [x.encode('utf-8') for x in s]

    for i in xrange(len(s)):
        if s[i] == "n't":
            s[i] = "not"
        elif s[i] == "'m":
            s[i] = "am"

    s = nltk.pos_tag(s)

    return s


def lemma_weighted_word_match(susp_sents, src_sents):
    susp_sents = takelab_preprocess(susp_sents)
    src_sents = takelab_preprocess(src_sents)

    susp_lem = get_lemmatized_words(susp_sents)
    src_lem = get_lemmatized_words(src_sents)

    return weighted_word_match(susp_lem, src_lem)

def token_weighted_word_match(susp_sents, src_sents):
    susp_sents = takelab_preprocess(susp_sents)
    src_sents = takelab_preprocess(src_sents)

    olca = get_locase_words(susp_sents)
    olcb = get_locase_words(src_sents)

    return weighted_word_match(olca, olcb)

def word_ngram_match_1(susp_sents, src_sents):
    susp_sents = takelab_preprocess(susp_sents)
    src_sents = takelab_preprocess(src_sents)

    olca = get_locase_words(susp_sents)
    olcb = get_locase_words(src_sents)
    lca = [w for w in olca if w not in stopwords]
    lcb = [w for w in olcb if w not in stopwords]

    return ngram_match(lca, lcb, 1)

def word_ngram_match_2(susp_sents, src_sents):
    susp_sents = takelab_preprocess(susp_sents)
    src_sents = takelab_preprocess(src_sents)

    olca = get_locase_words(susp_sents)
    olcb = get_locase_words(src_sents)
    lca = [w for w in olca if w not in stopwords]
    lcb = [w for w in olcb if w not in stopwords]

    return ngram_match(lca, lcb, 2)

def word_ngram_match_3(susp_sents, src_sents):
    susp_sents = takelab_preprocess(susp_sents)
    src_sents = takelab_preprocess(src_sents)

    olca = get_locase_words(susp_sents)
    olcb = get_locase_words(src_sents)
    lca = [w for w in olca if w not in stopwords]
    lcb = [w for w in olcb if w not in stopwords]

    return ngram_match(lca, lcb, 3)

def lemma_ngram_match_1(susp_sents, src_sents):
    susp_sents = takelab_preprocess(susp_sents)
    src_sents = takelab_preprocess(src_sents)

    susp_lem = get_lemmatized_words(susp_sents)
    src_lem = get_lemmatized_words(src_sents)

    return ngram_match(susp_lem, src_lem, 1)

def lemma_ngram_match_2(susp_sents, src_sents):
    susp_sents = takelab_preprocess(susp_sents)
    src_sents = takelab_preprocess(src_sents)

    susp_lem = get_lemmatized_words(susp_sents)
    src_lem = get_lemmatized_words(src_sents)

    return ngram_match(susp_lem, src_lem, 1)

def lemma_ngram_match_3(susp_sents, src_sents):
    susp_sents = takelab_preprocess(susp_sents)
    src_sents = takelab_preprocess(src_sents)

    susp_lem = get_lemmatized_words(susp_sents)
    src_lem = get_lemmatized_words(src_sents)

    return ngram_match(susp_lem, src_lem, 1)

def wn_sim_match_dist(susp_sents, src_sents):
    susp_sents = takelab_preprocess(susp_sents)
    src_sents = takelab_preprocess(src_sents)

    susp_lem = get_lemmatized_words(susp_sents)
    src_lem = get_lemmatized_words(src_sents)

    return wn_sim_match(susp_lem, src_lem)

def nyt_dist_sim(susp_sents, src_sents):
    susp_sents = takelab_preprocess(susp_sents)
    src_sents = takelab_preprocess(src_sents)

    susp_lem = get_lemmatized_words(susp_sents)
    src_lem = get_lemmatized_words(src_sents)

    return dist_sim(nyt_sim, susp_lem, src_lem)

def weighted_nyt_dist_sim(susp_sents, src_sents):
    susp_sents = takelab_preprocess(susp_sents)
    src_sents = takelab_preprocess(src_sents)

    susp_lem = get_lemmatized_words(susp_sents)
    src_lem = get_lemmatized_words(src_sents)

    return weighted_dist_sim(nyt_sim, susp_lem, src_lem)

def weighted_wiki_dist_sim(susp_sents, src_sents):
    susp_sents = takelab_preprocess(susp_sents)
    src_sents = takelab_preprocess(src_sents)

    susp_lem = get_lemmatized_words(susp_sents)
    src_lem = get_lemmatized_words(src_sents)

    return weighted_dist_sim(wiki_sim, susp_lem, src_lem)

def relative_len_dist(susp_sents, src_sents):
    susp_sents = takelab_preprocess(susp_sents)
    src_sents = takelab_preprocess(src_sents)

    olca = get_locase_words(susp_sents)
    olcb = get_locase_words(src_sents)
    lca = [w for w in olca if w not in stopwords]
    lcb = [w for w in olcb if w not in stopwords]

    return relative_len_difference(lca, lcb)

def relative_ic_len_dist(susp_sents, src_sents):
    susp_sents = takelab_preprocess(susp_sents)
    src_sents = takelab_preprocess(src_sents)

    olca = get_locase_words(susp_sents)
    olcb = get_locase_words(src_sents)

    return relative_ic_difference(olca, olcb)
