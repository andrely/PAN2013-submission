package sentence;

import org.json.JSONException;
import org.json.JSONObject;

import java.nio.file.Path;
import java.util.List;


public class NLPSentence {

    protected int number, start, length;
    protected String text;
    private Path file;
    private String[] postags;
    protected List<WordToken> words;

    public NLPSentence(Path file, int number, int start, int length, List<WordToken> words, String[] postags) {
        this(file, number, start, length);
        this.postags = postags;
    }

    public NLPSentence(Path file, int number, int start, int length, List<WordToken> words) {
        this(file, number, start, length);
        this.words = words;
    }

    public NLPSentence(Path file, int number, int start, int length) {
        this.file = file;
        this.number = number;
        this.start = start;
        this.length = length;
    }

    public int getLength() {
        return length;
    }

    public int getNumber() {
        return number;
    }

    public int getStart() {
        return start;
    }

    public String[] getPostags() {
        return postags;
    }

    public void setPostags(String[] postags) {
        this.postags = postags;
    }

    public List<WordToken> getWords() {
        return words;
    }

    public void addWord(WordToken word) {
        words.add(word);
    }

    public Path getFile() {
        return file;
    }

    public void setFile(Path file) {
        this.file = file;
    }

    public String getFilename() {
        return file.getFileName().toString();
    }

    public JSONObject toJson() throws JSONException {
        JSONObject jsonSentence = new JSONObject();
        jsonSentence.put("sentenceNumber", number);
        jsonSentence.put("offset", start);
        jsonSentence.put("length", getLength());

        return jsonSentence;
    }
}
