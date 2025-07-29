#include "Client.h"
#include "Exceptions.h"
#include <iostream>
#include <unistd.h> // Para close()
#include <cstring>  // Para strlen()

Client::Client(int clientSocket) : m_clientSocket(clientSocket) {
}

Client::~Client() {
    std::cout << "Cliente com socket " << m_clientSocket << " desconectado." << std::endl;
    if (m_clientSocket > 0) {
        close(m_clientSocket);
    }
}

void Client::setConnection(std::unique_ptr<Connection> connection) {
    m_connection = std::move(connection);
}
void Client::run() {
    try {
        std::cout << "Manuseando cliente com socket " << m_clientSocket << " na thread." << std::endl;
        
        if (m_connection) {
            if (m_connection->establish()) {
                m_connection->handleData();
            }
        } else {
            std::cerr << "Nenhuma conexão configurada para o cliente " << m_clientSocket << std::endl;
        }

    } catch (const ConnectionException& e) {
        std::cerr << "Erro na conexão com o cliente " << m_clientSocket << ": " << e.what() << std::endl;
    } catch (const std::exception& e) {
        std::cerr << "Erro inesperado na thread do cliente " << m_clientSocket << ": " << e.what() << std::endl;
    }
}


bool Client::isConnected() const {
    return m_clientSocket > 0;
}

int Client::getSocketFd() const {
    return m_clientSocket;
}




ssize_t Client::receive(char* buffer, size_t size) {
    if (m_connection) {
        return m_connection->read(buffer, size);
    }
    return -1; // Or throw an exception
}

ssize_t Client::send(const char* buffer, size_t size) {
    if (m_connection) {
        return m_connection->write(buffer, size);
    }
    return -1; // Or throw an exception
}




