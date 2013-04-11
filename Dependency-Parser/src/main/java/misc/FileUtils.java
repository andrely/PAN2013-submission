package misc;

import org.apache.commons.io.IOUtils;
import org.json.JSONObject;
import sun.reflect.generics.reflectiveObjects.NotImplementedException;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

public class FileUtils {

    public static void writeToFile(String file, JSONObject json) {
        createParentFolders(file);

        FileWriter fw = null;
        try {
            fw = new FileWriter(file);
            fw.write(json.toString());
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            IOUtils.closeQuietly(fw);
        }
    }

    public static void createParentFolders(String filename) {
        File f = new File(filename);
        f.mkdirs();
    }

    public static List<Path> getFiles(String dir) {
        /**
         * Returns a list of file strings relative to baseDir
         * Example input: dir: /home/data/file.txt, baseDir: /home/
         * Example output: [data/file.txt]
         */
        Path path = Paths.get(dir);
        return getFiles(path, path);
    }

    private static List<Path> getFiles(Path dir, Path baseDir) {
        List<Path> files = new ArrayList<>();

        for (File file : getFiles(dir.toFile())) {
            if(file.isFile()) {
                files.add(baseDir.relativize(file.toPath()));
            }else if(file.isDirectory()) {
                files.addAll(getFiles(file.toPath(), baseDir));
            }
        }
        return files;
    }

    private static File[] getFiles(File dir) {
        return dir.listFiles();
    }
}
