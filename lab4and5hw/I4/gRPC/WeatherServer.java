package io.grpc.examples.weather;

import io.grpc.*;
import io.grpc.stub.StreamObserver;

import java.io.IOException;
import java.util.*;
import java.util.concurrent.TimeUnit;
import java.util.logging.Logger;
import java.util.concurrent.ThreadLocalRandom;



public class WeatherServer {
    private static final Logger logger = Logger.getLogger(WeatherServer.class.getName());

    private final int port;
    private final Server server;

    /** Create a Weather server using serverBuilder as a base and features as data. */
    public WeatherServer(int port) {
        ServerBuilder<?> serverBuilder = Grpc.newServerBuilderForPort(port, InsecureServerCredentials.create());
        this.port = port;
        server = serverBuilder.addService(new WeatherService(new LinkedList<>()))
                .build();
    }

    /** Start serving requests. */
    public void start() throws IOException {
        server.start();
        logger.info("Server started, listening on " + port);
        Runtime.getRuntime().addShutdownHook(new Thread(() -> {
            // Use stderr here since the logger may have been reset by its JVM shutdown hook.
            System.err.println("*** shutting down gRPC server since JVM is shutting down");
            try {
                WeatherServer.this.stop();
            } catch (InterruptedException e) {
                e.printStackTrace(System.err);
            }
            System.err.println("*** server shut down");
        }));
    }

    /** Stop serving requests and shutdown resources. */
    public void stop() throws InterruptedException {
        if (server != null) {
            server.shutdown().awaitTermination(30, TimeUnit.SECONDS);
        }
    }

    /**
     * Await termination on the main thread since the grpc library uses daemon threads.
     */
    private void blockUntilShutdown() throws InterruptedException {
        if (server != null) {
            server.awaitTermination();
        }
    }

    /**
     * Main method.  This comment makes the linter happy.
     */
    public static void main(String[] args) throws Exception {
        WeatherServer server = new WeatherServer(50051);
        server.start();
        server.blockUntilShutdown();
    }

    private static class WeatherService extends WeatherSubscriptionGrpc.WeatherSubscriptionImplBase {
        private final Collection<SubscriptionResponse> subscriptionResponses;

        WeatherService(Collection<SubscriptionResponse> subscriptionResponses) {
            this.subscriptionResponses = subscriptionResponses;
            SubscriptionResponse weatherInPoland = SubscriptionResponse.newBuilder().setCountry("Poland").setHumidity(60).build();
            SubscriptionResponse weatherInGermany = SubscriptionResponse.newBuilder().setCountry("Germany").setTemperature(10).build();
            SubscriptionResponse weatherInSpain = SubscriptionResponse.newBuilder().setTemperature(35).setHumidity(20).build();
            subscriptionResponses.add(weatherInPoland);
            subscriptionResponses.add(weatherInGermany);
            subscriptionResponses.add(weatherInSpain);
        }

        @Override
        public void subscribe(SubscriptionRequest request, StreamObserver<SubscriptionResponse> response) {
            for (SubscriptionResponse responseWeatherInformation : subscriptionResponses) {
                int requestWeatherInformationTypes = request.getWeatherInformationCount();
                if (requestWeatherInformationTypes == 0) {
                    response.onError(Status.INVALID_ARGUMENT.withDescription("You must set at least one of the weather information types.").asException());
                }
                int satisfiedRequestWeatherInformationTypes = 0;
                for (WeatherInformation requestWeatherInformationType : request.getWeatherInformationList()) {
                    if (requestWeatherInformationType == WeatherInformation.Temperature) {
                        if (request.hasMinTemperature() && request.hasMaxTemperature()) {
                            if (request.getMinTemperature() <= responseWeatherInformation.getTemperature() &&
                                request.getMaxTemperature() >= responseWeatherInformation.getTemperature()) {
                                ++satisfiedRequestWeatherInformationTypes;
                            } else {
                                break;
                            }
                        } else if (request.hasMinTemperature()) {
                            if (request.getMinTemperature() <= responseWeatherInformation.getTemperature()) {
                                ++satisfiedRequestWeatherInformationTypes;
                            } else {
                                break;
                            }
                        } else if (request.hasMaxTemperature()) {
                            if (request.getMaxTemperature() >= responseWeatherInformation.getTemperature()) {
                                ++satisfiedRequestWeatherInformationTypes;
                            } else {
                                break;
                            }
                        } else {
                            response.onError(Status.INVALID_ARGUMENT.withDescription("You must set at least one of the following: 'min_temperature', 'max_temperature'.").asException());
                        }
                    } else if (requestWeatherInformationType == WeatherInformation.Humidity) {
                        if (request.hasMinHumidity() && request.hasMaxHumidity()) {
                            if (request.getMinHumidity() <= responseWeatherInformation.getHumidity() &&
                                request.getMaxHumidity() >= responseWeatherInformation.getHumidity()) {
                                ++satisfiedRequestWeatherInformationTypes;
                            } else {
                                break;
                            }
                        } else if (request.hasMinTemperature()) {
                            if (request.getMinHumidity() <= responseWeatherInformation.getHumidity()) {
                                ++satisfiedRequestWeatherInformationTypes;
                            } else {
                                break;
                            }
                        } else if (request.hasMaxHumidity()) {
                            if (request.getMaxHumidity() >= responseWeatherInformation.getHumidity()) {
                                ++satisfiedRequestWeatherInformationTypes;
                            } else {
                                break;
                            }
                        } else {
                            response.onError(Status.INVALID_ARGUMENT.withDescription("You must set at least one of the following: 'min_humidity', 'max_humidity'.").asException());
                        }
                    }
                }
                if (requestWeatherInformationTypes == satisfiedRequestWeatherInformationTypes) {
                    // Simulate server response
                    try {
                        Thread.sleep(ThreadLocalRandom.current().nextInt(5_000, 10_000 + 1));
                        response.onNext(responseWeatherInformation);
                    } catch (InterruptedException exception) {
                        exception.printStackTrace();
                    }
                }

            }
            response.onCompleted();
        }
    }
}
