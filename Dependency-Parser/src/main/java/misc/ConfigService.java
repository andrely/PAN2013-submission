package misc;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.Properties;

import org.apache.commons.io.IOUtils;


public class ConfigService {

    private Properties configFile;
    private InputStream is;

    public ConfigService() {
        configFile = new Properties();
        try{
            is = new FileInputStream("app.properties");
            configFile.load(is);
            is.close();
        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            IOUtils.closeQuietly(is);
        }
    }

    public String getOutDir() {
        return configFile.getProperty("OUT_DIR");
    }

    public String getDataDir() {
        return configFile.getProperty("DATA_DIR");
    }

    public String getMaltParams() {
        return configFile.getProperty("MALT_PARAMS");
    }

    public String getPOSTaggerParams() {
        return configFile.getProperty("POSTAGGER_PARAMS");
    }

    public int getPOSTaggerThreadCount() {
        return Integer.parseInt(configFile.getProperty("POSTAGGER_THREADS"));
    }

    public int getMaltParserThreadCount() {
        return Integer.parseInt(configFile.getProperty("MALTPARSER_THREADS"));
    }
}
