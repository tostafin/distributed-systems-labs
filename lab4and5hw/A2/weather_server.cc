#include <iostream>
#include <memory>
#include <string>
#include <stdlib.h>


#include <grpcpp/ext/proto_server_reflection_plugin.h>
#include <grpcpp/grpcpp.h>
#include <grpcpp/health_check_service_interface.h>

#include "weather.grpc.pb.h"

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::ServerWriter;
using grpc::Status;
using weather::WeatherSubscription;
using weather::SubscriptionRequest;
using weather::SubscriptionResponse;

class WeatherImpl final : public WeatherSubscription::Service
{
    Status subscribe(ServerContext* context, const SubscriptionRequest* request,
                     ServerWriter<SubscriptionResponse>* reply) override
    {
        sleep(10);
        return Status::OK;
    }
};

void runServer(const uint16_t port)
{
    std::string serverAddress = "0.0.0.0:" + std::to_string(port);
    WeatherImpl service;

    grpc::EnableDefaultHealthCheckService(true);
    grpc::reflection::InitProtoReflectionServerBuilderPlugin();
    ServerBuilder builder;
    // Listen on the given address without any authentication mechanism.
    builder.AddListeningPort(serverAddress, grpc::InsecureServerCredentials());
    // Register "service" as the instance through which we'll communicate with
    // clients. In this case it corresponds to an *synchronous* service.
    builder.RegisterService(&service);
    // Finally assemble the server.
    std::unique_ptr<Server> server(builder.BuildAndStart());
    std::cout << "Server listening on " << serverAddress << std::endl;

    // Wait for the server to shutdown. Note that some other thread must be
    // responsible for shutting down the server for this call to ever return.
    server->Wait();
}

int main(int argc, char** argv)
{
    runServer(50051);
    return 0;
}
