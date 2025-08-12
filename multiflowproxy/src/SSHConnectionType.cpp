#include "SSHConnectionType.h"
#include "Server.h"
#include "Client.h"
#include "Logger.h" // Assegure

SSHConnectionType::SSHConnectionType(std::shared_ptr<Client> client, int socket_fd, int ssh_port) 
    : ConnectionType(client, socket_fd), ssh_port_(ssh_port) {
}

SSHConnectionType::~SSHConnectionType() {
}

bool SSHConnectionType::establish() {
    if (!client_ || !client_->isConnected()) {
        return false;
    }
    
    if (!connectToSSHServer()) {
        return false;
    }
    
    if (!setupTunnel()) {
        return false;
    }
    
    setActive(true);
    return true;
}

void SSHConnectionType::handleData() {
    if (!isActive() || !client_ || !server_) {
        return;
    }
    
    // Create threads for bidirectional data forwarding
    std::thread client_to_server([this]() {
        forwardData(client_->getSocketFd(), server_->getSocketFd());
    });
    
    std::thread server_to_client([this]() {
        forwardData(server_->getSocketFd(), client_->getSocketFd());
    });
    
    // Wait for either thread to finish (connection closed)
    client_to_server.join();
    server_to_client.join();
    
    setActive(false);
}

std::string SSHConnectionType::getTypeName() const {
    return "SSH";
}

bool SSHConnectionType::detectProtocol(const std::string& initial_data) {
    return isSSHProtocol(initial_data);
}

bool SSHConnectionType::setupTunnel() {
    // SSH tunnel is established by connecting to the SSH server
    // The actual SSH protocol negotiation is handled by the SSH server
    return server_ && server_->isConnected();
}

bool SSHConnectionType::isSSHProtocol(const std::string& data) const {
    // SSH protocol identification string starts with "SSH-"
    return data.find("SSH-") == 0;
}

bool SSHConnectionType::connectToSSHServer() {
    for(int tries = 0; tries < 3; ++tries) {
        try {
            // Connect to config remote_host SSH server
            server_ = std::make_shared<Server>(config_.remote_host, ssh_port_);
            
            if (server_->connect()) {
                LOG_INFO("Connected to SSH server on " << config_.remote_host << ":" << ssh_port_ << " (try " << tries+1 << ")");
                return true;
            }
        } catch (const std::exception& e) {
            LOG_ERROR("SSH connection error on " << config_.remote_host << " (try " << tries+1 << "): " << e.what());
            std::this_thread::sleep_for(std::chrono::seconds(2));
        }
    }
    LOG_ERROR("Failed to connect to SSH server after 3 tries");
    return false;
}

ssize_t SSHConnectionType::read(char* buffer, size_t size) {
    return Connection::read(buffer, size);
}

ssize_t SSHConnectionType::write(const char* buffer, size_t size) {
    return Connection::write(buffer, size);
}
