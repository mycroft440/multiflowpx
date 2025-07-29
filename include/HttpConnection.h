#ifndef HTTP_CONNECTION_H
#define HTTP_CONNECTION_H

#include "Connection.h"
#include "Client.h"

class HttpConnection : public Connection {
public:
    HttpConnection(std::shared_ptr<Client> client, int socket_fd);
    ~HttpConnection();

    bool establish() override;
    void handleData() override;
    ssize_t read(char* buffer, size_t size) override;
    ssize_t write(const char* buffer, size_t size) override;
    void close() override;

private:
    // Implementações específicas para HTTP
};

#endif // HTTP_CONNECTION_H


