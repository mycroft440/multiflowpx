#include "ResponseParser.h"
#include <algorithm>

ResponseParser::ResponseParser(const std::string& default_response) 
    : default_response_(default_response) {
}

ResponseParser::~ResponseParser() {
}

std::string ResponseParser::parseResponse(const std::string& request) {
    if (isWebSocketUpgrade(request)) {
        return Constants::WEBSOCKET_UPGRADE_RESPONSE;
    }
    
    return default_response_;
}

bool ResponseParser::isWebSocketUpgrade(const std::string& request) {
    std::string headers = extractHeaders(request);
    
    return hasHeader(headers, "upgrade", "websocket") ||
           hasHeader(headers, "upgrade", "ws");
}

void ResponseParser::setDefaultResponse(const std::string& response) {
    default_response_ = response;
}

std::string ResponseParser::getDefaultResponse() const {
    return default_response_;
}

std::string ResponseParser::extractMethod(const std::string& request) {
    size_t space_pos = request.find(' ');
    if (space_pos == std::string::npos) {
        return "";
    }
    
    return request.substr(0, space_pos);
}

std::string ResponseParser::extractPath(const std::string& request) {
    size_t first_space = request.find(' ');
    if (first_space == std::string::npos) {
        return "";
    }
    
    size_t second_space = request.find(' ', first_space + 1);
    if (second_space == std::string::npos) {
        return "";
    }
    
    return request.substr(first_space + 1, second_space - first_space - 1);
}

std::string ResponseParser::extractHeaders(const std::string& request) {
    size_t header_start = request.find("\r\n");
    if (header_start == std::string::npos) {
        return "";
    }
    
    return request.substr(header_start + 2);
}

bool ResponseParser::hasHeader(const std::string& headers, const std::string& header_name, const std::string& header_value) {
    std::string lower_headers = headers;
    std::string lower_name = header_name;
    std::string lower_value = header_value;
    
    std::transform(lower_headers.begin(), lower_headers.end(), lower_headers.begin(), ::tolower);
    std::transform(lower_name.begin(), lower_name.end(), lower_name.begin(), ::tolower);
    std::transform(lower_value.begin(), lower_value.end(), lower_value.begin(), ::tolower);
    
    size_t header_pos = lower_headers.find(lower_name + ":");
    if (header_pos == std::string::npos) {
        return false;
    }
    
    size_t value_start = header_pos + lower_name.length() + 1;
    size_t line_end = lower_headers.find("\r\n", value_start);
    if (line_end == std::string::npos) {
        line_end = lower_headers.length();
    }
    
    std::string header_line = lower_headers.substr(value_start, line_end - value_start);
    return header_line.find(lower_value) != std::string::npos;
}

