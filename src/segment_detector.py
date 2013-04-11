import codecs
import logging
from operator import itemgetter
import os
import re
from BeautifulSoup import BeautifulStoneSoup
from numpy.ma import mean
from data import pan2013_ta_susp_path, pan2013_ta_src_path, pan2013_ta_pairs, pan2013_ta_section_paths
import numpy
from dist_measures import lemma_weighted_word_match
from sentence import Sentence

PARSED_FILE_SUFFIX = 'malt'

def read_parsed_file(path):
    with codecs.open(path, 'r', 'utf-8') as f:
        sentences = []
        sent = []

        for line in f.readlines():
            line = line.strip()

            # we only bother to track the end tags
            if line == '<s>':
                continue
            elif line == '</s>':
                if sent:
                    sentences.append(Sentence(sent))
                    sent =[]
            else:
                _, _, word, lemma, pos, _, _, _ = line.split("\t")
                sent.append((word, lemma, pos))

        if sent:
            sentences.append(Sentence(sent))

        return sentences


def generate_segs(size, segment_length, overlap):
    start = range(0, size, overlap)
    end = [min(x + segment_length, size) for x in start]

    return zip(start, end)

def token_match(susp_segs, src_segs):
    susp_tokens = set(" ".join(susp_segs).split())
    src_tokens = set(" ".join(src_segs).split())

    return len(susp_tokens.intersection(src_tokens)) / (len(src_tokens) * 1.0)

def compute_distances(susp_fn, src_fn, segment_length=10, overlap=5, dist_func=token_match):
    susp_path = os.path.join(pan2013_ta_susp_path,
                             os.path.splitext(susp_fn)[0] + os.path.extsep + PARSED_FILE_SUFFIX)
    src_path = os.path.join(pan2013_ta_src_path,
                            os.path.splitext(src_fn)[0] + os.path.extsep + PARSED_FILE_SUFFIX)

    susp_sents = [unicode(sent) for sent in read_parsed_file(susp_path)]
    src_sents = [unicode(sent) for sent in read_parsed_file(src_path)]

    susp_segs = generate_segs(len(susp_sents), segment_length, overlap)
    src_segs = generate_segs(len(src_sents), segment_length, overlap)

    dists = numpy.zeros((len(src_segs), len(susp_segs)))

    for i, (susp_start, susp_end) in enumerate(susp_segs):
        for j, (src_start, src_end) in enumerate(src_segs):
            dists[j, i] = apply(dist_func, [susp_sents[susp_start:susp_end], src_sents[src_start:src_end]])

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

def get_plagiarized_sents(section, src_fn, susp_fn):
    plagiarism_fn = os.path.join(pan2013_ta_section_paths[section],
                                 "%s-%s.xml" % (os.path.splitext(susp_fn)[0], os.path.splitext(src_fn)[0]))

    doc = BeautifulStoneSoup(open(plagiarism_fn).read())

    plag_spans = []

    for feature in doc.findAll('feature'):
        if feature['name'] == 'plagiarism':
            src_span = (int(feature['source_offset']), int(feature['source_length']))
            susp_span = (int(feature['this_offset']), int(feature['this_length']))

            plag_spans.append((susp_span, src_span))

    susp_fn = os.path.join(pan2013_ta_susp_path,
                           os.path.splitext(susp_fn)[0] + os.path.extsep + PARSED_FILE_SUFFIX)
    src_fn = os.path.join(pan2013_ta_src_path,
                          os.path.splitext(src_fn)[0] + os.path.extsep + PARSED_FILE_SUFFIX)

    susp_sents = [unicode(sent) for sent in read_parsed_file(susp_fn)]
    src_sents = [unicode(sent) for sent in read_parsed_file(src_fn)]

    plag_segs = []

    for (susp_offset, susp_len), (src_offset, src_len) in plag_spans:
        susp_seg = match_seg(susp_sents, susp_offset, susp_len)
        src_seg = match_seg(src_sents, src_offset, src_len)

        plag_segs.append((susp_seg, src_seg))

    return plag_segs


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

if __name__ == '__main__':
    section = 'no-obfuscation'

    src_scores = []
    susp_scores = []
    detected_counts = []

    overlap = 5
    seg_len = 10

    for susp_fn, src_fn in pan2013_ta_pairs[section]:
        print "%s - %s" % (susp_fn, src_fn)

        seg_dists = compute_distances(susp_fn, src_fn, segment_length=seg_len, overlap=overlap,
                                      dist_func=token_match)
        detected = detect_segments(seg_dists)

        detected_count = len(detected)
        detected_susp_count = len(set(map(itemgetter(0), detected)))
        detected_src_count = len(set(map(itemgetter(1), detected)))

        detected_counts.append((detected_count, detected_susp_count, detected_src_count))

        detected = [(seg_to_sent(susp, seg_len, overlap), seg_to_sent(src, seg_len, overlap))
                for susp, src in detected]

        susp_det = []
        src_det = []

        for susp, src in detected:
            susp_det += susp
            src_det += src

        plag_segs = get_plagiarized_sents(section, src_fn, susp_fn)

        susp_plag = []
        src_plag = []

        for susp, src in plag_segs:
            susp_plag += range(susp[0], susp[0]+susp[1])
            src_plag += range(src[0], src[0]+src[1])

        susp_score = score(susp_plag, susp_det)
        susp_scores.append(susp_score)
        print "Suspicious p: %.2f r: %.2f f: %.2f segments %d/%d" % (susp_score[0], susp_score[1], susp_score[2],
                                                                     detected_susp_count, detected_count)

        src_score = score(src_plag, src_det)
        src_scores.append(src_score)
        print "Source     p: %.2f r: %.2f f: %.2f segments %d/%d" % (src_score[0], src_score[1], src_score[2],
                                                                     detected_src_count, detected_count)

    print "Overall suspicious: p: %.2f, r: %.2f, f: %.2f" % (mean(map(itemgetter(0), susp_scores)),
                                                             mean(map(itemgetter(1), susp_scores)),
                                                             mean(map(itemgetter(2), susp_scores)))

    print "Overall source:     p: %.2f, r: %.2f, f: %.2f" % (mean(map(itemgetter(0), src_scores)),
                                                             mean(map(itemgetter(1), src_scores)),
                                                             mean(map(itemgetter(2), src_scores)))

    print "Overall segment counts: pairs: %.2f, susp: %.2f, src: %.2f" % (mean(map(itemgetter(0), detected_counts)),
                                                                          mean(map(itemgetter(1), detected_counts)),
                                                                          mean(map(itemgetter(2), detected_counts)))