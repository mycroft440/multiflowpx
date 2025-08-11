#include "OpenVPNConnectionType.h"
#include "Server.h"
#include "Client.h"

OpenVPNConnectionType::OpenVPNConnectionType(std::shared_ptr<Client> client, int socket_fd, int openvpn_port) 
    : ConnectionType(client, socket_fd), openvpn_port_(openvpn_port) {
}

OpenVPNConnectionType::~OpenVPNConnectionType() {
}

bool OpenVPNConnectionType::establish() {
    if (!client_ || !client_->isConnected()) {
        return false;
    }
    
    if (!connectToOpenVPNServer()) {
        return false;
    }
    
    if (!setupTunnel()) {
        return false;
    }
    
    setActive(true);
    return true;
}

void OpenVPNConnectionType::handleData() {
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

std::string OpenVPNConnectionType::getTypeName() const {
    return "OpenVPN";
}

bool OpenVPNConnectionType::detectProtocol(const std::string& initial_data) {
    return isOpenVPNProtocol(initial_data);
}

bool OpenVPNConnectionType::setupTunnel() {
    // OpenVPN tunnel is established by connecting to the OpenVPN server
    // The actual OpenVPN protocol negotiation is handled by the OpenVPN server
    return server_ && server_->isConnected();
}

bool OpenVPNConnectionType::isOpenVPNProtocol(const std::string& data) const {
    if (data.length() < 2) {
        return false;
    }
    
    unsigned char first_byte = static_cast<unsigned char>(data[0]);
    unsigned char second_byte = static_cast<unsigned char>(data[1]);
    
    // OpenVPN UDP packets often start with these patterns
    // This is a simplified detection - real implementation would be more complex
    if ((first_byte & 0xF0) == 0x20 || (first_byte & 0xF0) == 0x30) {
        return true;
    }
    
    // Check for OpenVPN TCP patterns
    if (first_byte == 0x00 && second_byte > 0x00) {
        return true;
    }
    
    return false;
}

bool OpenVPNConnectionType::connectToOpenVPNServer() {
    try {
        // Connect to localhost OpenVPN server (assuming OpenVPN server is running locally)
        server_ = std::make_shared<Server>("127.0.0.1", openvpn_port_);
        
        if (!server_->connect()) {
            std::cerr << "Failed to connect to OpenVPN server on port " << openvpn_port_ << std::endl;
            return false;
        }
        
        return true;
    } catch (const std::exception& e) {
        std::cerr << "OpenVPN connection error: " << e.what() << std::endl;
        return false;
    }
}



ssize_t OpenVPNConnectionType::read(char* buffer, size_t size) {
    return Connection::read(buffer, size);
}

ssize_t OpenVPNConnectionType::write(const char* buffer, size_t size) {
    return Connection::write(buffer, size);
}


