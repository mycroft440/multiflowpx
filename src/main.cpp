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
            LOG_ERROR("Uso: " << argv[0] << " --port <porta>");
            return 1;
        }

        // Cria e executa o servidor.
        Server server(port);
        LOG_INFO("Servidor iniciado na porta " << port);
        server.run();

    } catch (const ProxyException& e) {
        // Captura exceções específicas do proxy (ex: falha ao criar socket).
        LOG_ERROR("Erro fatal no servidor: " << e.what());
        return 1;
    } catch (const std::exception& e) {
        // Captura outras exceções padrão.
        LOG_ERROR("Ocorreu um erro inesperado: " << e.what());
        return 1;
    }

    return 0;
}


