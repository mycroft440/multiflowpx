#!/bin/bash
set -euo pipefail

# Cores para a saída
VERDE='\033[0;32m'
AMARELO='\033[1;33m'
VERMELHO='\033[0;31m'
NC='\033[0m' # Sem Cor

# Variáveis do Projeto
PROJETO_DIR="/opt/multiflowpx"
REPO_URL="https://github.com/mycroft440/multiflowpx.git"

# Caminhos e nomes alinhados com a nova estrutura
SRC_CPP_DIR="$PROJETO_DIR/multiflowproxy"
BUILD_DIR="$SRC_CPP_DIR/build"
DEPS_SCRIPT="$SRC_CPP_DIR/instalar_deps_multiflowpx.py"

MENU_SRC="$PROJETO_DIR/menu_multiflowproxy.py"
MENU_BIN="/usr/local/bin/multiflowpx_menu"
MENU_ALIAS="/usr/local/bin/g"

SERVICE_NAME="multiflowpx.service"
SERVICE_SRC="$SRC_CPP_DIR/$SERVICE_NAME"
SERVICE_DST="/etc/systemd/system/$SERVICE_NAME"

CONFIG_DIR="/etc/multiflowpx"
CONFIG_FILE="$CONFIG_DIR/config.json"

INSTALL_BIN="/usr/local/bin/multiflowpx_proxy"

# Defaults do config.json (alinhado ao core/menu)
DEFAULT_CONFIG='{
    "mode": [],
    "port": [],
    "host": "127.0.0.1:22",
    "sni": "example.com",
    "workers": 4,
    "buffer_size": 8192,
    "log_level": 1
}'

# Funções de log
log() { echo -e "${AMARELO}[LOG] $1${NC}"; }
sucesso() { echo -e "${VERDE}[SUCESSO] $1${NC}"; }
erro() { echo -e "${VERMELHO}[ERRO] $1${NC}" >&2; exit 1; }

has_cmd() { command -v "$1" >/dev/null 2>&1; }

# 1. Verificar privilégios de root
log "Verificando privilégios de root..."
if [ "$(id -u)" -ne 0 ]; then
    erro "Este script precisa ser executado como root. Por favor, use 'sudo bash install.sh'."
fi
sucesso "Executando como root."

# 2. Instalar dependências básicas
if has_cmd apt-get; then
  log "Atualizando a lista de pacotes e instalando dependências..."
  apt-get update -y > /dev/null 2>&1 || true
  DEBIAN_FRONTEND=noninteractive apt-get install -y git python3 python3-pip build-essential cmake pkg-config || erro "Falha ao instalar dependências com apt-get."
else
  erro "apt-get não encontrado. Instale manualmente: git, python3, python3-pip, build-essential, cmake, pkg-config."
fi
sucesso "Dependências instaladas/verificadas."

# 3. Gerir o diretório do projeto (Clonar ou Atualizar)
if [ -d "$PROJETO_DIR/.git" ]; then
    log "O diretório do projeto já existe. Atualizando o repositório..."
    cd "$PROJETO_DIR" || erro "Não foi possível aceder ao diretório $PROJETO_DIR."
    git pull --rebase origin main || erro "Falha ao atualizar o repositório com 'git pull'."
else
    log "Clonando o repositório do projeto para $PROJETO_DIR..."
    git clone "$REPO_URL" "$PROJETO_DIR" || erro "Falha ao clonar o repositório."
    cd "$PROJETO_DIR" || erro "Não foi possível aceder ao diretório $PROJETO_DIR."
fi
sucesso "Código-fonte pronto em $PROJETO_DIR."

# 4. Instalar dependências Python do projeto
if [ -f "$DEPS_SCRIPT" ]; then
  log "Executando script de dependências Python: $DEPS_SCRIPT"
  python3 "$DEPS_SCRIPT" || erro "Falha ao executar o script de instalação de dependências Python."
  sucesso "Dependências Python instaladas via instalar_deps_multiflowpx.py."
else
  log "Script de dependências Python não encontrado em $DEPS_SCRIPT (pulando)."
fi

