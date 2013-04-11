import os
from config import get_config


def read_pairs_file(fn):
    pairs = []

    with open(fn) as f:
        for line in f.readlines():
            susp_fn, source_fn = line.split()

            pairs.append((susp_fn, source_fn))

    return pairs

pan2013_ta_path = get_config('data_path')
pan2013_ta_susp_path = os.path.join(pan2013_ta_path, 'susp')
pan2013_ta_src_path = os.path.join(pan2013_ta_path, 'src')

pan2013_ta_sections = [
    'no-plagiarism',
    'no-obfuscation',
    'random-obfuscation',
    'translation-obfuscation',
    'summary-obfuscation'
]

pan2013_ta_section_paths = dict(zip(pan2013_ta_sections,
                                    [os.path.join(pan2013_ta_path,  "%02d-%s" % section)
                                     for section in enumerate(pan2013_ta_sections, start=1)]))

pan2013_ta_pair_fns = dict(zip(pan2013_ta_sections,
                               [os.path.join(pan2013_ta_section_paths[section], 'pairs')
                                for section in pan2013_ta_sections]))


pan2013_ta_pairs = dict(zip(pan2013_ta_sections,
                            [read_pairs_file(os.path.join(pan2013_ta_section_paths[section], 'pairs'))
                             for section in pan2013_ta_sections]))
