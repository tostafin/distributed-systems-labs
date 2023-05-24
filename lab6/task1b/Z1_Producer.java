import com.rabbitmq.client.Channel;
import com.rabbitmq.client.Connection;
import com.rabbitmq.client.ConnectionFactory;

import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Z1_Producer {

    public static void main(String[] argv) throws Exception {

        // info
        System.out.println("Z1 PRODUCER");

        // connection & channel
        ConnectionFactory factory = new ConnectionFactory();
        factory.setHost("localhost");
        Connection connection = factory.newConnection();
        Channel channel = connection.createChannel();

        // queue
        String QUEUE_NAME = "queue1";
        channel.queueDeclare(QUEUE_NAME, false, false, false, null);        

        // producer (publish msg)
//        String message = "Hello world!";
//        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
//        var message = br.readLine();
//
//        channel.basicPublish("", QUEUE_NAME, null, message.getBytes());
//        System.out.println("Sent: " + message);

        for (int i = 0; i < 5; ++i) {
            channel.basicPublish("", QUEUE_NAME, null, "1".getBytes());
            channel.basicPublish("", QUEUE_NAME, null, "5".getBytes());
        }

        // close
        channel.close();
        connection.close();
    }
}
