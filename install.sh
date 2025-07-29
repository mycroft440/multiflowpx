#!/bin/bash

# ==============================================================================
# Script de Instalação para o MultiFlowPX Proxy Server
#
# Este script automatiza o processo de:
# 1. Verificação de permissões de root.
# 2. Instalação de dependências do sistema (via apt, yum, etc.).
# 3. Instalação de dependências Python.
# 4. Clonagem do repositório do GitHub.
# 5. Compilação do projeto com CMake e make.
# 6. Instalação dos binários e scripts de menu.
# 7. Limpeza dos arquivos de build.
# ==============================================================================

# --- Funções Auxiliares para Logs Coloridos ---

# Exibe uma mensagem de informação (azul)
log_info() {
    echo -e "\e[34m[INFO]\e[0m $1"
}

# Exibe uma mensagem de sucesso (verde)
log_success() {
    echo -e "\e[32m[SUCCESS]\e[0m $1"
}

# Exibe uma mensagem de erro (vermelho)
log_error() {
    echo -e "\e[31m[ERROR]\e[0m $1"
}

# Exibe uma mensagem de aviso (amarelo)
log_warning() {
    echo -e "\e[33m[WARNING]\e[0m $1"
}

# --- Verificações Iniciais ---

# Garante que o script está sendo executado com privilégios de root (sudo)
check_root() {
    if [ "$(id -u)" -ne 0 ]; then
        log_error "Este script precisa ser executado como root. Use 'sudo ./install.sh'."
        exit 1
    fi
}

# --- Início da Execução do Script ---

log_info "Iniciando a instalação do MultiFlowPX Proxy Server..."
check_root

# Salva o diretório onde o script foi iniciado para referência futura
INITIAL_DIR="$(pwd)"

install_deps_fallback() {
    log_info "Tentando instalar dependências via shell (fallback)."
    if command -v apt-get >/dev/null 2>&1; then
        log_info "Detectado APT. Instalando dependências..."
        apt-get update && apt-get install -y build-essential cmake libssl-dev libcurl4-openssl-dev libboost-all-dev
    elif command -v yum >/dev/null 2>&1; then
        log_info "Detectado YUM. Instalando dependências..."
        yum install -y gcc-c++ make cmake openssl-devel libcurl-devel boost-devel
    elif command -v dnf >/dev/null 2>&1; then
        log_info "Detectado DNF. Instalando dependências..."
        dnf install -y gcc-c++ make cmake openssl-devel libcurl-devel boost-devel
    else
        log_error "Gerenciador de pacotes não suportado. Instale manualmente: build-essential, cmake, libssl-dev, libcurl4-openssl-dev, libboost-all-dev"
        exit 1
    fi
}

# --- Instalação de Dependências Python (com fallback) ---

log_info "Verificando e instalando dependências..."

if command -v python3 >/dev/null 2>&1; then
    log_info "Python 3 encontrado. Tentando usar script Python para dependências..."
    wget -O "${INITIAL_DIR}/instalar_deps_multiflowpx.py" https://raw.githubusercontent.com/mycroft440/multiflowpx/refs/heads/main/instalar_deps_multiflowpx.py || { log_error "Falha ao baixar instalar_deps_multiflowpx.py."; install_deps_fallback; }
    chmod +x "${INITIAL_DIR}/instalar_deps_multiflowpx.py" || { log_error "Falha ao dar permissão de execução para instalar_deps_multiflowpx.py."; install_deps_fallback; }
    
    if python3 "${INITIAL_DIR}/instalar_deps_multiflowpx.py"; then
        log_success "Script de dependências Python executado com sucesso."
    else
        log_warning "Script Python falhou. Tentando instalação básica via shell..."
        install_deps_fallback
    fi
else
    log_warning "Python 3 não encontrado. Usando instalação básica via shell..."
    install_deps_fallback
fi

# --- Gerenciamento do Repositório ---

# Define as variáveis do repositório para fácil manutenção
REPO_NAME="multiflowpx"
REPO_URL="https://github.com/MultiFlowPX/multiflowpx.git"

# Verifica se o diretório do repositório já existe para evitar clonagem duplicada
if [ ! -d "$REPO_NAME" ]; then
    log_info "Clonando o repositório $REPO_NAME..."
    git clone "$REPO_URL" || { log_error "Falha ao clonar o repositório $REPO_NAME."; exit 1; }
    cd "$REPO_NAME" || { log_error "Falha ao entrar no diretório $REPO_NAME."; exit 1; }
    log_success "Repositório clonado com sucesso."
