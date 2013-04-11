# coding=utf-8

import re
import nltk
from takelab_features import fix_compounds, get_lemmatized_words, weighted_word_match
from tools import flatten

def takelab_preprocess(text):
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
    susp_sents = takelab_preprocess("\n".join(susp_sents))
    src_sents = takelab_preprocess("\n".join(src_sents))

    susp_lem = get_lemmatized_words(susp_sents)
    src_lem = get_lemmatized_words(src_sents)

    return weighted_word_match(susp_lem, src_lem)
