#ifndef CONNECTION_TYPE_H
#define CONNECTION_TYPE_H

#include "Common.h"
#include "Connection.h"

class ConnectionType : public Connection {
public:
    ConnectionType(std::shared_ptr<Client> client, int socket_fd);
    virtual ~ConnectionType();
    
    virtual bool establish() override = 0;
    virtual void handleData() override = 0;
    virtual std::string getTypeName() const = 0;
    
protected:
    virtual bool detectProtocol(const std::string& initial_data) = 0;
    virtual bool setupTunnel() = 0;
};

// Factory for creating connection types
class ConnectionTypeFactory {
public:
    static std::unique_ptr<ConnectionType> createConnection(
        std::shared_ptr<Client> client, 
        const std::string& initial_data,
        int socket_fd,
        bool ssh_only = false
    );
    
private:
    static std::string detectConnectionType(const std::string& initial_data);
};

#endif // CONNECTION_TYPE_H

