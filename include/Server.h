#ifndef SERVER_H
#define SERVER_H

class Client;

#include <vector>
#include <memory> // Para std::unique_ptr
#include "Logger.h"

class Server {
public:
    // Construtor que recebe a porta para escutar.
    Server(int port);
    Server(const std::string& ip_address, int port);

    // Destrutor virtual para permitir herança.
    virtual ~Server();

    // Inicia o loop principal do servidor para aceitar conexões.
    void run();
    int getSocketFd() const;
    bool isConnected() const;
    bool connect();
    void cleanupInactiveClients();

protected:
    // Aceita uma nova conexão de cliente.
    virtual int acceptClient();

    int m_port;
    int m_serverFd;

    // Vetor de ponteiros inteligentes para gerenciar o ciclo de vida dos clientes.
    // std::unique_ptr garante que a memória do Client seja liberada quando removido do vetor.
    std::vector<std::shared_ptr<Client>> m_clients;

    // O vetor de threads foi removido para evitar vazamento de memória,
    // já que as threads são criadas como "detached".
};

#endif // SERVER_H
