package dependencyparser;

import misc.FileUtils;
import sentence.NLPSentence;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.maltparser.MaltParserService;
import org.maltparser.core.exception.MaltChainedException;
import postagger.ParseJob;

import java.nio.file.Path;
import java.nio.file.Paths;


public class DependencyParser {

    private MaltParserService maltService;
    private Path outdir;

    public DependencyParser(String maltParams, String outdir) {
        this.outdir = Paths.get(outdir);
        try {
            this.maltService = new MaltParserService();
            maltService.initializeParserModel(maltParams);
        } catch (MaltChainedException e) {
            e.printStackTrace();
        }
    }

    public void dependencyParse(ParseJob job) throws JSONException {
        for(NLPSentence sentence : job.getSentences()) {
            String outfile = outdir.toString()+"/"+sentence.getFile().toString();
            FileUtils.writeToFile(outfile, parseSentence(sentence));
        }
    }

    public JSONObject parseSentence(NLPSentence sentence) throws JSONException {
        JSONObject obj = new JSONObject();
        try {
            obj.put("id", sentence.getFilename()+"-"+sentence.getNumber());
            obj.put("filename", sentence.getFilename());
            obj.put("sentenceNumber", sentence.getNumber());
            obj.put("offset", sentence.getStart());
            obj.put("length", sentence.getLength());
            String[] parsedSentence = maltService.parseTokens(sentence.getPostags());

            JSONArray tokenList = new JSONArray();
            for(String parsedToken : parsedSentence) {
                tokenList.put(getToken(parsedToken));
            }

            obj.put("tokens", tokenList);
        } catch (MaltChainedException e) {
            e.printStackTrace();
        }

        return obj;
    }


    public JSONObject getToken(String parsedToken) throws JSONException {
        JSONObject obj = new JSONObject();
        String[] token = parsedToken.split("\t");
        obj.put("id", token[0]);
        obj.put("word", token[1]);
        obj.put("lemma", token[2]);
        obj.put("pos", token[4]);
        obj.put("rel", token[6]);
        obj.put("deprel", token[7]);

        return obj;
    }
}
