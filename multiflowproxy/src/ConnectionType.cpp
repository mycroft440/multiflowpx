#include "ConnectionType.h"
#include "SSHConnectionType.h"
#include "OpenVPNConnectionType.h"
#include "V2RayConnectionType.h"
#include "Logger.h" // Assegure include

ConnectionType::ConnectionType(std::shared_ptr<Client> client, int socket_fd) 
    : Connection(client, socket_fd) {
}

ConnectionType::~ConnectionType() {
}

std::unique_ptr<ConnectionType> ConnectionTypeFactory::createConnection(
    std::shared_ptr<Client> client, 
    const std::string& initial_data,
    int socket_fd,
    bool ssh_only) {
    
    std::string connection_type = detectConnectionType(initial_data);
    
    if (connection_type == "SSH") {
        return std::make_unique<SSHConnectionType>(client, socket_fd);
    }
    
    if (!ssh_only) {
        if (connection_type == "OpenVPN") {
            return std::make_unique<OpenVPNConnectionType>(client, socket_fd);
        }
        
        if (connection_type == "V2Ray") {
            return std::make_unique<V2RayConnectionType>(client, socket_fd);
        }
    }
    
    // Default to SSH if no specific type detected
    return std::make_unique<SSHConnectionType>(client, socket_fd);
}

std::string ConnectionTypeFactory::detectConnectionType(const std::string& initial_data) {
    LOG_INFO("Detecting protocol from initial data: " << initial_data.substr(0, 32)); // Log aprimorado
    // SSH detection - look for SSH protocol identifier
    if (initial_data.find("SSH-") == 0) {
        return "SSH";
    }
    
    // OpenVPN detection - look for OpenVPN specific patterns
    // OpenVPN typically starts with specific byte patterns
    if (initial_data.length() >= 2) {
        unsigned char first_byte = static_cast<unsigned char>(initial_data[0]);
        unsigned char second_byte = static_cast<unsigned char>(initial_data[1]);
        
        // OpenVPN UDP packets often start with these patterns
        if ((first_byte & 0xF0) == 0x20 || (first_byte & 0xF0) == 0x30) {
            return "OpenVPN";
        }
    }
    
    // V2Ray detection - look for V2Ray specific patterns
    // V2Ray VMess protocol has specific header patterns
    if (initial_data.length() >= 16) {
        // Check for VMess protocol patterns
        // This is a simplified detection - real implementation would be more complex
        bool has_vmess_pattern = false;
        int high_byte_count = 0;
        for (size_t i = 0; i < std::min(initial_data.length(), size_t(16)); ++i) {
            if (static_cast<unsigned char>(initial_data[i]) > 0x7F) {
                high_byte_count++;
            }
        }
        if (high_byte_count > 8 || (initial_data[0] == '\x01' && initial_data[1] == '\x00')) {
            has_vmess_pattern = true;
        }
        
        if (has_vmess_pattern) {
            return "V2Ray";
        }
    }
    
    // Default to SSH
    return "SSH";
}
