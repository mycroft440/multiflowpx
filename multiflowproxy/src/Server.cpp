#include "Server.h"
#include "Exceptions.h"
#include "Client.h" // Incluído para definição completa de Client
#include "HttpConnection.h" // Incluído para definição completa de HttpConnection
#include <iostream>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h> // Para inet_pton
#include <unistd.h>
#include <cstring> // Para strerror
#include <cerrno>  // Para errno
#include <thread>  // Para std::thread
#include <algorithm> // Para std::remove_if
#include "Logger.h"

Server::Server(int port) : m_port(port), m_serverFd(0) {
    // Cria o socket do servidor.
    m_serverFd = socket(AF_INET, SOCK_STREAM, 0);
    if (m_serverFd == -1) {
        throw SocketException("Falha ao criar o socket: " + std::string(strerror(errno)));
    }

    // Configura o endereço do servidor.
    sockaddr_in serverAddr{};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_addr.s_addr = INADDR_ANY;
    serverAddr.sin_port = htons(m_port);

    // Associa o socket ao endereço e porta.
    if (bind(m_serverFd, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        throw SocketException("Falha no bind: " + std::string(strerror(errno)));
    }

    // Coloca o servidor em modo de escuta.
    if (listen(m_serverFd, 10) < 0) {
        throw SocketException("Falha no listen: " + std::string(strerror(errno)));
    }
}

Server::Server(const std::string& ip_address, int port) : m_port(port), m_serverFd(0) {
    m_serverFd = socket(AF_INET, SOCK_STREAM, 0);
    if (m_serverFd == -1) {
        throw SocketException("Falha ao criar o socket: " + std::string(strerror(errno)));
    }

    sockaddr_in serverAddr{};
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(m_port);

    if (inet_pton(AF_INET, ip_address.c_str(), &serverAddr.sin_addr) <= 0) {
        throw SocketException("Endereço IP inválido ou erro de conversão: " + std::string(strerror(errno)));
    }

    if (bind(m_serverFd, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) < 0) {
        throw SocketException("Falha no bind: " + std::string(strerror(errno)));
    }

    if (listen(m_serverFd, 10) < 0) {
        throw SocketException("Falha no listen: " + std::string(strerror(errno)));
    }
}

Server::~Server() {
    // Fecha o socket do servidor ao destruir o objeto.
    if (m_serverFd > 0) {
        close(m_serverFd);
    }
    // Os unique_ptrs no vetor m_clients cuidarão de liberar a memória dos Clientes.
}

void Server::run() {
    LOG_INFO("Aguardando conexões...");
    while (true) {
        try {
            // Aceita uma nova conexão de cliente.
            int clientSocket = acceptClient();
            LOG_INFO("Cliente conectado com socket: " << clientSocket);

            // Cria um novo objeto Client usando um ponteiro inteligente.
            auto shared_client = std::make_shared<Client>(clientSocket);
            auto httpConnection = std::make_unique<HttpConnection>(shared_client, clientSocket);
            shared_client->setConnection(std::move(httpConnection));
            
            // Adiciona o cliente ao vetor e inicia a thread.
            m_clients.push_back(shared_client);
            std::thread(&Client::run, shared_client.get()).detach();

            // Limpa clientes desconectados para evitar vazamento de memória.
            cleanupInactiveClients();

        } catch (const SocketException& e) {
            LOG_ERROR("Erro ao aceitar cliente: " << e.what());
            // Continua o loop para aceitar outras conexões.
        }
    }
}

void Server::cleanupInactiveClients() {
    m_clients.erase(std::remove_if(m_clients.begin(), m_clients.end(),
                                 [](const std::shared_ptr<Client>& client) {
                                     // Retorna true se o cliente não está mais conectado
                                     // ou se o shared_ptr é nulo (objeto já destruído).
                                     return !client || !client->isConnected();
                                 }),
                    m_clients.end());
}

int Server::acceptClient() {
    sockaddr_in clientAddr{};
    socklen_t clientLen = sizeof(clientAddr);
    int clientSocket = accept(m_serverFd, (struct sockaddr*)&clientAddr, &clientLen);

    if (clientSocket < 0) {
        // Lança uma exceção em vez de encerrar o programa.
        throw SocketException("Falha ao aceitar conexão: " + std::string(strerror(errno)));
    }
    return clientSocket;
}


int Server::getSocketFd() const {
    return m_serverFd;
}

bool Server::isConnected() const {
    return m_serverFd > 0;
}

bool Server::connect() {
    // Para um servidor, 'connect' geralmente não faz sentido no mesmo contexto de um cliente.
    // Se a intenção é verificar se o servidor está escutando, 'isConnected' já faz isso.
    // Se for para conectar a outro servidor, essa lógica deveria estar em outro lugar.
    // Por enquanto, retorna true se o socket do servidor estiver válido.
    return m_serverFd > 0;
}



