#include "SSHConnectionType.h"
#include "Server.h"
#include "Client.h"

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
    try {
        // Connect to localhost SSH server (assuming SSH server is running locally)
        server_ = std::make_shared<Server>("127.0.0.1", ssh_port_);
        
        if (!server_->connect()) {
            std::cerr << "Failed to connect to SSH server on port " << ssh_port_ << std::endl;
            return false;
        }
        
        return true;
    } catch (const std::exception& e) {
        std::cerr << "SSH connection error: " << e.what() << std::endl;
        return false;
    }
}



ssize_t SSHConnectionType::read(char* buffer, size_t size) {
    return Connection::read(buffer, size);
}

ssize_t SSHConnectionType::write(const char* buffer, size_t size) {
    return Connection::write(buffer, size);
}


