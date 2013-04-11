import os
from data import pan2013_ta_susp_path, pan2013_ta_src_path, pan2013_ta_section_paths

PARSED_FILE_SUFFIX = 'malt'

# a generator of alignment pair instances from a pairs file
def alignment_pairs(pair_fn, section=None):
    with open(pair_fn) as f:
        while True:
            line = f.readline()

            if line == '':
                break

            susp_fn, src_fn = line.strip().split()

            yield AlignmentPair(susp_fn, src_fn, section=section)

# keep tracks of filenames and other info for a pair of siource/suspicious
# files that are being analyzed
class AlignmentPair:
    def __init__(self, susp_fn, src_fn, section=None):
        self.susp_fn = susp_fn
        self.src_fn = src_fn
        self.section = section

    def __str__(self):
        return "%s - %s" % (self.susp_fn, self.src_fn)

    def susp_parsed_fn(self):
        return os.path.join(pan2013_ta_susp_path,
                            os.path.splitext(self.susp_fn)[0] + os.path.extsep + PARSED_FILE_SUFFIX)

    def src_parsed_fn(self):
        return os.path.join(pan2013_ta_src_path,
                            os.path.splitext(self.src_fn)[0] + os.path.extsep + PARSED_FILE_SUFFIX)

    def plagiarism_xml_fn(self):
        if not self.section:
            return None
        else:
            return os.path.join(pan2013_ta_section_paths[self.section],
                                "%s-%s.xml" % (os.path.splitext(self.susp_fn)[0], os.path.splitext(self.src_fn)[0]))
