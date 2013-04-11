# holds sentences
# each token should be a tuble with:
# (word, lemma, pos)

class Sentence:
    def __init__(self, parsed_tokens):
        self.parsed_tokens = parsed_tokens

    def __unicode__(self):
        return u" ".join([tok[0] for tok in self.parsed_tokens])
