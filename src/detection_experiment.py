import logging
from alignment_detection import detect_alignments, read_gold_alignments, score_alignment, \
    summarize_scores, DetectionStatistics
from alignment_pair import alignment_pairs
from data import pan2013_ta_sections, pan2013_ta_pair_fns

def print_summary(summary):
    susp, src = summary

    print "Overall suspicious: p: %.2f, r: %.2f, f: %.2f" % susp
    print "Overall source:     p: %.2f, r: %.2f, f: %.2f" % src

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    for section in pan2013_ta_sections:
        logging.info("Processing section %s" % section)
        scores = []

        stats = DetectionStatistics()

        for pair in alignment_pairs(section=section):
            alignments = detect_alignments(pair, statistics=stats)

            gold_alignments = read_gold_alignments(pair)

            scores.append(score_alignment(gold_alignments, alignments))

        summary = summarize_scores(scores)

        print "Section: %s" % section

        print_summary(summary)
        print stats.summary()
