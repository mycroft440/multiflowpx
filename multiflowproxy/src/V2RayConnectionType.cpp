#include "V2RayConnectionType.h"
#include "Server.h"
#include "Client.h"

V2RayConnectionType::V2RayConnectionType(std::shared_ptr<Client> client, int socket_fd, int v2ray_port) 
    : ConnectionType(client, socket_fd), v2ray_port_(v2ray_port) {
}

V2RayConnectionType::~V2RayConnectionType() {
}

bool V2RayConnectionType::establish() {
    if (!client_ || !client_->isConnected()) {
        return false;
    }
    
    if (!connectToV2RayServer()) {
        return false;
    }
    
    if (!setupTunnel()) {
        return false;
    }
    
    setActive(true);
    return true;
}

void V2RayConnectionType::handleData() {
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

std::string V2RayConnectionType::getTypeName() const {
    return "V2Ray";
}

bool V2RayConnectionType::detectProtocol(const std::string& initial_data) {
    return isV2RayProtocol(initial_data);
}

bool V2RayConnectionType::setupTunnel() {
    // V2Ray tunnel is established by connecting to the V2Ray server
    // The actual V2Ray protocol negotiation is handled by the V2Ray server
    return server_ && server_->isConnected();
}

bool V2RayConnectionType::isV2RayProtocol(const std::string& data) const {
    if (data.length() < 16) {
        return false;
    }
    
    // V2Ray VMess protocol has specific header patterns
    // This is a simplified detection - real implementation would be more complex
    
    // Check for VMess protocol patterns
    // VMess typically has encrypted headers with specific characteristics
    bool has_vmess_pattern = false;
    int high_byte_count = 0;
    
    for (size_t i = 0; i < std::min(data.length(), size_t(16)); ++i) {
        unsigned char byte = static_cast<unsigned char>(data[i]);
        if (byte > 0x7F) {
            high_byte_count++;
        }
    }
    
    // If more than half of the first 16 bytes are high bytes, it might be V2Ray
    if (high_byte_count > 8) {
        has_vmess_pattern = true;
    }
    
    // Additional checks for V2Ray patterns
    if (data.length() >= 4) {
        unsigned char first_four[4];
        for (int i = 0; i < 4; ++i) {
            first_four[i] = static_cast<unsigned char>(data[i]);
        }
        
        // Check for specific V2Ray handshake patterns
        if (first_four[0] == 0x01 && first_four[1] == 0x00) {
            has_vmess_pattern = true;
        }
    }
    
    return has_vmess_pattern;
}

bool V2RayConnectionType::connectToV2RayServer() {
    try {
        // Connect to localhost V2Ray server (assuming V2Ray server is running locally)
        server_ = std::make_shared<Server>("127.0.0.1", v2ray_port_);
        
        if (!server_->connect()) {
            std::cerr << "Failed to connect to V2Ray server on port " << v2ray_port_ << std::endl;
            return false;
        }
        
        return true;
    } catch (const std::exception& e) {
        std::cerr << "V2Ray connection error: " << e.what() << std::endl;
        return false;
    }
}



ssize_t V2RayConnectionType::read(char* buffer, size_t size) {
    return Connection::read(buffer, size);
}

ssize_t V2RayConnectionType::write(const char* buffer, size_t size) {
    return Connection::write(buffer, size);
}


