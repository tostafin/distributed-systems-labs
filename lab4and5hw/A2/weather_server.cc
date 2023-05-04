#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <random>
#include <algorithm>
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
using grpc::StatusCode;
using weather::WeatherSubscription;
using weather::SubscriptionRequest;
using weather::SubscriptionResponse;
using weather::WeatherInformation;

class WeatherImpl final : public WeatherSubscription::Service
{
public:
    WeatherImpl()
    {
        auto weatherInPoland = SubscriptionResponse();
        weatherInPoland.set_country("Poland");
        weatherInPoland.set_temperature(20);
        weatherInPoland.set_humidity(60);

        auto weatherInGermany = SubscriptionResponse();
        weatherInGermany.set_country("Germany");
        weatherInGermany.set_temperature(10);
        weatherInGermany.set_humidity(90);

        auto weatherInSpain = SubscriptionResponse();
        weatherInSpain.set_country("Spain");
        weatherInSpain.set_temperature(35);
        weatherInSpain.set_humidity(20);

        subscriptionResponses_ = {
            weatherInPoland,
            weatherInGermany,
            weatherInSpain
        };
    }

    Status subscribe(ServerContext* context, const SubscriptionRequest* request,
                     ServerWriter<SubscriptionResponse>* response) override
    {
        std::random_device dev;
        std::mt19937 rng(dev());
        std::uniform_int_distribution<std::mt19937::result_type> dist10(1, 5);
        for (const auto& responseWeatherInformation : subscriptionResponses_)
        {
            const auto requestWeatherInformationTypes = request->weather_information().size();
            if (requestWeatherInformationTypes == 0)
            {
                return Status{StatusCode::INVALID_ARGUMENT,
                    "You must set at least one of the weather information types."
                };
            }
            auto satisfiedRequestWeatherInformationTypes = decltype(requestWeatherInformationTypes){0};
            
            for (const auto& requestWeatherInformationType : request->weather_information())
            {
                if (requestWeatherInformationType == WeatherInformation::Temperature)
                {
                    if (request->has_min_temperature() && request->has_max_temperature())
                    {
                        if (request->min_temperature() <= responseWeatherInformation.temperature() &&
                            request->max_temperature() >= responseWeatherInformation.temperature())
                        {
                            ++satisfiedRequestWeatherInformationTypes;
                        }
                        else
                        {
                            break;
                        }
                    }
                    else if (request->has_min_temperature())
                    {
                        if (request->min_temperature() <= responseWeatherInformation.temperature())
                        {
                            ++satisfiedRequestWeatherInformationTypes;
                        }
                        else
                        {
                            break;
                        }
                    }
                    else if (request->has_max_temperature())
                    {
                        if (request->max_temperature() >= responseWeatherInformation.temperature())
                        {
                            ++satisfiedRequestWeatherInformationTypes;
                        }
                        else
                        {
                            break;
                        }
                    }
                    else
                    {
                        return Status{StatusCode::INVALID_ARGUMENT,
                            "You must set at least one of the following: 'min_temperature', 'max_temperature'."
                        };
                    }
                }

                else if (requestWeatherInformationType == WeatherInformation::Humidity)
                {
                    if (request->has_min_humidity() && request->has_max_humidity())
                    {
                        if (request->min_humidity() <= responseWeatherInformation.humidity() &&
                            request->max_humidity() >= responseWeatherInformation.humidity())
                        {
                            ++satisfiedRequestWeatherInformationTypes;
                        }
                        else
                        {
                            break;
                        }
                    }
                    else if (request->has_min_humidity())
                    {
                        if (request->min_humidity() <= responseWeatherInformation.humidity())
                        {
                            ++satisfiedRequestWeatherInformationTypes;
                        }
                        else
                        {
                            break;
                        }
                    }
                    else if (request->has_max_humidity())
                    {
                        if (request->max_humidity() >= responseWeatherInformation.humidity())
                        {
                            ++satisfiedRequestWeatherInformationTypes;
                        }
                        else
                        {
                            break;
                        }
                    }
                    else
                    {
                        return Status{StatusCode::INVALID_ARGUMENT,
                            "You must set at least one of the following: 'min_humidity', 'max_humidity'."
                        };
                    }
                }
            }

            // Simulate response for the server
            sleep(dist10(rng));

            if (requestWeatherInformationTypes == satisfiedRequestWeatherInformationTypes)
            {
                response->Write(responseWeatherInformation);
            }
        }
        return Status::OK;
    }

private:
    std::vector<SubscriptionResponse> subscriptionResponses_;
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
