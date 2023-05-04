#include <iostream>
#include <memory>
#include <string>
#include <optional>
#include <charconv>
#include <stdexcept>

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

    void subscribe(const std::optional<int32_t>& minTemperature, const std::optional<int32_t>& maxTemperature,
                   const std::optional<uint32_t>& minHumidity, const std::optional<uint32_t>& maxHumidity)
    {
        // Context for the client.
        ClientContext context;
        context.set_wait_for_ready(true);

        // Data we are sending to the server.
        SubscriptionRequest subscriptionRequest;
        if (minTemperature.has_value() || maxTemperature.has_value())
        {
            subscriptionRequest.add_weather_information(WeatherInformation::Temperature);
        }
        if (minHumidity.has_value() || maxHumidity.has_value())
        {
            subscriptionRequest.add_weather_information(WeatherInformation::Humidity);
        }

        if (minTemperature.has_value())
        {
            subscriptionRequest.set_min_temperature(*minTemperature);
        }
        if (maxTemperature.has_value())
        {
            subscriptionRequest.set_max_temperature(*maxTemperature);
        }
        if (minHumidity.has_value())
        {
            subscriptionRequest.set_min_humidity(*minHumidity);
        }
        if (maxHumidity.has_value())
        {
            subscriptionRequest.set_max_humidity(*maxHumidity);
        }

        // Container for the data we expect from the server.
        std::unique_ptr<ClientReader<SubscriptionResponse>> reader{stub_->subscribe(&context, subscriptionRequest)};
        SubscriptionResponse subscriptionResponse;
        while (reader->Read(&subscriptionResponse))
        {
            std::cout << "Found a country named " << subscriptionResponse.country()
            << " with temperature " << subscriptionResponse.temperature() << "°C and humidity "
            << subscriptionResponse.humidity() << "%.\n";
        }

        // The actual RPC.
        Status status = reader->Finish();

        if (status.ok())
        {
            std::cout << "subscribe rpc succeeded." << std::endl;
        }
        else
        {
            std::cout << "Error code " << status.error_code() << ": " << status.error_message() << std::endl;
        }
    }

private:
    std::unique_ptr<WeatherSubscription::Stub> stub_;
};

template<typename T>
T parseArgument(const std::string_view& argValue, const std::string& option)
{
    T value;
    auto [ptr, ec] = std::from_chars(argValue.data(), argValue.data() + argValue.size(), value);
    if (ec == std::errc::invalid_argument || ptr[0] != '\0')
    {
        throw std::invalid_argument(std::string{"The value in the option "} + option.data() + " is not an integer.");
    }
    else if (ec == std::errc::result_out_of_range)
    {
        throw std::out_of_range(std::string{"The value in the option "} + option.data() + " is too large.");
    }
    
    return value;
}

int main(int argc, char** argv)
{
    const auto& minTemperatureOption = std::string{"--min-temperature"};
    const auto& maxTemperatureOption = std::string{"--max-temperature"};
    const auto& minHumidityOption = std::string{"--min-humidity"};
    const auto& maxHumidityOption = std::string{"--max-humidity"};
    if (argc < 2)
    {
        std::cout << "Usage: " << argv[0] << " [OPTIONS]\n";
        std::cout << "Options:\n";
        std::cout << "\t" << minTemperatureOption << "=[value]: Find a country with minimum temperature of [value].\n";
        std::cout << "\t" << maxTemperatureOption << "=[value]: Find a country with maximum temperature of [value].\n";
        std::cout << "\t" << minHumidityOption << "=[value]: Find a country with minimum humidity of [value].\n";
        std::cout << "\t" << maxHumidityOption << "=[value]: Find a country with maximum humidity of [value].\n";
        return EXIT_FAILURE;
    }
    std::optional<int32_t> minTemperature;
    std::optional<int32_t> maxTemperature;
    std::optional<uint32_t> minHumidity;
    std::optional<uint32_t> maxHumidity;

    for (auto i = 1; i < argc; ++i)
    {
        const auto& arg = std::string_view(argv[i]);
        try
        {
            if (!arg.compare(0, minTemperatureOption.size(), minTemperatureOption))
            {
                minTemperature = parseArgument<int32_t>(arg.substr(minTemperatureOption.size() + 1), minTemperatureOption);
            }
            else if (!arg.compare(0, maxTemperatureOption.size(), maxTemperatureOption))
            {
                maxTemperature = parseArgument<int32_t>(arg.substr(maxTemperatureOption.size() + 1), maxTemperatureOption);
            }
            else if (!arg.compare(0, minHumidityOption.size(), minHumidityOption))
            {
                minHumidity = parseArgument<uint32_t>(arg.substr(minHumidityOption.size() + 1), minHumidityOption);
            }
            else if (!arg.compare(0, maxHumidityOption.size(), maxHumidityOption))
            {
                maxHumidity = parseArgument<uint32_t>(arg.substr(maxHumidityOption.size() + 1), maxHumidityOption);
            }
            else
            {
                std::cout << "Unkown argument " << arg << ".\n";
                return EXIT_FAILURE;
            }   
        }
        catch (const std::exception& exception)
        {
            std::cout << exception.what() << "\n";
            return EXIT_FAILURE;
        }
        
    }

    // We ping every 10 seconds to persist NAT/PAT table entries.
    grpc::ChannelArguments channelArguments;
    channelArguments.SetInt(GRPC_ARG_KEEPALIVE_TIME_MS, 10000);
    channelArguments.SetInt(GRPC_ARG_KEEPALIVE_TIMEOUT_MS, 5000);
    channelArguments.SetInt(GRPC_ARG_KEEPALIVE_PERMIT_WITHOUT_CALLS, 1);
    const auto& channel = grpc::CreateCustomChannel("localhost:50051", grpc::InsecureChannelCredentials(), channelArguments);
    WeatherClient client{channel};
    client.subscribe(minTemperature, maxTemperature, minHumidity, maxHumidity);

    return 0;
}
