import com.rabbitmq.client.*;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.concurrent.TimeoutException;

class OrderConfirmation extends Thread {
    private final Channel channel;
    private final String queueName;

    OrderConfirmation(Channel channel, String queueName) {
        this.channel = channel;
        this.queueName = queueName;
    }

    @Override
    public void run() {
        // consumer (message handling)
        final var consumer = new DefaultConsumer(channel) {
            @Override
            public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties, byte[] body) throws IOException {
                System.out.println(new String(body, StandardCharsets.UTF_8));
                channel.basicAck(envelope.getDeliveryTag(), false);
            }
        };

        try {
            channel.basicConsume(queueName, false, consumer);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }
}

public class Agency {
    public static void main(String[] args) throws IOException, TimeoutException {
        // info
        System.out.println("Agency running...");

        System.out.println("Pick a name for this agency:");
        final var agencyName = Settings.BR.readLine();

        // connection & channel
        final var factory = new ConnectionFactory();
        factory.setHost(Settings.HOST);
        final var connection = factory.newConnection();
        final var channel = connection.createChannel();

        // exchange
        channel.exchangeDeclare(Settings.EXCHANGE_NAME, BuiltinExchangeType.TOPIC);

        // a queue for orders' confirmations
        final var queueName = channel.queueDeclare().getQueue();
        channel.queueBind(queueName, Settings.EXCHANGE_NAME, "*.confirmation." + agencyName);
        System.out.println("Created a queue for orders' confirmations: " + queueName);
        new OrderConfirmation(channel, queueName).start();

        System.out.println("Here's a list of three types of deliveries we offer: " + Arrays.toString(Settings.DELIVERY_TYPES.toArray()));
        var orderNo = 1;
        while (true) {
            // read msg
            System.out.println("Pick a delivery to order it:");
            final var deliveryType = Settings.BR.readLine();
            if (deliveryType.equals("exit")) {
                break;
            }
            if (!Settings.DELIVERY_TYPES.contains(deliveryType)) {
                System.out.println("Non-existing delivery type picked. Try again.");
                continue;
            }

            // publish
            channel.basicPublish(Settings.EXCHANGE_NAME, agencyName + ".delivery." + deliveryType, null, (orderNo + ":" + agencyName + ":" + deliveryType).getBytes(StandardCharsets.UTF_8));
            System.out.println("You ordered: " + deliveryType);
            ++orderNo;
        }
    }
}
