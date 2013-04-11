package dependencyparser;

import application.App;
import org.json.JSONException;
import postagger.ParseJob;

import java.util.concurrent.BlockingQueue;


public class DependencyParserWorker extends Thread{
    private final BlockingQueue<ParseJob> queue;
    private App.PreProcessor preprocessor;
    private boolean running;
    private DependencyParser parser;

    public DependencyParserWorker(String maltParams, String outdir, BlockingQueue<ParseJob> queue, App.PreProcessor preprocessor) {
        this.queue = queue;
        this.preprocessor = preprocessor;
        this.parser = new DependencyParser(maltParams, outdir);
    }

    @Override
    public void run() {
        running = true;
        while(running) {
            try {
                ParseJob job = queue.take();
                try {
                    parser.dependencyParse(job);
                    preprocessor.parseJobDone("parse queue: " + queue.size());
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            } catch (InterruptedException | NullPointerException e) {
                e.printStackTrace();
                running = false;
                return;
            }
        }
        System.out.println("Stopping "+Thread.currentThread().getName()+": all files are parsed.");
    }

    public synchronized void kill() {
        running = false;
    }
}
