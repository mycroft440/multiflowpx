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
        else if (arg == "--remote-host" && i + 1 < argc) { // Nova
            config.remote_host = argv[++i];
        }
        else if (arg == "--help") {
            printHelp();
            exit(0);
        }
    }
    validateConfig(config);
    return config;
}

void ArgumentParser::printHelp() const {
    // ... (mantenha o original, adicione linha para --remote-host)
    std::cout << "  --remote-host <host>        Specify the remote host for connections (default is 127.0.0.1)" << std::endl;
    // ... resto truncado, adicione ao seu
}

void ArgumentParser::printVersion() const {
    // Mantenha original
}

void ArgumentParser::validateConfig(const ProxyConfig& config) const {
    // Mantenha original, adicione:
    if (config.remote_host.empty()) {
        throw std::invalid_argument("Invalid remote host");
    }
    // ... resto
}
