package postagger;

import edu.stanford.nlp.ling.*;
import edu.stanford.nlp.objectbank.TokenizerFactory;
import edu.stanford.nlp.process.DocumentPreprocessor;
import edu.stanford.nlp.process.Morphology;
import edu.stanford.nlp.process.PTBTokenizer;
import edu.stanford.nlp.tagger.maxent.MaxentTagger;
import sentence.NLPSentence;
import org.apache.commons.io.IOUtils;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class PosTagger {

    private MaxentTagger tagger;
    private Morphology lemmatiser;
    private Path rootdir;

    public PosTagger(String posParams, String rootdir) {
        lemmatiser = new Morphology();
        this.rootdir = Paths.get(rootdir);
        try {
            this.tagger = new MaxentTagger(posParams);
        } catch (ClassNotFoundException | IOException e) {
            e.printStackTrace();
        }
    }

    public ParseJob posTagFile(Path file) {

        BufferedReader reader = null;
        try {
            ParseJob parseJob = new ParseJob(file);

            String inputfile = rootdir.toString()+"/"+file.toString();
            reader = new BufferedReader(new InputStreamReader(new FileInputStream(inputfile)));
            DocumentPreprocessor dp = new DocumentPreprocessor(reader);

            //TODO: somehow keep original text? PTBTokenizer documentation mentions invertible flag in options, but how to get original text?

            TokenizerFactory<CoreLabel> ptbTokenizerFactory = PTBTokenizer.PTBTokenizerFactory.newCoreLabelTokenizerFactory("untokenizable=noneKeep");
            dp.setTokenizerFactory(ptbTokenizerFactory);

            for(NLPSentence sentence : getSentences(dp, file)) {
                parseJob.addSentence(sentence);
            }

            return parseJob;
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } finally {
            IOUtils.closeQuietly(reader);
        }
        return null;
    }

    public String[] postagSentence(String sentence) {
        String taggedSentence = tagger.tagString(sentence);

        List<String> tokens = new ArrayList<>();
        int i = 1;
        for(String token : taggedSentence.split(" ")) {
            String[] temp = token.split("_");
            String lemma = lemmatiser.lemma(temp[0], temp[1]);
            tokens.add(i+"\t"+temp[0]+"\t"+lemma+"\t"+temp[1]+"\t"+temp[1]+"\t_");
            i++;
        }

        return tokens.toArray(new String[0]);
    }

    private List<NLPSentence> getSentences(DocumentPreprocessor dp, Path file) {
        /**
         * Retrieves all sentences from a file.
         * Sentences with less than 3 words, and more than 80 words are omitted,
         * as these sentences are most likely wrongly parsed.
         */
        List<NLPSentence> sentences = new ArrayList<>();

        int sentenceNumber = 1;
        for(List<HasWord> words : dp) {
            List<TaggedWord> taggedWords = tagger.tagSentence(words);
            if(taggedWords.size()>3 && taggedWords.size()<80) {
                int start = taggedWords.get(0).beginPosition();

                int end = taggedWords.get(taggedWords.size()-1).endPosition();
                NLPSentence sentence = new NLPSentence(file, sentenceNumber, start, end-start);
                sentence.setPostags(getPosTagString(taggedWords));
                sentences.add(sentence);
                sentenceNumber++;

            }
        }

        return sentences;
    }

    private String[] getPosTagString(List<TaggedWord> taggedWords) {
        List<String> temp = new ArrayList<>();
        int i = 1;
        for (TaggedWord token : taggedWords) {
            WordLemmaTag lemma = lemmatiser.lemmatize(new WordTag(token.word(), token.tag()));

            temp.add(i+"\t"+token.word()+"\t"+lemma.lemma()+"\t"+token.tag()+"\t"+token.tag()+"\t"+"_");
            i++;
        }

        return temp.toArray(new String[0]);
    }
}