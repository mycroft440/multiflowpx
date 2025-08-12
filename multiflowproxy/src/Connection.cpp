#include "Connection.h"
#include "Exceptions.h"
#include <unistd.h>
#include <sys/socket.h>
#include <cstring>
#include <cerrno>
#include <sys/select.h> // Adicionado

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
        socket_fd_ = -1;
    }
}

bool Connection::isActive() const {
    return active_;
}

void Connection::setActive(bool active) {
    active_ = active;
}

void Connection::forwardData(int from_fd, int to_fd) {
    char buffer[Constants::DEFAULT_BUFFER_SIZE];
    ssize_t bytes_read;
    while (true) {
        fd_set read_fds;
        FD_ZERO(&read_fds);
        FD_SET(from_fd, &read_fds);
        struct timeval tv = {1, 0}; // Timeout 1s
        int sel_ret = select(from_fd + 1, &read_fds, NULL, NULL, &tv);
        if (sel_ret > 0) {
            bytes_read = ::read(from_fd, buffer, sizeof(buffer));
            if (bytes_read <= 0) {
                if (bytes_read < 0) LOG_ERROR("Read error: " << strerror(errno));
                break;
            }
            ssize_t bytes_written = 0;
            while (bytes_written < bytes_read) { // Retry partial writes
                ssize_t written = ::write(to_fd, buffer + bytes_written, bytes_read - bytes_written);
                if (written < 0) {
                    LOG_ERROR("Write error: " << strerror(errno));
                    break;
                }
                bytes_written += written;
            }
        } else if (sel_ret == 0) {
            // Timeout: checa active
            if (!isActive()) break;
        } else {
            LOG_ERROR("Select error: " << strerror(errno));
            break;
        }
    }
}

bool Connection::parseInitialRequest(const std::string& request) {
    return true; 
}
