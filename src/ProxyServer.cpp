#include "ProxyServer.h"
#include "HttpParseResponse.h"
#include "Client.h" // Incluído para definição completa de Client
#include <signal.h>
#include <sys/resource.h>

ProxyServer* ProxyServer::instance_ = nullptr;

ProxyServer::ProxyServer(const ProxyConfig& config) 
    : config_(config), running_(false), should_stop_(false), 
      server_socket_(-1), epoll_fd_(-1) {
    instance_ = this;
}

ProxyServer::~ProxyServer() {
    cleanup();
    instance_ = nullptr;
}

bool ProxyServer::initialize() {
    try {
        // Set file limit
        if (!setFileLimit()) {
            std::cerr << "Failed to set the file limit." << std::endl;
            return false;
        }
        
        // Create server socket
        if (!createServerSocket()) {
            return false;
        }
        
        // Set socket options
        if (!setSocketOptions()) {
            return false;
        }
        
        // Bind and listen
        if (!bindAndListen()) {
            return false;
        }
        
        // Setup epoll
        if (!setupEpoll()) {
            return false;
        }
        
        // Initialize worker pool
        worker_pool_ = std::make_unique<WorkerPool>(config_.workers);
        worker_pool_->start();
        
        // Initialize response parser
        response_parser_ = std::make_unique<HttpParseResponse>(config_.response_message);
        
        // Setup signal handlers
        setupSignalHandlers();
        
        printServerInfo();
        
        return true;
    } catch (const std::exception& e) {
        std::cerr << "Initialization error: " << e.what() << std::endl;
        return false;
    }
}

void ProxyServer::run() {
    if (!initialize()) {
        return;
    }
    
    running_ = true;
    
    while (running_ && !should_stop_) {
        try {
            processEpollEvents();
        } catch (const std::exception& e) {
            std::cerr << "Error processing events: " << e.what() << std::endl;
        }
    }
    
    cleanup();
}

void ProxyServer::stop() {
    should_stop_ = true;
    running_ = false;
}

void ProxyServer::cleanup() {
    if (worker_pool_) {
        worker_pool_->stop();
        worker_pool_.reset();
    }
    
    if (epoll_fd_ >= 0) {
        close(epoll_fd_);
        epoll_fd_ = -1;
    }
    
    if (server_socket_ >= 0) {
        close(server_socket_);
        server_socket_ = -1;
    }
    
    running_ = false;
}

bool ProxyServer::isRunning() const {
    return running_;
}

const ProxyConfig& ProxyServer::getConfig() const {
    return config_;
}

bool ProxyServer::createServerSocket() {
    server_socket_ = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket_ < 0) {
        perror("Failed to create socket");
        return false;
    }
    
    return true;
}

bool ProxyServer::bindAndListen() {
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(config_.port);
    
    if (bind(server_socket_, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("Failed to bind socket");
        return false;
    }
    
    if (listen(server_socket_, SOMAXCONN) < 0) {
        perror("Failed to listen on socket");
        return false;
    }
    
    return true;
}

bool ProxyServer::setupEpoll() {
    epoll_fd_ = epoll_create1(0);
    if (epoll_fd_ < 0) {
        perror("Error creating epoll");
        return false;
    }
    
    struct epoll_event event;
    event.events = EPOLLIN;
    event.data.fd = server_socket_;
    
    if (epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, server_socket_, &event) < 0) {
        perror("Error adding socket fd to epoll");
        return false;
    }
    
    return true;
}

bool ProxyServer::setSocketOptions() {
    int opt = 1;
    if (setsockopt(server_socket_, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0) {
        perror("Failed to set socket options");
        return false;
    }
    
    return true;
}

bool ProxyServer::setFileLimit() {
    struct rlimit limit;
    limit.rlim_cur = config_.ulimit;
    limit.rlim_max = config_.ulimit;
    
    return setrlimit(RLIMIT_NOFILE, &limit) == 0;
}

std::shared_ptr<Client> ProxyServer::acceptConnection() {
    struct sockaddr_in client_addr;
    socklen_t client_len = sizeof(client_addr);
    
    int client_fd = accept(server_socket_, (struct sockaddr*)&client_addr, &client_len);
    if (client_fd < 0) {
        if (errno != EAGAIN && errno != EWOULDBLOCK) {
            perror("accept failed");
        }
        return nullptr;
    }
    
    // Set non-blocking
    if (!Utils::setNonBlocking(client_fd)) {
        close(client_fd);
        return nullptr;
    }
    
    return std::make_shared<Client>(client_fd);
}

void ProxyServer::handleConnection(std::shared_ptr<Client> client) {
    if (!client || !client->isConnected()) {
        return;
    }
    
    try {
        // Read initial data to determine connection type
        char buffer[config_.buffer_size];
        ssize_t bytes_read = client->receive(buffer, sizeof(buffer) - 1);
        
        if (bytes_read <= 0) {
            return;
        }
        
        buffer[bytes_read] = '\0';
        std::string initial_data(buffer, bytes_read);
        
        // Create appropriate connection type
        auto connection = ConnectionTypeFactory::createConnection(client, initial_data, client->getSocketFd(), config_.ssh_only);
        if (connection) {
            if (connection->establish()) {
                connection->handleData();
            }
        } else {
            // Handle as HTTP request
            std::string response = response_parser_->parseResponse(initial_data);
            client->send(response.c_str(), response.length());
        }
    } catch (const std::exception& e) {
        std::cerr << "Error handling connection: " << e.what() << std::endl;
    }
}

void ProxyServer::processEpollEvents() {
    const int MAX_EVENTS = 64;
    struct epoll_event events[MAX_EVENTS];
    
    int num_events = epoll_wait(epoll_fd_, events, MAX_EVENTS, 1000); // 1 second timeout
    
    for (int i = 0; i < num_events; ++i) {
        if (events[i].data.fd == server_socket_) {
            // New connection
            auto client = acceptConnection();
            if (client) {
                worker_pool_->submitTask([this, client]() {
                    this->handleConnection(client);
                });
            }
        }
    }
}

void ProxyServer::printServerInfo() const {
    std::cout << "DTunnel Proxy Server v" << Constants::PROXY_SERVER_VERSION << std::endl;
    std::cout << "Author: " << Constants::PROXY_SERVER_AUTHOR << std::endl;
    std::cout << "Server running (" << (config_.use_https ? "HTTPS" : "HTTP") << ") on port " << config_.port << std::endl;
    std::cout << "Workers: " << config_.workers << std::endl;
    std::cout << "Buffer size: " << config_.buffer_size << " bytes" << std::endl;
    
    if (config_.ssh_only) {
        std::cout << "Mode: SSH only" << std::endl;
    } else {
        std::cout << "SSH port: " << config_.ssh_port << std::endl;
        std::cout << "OpenVPN port: " << config_.openvpn_port << std::endl;
        std::cout << "V2Ray port: " << config_.v2ray_port << std::endl;
    }
}

void ProxyServer::signalHandler(int signal) {
    std::cout << "\nReceived signal " << signal << ", shutting down..." << std::endl;
    stop();
}

void ProxyServer::staticSignalHandler(int signal) {
    if (instance_) {
        instance_->signalHandler(signal);
    }
}

void ProxyServer::setupSignalHandlers() {
    signal(SIGINT, staticSignalHandler);
    signal(SIGTERM, staticSignalHandler);
}

