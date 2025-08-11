#ifndef PROXY_SERVER_H
#define PROXY_SERVER_H

#include "Common.h"
#include "ArgumentParser.h"
#include "Worker.h"
#include "Client.h"
#include "ResponseParser.h"
#include "ConnectionType.h"

class ProxyServer {
public:
    ProxyServer(const ProxyConfig& config);
    virtual ~ProxyServer();
    
    virtual bool initialize();
    virtual void run();
    virtual void stop();
    virtual void cleanup();
    
    bool isRunning() const;
    const ProxyConfig& getConfig() const;
    
protected:
    ProxyConfig config_;
    std::atomic<bool> running_;
    std::atomic<bool> should_stop_;
    
    int server_socket_;
    int epoll_fd_;
    
    std::unique_ptr<WorkerPool> worker_pool_;
    std::unique_ptr<ResponseParser> response_parser_;
    
    virtual bool createServerSocket();
    virtual bool bindAndListen();
    virtual bool setupEpoll();
    virtual bool setSocketOptions();
    virtual bool setFileLimit();
    
    virtual std::shared_ptr<Client> acceptConnection();
    virtual void handleConnection(std::shared_ptr<Client> client);
    virtual void processEpollEvents();
    
    void printServerInfo() const;

private:
    static ProxyServer* instance_;
    static void staticSignalHandler(int signal);
    void signalHandler(int signal);
    void setupSignalHandlers();
};

#endif // PROXY_SERVER_H

