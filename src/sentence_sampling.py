import logging
import os
from numpy import array
from numpy.random.mtrand import randint, choice
from pandas import DataFrame
from alignment_detection import token_match
from alignment_pair import alignment_pairs, AlignmentPair
from data import pan2013_ta_sections
from dist_measures import lemma_weighted_word_match, token_weighted_word_match, word_ngram_match_1, word_ngram_match_2, word_ngram_match_3, lemma_ngram_match_1, lemma_ngram_match_2, lemma_ngram_match_3, relative_ic_len_dist, relative_len_dist, weighted_wiki_dist_sim, weighted_nyt_dist_sim, nyt_dist_sim, wn_sim_match_dist

all_dists = [lemma_weighted_word_match,
             token_weighted_word_match,
             word_ngram_match_1,
             word_ngram_match_2,
             word_ngram_match_3,
             lemma_ngram_match_1,
             lemma_ngram_match_2,
             lemma_ngram_match_3,
             wn_sim_match_dist,
             nyt_dist_sim,
             weighted_nyt_dist_sim,
             weighted_wiki_dist_sim,
             relative_len_dist,
             relative_ic_len_dist,
             token_match]

def sample_sentences(section, n=1000):
    pair_list = array(list(alignment_pairs(section=section)))

    pair_len = len(pair_list)

    plagiarized_sample = []
    non_plagiarized_sample = []

    # draw plagiarized sentences
    for pair in pair_list[randint(0, high=pair_len, size=n)]:
        gold = pair.gold_alignments()

        if len(gold) > 0:
            susp_draw, src_draw = gold[randint(0, high=len(gold))]

            plagiarized_sample.append((pair.susp_fn, pair.src_fn, susp_draw, src_draw))
        else:
            logging.warn("Empty gold alignment for %s - %s" % (pair.susp_fn, pair.src_fn))

    # draw random non-plagiarized sentence pairs
    for pair in pair_list[randint(0, high=pair_len, size=n)]:
        gold = pair.gold_alignments()
        gold_susp_indexes = [x[0] for x in gold]
        gold_src_indexes = [x[1] for x in gold]

        susp_draw = choice([x for x in xrange(len(pair.susp_doc)) if x not in gold_susp_indexes])
        src_draw = choice([x for x in xrange(len(pair.src_doc)) if x not in gold_src_indexes])

        non_plagiarized_sample.append((pair.susp_fn, pair.src_fn, susp_draw, src_draw))

    return plagiarized_sample, non_plagiarized_sample

def generate_sample(dists=all_dists, n=1000, section='no-obfuscation'):
    plag_sample, non_plag_sample = sample_sentences(section, n=n)

    sample = []

    for susp_fn, src_fn, susp_idx, src_idx in plag_sample:
        pair = AlignmentPair(susp_fn, src_fn, section)
        susp_sents = [pair.susp_doc[min(susp_idx, len(pair.susp_doc)-1)]]
        src_sents = [pair.src_doc[min(src_idx, len(pair.src_doc)-1)]]

        dist_scores = [apply(func, [susp_sents, src_sents]) for func in dists]

        sample.append([susp_fn, src_fn, susp_idx, src_idx, section, True] + dist_scores)

    for susp_fn, src_fn, susp_idx, src_idx in non_plag_sample:
        pair = AlignmentPair(susp_fn, src_fn, section)
        susp_sents = [pair.susp_doc[min(susp_idx, len(pair.susp_doc)-1)]]
        src_sents = [pair.src_doc[min(src_idx, len(pair.src_doc)-1)]]

        dist_scores = [apply(func, [susp_sents, src_sents]) for func in dists]

        sample.append([susp_fn, src_fn, susp_idx, src_idx, section, False] + dist_scores)

    return sample


def col_names(dist_funcs=all_dists):
    return ["susp_fn", "src_fn", "susp_idx", "src_idx", "section", "plagiarism"] + \
           [dist_func.func_name for dist_func in dist_funcs]


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    for section in pan2013_ta_sections:
        logging.info("Generating sample for %s" % section)

        df = DataFrame(generate_sample(section=section), columns=col_names())
        fn = section + '_dists.csv'

        logging.info("Writing sample to %s" % fn)

        if os.path.exists(fn):
            logging.error("file %s exists" % fn)
        else:
            df.to_csv(fn)
