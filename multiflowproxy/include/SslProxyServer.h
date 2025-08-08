#ifndef SSL_PROXY_SERVER_H
#define SSL_PROXY_SERVER_H

#include "ProxyServer.h"

class SslProxyServer : public ProxyServer {
public:
    SslProxyServer(const ProxyConfig& config);
    virtual ~SslProxyServer();
    
    virtual bool initialize() override;
    virtual void cleanup() override;
    
protected:
    virtual std::shared_ptr<Client> acceptConnection() override;
    virtual bool handleSSLHandshake(int client_fd);
    
private:
    SSL_CTX* ssl_context_;
    
    bool initializeSSLContext();
    void cleanupSSLContext();
    bool loadCertificates();
    bool loadPrivateKey();
    
    static void initializeOpenSSL();
    static void cleanupOpenSSL();
};

#endif // SSL_PROXY_SERVER_H

