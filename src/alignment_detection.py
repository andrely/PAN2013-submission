import logging
from operator import itemgetter

from BeautifulSoup import BeautifulStoneSoup
from numpy.ma import mean
import numpy

from data import pan2013_ta_pair_fns, read_parsed_file
from alignment_pair import alignment_pairs
from tools import flatten

class DetectionStatistics:
    def __init__(self):
        self.detected_counts = []
        self.susp_detected_counts = []
        self.src_detected_counts = []

    def add_detected_count(self, count):
        self.detected_counts.append(count)

    def add_susp_detected_count(self, count):
        self.susp_detected_counts.append(count)

    def add_src_detected_count(self, count):
        self.src_detected_counts.append(count)

    def summary(self):
        return "Overall segment counts: pairs: %.2f, susp: %.2f, src: %.2f" % (mean(self.detected_counts),
                                                                               mean(self.susp_detected_counts),
                                                                               mean(self.src_detected_counts))

def generate_segs(size, segment_length, spacing):
    """ Generate segment windows for a document.

    :param size: Number of sentences in the document
    :param segment_length: Length of segments to generate
    :param spacing: Number of sentences between each segment
    :return: List of segments, each segment is tuple with the start and (not inclusive)
        end index in the document.
    """
    start = range(0, size, spacing)
    end = [min(x + segment_length, size) for x in start]

    return zip(start, end)

# simple text distance
# ratio of token types in source document shared with the suspicicious document
def token_match(susp_sents, src_sents):
    susp_tokens = set(flatten([sent.words() for sent in susp_sents]))
    src_tokens = set(flatten([sent.words() for sent in src_sents]))

    return len(susp_tokens.intersection(src_tokens)) / (len(src_tokens) * 1.0)

def compute_distances(susp_doc, src_doc, segment_length=10, overlap=5, dist_func=token_match):
    susp_segs = generate_segs(len(susp_doc), segment_length, overlap)
    src_segs = generate_segs(len(src_doc), segment_length, overlap)

    dists = numpy.zeros((len(src_segs), len(susp_segs)))

    for i, (susp_start, susp_end) in enumerate(susp_segs):
        for j, (src_start, src_end) in enumerate(src_segs):
            dists[j, i] = apply(dist_func, [susp_doc[susp_start:susp_end], src_doc[src_start:src_end]])

    return dists


def match_seg(sentences, offset, length):
    tot_len = 0

    seg_start = None
    seg_len = None

    for i, sent in enumerate(sentences):
        next_len = tot_len + len(sent)

        if not seg_start and offset < next_len:
            if offset-tot_len > next_len-offset:
                seg_start = i
            else:
                seg_start = max(i-1, 0)

            seg_len = 1
        elif seg_start and offset+length > next_len:
            seg_len += 1
        elif seg_start and offset+length < next_len and abs(offset+length-next_len) < len(sent)/2:
            seg_len += 1
        elif seg_start and seg_len:
            break

        tot_len = next_len

    return seg_start, seg_len

def read_gold_alignments(alignment_pair):
    doc = BeautifulStoneSoup(open(alignment_pair.plagiarism_xml_fn()).read())

    plag_spans = []

    for feature in doc.findAll('feature'):
        if feature['name'] == 'plagiarism':
            src_span = (int(feature['source_offset']), int(feature['source_length']))
            susp_span = (int(feature['this_offset']), int(feature['this_length']))

            plag_spans.append((susp_span, src_span))

    plag_segs = []

    for (susp_offset, susp_len), (src_offset, src_len) in plag_spans:
        susp_seg = match_seg(alignment_pair.susp_doc, susp_offset, susp_len)
        src_seg = match_seg(alignment_pair.src_doc, src_offset, src_len)

        plag_segs.append((susp_seg, src_seg))

    return flatten(plag_segs)

def detect_segments(seg_dists, cutoff=0.5):
    plag_ind = seg_dists >= cutoff
    src, susp = numpy.where(plag_ind == True)

    return zip(susp, src)

def seg_to_sent(seg, seg_len, overlap):
    segs = generate_segs((seg+1)*seg_len, seg_len, overlap)
    start = segs[seg][0]
    end = segs[seg][1]
    return range(start, end)

def score(true_vals, pred_vals):
    true_vals = set(true_vals)
    pred_vals = set(pred_vals)

    correct = len(pred_vals.intersection(true_vals))

    if not pred_vals and not true_vals:
        return 1.0, 1.0, 1.0

    if pred_vals:
        prec = correct / (len(pred_vals) * 1.0)
    else:
        prec = 0.0

    if true_vals:
        rec = correct / (len(true_vals) * 1.0)
    else:
        rec = 1.0

    if prec+rec > 0.0:
        f = 2 * ((prec*rec)/(prec+rec))
    else:
        f = 0

    return prec, rec, f

def detect_alignments(alignment_pair, segment_length=10, overlap=5, statistics=None):
    logging.debug(str(alignment_pair))

    seg_dists = compute_distances(alignment_pair.susp_doc, alignment_pair.src_doc,
                                  segment_length=segment_length, overlap=overlap,
                                  dist_func=token_match)
    detected = detect_segments(seg_dists)

    if statistics:
        statistics.add_detected_count(len(detected))
        statistics.add_susp_detected_count(len(set(map(itemgetter(0), detected))))
        statistics.add_src_detected_count(len(set(map(itemgetter(1), detected))))

    detected = flatten([zip(seg_to_sent(susp, segment_length, overlap), seg_to_sent(src, segment_length, overlap))
                        for susp, src in detected])

    return detected

def score_alignment(gold_alignments, alignments):
    susp = [align[0] for align in alignments]
    susp_gold = [align[0] for align in gold_alignments]

    src = [align[1] for align in alignments]
    src_gold = [align[1] for align in gold_alignments]

    return (score(susp_gold, susp), score(src_gold, src))

def summarize_scores(scores):
    susp_scores = [s[0] for s in scores]
    src_scores = [s[1] for s in scores]

    susp_summary = (mean(map(itemgetter(0), susp_scores)),
                    mean(map(itemgetter(1), susp_scores)),
                    mean(map(itemgetter(2), susp_scores)))

    src_summary = (mean(map(itemgetter(0), src_scores)),
                   mean(map(itemgetter(1), src_scores)),
                   mean(map(itemgetter(2), src_scores)))

    return susp_summary, src_summary
