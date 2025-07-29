#ifndef OPENVPN_CONNECTION_TYPE_H
#define OPENVPN_CONNECTION_TYPE_H

#include "ConnectionType.h"

class OpenVPNConnectionType : public ConnectionType {
public:
    OpenVPNConnectionType(std::shared_ptr<Client> client, int socket_fd, int openvpn_port = Constants::DEFAULT_OPENVPN_PORT);
    virtual ~OpenVPNConnectionType();
    
    virtual bool establish() override;
    virtual void handleData() override;
    virtual ssize_t read(char* buffer, size_t size) override;
    virtual ssize_t write(const char* buffer, size_t size) override;
    virtual std::string getTypeName() const override;
    
protected:
    virtual bool detectProtocol(const std::string& initial_data) override;
    virtual bool setupTunnel() override;
    
private:
    int openvpn_port_;
    
    bool isOpenVPNProtocol(const std::string& data) const;
    bool connectToOpenVPNServer();
};

#endif // OPENVPN_CONNECTION_TYPE_H

