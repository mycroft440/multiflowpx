#ifndef CONNECTION_H
#define CONNECTION_H

class Client;
class Server;

#include "Common.h"

class Connection {
public:
    Connection(std::shared_ptr<Client> client, int socket_fd);
    virtual ~Connection();
    
    virtual bool establish() = 0;
    virtual void handleData() = 0;
    virtual ssize_t read(char* buffer, size_t size) = 0;
    virtual ssize_t write(const char* buffer, size_t size) = 0;
    virtual void close();
    
    std::shared_ptr<Client> getClient() const;
    std::shared_ptr<Server> getServer() const;
    
    bool isActive() const;
    void setActive(bool active);
    
protected:
    std::shared_ptr<Client> client_;
    std::shared_ptr<Server> server_;
    bool active_;
    std::mutex mutex_;
    int socket_fd_;
    
    virtual void forwardData(int from_fd, int to_fd);
    virtual bool parseInitialRequest(const std::string& request);
};

#endif // CONNECTION_H

