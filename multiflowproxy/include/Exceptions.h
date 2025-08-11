#ifndef EXCEPTIONS_H
#define EXCEPTIONS_H

#include <stdexcept>
#include <string>

/**
 * @class ProxyException
 * @brief Exceção base para todos os erros relacionados ao proxy.
 *
 * Fornece uma base comum para capturar todas as exceções específicas da aplicação.
 */
class ProxyException : public std::runtime_error {
public:
    explicit ProxyException(const std::string& message)
        : std::runtime_error(message) {}
};

/**
 * @class SocketException
 * @brief Exceção para erros relacionados a operações de socket.
 *
 * Usada para sinalizar falhas em chamadas como socket(), bind(), listen(), accept(), etc.
 */
class SocketException : public ProxyException {
public:
    explicit SocketException(const std::string& message)
        : ProxyException(message) {}
};

/**
 * @class ConnectionException
 * @brief Exceção para erros durante o manuseio de uma conexão de cliente.
 *
 * Usada para sinalizar problemas durante a leitura, escrita ou processamento
 * de dados de uma conexão ativa.
 */
class ConnectionException : public ProxyException {
public:
    explicit ConnectionException(const std::string& message)
        : ProxyException(message) {}
};

#endif // EXCEPTIONS_H
