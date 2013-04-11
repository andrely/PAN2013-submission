package postagger;

import sentence.NLPSentence;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class ParseJob {

    private List<NLPSentence> sentences;
    private Path file;
    private boolean isLastInQueue;

    public ParseJob(Path file) {
        this.file = file;
        this.sentences = new ArrayList<>();
    }


    public String getFilename() {
        return file.getFileName().toString();
    }

    public Path getFile() {
        return file;
    }

    public void setFile(Path file) {
        this.file = file;
    }

    public List<NLPSentence> getSentences() {
        return sentences;
    }

    public void addSentence(NLPSentence sentence) {
        sentences.add(sentence);
    }

    public boolean isLastInQueue() {
        return isLastInQueue;
    }

    public void setLastInQueue(boolean lastInQueue) {
        isLastInQueue = lastInQueue;
    }
}
