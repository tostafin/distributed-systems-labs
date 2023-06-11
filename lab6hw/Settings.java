import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.Arrays;

public class Settings {
    public final static BufferedReader BR = new BufferedReader(new InputStreamReader(System.in));
    public final static String HOST = "localhost";
    public final static ArrayList<String> DELIVERY_TYPES = new ArrayList<>(Arrays.asList("People", "Cargo", "Satellite"));
    public final static String EXCHANGE_NAME = "exchange1";
}
