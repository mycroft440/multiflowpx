#!/bin/bash

# set -e: Sai imediatamente se um comando falhar.
# set -u: Trata variáveis não definidas como um erro.
# set -o pipefail: O status de saída de um pipeline é o do último comando a falhar.
set -euo pipefail

# --- Variáveis e Constantes ---
readonly PROXY_DIR="multiflowproxy"
readonly SERVICE_NAME="multiflowpx.service"
readonly BIN_NAME="multiflowpx"

# Cores para a saída
readonly VERDE='\033[0;32m'
readonly VERMELHO='\033[0;31m'
readonly NC='\033[0m' # Sem Cor

# --- Funções ---

# Exibe uma mensagem de sucesso.
sucesso() {
    echo -e "${VERDE}✔ $1${NC}"
}

# Exibe uma mensagem de erro e sai.
erro() {
    echo -e "${VERMELHO}✖ $1${NC}" >&2
    exit 1
}

# Função principal que executa a instalação.
main() {
    # Determina o diretório do script e muda para ele.
    local SCRIPT_PATH
    SCRIPT_PATH=$(readlink -f "$0")
    local SCRIPT_DIR
    SCRIPT_DIR=$(dirname "$SCRIPT_PATH")
    cd "$SCRIPT_DIR"
    sucesso "Diretório de trabalho definido para: $SCRIPT_DIR"

    # Verifica se o script está sendo executado como root.
    if [ "$(id -u)" -ne 0 ]; then
        erro "Este script precisa ser executado como root. Use: sudo $0"
    fi

    sucesso "Iniciando a instalação do MultiflowPX..."

    sucesso "Atualizando a lista de pacotes..."
    apt-get update

    sucesso "Instalando dependências essenciais..."
    apt-get install -y python3 python3-pip cmake g++ libssl-dev libboost-all-dev python3-psutil

    sucesso "Dependências instaladas com sucesso."

    if [ ! -d "$PROXY_DIR" ]; then
        erro "Diretório '$PROXY_DIR' não encontrado. O script não parece estar na raiz do projeto."
    fi

    sucesso "Compilando o proxy..."
    cd "$PROXY_DIR"
    
    mkdir -p build
    cd build

    cmake ..
    make
    
    sucesso "Proxy compilado com sucesso."

    sucesso "Instalando o executável '$BIN_NAME'..."
    cp "$BIN_NAME" /usr/local/bin/
    
    cd .. # Volta para o diretório do proxy

    sucesso "Configurando o serviço systemd..."
    cp "$SERVICE_NAME" /etc/systemd/system/
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    systemctl start "$SERVICE_NAME"
    
    sucesso "----------------------------------------"
    sucesso "Instalação concluída com sucesso!"
    sucesso "Use o comando 'proxy_menu' para gerenciar o serviço."
    sucesso "----------------------------------------"
}

# --- Ponto de Entrada ---
# Executa a função principal.
main

