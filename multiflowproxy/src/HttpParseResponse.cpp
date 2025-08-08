#include "HttpParseResponse.h"

HttpParseResponse::HttpParseResponse(const std::string& default_response) 
    : ResponseParser(default_response) {
}

HttpParseResponse::~HttpParseResponse() {
}

std::string HttpParseResponse::parseResponse(const std::string& request) {
    if (isWebSocketUpgrade(request)) {
        return Constants::WEBSOCKET_UPGRADE_RESPONSE;
    }
    
    std::string method = extractMethod(request);
    std::string path = extractPath(request);
    
    if (method.empty()) {
        return generateErrorResponse(400, "Bad Request");
    }
    
    return generateHttpResponse(method, path);
}

bool HttpParseResponse::isWebSocketUpgrade(const std::string& request) {
    return ResponseParser::isWebSocketUpgrade(request);
}

std::string HttpParseResponse::generateHttpResponse(const std::string& method, const std::string& path) {
    // For most requests, return the default response
    if (method == "GET" || method == "POST" || method == "HEAD") {
        return default_response_;
    }
    
    return generateErrorResponse(405, "Method Not Allowed");
}

std::string HttpParseResponse::generateErrorResponse(int status_code, const std::string& message) {
    std::string response = "HTTP/1.1 " + std::to_string(status_code) + " " + message + "\r\n";
    response += "Content-Type: text/plain\r\n";
    response += "Content-Length: " + std::to_string(message.length()) + "\r\n";
    response += "Connection: close\r\n";
    response += "\r\n";
    response += message;
    
    return response;
}

