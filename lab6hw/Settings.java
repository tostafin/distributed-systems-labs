import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.LinkedHashSet;
import java.util.Set;

public class Settings {
    public final static BufferedReader BR = new BufferedReader(new InputStreamReader(System.in));
    public final static String HOST = "localhost";
    public final static LinkedHashSet<String> DELIVERY_TYPES = new LinkedHashSet<>(Set.of("People", "Cargo", "Satellite"));
    public final static String EXCHANGE_NAME = "exchange1";
}
