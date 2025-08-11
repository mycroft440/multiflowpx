#ifndef CLIENT_H
#define CLIENT_H

#include "Connection.h"
#include <memory> // Para std::unique_ptr

class Client {
public:
    // Construtor que recebe o socket do cliente.
    explicit Client(int clientSocket);

    // Destrutor.
    ~Client();

    // Método principal executado em uma thread para manusear a conexão.
    void run();

    void setConnection(std::unique_ptr<Connection> connection);
    bool isConnected() const;
    int getSocketFd() const;
    ssize_t receive(char* buffer, size_t size);
    ssize_t send(const char* buffer, size_t size);

private:
    int m_clientSocket;
    std::unique_ptr<Connection> m_connection;
};
#endif // CLIENT_H

