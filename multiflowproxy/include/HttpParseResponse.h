#ifndef HTTP_PARSE_RESPONSE_H
#define HTTP_PARSE_RESPONSE_H

#include "ResponseParser.h"

class HttpParseResponse : public ResponseParser {
public:
    HttpParseResponse(const std::string& default_response = Constants::DEFAULT_HTTP_RESPONSE);
    virtual ~HttpParseResponse();
    
    virtual std::string parseResponse(const std::string& request) override;
    virtual bool isWebSocketUpgrade(const std::string& request) override;
    
private:
    std::string generateHttpResponse(const std::string& method, const std::string& path);
    std::string generateErrorResponse(int status_code, const std::string& message);
};

#endif // HTTP_PARSE_RESPONSE_H

