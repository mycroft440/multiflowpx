#ifndef ARGUMENT_PARSER_H
#define ARGUMENT_PARSER_H

#include "Common.h"

struct ProxyConfig {
    std::string token;
    bool validate_only = false;
    int port = Constants::DEFAULT_PORT;
    bool use_http = false;
    bool use_https = false;
    std::string response_message = Constants::DEFAULT_HTTP_RESPONSE;
    std::string cert_path;
    int workers = Constants::DEFAULT_WORKERS;
    int ulimit = Constants::DEFAULT_ULIMIT;
    bool ssh_only = false;
    int buffer_size = Constants::DEFAULT_BUFFER_SIZE;
    int ssh_port = Constants::DEFAULT_SSH_PORT;
    int openvpn_port = Constants::DEFAULT_OPENVPN_PORT;
    int v2ray_port = Constants::DEFAULT_V2RAY_PORT;
    bool show_help = false;
    std::string remote_host = "127.0.0.1"; // Nova opção para flexibilidade
};

class ArgumentParser {
public:
    ArgumentParser();
    ~ArgumentParser();
    
    ProxyConfig parse(int argc, char* argv[]);
    void printHelp() const;
    void printVersion() const;
    
private:
    void validateConfig(const ProxyConfig& config) const;
};

#endif // ARGUMENT_PARSER_H
