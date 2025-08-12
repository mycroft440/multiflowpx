# Define a versão mínima necessária do CMake e o nome do projeto.
# A versão foi atualizada para 3.15 para garantir acesso a funcionalidades modernas do CMake.
cmake_minimum_required(VERSION 3.15)
project(multiflowpx CXX)

# Define o padrão C++ a ser utilizado (C++17).
# CMAKE_CXX_STANDARD_REQUIRED garante que o compilador suporte o padrão especificado.
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Encontra as dependências necessárias: OpenSSL e Boost (threads e system) e CURL.
# REQUIRED garante que o CMake falhará se não encontrar as bibliotecas.
find_package(OpenSSL REQUIRED)
find_package(Boost REQUIRED COMPONENTS thread system)
find_package(CURL REQUIRED)

# Nome do executável alinhado com o install.sh e o service: multiflowpx_proxy
set(EXEC_NAME multiflowpx_proxy)

# Define o executável principal do projeto.
add_executable(${EXEC_NAME})

# Adiciona os diretórios de cabeçalho ao alvo.
target_include_directories(${EXEC_NAME} PUBLIC
    ${PROJECT_SOURCE_DIR}/include
)

# Lista todos os arquivos-fonte (.cpp) que compõem o executável.
target_sources(${EXEC_NAME} PRIVATE
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

# Linka as bibliotecas necessárias ao alvo.
target_link_libraries(${EXEC_NAME} PRIVATE
    ${OPENSSL_LIBRARIES}
    Boost::thread
    Boost::system
    ${CURL_LIBRARIES}
)

# Comando para instalar o executável no diretório 'bin' (prefixo padrão: /usr/local).
install(TARGETS ${EXEC_NAME} DESTINATION bin)
