package application;

import dependencyparser.DependencyParserWorker;
import misc.ConfigService;
import misc.FileUtils;
import misc.ProgressPrinter;
import postagger.ParseJob;
import postagger.PosTagWorker;

import java.nio.file.Path;
import java.util.List;
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;

public class App {
    public static void main(String[] args) {
        PreProcessor parser = new PreProcessor(new ConfigService());
        parser.start();
    }


    public static class PreProcessor {

        private BlockingQueue<Path> posTagQueue;

        private LinkedBlockingQueue<ParseJob> parseQueue;
        private ConfigService cs;
        private DependencyParserWorker[] dependencyParserThreads;
        private PosTagWorker[] posTagThreads;
        private int dependencyParserCount, posTagCount;
        private ProgressPrinter progressPrinter;


        public PreProcessor(ConfigService cs) {
            this.cs = cs;
        }


        public void start() {
            List<Path> files = FileUtils.getFiles(cs.getDataDir());
            progressPrinter = new ProgressPrinter(files.size());
            addFilesToParseQueue(files);
            initParsers();
        }

        private void addFilesToParseQueue(List<Path> files) {
            posTagQueue = new LinkedBlockingQueue<>();
            for (Path file : files) {
                try {
                    posTagQueue.put(file);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }

        private void initParsers() {

            posTagCount = cs.getPOSTaggerThreadCount();
            parseQueue = new LinkedBlockingQueue<>(15);
            posTagThreads = new PosTagWorker[posTagCount];

            for (int i = 0; i < posTagCount; i++) {
                posTagThreads[i] = new PosTagWorker(cs.getPOSTaggerParams(), cs.getDataDir(), posTagQueue, parseQueue);
                posTagThreads[i].setName("Postag-thread-"+i);
                posTagThreads[i].start();
            }

            dependencyParserCount = cs.getMaltParserThreadCount();

            dependencyParserThreads = new DependencyParserWorker[dependencyParserCount];
            for (int i = 0; i < dependencyParserCount; i++) {
                dependencyParserThreads[i] =  new DependencyParserWorker(cs.getMaltParams(), cs.getOutDir(), parseQueue, this);
                dependencyParserThreads[i].setName("Dependency-postagger-"+i);
                dependencyParserThreads[i].start();
            }
        }

        public ProgressPrinter getProgressPrinter() {
            return progressPrinter;
        }

        public void parseJobDone(String text) {
            progressPrinter.printProgressbar(text);

            if(progressPrinter.isDone()) {
                for(DependencyParserWorker thread : dependencyParserThreads) {
                    thread.kill();
                }

                System.out.println("Preprocessing done. Exiting)");
            }
        }

    }


}
