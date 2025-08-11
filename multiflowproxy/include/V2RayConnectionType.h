#ifndef V2RAY_CONNECTION_TYPE_H
#define V2RAY_CONNECTION_TYPE_H

#include "ConnectionType.h"

class V2RayConnectionType : public ConnectionType {
public:
    V2RayConnectionType(std::shared_ptr<Client> client, int socket_fd, int v2ray_port = Constants::DEFAULT_V2RAY_PORT);
    virtual ~V2RayConnectionType();
    
    virtual bool establish() override;
    virtual void handleData() override;
    virtual ssize_t read(char* buffer, size_t size) override;
    virtual ssize_t write(const char* buffer, size_t size) override;
    virtual std::string getTypeName() const override;
    
protected:
    virtual bool detectProtocol(const std::string& initial_data) override;
    virtual bool setupTunnel() override;
    
private:
    int v2ray_port_;
    
    bool isV2RayProtocol(const std::string& data) const;
    bool connectToV2RayServer();
};

#endif // V2RAY_CONNECTION_TYPE_H

