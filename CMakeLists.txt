# Define a versão mínima necessária do CMake e o nome do projeto.
# A versão foi atualizada para 3.15 para garantir acesso a funcionalidades modernas do CMake.
cmake_minimum_required(VERSION 3.15)
project(multiflowpx CXX)

# Define o padrão C++ a ser utilizado (C++17).
# CMAKE_CXX_STANDARD_REQUIRED garante que o compilador suporte o padrão especificado.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Encontra as dependências necessárias: OpenSSL e Boost (threads e system).
# REQUIRED garante que o CMake falhará se não encontrar as bibliotecas.
find_package(OpenSSL REQUIRED)
find_package(Boost REQUIRED COMPONENTS thread system)
find_package(CURL REQUIRED)

# Define o executável principal do projeto, chamado "proxy".
add_executable(proxy)

# Adiciona os diretórios de cabeçalho ao alvo "proxy".
# Usar target_include_directories com PUBLIC garante que outros alvos que linkarem
# com "proxy" também terão acesso a esses includes.
target_include_directories(proxy PUBLIC
    ${PROJECT_SOURCE_DIR}/include
)

# Lista todos os arquivos-fonte (.cpp) que compõem o executável.
target_sources(proxy PRIVATE
    src/main.cpp
    src/ArgumentParser.cpp
    src/Client.cpp
    src/Common.cpp
    src/Connection.cpp
    src/ConnectionType.cpp
    src/HttpParseResponse.cpp
    src/HttpConnection.cpp
    src/OpenVPNConnectionType.cpp
    src/ProxyServer.cpp
    src/ResponseParser.cpp
    src/Server.cpp
    src/SslProxyServer.cpp
    src/SSHConnectionType.cpp
    src/V2RayConnectionType.cpp
    src/WebsocketParseResponse.cpp
    src/Worker.cpp
)

# Linka as bibliotecas necessárias (OpenSSL e Boost) ao alvo "proxy".
# Usar target_link_libraries é a prática moderna para vincular dependências
# a um alvo específico, evitando poluir o escopo global.
target_link_libraries(proxy PRIVATE
    ${OPENSSL_LIBRARIES}
    Boost::thread
    Boost::system
    ${CURL_LIBRARIES}
)
# Comando para instalar o executável no diretório 'bin' do sistema.
install(TARGETS proxy DESTINATION bin)
