#!/bin/bash

# Cores para a saída
VERDE=\'\033[0;32m\'
AMARELO=\'\033[1;33m\'
VERMELHO=\'\033[0;31m\'
NC=\'\033[0m\' # Sem Cor

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
    erro "Este script precisa ser executado como root. Por favor, use \'sudo bash install.sh\'."
fi
sucesso "Executando como root."

# 2. Instalar dependências básicas (git)
log "Atualizando a lista de pacotes e instalando o git..."
apt-get update > /dev/null 2>&1
apt-get install -y git || erro "Falha ao instalar o git."

# 3. Gerir o diretório do projeto (Clonar ou Atualizar)
if [ -d "$PROJETO_DIR/.git" ]; then
    log "O diretório do projeto já existe. Atualizando o repositório..."
    cd "$PROJETO_DIR" || erro "Não foi possível aceder ao diretório $PROJETO_DIR."
    git pull origin main || erro "Falha ao atualizar o repositório com \'git pull\'."
else
    log "Clonando o repositório do projeto para $PROJETO_DIR..."
    git clone "$REPO_URL" "$PROJETO_DIR" || erro "Falha ao clonar o repositório."
    cd "$PROJETO_DIR" || erro "Não foi possível aceder ao diretório $PROJETO_DIR."
fi
sucesso "Código-fonte pronto em $PROJETO_DIR."

# 4. Instalar dependências de compilação
log "Instalando dependências de compilação (build-essential, cmake, libssl-dev, libboost-all-dev, libcurl4-openssl-dev)..."
apt-get install -y build-essential cmake libssl-dev libboost-all-dev libcurl4-openssl-dev || erro "Falha ao instalar as dependências de compilação."
sucesso "Dependências de compilação instaladas."

# 5. Compilar o projeto
log "Navegando para o diretório do proxy para compilação..."
cd multiflowproxy || erro "Não foi possível encontrar o subdiretório \'multiflowproxy\'."

log "Criando o diretório de compilação..."
mkdir -p build
cd build || erro "Não foi possível entrar no diretório \'build\'."

log "Executando o CMake..."
cmake .. || erro "O CMake falhou."
log "Compilando o projeto com o make..."
make || erro "A compilação (make) falhou."
sucesso "Projeto compilado com sucesso."

# 6. Instalar o binário e o serviço
log "Instalando o binário \'multiflowpx\' em /usr/local/bin/..."
install -m 755 proxy /usr/local/bin/proxy || erro "Falha ao instalar o binário."
sucesso "Binário instalado."

log "Instalando o serviço systemd..."
cd .. # Voltar para o diretório multiflowproxy

# Criar o arquivo de serviço com o conteúdo corrigido
cat <<EOF > /etc/systemd/system/multiflowpx.service
[Unit]
Description=MultiFlowPX Proxy Server
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/proxy
Restart=on-failure
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF

sucesso "Ficheiro de serviço instalado."

# 7. Habilitar e iniciar o serviço
log "Recarregando o systemd, habilitando e iniciando o serviço multiflowpx..."
systemctl daemon-reload || erro "Falha ao recarregar o systemd."
systemctl enable multiflowpx.service || erro "Falha ao habilitar o serviço."
systemctl start multiflowpx.service || erro "Falha ao iniciar o serviço."

# 8. Verificar o status do serviço
log "Verificando o status do serviço..."
if systemctl is-active --quiet multiflowpx.service; then
    sucesso "O serviço multiflowpx está ativo e a ser executado."
else
    erro "O serviço multiflowpx falhou ao iniciar. Verifique os logs com \'journalctl -u multiflowpx\'."
fi

# 9. Criar link simbólico para o menu
log "Criando link simbólico para o menu do MultiFlowPX..."
MENU_SCRIPT="$PROJETO_DIR/proxy_menu.py"
MENU_ALIAS="/usr/local/bin/g"

if [ -f "$MENU_SCRIPT" ]; then
    chmod +x "$MENU_SCRIPT" || erro "Falha ao adicionar permissão de execução ao script do menu."
    ln -sf "$MENU_SCRIPT" "$MENU_ALIAS" || erro "Falha ao criar o link simbólico para o menu."
    sucesso "Link simbólico \'g\' criado para o menu do MultiFlowPX."
else
    erro "Script do menu ($MENU_SCRIPT) não encontrado. Não foi possível criar o link simbólico.\"
fi

echo -e "\n${VERDE}====================================================="
echo -e " Instalação do MultiFlowPX concluída com sucesso!"
echo -e " O programa foi instalado em $PROJETO_DIR"
echo -e " O comando \'multiflowpx\' agora está disponível no sistema."
echo -e " Para acessar o menu, digite \'g\' no terminal."
echo -e "=====================================================${NC}"
