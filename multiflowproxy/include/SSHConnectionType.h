#ifndef SSH_CONNECTION_TYPE_H
#define SSH_CONNECTION_TYPE_H

#include "ConnectionType.h"

class SSHConnectionType : public ConnectionType {
public:
    SSHConnectionType(std::shared_ptr<Client> client, int socket_fd, int ssh_port = Constants::DEFAULT_SSH_PORT);
    virtual ~SSHConnectionType();
    
    virtual bool establish() override;
    virtual void handleData() override;
    virtual ssize_t read(char* buffer, size_t size) override;
    virtual ssize_t write(const char* buffer, size_t size) override;
    virtual std::string getTypeName() const override;
    
protected:
    virtual bool detectProtocol(const std::string& initial_data) override;
    virtual bool setupTunnel() override;
    
private:
    int ssh_port_;
    
    bool isSSHProtocol(const std::string& data) const;
    bool connectToSSHServer();
};

#endif // SSH_CONNECTION_TYPE_H

