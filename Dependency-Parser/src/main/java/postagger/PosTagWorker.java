package postagger;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.TimeUnit;


public class PosTagWorker extends Thread {

    private final BlockingQueue<ParseJob> queue;
    private BlockingQueue<Path> unparsedFiles;
    private PosTagger parser;


    public PosTagWorker(String posParams, String rootDir, BlockingQueue<Path> unparsedFiles, BlockingQueue<ParseJob> queue){
        this.queue = queue;
        this.unparsedFiles = unparsedFiles;
        this.parser = new PosTagger(posParams, rootDir);
    }

    @Override
    public void run() {
        boolean running = true;
        while(running) {
            try {
                Path file = unparsedFiles.poll(20, TimeUnit.SECONDS);
                if(file != null) {
                    ParseJob parseJob = parser.posTagFile(file);
                    queue.put(parseJob);
                }else {
                    running = false;
                }
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }

        System.out.println("stopping postagger thread: "+Thread.currentThread().getName());
    }
}
