#!/bin/bash

# Cores para a saída
VERDE='\033[0;32m'
AMARELO='\033[1;33m'
VERMELHO='\033[0;31m'
NC='\033[0m' # Sem Cor

# Variáveis do Projeto
PROJETO_DIR="/opt/multiflowpx"
REPO_URL="https://github.com/mycroft440/multiflowpx.git"

# Funções de log
log() { echo -e "${AMARELO}[LOG] $1${NC}"; }
sucesso() { echo -e "${VERDE}[SUCESSO] $1${NC}"; }
erro() { echo -e "${VERMELHO}[ERRO] $1${NC}" >&2; exit 1; }

# 1. Verificar privilégios de root
log "Verificando privilégios de root..."
if [ "$(id -u)" -ne 0 ]; then
    erro "Este script precisa ser executado como root. Por favor, use 'sudo bash install.sh'."
fi
sucesso "Executando como root."

# 2. Instalar dependências básicas (git e python3)
log "Atualizando a lista de pacotes e instalando o git e python3..."
apt-get update > /dev/null 2>&1
apt-get install -y git python3 || erro "Falha ao instalar o git ou python3."

# 3. Gerir o diretório do projeto (Clonar ou Atualizar)
if [ -d "$PROJETO_DIR/.git" ]; then
    log "O diretório do projeto já existe. Atualizando o repositório..."
    cd "$PROJETO_DIR" || erro "Não foi possível aceder ao diretório $PROJETO_DIR."
    git pull origin main || erro "Falha ao atualizar o repositório com 'git pull'."
else
    log "Clonando o repositório do projeto para $PROJETO_DIR..."
    git clone "$REPO_URL" "$PROJETO_DIR" || erro "Falha ao clonar o repositório."
    cd "$PROJETO_DIR" || erro "Não foi possível aceder ao diretório $PROJETO_DIR."
fi
sucesso "Código-fonte pronto em $PROJETO_DIR."

# 4. Chamar o script de instalação de dependências Python
log "Executando o script de instalação de dependências Python..."
python3 "$PROJETO_DIR/multiflowproxy/instalar_deps_multiflowpx.py" || erro "Falha ao executar o script de instalação de dependências."
sucesso "Dependências instaladas via instalar_deps_multiflowpx.py."

# 5. Criar link simbólico para o menu
log "Criando link simbólico para o menu do MultiFlowPX..."
MENU_SCRIPT="$PROJETO_DIR/proxy_menu.py"
MENU_ALIAS="/usr/local/bin/g"

if [ -f "$MENU_SCRIPT" ]; then
    chmod +x "$MENU_SCRIPT" || erro "Falha ao adicionar permissão de execução ao script do menu."
    ln -sf "$MENU_SCRIPT" "$MENU_ALIAS" || erro "Falha ao criar o link simbólico para o menu."
    sucesso "Link simbólico 'g' criado para o menu do MultiFlowPX."
else
    erro "Script do menu ($MENU_SCRIPT) não encontrado. Não foi possível criar o link simbólico."
fi

echo -e "\n${VERDE}====================================================="
echo -e " Instalação do MultiFlowPX concluída com sucesso!"
echo -e " O programa foi instalado em $PROJETO_DIR"
echo -e " Para acessar o menu, digite 'g' no terminal."
echo -e "=====================================================${NC}"

