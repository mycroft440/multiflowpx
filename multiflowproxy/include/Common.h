#ifndef COMMON_H
#define COMMON_H

#include <string>
#include <vector>
#include <memory>
#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <queue>
#include <functional>
#include <atomic>
#include <chrono>
#include <exception>
#include <stdexcept>

// Network includes
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <sys/resource.h>

// OpenSSL includes
#include <openssl/ssl.h>
#include <openssl/err.h>
#include <openssl/crypto.h>

// cURL includes
#include <curl/curl.h>

// Constants
namespace Constants {
    const std::string PROXY_SERVER_AUTHOR = "@DuTra01";
    const std::string PROXY_SERVER_VERSION = "1.2.6";
    const std::string PROXY_SERVER_CREATED_AT = "23/06/2023";
    const std::string PROXY_SERVER_IDENTIFICATION = "PenguinEhisCracked(17/10/23)";
    const std::string API_TOKEN_VALIDATOR = "https://proxy.multiflowpx.com.br/api/v1/token/validate";
    const std::string IP_CHECK_URL = "https://ipv4.icanhazip.com/";
    
    const int DEFAULT_PORT = 8080;
    const int DEFAULT_WORKERS = 4;
    const int DEFAULT_BUFFER_SIZE = 16384; // Aumentado para evitar premature close
    const int DEFAULT_SSH_PORT = 22;
    const int DEFAULT_OPENVPN_PORT = 1194;
    const int DEFAULT_V2RAY_PORT = 10086;
    const int DEFAULT_ULIMIT = 65536;
    
    const std::string DEFAULT_HTTP_RESPONSE = "HTTP/1.1 200 OK\r\n\r\n";
    const std::string WEBSOCKET_UPGRADE_RESPONSE = "HTTP/1.1 101 Switching Protocols\r\n"
                                                   "Upgrade: websocket\r\n"
                                                   "Connection: Upgrade\r\n\r\n";
}

// Utility functions
namespace Utils {
    std::string trim(const std::string& str);
    std::vector<std::string> split(const std::string& str, char delimiter);
    bool isValidPort(int port);
    bool setNonBlocking(int fd);
    std::string getCurrentIP();
}

#endif // COMMON_H