# 5. Compilar o projeto C++ (via CMake)
if [ -f "$SRC_CPP_DIR/CMakeLists.txt" ]; then
  log "Compilando projeto C++ com CMake..."
  mkdir -p "$BUILD_DIR"
  cmake -S "$SRC_CPP_DIR" -B "$BUILD_DIR" -DCMAKE_BUILD_TYPE=Release
  cmake --build "$BUILD_DIR" --config Release -j"$(nproc 2>/dev/null || echo 2)"

  log "Localizando binário compilado..."
  CANDIDATE_BIN=""
  for p in \
    "$BUILD_DIR/multiflowpx_proxy" \
    "$BUILD_DIR/src/multiflowpx_proxy" \
    "$BUILD_DIR/multiflowproxy" \
    "$BUILD_DIR/src/multiflowproxy"
  do
    if [ -f "$p" ] && [ -x "$p" ]; then CANDIDATE_BIN="$p"; break; fi
  done

  if [ -z "${CANDIDATE_BIN:-}" ]; then
    CANDIDATE_BIN="$(find "$BUILD_DIR" -type f -executable -name 'multiflow*' | head -n1 || true)"
  fi

  if [ -z "${CANDIDATE_BIN:-}" ]; then
    erro "Não foi possível localizar o binário compilado (padrão multiflow*). Verifique o CMakeLists.txt."
  fi

  log "Instalando binário em $INSTALL_BIN"
  install -d "$(dirname "$INSTALL_BIN")"
  install -m 0755 "$CANDIDATE_BIN" "$INSTALL_BIN"
  sucesso "Binário instalado: $INSTALL_BIN"
else
  erro "CMakeLists.txt não encontrado em $SRC_CPP_DIR. Não é possível compilar o binário."
fi

# 6. Garantir arquivo de configuração
log "Garantindo arquivo de configuração em $CONFIG_FILE"
install -d "$CONFIG_DIR"
if [ ! -f "$CONFIG_FILE" ]; then
  echo "$DEFAULT_CONFIG" > "$CONFIG_FILE"
  sucesso "Config padrão criado."
else
  # Validação leve do JSON; se inválido, regrava default
  if ! python3 - <<'PY' "$CONFIG_FILE"
import json, sys
p = sys.argv[1]
try:
    with open(p, 'r') as f:
        json.load(f)
    print("OK")
except Exception:
    print("BAD")
    sys.exit(1)
PY
  then
    log "Config existente inválido/corrompido. Recriando com defaults."
    echo "$DEFAULT_CONFIG" > "$CONFIG_FILE"
  fi
  sucesso "Config verificado."
fi

# 7. Instalar serviço systemd
if [ -f "$SERVICE_SRC" ]; then
  log "Instalando serviço systemd a partir de $SERVICE_SRC"
  install -m 0644 "$SERVICE_SRC" "$SERVICE_DST"
else
  log "Arquivo de serviço não encontrado em $SERVICE_SRC. Criando unit padrão."
  cat > "$SERVICE_DST" <<EOF
[Unit]
Description=MultiFlowPX Proxy
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root
ExecStart=$INSTALL_BIN --config $CONFIG_FILE
Restart=on-failure
RestartSec=2s
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
EOF
fi

# Força ExecStart correto (caso o unit do repo tenha outro caminho)
if grep -q '^ExecStart=' "$SERVICE_DST"; then
  sed -i "s#^ExecStart=.*#ExecStart=$INSTALL_BIN --config $CONFIG_FILE#g" "$SERVICE_DST" || true
fi

if has_cmd systemctl; then
  log "Recarregando daemon do systemd e habilitando serviço..."
  systemctl daemon-reload
  systemctl enable "$SERVICE_NAME" || true
else
  log "systemctl não encontrado. Pulos relacionados ao serviço."
fi
sucesso "Serviço instalado em $SERVICE_DST."

# 8. Instalar o menu CLI e criar alias
log "Instalando menu CLI..."
if [ -f "$MENU_SRC" ]; then
  install -m 0755 "$MENU_SRC" "$MENU_BIN"
  ln -sf "$MENU_BIN" "$MENU_ALIAS"
  sucesso "Menu instalado: $MENU_BIN"
  sucesso "Alias criado: $MENU_ALIAS -> $MENU_BIN (use 'g' para abrir o menu)"
else
  erro "Script do menu ($MENU_SRC) não encontrado."
fi

# 9. Iniciar/Restartar serviço
if has_cmd systemctl; then
  log "Iniciando (ou reiniciando) o serviço..."
  systemctl restart "$SERVICE_NAME" || systemctl start "$SERVICE_NAME" || true
  systemctl status "$SERVICE_NAME" --no-pager -l || true
fi

echo -e "\n${VERDE}====================================================="
echo -e " Instalação do MultiFlowPX concluída com sucesso!"
echo -e " Diretório do projeto: $PROJETO_DIR"
echo -e " Binário: $INSTALL_BIN"
echo -e " Serviço: $SERVICE_NAME (systemd)"
echo -e " Config:  $CONFIG_FILE"
echo -e " Menu:    $MENU_BIN (atalho: 'g')"
echo -e " Para acessar o menu, digite: g"
echo -e "===================================================== ${NC}"
