#ifndef WEBSOCKET_PARSE_RESPONSE_H
#define WEBSOCKET_PARSE_RESPONSE_H

#include "ResponseParser.h"

class WebsocketParseResponse : public ResponseParser {
public:
    WebsocketParseResponse();
    virtual ~WebsocketParseResponse();
    
    virtual std::string parseResponse(const std::string& request) override;
    virtual bool isWebSocketUpgrade(const std::string& request) override;
    
private:
    std::string generateWebSocketHandshake(const std::string& request);
    std::string extractWebSocketKey(const std::string& request);
    std::string generateWebSocketAccept(const std::string& key);
    bool validateWebSocketRequest(const std::string& request);
};

#endif // WEBSOCKET_PARSE_RESPONSE_H

