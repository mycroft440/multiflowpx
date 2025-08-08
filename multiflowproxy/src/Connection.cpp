#include "Connection.h"
#include "Exceptions.h"
#include <unistd.h>
#include <sys/socket.h>
#include <cstring>
#include <cerrno>

Connection::Connection(std::shared_ptr<Client> client, int socket_fd) : client_(client), socket_fd_(socket_fd) {}

Connection::~Connection() {
    if (socket_fd_ > 0) {
        ::close(socket_fd_);
    }
}

ssize_t Connection::read(char* buffer, size_t size) {
    ssize_t bytesRead = ::read(socket_fd_, buffer, size);
    if (bytesRead < 0) {
        throw ConnectionException("Erro ao ler do socket: " + std::string(strerror(errno)));
    }
    return bytesRead;
}

ssize_t Connection::write(const char* buffer, size_t size) {
    ssize_t bytesWritten = ::write(socket_fd_, buffer, size);
    if (bytesWritten < 0) {
        throw ConnectionException("Erro ao escrever no socket: " + std::string(strerror(errno)));
    }
    return bytesWritten;
}


void Connection::close() {
    if (socket_fd_ > 0) {
        ::close(socket_fd_);
        socket_fd_ = -1; // Invalida o socket após o fechamento
    }
}

bool Connection::isActive() const {
    return active_;
}

void Connection::setActive(bool active) {
    active_ = active;
}

void Connection::forwardData(int from_fd, int to_fd) {
    char buffer[4096];
    ssize_t bytes_read;
    while ((bytes_read = ::read(from_fd, buffer, sizeof(buffer))) > 0) {
        ssize_t bytes_written = ::write(to_fd, buffer, bytes_read);
        if (bytes_written < 0) {
            // Handle write error
            break;
        }
    }
}

bool Connection::parseInitialRequest(const std::string& request) {
    // This is a placeholder. Real implementation would parse the request
    // to determine the protocol (HTTP, SSH, etc.)
    return true; 
}


