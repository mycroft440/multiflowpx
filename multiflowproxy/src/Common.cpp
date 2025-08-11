#include "Common.h"
#include <algorithm>
#include <sstream>
#include <curl/curl.h>

namespace Utils {

std::string trim(const std::string& str) {
    size_t start = str.find_first_not_of(" \t\r\n");
    if (start == std::string::npos) {
        return "";
    }
    size_t end = str.find_last_not_of(" \t\r\n");
    return str.substr(start, end - start + 1);
}

std::vector<std::string> split(const std::string& str, char delimiter) {
    std::vector<std::string> tokens;
    std::stringstream ss(str);
    std::string token;
    
    while (std::getline(ss, token, delimiter)) {
        tokens.push_back(token);
    }
    
    return tokens;
}

bool isValidPort(int port) {
    return port > 0 && port <= 65535;
}

bool setNonBlocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    if (flags == -1) {
        return false;
    }
    
    flags |= O_NONBLOCK;
    return fcntl(fd, F_SETFL, flags) != -1;
}

std::string getCurrentIP() {
    CURL* curl = curl_easy_init();
    if (!curl) {
        return "127.0.0.1";
    }
    
    std::string response_data;
    
    curl_easy_setopt(curl, CURLOPT_URL, Constants::IP_CHECK_URL.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, [](void* contents, size_t size, size_t nmemb, std::string* response) -> size_t {
        size_t total_size = size * nmemb;
        response->append(static_cast<char*>(contents), total_size);
        return total_size;
    });
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_data);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 10L);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
    
    CURLcode res = curl_easy_perform(curl);
    curl_easy_cleanup(curl);
    
    if (res == CURLE_OK) {
        return trim(response_data);
    }
    
    return "127.0.0.1";
}

} // namespace Utils

