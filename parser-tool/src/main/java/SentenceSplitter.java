import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.ling.HasWord;
import edu.stanford.nlp.ling.TaggedWord;
import edu.stanford.nlp.objectbank.TokenizerFactory;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.process.Morphology;
import edu.stanford.nlp.process.PTBTokenizer;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import org.apache.commons.io.FilenameUtils;
import org.maltparser.MaltParserService;
import org.maltparser.core.exception.MaltChainedException;

import java.io.*;
import java.util.ArrayList;
import java.util.List;
import java.util.logging.Logger;

public class SentenceSplitter {
    public Logger logger = Logger.getLogger(SentenceSplitter.class.getName());

    public MaxentTagger tagger;
    public Morphology lemmatizer;
    public MaltParserService parser;

    public SentenceSplitter() {
        lemmatizer = new Morphology();
        try {
            parser = new MaltParserService();
            parser.initializeParserModel("-c engmalt.linear-1.7.mco -m parse -w /Users/stinky/Work/PAN2013/NLP-Graphs/ -lfi parser.log");
        } catch (MaltChainedException e) {
            e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
        }

        try {
            tagger = new MaxentTagger("/Users/stinky/Work/PAN2013/NLP-Graphs/english-left3words-distsim.tagger");
        } catch (IOException e) {
            e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
        } catch (ClassNotFoundException e) {
            e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
        }
    }

    public static void main(String[] args) {
        SentenceSplitter splitter = new SentenceSplitter();
        for (String fn : args) {
            List<String[]> sentences = splitter.process(new File(fn));

            String new_fn = FilenameUtils.removeExtension(fn) + ".malt";

            splitter.write(new_fn, sentences);
        }
    }

    private void write(String fn, List<String[]> sentences) {
        try {
            BufferedWriter out = new BufferedWriter(new FileWriter(fn));

            for (String[] sentence : sentences) {
                ArrayList<String> words = new ArrayList<String>();

                out.write("<s>\n");

                for (String w : sentence) {
                    out.write(w + "\n");
                }

                out.write("</s>\n");
            }

            out.close();
        } catch (IOException e) {
            e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
        }
    }

    public List<String[]> process(File fn) {
        try {
            logger.info("Processing file: " + fn);

            BufferedReader reader =
                    new BufferedReader(new InputStreamReader(new FileInputStream(fn)));

            DocumentPreprocessor dp = new DocumentPreprocessor(reader);
            TokenizerFactory<CoreLabel> ptbTokenizerFactory =
                    PTBTokenizer.PTBTokenizerFactory.newCoreLabelTokenizerFactory("untokenizable=noneKeep");
            dp.setTokenizerFactory(ptbTokenizerFactory);

            List<String[]> sentences = new ArrayList<String[]>();

            for (List<HasWord> sentence : dp) {
                List<TaggedWord> taggedWords = tagger.tagSentence(sentence);

                String[] parseInput = new String[taggedWords.size()];

                for (int i = 0; i < sentence.size(); i++) {
                    TaggedWord w = taggedWords.get(i);
                    parseInput[i] = String.format("‰d\t%s\t%s\t%s\t%s\t_",
                            i, w.word(), lemmatizer.lemma(w.word(), w.tag()), w.tag(), w.tag());
                }

                try {
                    String[] parse = parser.parseTokens(parseInput);
                    sentences.add(parse);
                } catch (MaltChainedException e) {
                    e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
                }
            }

            logger.info("Length: " + sentences.size());

            return sentences;
        } catch (FileNotFoundException e) {
            e.printStackTrace();  //To change body of catch statement use File | Settings | File Templates.
        }

        return null;
    }
}
