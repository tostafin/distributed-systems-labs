import com.rabbitmq.client.*;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
import java.util.concurrent.TimeoutException;

public class Carrier {
    private static String inputDeliveryType(String alreadyPickedDeliveryType) throws IOException {
        do {
            final var deliveryType = Settings.BR.readLine();
            if (deliveryType.equals(alreadyPickedDeliveryType)) {
                System.out.println("You already picked this delivery type. Try again.");
            } else if (Settings.DELIVERY_TYPES.contains(deliveryType)) {
                return deliveryType;
            } else {
                System.out.println("Non-existing delivery type picked. Try again.");
            }
        } while (true);
    }

    public static void main(String[] args) throws IOException, TimeoutException {
        // info
        System.out.println("Carrier running...");
        System.out.println("Pick a name for this carrier:");

        final var carrierName = Settings.BR.readLine();

        System.out.println("Here's a list of three types of deliveries we offer: " + Arrays.toString(Settings.DELIVERY_TYPES.toArray()) + ". You have to pick two of them.");

        System.out.println("Pick the first one:");
        String firstDeliveryType = inputDeliveryType(null);

        System.out.println("Pick the second one:");
        String secondDeliveryType = inputDeliveryType(firstDeliveryType);

        // connection & channel
        final var factory = new ConnectionFactory();
        factory.setHost(Settings.HOST);
        final var connection = factory.newConnection();
        final var channel = connection.createChannel();

        // exchange
        channel.exchangeDeclare(Settings.EXCHANGE_NAME, BuiltinExchangeType.TOPIC);

        // queue & bind
        final var firstQueueName = channel.queueDeclare().getQueue();
        channel.queueBind(firstQueueName, Settings.EXCHANGE_NAME, "*.delivery." + firstDeliveryType);
        System.out.println("Created a queue for the first delivery type: " + firstQueueName);

        final var secondQueueName = channel.queueDeclare().getQueue();
        channel.queueBind(secondQueueName, Settings.EXCHANGE_NAME, "*.delivery." + secondDeliveryType);
        System.out.println("Created a queue for the second delivery type: " + secondQueueName);

        // consumer (message handling)
        final var consumer = new DefaultConsumer(channel) {
            @Override
            public void handleDelivery(String consumerTag, Envelope envelope, AMQP.BasicProperties properties, byte[] body) throws IOException {
                final var message = new String(body, StandardCharsets.UTF_8).split(":");
                System.out.println("Received an order number " + message[0] + " from " + message[1] + " for " + message[2] + ".");
                channel.basicPublish(Settings.EXCHANGE_NAME, carrierName + ".confirmation." + message[1], null, ("Order " + message[0] + " confirmed.").getBytes(StandardCharsets.UTF_8));
                channel.basicAck(envelope.getDeliveryTag(), false);
            }
        };

        // start listening
        System.out.println("Waiting for orders...");
        channel.basicConsume(firstQueueName, false, consumer);
        channel.basicConsume(secondQueueName, false, consumer);
    }
}
