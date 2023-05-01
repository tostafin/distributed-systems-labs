#include <iostream>
#include <memory>
#include <string>

#include <grpcpp/grpcpp.h>

#include "weather.grpc.pb.h"

using grpc::Channel;
using grpc::ClientContext;
using grpc::ClientReader;
using grpc::Status;
using weather::WeatherSubscription;
using weather::SubscriptionRequest;
using weather::SubscriptionResponse;
using weather::WeatherInformation;

class WeatherClient
{
public:
    WeatherClient(std::shared_ptr<Channel> channel) : stub_(WeatherSubscription::NewStub(channel)) {}

    void subscribe()
    {
        // Context for the client. It could be used to convey extra information to
        // the server and/or tweak certain RPC behaviors.
        ClientContext context;

        // Data we are sending to the server.
        SubscriptionRequest request;
        request.add_weatherinformation(WeatherInformation::Temperature);
        request.add_weatherinformation(WeatherInformation::Humidity);

        // Container for the data we expect from the server.
        std::unique_ptr<ClientReader<SubscriptionResponse> > reader{stub_->subscribe(&context, request)};
        SubscriptionResponse subscriptionResponse;
        while (reader->Read(&subscriptionResponse))
        {
            std::cout << "Found country called " << subscriptionResponse.country() << std::endl;
        }

        // The actual RPC.
        Status status = reader->Finish();

        if (status.ok())
        {
            std::cout << "subscribe rpc succeeded." << std::endl;
        }
        else
        {
            std::cout << status.error_code() << ": " << status.error_message() << std::endl;
        }
    }

private:
    std::unique_ptr<WeatherSubscription::Stub> stub_;
};

int main(int argc, char** argv) {
    // Instantiate the client. It requires a channel, out of which the actual RPCs
    // are created. This channel models a connection to an endpoint specified by
    // the argument "--target=" which is the only expected argument.
    // We indicate that the channel isn't authenticated (use of
    // InsecureChannelCredentials()).
    WeatherClient client{grpc::CreateChannel("localhost:50051", grpc::InsecureChannelCredentials())};
    client.subscribe();

    return 0;
}
