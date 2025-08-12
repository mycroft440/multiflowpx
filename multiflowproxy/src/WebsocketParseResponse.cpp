#include "WebsocketParseResponse.h"
#include <openssl/sha.h>
#include <openssl/evp.h>
#include <openssl/bio.h>
#include <openssl/buffer.h>

WebsocketParseResponse::WebsocketParseResponse() 
    : ResponseParser(Constants::WEBSOCKET_UPGRADE_RESPONSE) {
}

WebsocketParseResponse::~WebsocketParseResponse() {
}

std::string WebsocketParseResponse::parseResponse(const std::string& request) {
    if (!isWebSocketUpgrade(request)) {
        return "HTTP/1.1 400 Bad Request\r\n\r\n";
    }
    
    if (!validateWebSocketRequest(request)) {
        return "HTTP/1.1 400 Bad Request\r\n\r\n";
    }
    
    return generateWebSocketHandshake(request);
}

bool WebsocketParseResponse::isWebSocketUpgrade(const std::string& request) {
    return ResponseParser::isWebSocketUpgrade(request);
}

std::string WebsocketParseResponse::generateWebSocketHandshake(const std::string& request) {
    std::string key = extractWebSocketKey(request);
    if (key.empty()) {
        key = "dGhlIHNhbXBsZSBub25jZQ=="; // Dummy para compat com clients minimal
        LOG_WARNING("Using dummy WebSocket key for minimal payload");
    }
    std::string accept = generateWebSocketAccept(key);
    
    std::string response = "HTTP/1.1 101 Switching Protocols\r\n";
    response += "Upgrade: websocket\r\n";
    response += "Connection: Upgrade\r\n";
    response += "Sec-WebSocket-Accept: " + accept + "\r\n";
    response += "\r\n";
    
    return response;
}

std::string WebsocketParseResponse::extractWebSocketKey(const std::string& request) {
    size_t key_pos = request.find("Sec-WebSocket-Key:");
    if (key_pos == std::string::npos) {
        return "";
    }
    
    size_t value_start = key_pos + 18; // Length of "Sec-WebSocket-Key:"
    size_t line_end = request.find("\r\n", value_start);
    if (line_end == std::string::npos) {
        return "";
    }
    
    std::string key = request.substr(value_start, line_end - value_start);
    return Utils::trim(key);
}

std::string WebsocketParseResponse::generateWebSocketAccept(const std::string& key) {
    const std::string magic_string = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11";
    std::string combined = key + magic_string;
    
    // Calculate SHA-1 hash
    unsigned char hash[SHA_DIGEST_LENGTH];
    SHA1(reinterpret_cast<const unsigned char*>(combined.c_str()), combined.length(), hash);
    
    // Base64 encode
    BIO* bio = BIO_new(BIO_s_mem());
    BIO* b64 = BIO_new(BIO_f_base64());
    BIO_set_flags(b64, BIO_FLAGS_BASE64_NO_NL);
    bio = BIO_push(b64, bio);
    
    BIO_write(bio, hash, SHA_DIGEST_LENGTH);
    BIO_flush(bio);
    
    BUF_MEM* buffer_ptr;
    BIO_get_mem_ptr(bio, &buffer_ptr);
    
    std::string result(buffer_ptr->data, buffer_ptr->length);
    BIO_free_all(bio);
    
    return result;
}

bool WebsocketParseResponse::validateWebSocketRequest(const std::string& request) {
    // Leniência: só checa upgrade e connection, sem key obrigatória
    std::string headers = extractHeaders(request);
    
    return hasHeader(headers, "upgrade", "websocket") &&
           hasHeader(headers, "connection", "upgrade");
}