else
    log_info "Diretório $REPO_NAME já existe. Pulando a clonagem."
    # Garante que o script continue a execução de dentro do diretório do projeto
    if [[ "$(basename "$(pwd)")" != "$REPO_NAME" ]]; then
        cd "$REPO_NAME" || { log_error "Falha ao entrar no diretório $REPO_NAME."; exit 1; }
    fi
fi



# --- Compilação do Projeto ---

log_info "Compilando o MultiFlowPX Proxy Server..."

# Define o diretório do projeto como o diretório de trabalho atual
PROJECT_DIR="$(pwd)"

# Remove o diretório de build antigo para garantir uma compilação limpa
if [ -d "${PROJECT_DIR}/build" ]; then
    log_info "Removendo diretório de build antigo: ${PROJECT_DIR}/build"
    rm -rf "${PROJECT_DIR}/build"
fi

log_info "Diretório do projeto detectado: ${PROJECT_DIR}"

# Cria e acessa o diretório de build
BUILD_DIR="${PROJECT_DIR}/build"
mkdir -p "${BUILD_DIR}" || { log_error "Falha ao criar diretório de build."; exit 1; }
cd "${BUILD_DIR}" || { log_error "Falha ao entrar no diretório de build."; exit 1; }

# Executa o CMake para configurar o projeto e o make para compilar
cmake .. || { log_error "Falha na configuração do CMake."; exit 1; }
make -j$(nproc) || { log_error "Falha na compilação do projeto."; exit 1; }

log_success "Projeto compilado com sucesso!"

# --- Instalação dos Arquivos ---

# Instala o executável principal no sistema
log_info "Instalando o executável 'proxy' em /usr/local/bin/ ..."
if [ -f "./proxy" ]; then
    cp "./proxy" /usr/local/bin/ || { log_error "Falha ao copiar o executável."; exit 1; }
    chmod +x /usr/local/bin/proxy || { log_error "Falha ao definir permissões do executável."; exit 1; }
    log_success "Executável 'proxy' instalado em /usr/local/bin/."
else
    log_error "Executável 'proxy' não encontrado após a compilação. Instalação falhou."
    exit 1
fi

# Instala o script de menu interativo em Python
log_info "Instalando o script do menu Python em /usr/local/bin/ ..."
if [ -f "${PROJECT_DIR}/proxy_menu.py" ]; then
    cp "${PROJECT_DIR}/proxy_menu.py" /usr/local/bin/proxy_menu || { log_error "Falha ao copiar o script do menu."; exit 1; }
    chmod +x /usr/local/bin/proxy_menu || { log_error "Falha ao definir permissões do script do menu."; exit 1; }
    log_success "Script 'proxy_menu' instalado em /usr/local/bin/."
    
    # Corrige o caminho do executável dentro do script de menu para o caminho de instalação global
    log_info "Corrigindo o caminho do executável no proxy_menu..."
    sed -i 's|self.proxy_path = "./build/proxy"|self.proxy_path = "/usr/local/bin/proxy"|g' /usr/local/bin/proxy_menu || { log_error "Falha ao corrigir o caminho no proxy_menu."; exit 1; }
    log_success "Caminho do executável corrigido no proxy_menu."
else
    log_warning "Script 'proxy_menu.py' não encontrado. O menu interativo não será instalado."
fi

# --- Limpeza Final ---

log_info "Limpando arquivos de build..."
cd "${PROJECT_DIR}" || { log_warning "Falha ao voltar para o diretório do projeto."; }
rm -rf "${BUILD_DIR}" || log_warning "Falha ao remover diretório de build. Limpeza manual pode ser necessária."

# --- Conclusão ---

log_success "Instalação do MultiFlowPX Proxy Server concluída com sucesso!"
log_info "Você pode agora executar o proxy digitando 'proxy' ou o menu interativo 'proxy_menu'."
log_info "Para mais informações, consulte o README.md e o MENU_GUIDE.md."

exit 0


# --- Instalação do Serviço Systemd ---

log_info "Instalando o serviço systemd para o MultiFlowPX..."
if [ -f "${PROJECT_DIR}/multiflowpx.service" ]; then
    cp "${PROJECT_DIR}/multiflowpx.service" /etc/systemd/system/ || { log_error "Falha ao copiar o arquivo de serviço systemd."; exit 1; }
    systemctl daemon-reload || { log_error "Falha ao recarregar daemons do systemd."; exit 1; }
    systemctl enable multiflowpx || { log_error "Falha ao habilitar o serviço multiflowpx."; exit 1; }
    log_success "Serviço systemd 'multiflowpx' instalado e habilitado."
else
    log_warning "Arquivo 'multiflowpx.service' não encontrado. O serviço systemd não será instalado."
fi


