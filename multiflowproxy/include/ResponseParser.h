#ifndef RESPONSE_PARSER_H
#define RESPONSE_PARSER_H

#include "Common.h"

class ResponseParserAbstract {
public:
    virtual ~ResponseParserAbstract() = default;
    virtual std::string parseResponse(const std::string& request) = 0;
    virtual bool isWebSocketUpgrade(const std::string& request) = 0;
};

class ResponseParser : public ResponseParserAbstract {
public:
    ResponseParser(const std::string& default_response = Constants::DEFAULT_HTTP_RESPONSE);
    virtual ~ResponseParser();
    
    virtual std::string parseResponse(const std::string& request) override;
    virtual bool isWebSocketUpgrade(const std::string& request) override;
    
    void setDefaultResponse(const std::string& response);
    std::string getDefaultResponse() const;
    
protected:
    std::string default_response_;
    
    virtual std::string extractMethod(const std::string& request);
    virtual std::string extractPath(const std::string& request);
    virtual std::string extractHeaders(const std::string& request);
    virtual bool hasHeader(const std::string& headers, const std::string& header_name, const std::string& header_value);
};

#endif // RESPONSE_PARSER_H

