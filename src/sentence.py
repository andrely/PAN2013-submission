# holds sentences
# each token should be a tuble with:
# (word, lemma, pos)

class Sentence:
    def __init__(self, parsed_tokens):
        self.parsed_tokens = parsed_tokens

        self.char_length = len(" ".join(self.words()))

    def __unicode__(self):
        return u" ".join([tok[0] for tok in self.parsed_tokens])

    def words(self):
        return [tok[0] for tok in self.parsed_tokens]

    def lemmas(self):
        return [tok[1] for tok in self.parsed_tokens]

    def pos_tags(self):
        return [tok[2] for tok in self.parsed_tokens]

    def __len__(self):
        return self.char_length