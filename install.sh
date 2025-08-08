#!/bin/bash

# ==============================================================================
# Script de Instalação para o MultiFlow Manager
#
# Este script prepara o ambiente para o MultiFlow Manager, instalando todas as
# dependências de sistema e de Python necessárias para todas as ferramentas,
# incluindo:
# - Gerenciador de usuários SSH
# - BadVPN
# - Proxy Socks
# - MultiFlow Proxy (dependências de compilação)
# - Ferramentas de otimização (Swap, ZRAM, etc.)
#
# IMPORTANTE: Este script NÃO compila nem instala os serviços. Ele apenas
# prepara o sistema. A compilação e o gerenciamento dos serviços devem ser
# feitos através do menu principal executando 'sudo python3 multiflow.py'.
# ==============================================================================

# --- Cores para a Saída ---
R='\033[1;31m'
G='\033[1;32m'
Y='\033[1;33m'
C='\033[1;36m'
W='\033[0m'

# --- Funções Auxiliares ---

# Imprime um cabeçalho formatado
print_header() {
    clear
    echo -e "${C}===============================================${W}"
    echo -e "${C}      Instalador do MultiFlow Manager      ${W}"
    echo -e "${C}===============================================${W}"
    echo
}

# Verifica se o script está sendo executado como root
check_root() {
    if [ "$EUID" -ne 0 ]; then
      echo -e "${R}Erro: Este script precisa ser executado como root.${W}"
      echo -e "${Y}Por favor, execute com: sudo bash install.sh${W}"
      exit 1
    fi
}

# Instala todas as dependências do sistema
install_system_deps() {
    echo -e "${Y}>>> Atualizando a lista de pacotes do sistema (apt-get update)...${W}"
    if ! apt-get update -y; then
        echo -e "${R}Falha ao atualizar a lista de pacotes. Verifique sua conexão e repositórios.${W}"
        exit 1
    fi
    
    echo -e "\n${Y}>>> Instalando dependências essenciais...${W}"
    echo -e "    (python3, pip, git, build-essential, cmake, libssl-dev, gcc)"
    
    # Lista de pacotes a serem instalados
    local packages=(
        python3 
        python3-pip 
        git 
        build-essential 
        cmake 
        libssl-dev 
        gcc
    )
    
    if ! apt-get install -y "${packages[@]}"; then
        echo -e "${R}Falha ao instalar pacotes do sistema. A instalação foi abortada.${W}"
        exit 1
    fi
}

# Instala as dependências de Python via pip
install_python_deps() {
    echo -e "\n${Y}>>> Instalando pacotes Python com pip...${W}"
    echo -e "    (psutil)"
    
    if ! pip3 install psutil; then
        echo -e "${R}Falha ao instalar pacotes Python. A instalação foi abortada.${W}"
        exit 1
    fi
}

# Define as permissões de execução para os scripts
set_permissions() {
    echo -e "\n${Y}>>> Configurando permissões de execução para scripts...${W}"
    
    # Encontra todos os scripts .sh e os torna executáveis
    find . -type f -name "*.sh" -exec chmod +x {} \;
    
    echo -e "${G}Permissões configuradas.${W}"
}


# --- Função Principal ---
main() {
    print_header
    check_root

    echo -e "${G}Bem-vindo ao instalador do MultiFlow Manager!${W}"
    echo -e "${Y}Este script irá preparar o ambiente, instalando todas as dependências.${W}"
    echo -e "---------------------------------------------------------------------"
    
    install_system_deps
    install_python_deps
    set_permissions

    echo
    echo -e "${C}=====================================================================${W}"
    echo -e "${G}      Ambiente preparado com sucesso!      ${W}"
    echo -e "${C}=====================================================================${W}"
    echo -e "\n${Y}Todos os pré-requisitos foram instalados.${W}"
    echo -e "${Y}Para compilar, configurar e gerenciar as conexões, execute o menu principal:${W}"
    echo -e "\n    ${C}sudo python3 multiflow.py${W}\n"
}

# Executa o script
main
