#include "Server.h"
#include "ArgumentParser.h"
#include "Exceptions.h" // Inclui as exceções customizadas
#include <iostream>
#include "Logger.h"

int main(int argc, char* argv[]) {
    try {
        // Analisa os argumentos da linha de comando.
        ArgumentParser argParser;
        ProxyConfig config = argParser.parse(argc, argv);

        int port = config.port;

        if (port == -1) {
            std::cerr << "Uso: " << argv[0] << " --port <porta>" << std::endl;
            return 1;
        }

        // Cria e executa o servidor.
        Server server(port);
        std::cout << "Servidor iniciado na porta " << port << std::endl;
        server.run();

    } catch (const ProxyException& e) {
        // Captura exceções específicas do proxy (ex: falha ao criar socket).
        std::cerr << "Erro fatal no servidor: " << e.what() << std::endl;
        return 1;
    } catch (const std::exception& e) {
        // Captura outras exceções padrão.
        std::cerr << "Ocorreu um erro inesperado: " << e.what() << std::endl;
        return 1;
    }

    return 0;
}

