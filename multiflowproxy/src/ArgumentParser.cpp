#include "ArgumentParser.h"
#include <iostream>
#include <sstream>

ArgumentParser::ArgumentParser() {
}

ArgumentParser::~ArgumentParser() {
}

ProxyConfig ArgumentParser::parse(int argc, char* argv[]) {
    ProxyConfig config;
    
    for (int i = 1; i < argc; ++i) {
        std::string arg = argv[i];
        
if (arg == "--token" && i + 1 < argc) {
            config.token = argv[++i];
        }
        else if (arg == "--validate") {
            config.validate_only = true;
        }
        else if (arg == "--port" && i + 1 < argc) {
            config.port = std::stoi(argv[++i]);
        }
        else if (arg == "--http") {
            config.use_http = true;
        }
        else if (arg == "--https") {
            config.use_https = true;
        }
        else if (arg == "--response" && i + 1 < argc) {
            config.response_message = argv[++i];
        }
        else if (arg == "--cert" && i + 1 < argc) {
            config.cert_path = argv[++i];
        }
        else if (arg == "--workers" && i + 1 < argc) {
            config.workers = std::stoi(argv[++i]);
        }
        else if (arg == "--ulimit" && i + 1 < argc) {
            config.ulimit = std::stoi(argv[++i]);
        }
        else if (arg == "--ssh-only") {
            config.ssh_only = true;
        }
        else if (arg == "--buffer-size" && i + 1 < argc) {
            config.buffer_size = std::stoi(argv[++i]);
        }
        else if (arg == "--ssh-port" && i + 1 < argc) {
            config.ssh_port = std::stoi(argv[++i]);
        }
        else if (arg == "--openvpn-port" && i + 1 < argc) {
            config.openvpn_port = std::stoi(argv[++i]);
        }
        else if (arg == "--v2ray-port" && i + 1 < argc) {
            config.v2ray_port = std::stoi(argv[++i]);
        }
        else if (arg == "--help") {
            printHelp();
            exit(0);
        }
        else if (arg == "--version") {
            printVersion();
            exit(0);
        }
        else {
            std::cerr << "Unknown argument: " << arg << std::endl;
            throw std::invalid_argument("Unknown argument: " + arg);
        }
    }
    
    // Set defaults if neither HTTP nor HTTPS is specified
    if (!config.use_http && !config.use_https) {
        config.use_http = true;
    }
    
    validateConfig(config);
    return config;
}

void ArgumentParser::printHelp() const {
    std::cout << "DTunnel Proxy Server v" << Constants::PROXY_SERVER_VERSION << std::endl;
    std::cout << "Author: " << Constants::PROXY_SERVER_AUTHOR << std::endl;
    std::cout << std::endl;
    std::cout << "Usage: proxy [options]" << std::endl;
    std::cout << std::endl;
    std::cout << "Options:" << std::endl;
    std::cout << "  --token [token]            Your Access Token for Proxy Initialization" << std::endl;
    std::cout << "  --validate                 Combine with --token, it returns success if your token is valid" << std::endl;
    std::cout << "  --port <port>              Specify the listening port (default is " << Constants::DEFAULT_PORT << ")" << std::endl;
    std::cout << "  --http                     Use HTTP" << std::endl;
    std::cout << "  --https                    Use HTTPS" << std::endl;
    std::cout << "  --response <message>       Specify the HTTP response message (default is " << Constants::DEFAULT_HTTP_RESPONSE << ")" << std::endl;
    std::cout << "  --cert <certificate_path>  Specify the path to the certificate file (required for HTTPS)" << std::endl;
    std::cout << "  --workers <num_workers>    Specify the maximum number of workers (default is " << Constants::DEFAULT_WORKERS << ")" << std::endl;
    std::cout << "  --ulimit <limit>           Specify the file limit (default is " << Constants::DEFAULT_ULIMIT << ")" << std::endl;
    std::cout << "  --ssh-only                 Use SSH only (Ignore: OpenVPN and V2ray)" << std::endl;
    std::cout << "  --buffer-size <size>       Specify the buffer size in bytes (default is " << Constants::DEFAULT_BUFFER_SIZE << ")" << std::endl;
    std::cout << "  --ssh-port <port>          Specify the port on which SSH connects (default is " << Constants::DEFAULT_SSH_PORT << ")" << std::endl;
    std::cout << "  --openvpn-port <port>      Specify the port on which OpenVPN connects (default is " << Constants::DEFAULT_OPENVPN_PORT << ")" << std::endl;
    std::cout << "  --v2ray-port <port>        Specify the port on which V2Ray connects (default is " << Constants::DEFAULT_V2RAY_PORT << ")" << std::endl;

}

void ArgumentParser::printVersion() const {
    std::cout << "DTunnel Proxy Server v" << Constants::PROXY_SERVER_VERSION << std::endl;
    std::cout << "Author: " << Constants::PROXY_SERVER_AUTHOR << std::endl;
    std::cout << "Created at: " << Constants::PROXY_SERVER_CREATED_AT << std::endl;
    std::cout << "Identification: " << Constants::PROXY_SERVER_IDENTIFICATION << std::endl;
}

void ArgumentParser::validateConfig(const ProxyConfig& config) const {
    if (!Utils::isValidPort(config.port)) {
        throw std::invalid_argument("Invalid port number: " + std::to_string(config.port));
    }
    
    if (!Utils::isValidPort(config.ssh_port)) {
        throw std::invalid_argument("Invalid SSH port number: " + std::to_string(config.ssh_port));
    }
    
    if (!Utils::isValidPort(config.openvpn_port)) {
        throw std::invalid_argument("Invalid OpenVPN port number: " + std::to_string(config.openvpn_port));
    }
    
    if (!Utils::isValidPort(config.v2ray_port)) {
        throw std::invalid_argument("Invalid V2Ray port number: " + std::to_string(config.v2ray_port));
    }
    
    if (config.use_https && config.cert_path.empty()) {
        throw std::invalid_argument("Error: --cert <certificate_path> is required when using --https.");
    }
    
    if (config.workers <= 0) {
        throw std::invalid_argument("Invalid number of workers: " + std::to_string(config.workers));
    }
    
    if (config.buffer_size <= 0) {
        throw std::invalid_argument("Invalid buffer size: " + std::to_string(config.buffer_size));
    }
    
    if (config.validate_only && config.token.empty()) {
        throw std::invalid_argument("Error: --token <token> is required when using --validate");
    }
}

