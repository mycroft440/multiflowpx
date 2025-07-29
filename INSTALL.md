MultiFlowPX Proxy Server

Este guia fornece instruções detalhadas para compilar e instalar o DTunnel Proxy Server.

## Requisitos do Sistema

### Sistema Operacional
- Linux (testado no Ubuntu 22.04)
- Arquitetura x86_64
- Kernel 3.2.0 ou superior

### Dependências de Build
- GCC 11+ ou Clang 12+
- CMake 3.10+
- Make

### Bibliotecas Necessárias
- OpenSSL 1.1+ (libssl-dev)
- libcurl 7.0+ (libcurl4-openssl-dev)
- pthread (geralmente incluído no sistema)

## Instalação das Dependências

### Ubuntu/Debian
```bash
# Atualizar repositórios
sudo apt-get update

# Instalar dependências de build
sudo apt-get install -y build-essential cmake

# Instalar bibliotecas
sudo apt-get install -y libssl-dev libcurl4-openssl-dev

# Verificar versões
gcc --version
cmake --version
pkg-config --modversion openssl
pkg-config --modversion libcurl
```

### CentOS/RHEL/Fedora
```bash
# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install cmake openssl-devel libcurl-devel

# Fedora
sudo dnf groupinstall "Development Tools"
sudo dnf install cmake openssl-devel libcurl-devel
```

### Arch Linux
```bash
sudo pacman -S base-devel cmake openssl curl
```

## Compilação

### 1. Preparar o Ambiente
```bash
# Navegar para o diretório do projeto
cd multiflowpx

# Verificar estrutura
ls -la
# Deve mostrar: src/ include/ CMakeLists.txt README.md
```

### 2. Configurar Build
```bash
# Criar diretório de build
mkdir -p build
cd build

# Configurar com CMake
cmake ..

# Verificar configuração
# Deve mostrar: "Configuring done" e "Generating done"
```

### 3. Compilar
```bash
# Compilação paralela (recomendado)
make -j$(nproc)

# Ou compilação sequencial
make

# Verificar sucesso
ls -la proxy
# Deve mostrar o executável 'proxy'
```

### 4. Verificar Compilação
```bash
# Testar help
./proxy --help

# Verificar dependências
ldd proxy
```

## Instalação do Sistema

### Instalação Local (Recomendado)
```bash
# Copiar executável para diretório local
mkdir -p ~/bin
cp proxy ~/bin/

# Adicionar ao PATH (adicionar ao ~/.bashrc)
echo 'export PATH="$HOME/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Testar
proxy --help
```

### Instalação do Sistema (Requer sudo)
```bash
# Instalar via CMake
sudo make install

# Ou instalação manual
sudo cp proxy /usr/local/bin/
sudo chmod +x /usr/local/bin/proxy

# Testar
proxy --help
```

## Configuração Inicial

### 1. Criar Diretório de Configuração
```bash
mkdir -p ~/.config/dtunnel
```

### 2. Certificados SSL (Para HTTPS)
```bash
# Gerar certificado auto-assinado para testes
openssl req -x509 -newkey rsa:4096 -keyout ~/.config/dtunnel/key.pem -out ~/.config/dtunnel/cert.pem -days 365 -nodes

# Combinar certificado e chave (se necessário)
cat ~/.config/dtunnel/cert.pem ~/.config/dtunnel/key.pem > ~/.config/dtunnel/combined.pem
```

### 3. Teste Básico
```bash
# Teste HTTP simples
proxy --port 8080 &
PID=$!

# Testar conexão
curl http://localhost:8080
# Deve retornar: HTTP/1.1 200 OK

# Parar servidor
kill $PID
```

## Resolução de Problemas

### Erro: "command not found"
```bash
# Verificar se está no PATH
which proxy

# Se não estiver, adicionar diretório ao PATH
export PATH="/caminho/para/multiflowpx/build:$PATH"
```

### Erro: "libssl.so not found"
```bash
# Instalar OpenSSL development
sudo apt-get install libssl-dev

# Verificar instalação
pkg-config --libs openssl
```

### Erro: "libcurl.so not found"
```bash
# Instalar libcurl development
sudo apt-get install libcurl4-openssl-dev

# Verificar instalação
pkg-config --libs libcurl
```

### Erro de Compilação: "C++ standard"
```bash
# Verificar versão do GCC
gcc --version

# Se muito antigo, atualizar
sudo apt-get install gcc-11 g++-11
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 100
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 100
```

### Erro: "Permission denied" na porta
```bash
# Usar porta > 1024 para usuários não-root
proxy --port 8080

# Ou usar sudo para portas < 1024
sudo proxy --port 80
```

### Erro: "Address already in use"
```bash
# Verificar processos usando a porta
sudo netstat -tlnp | grep :8080

# Matar processo se necessário
sudo kill -9 <PID>

# Ou usar porta diferente
proxy --port 8081
```

## Configuração de Produção

### 1. Usuário de Sistema
```bash
# Criar usuário dedicado
sudo useradd -r -s /bin/false dtunnel

# Criar diretórios
sudo mkdir -p /etc/dtunnel
sudo mkdir -p /var/log/dtunnel
sudo chown dtunnel:dtunnel /var/log/dtunnel
```

### 2. Certificados de Produção
```bash
# Usar Let's Encrypt ou certificados comerciais
sudo mkdir -p /etc/dtunnel/ssl
sudo chown root:dtunnel /etc/dtunnel/ssl
sudo chmod 750 /etc/dtunnel/ssl

# Copiar certificados
sudo cp cert.pem /etc/dtunnel/ssl/
sudo cp key.pem /etc/dtunnel/ssl/
sudo chmod 640 /etc/dtunnel/ssl/*
```

### 3. Systemd Service (Opcional)
```bash
# Criar arquivo de serviço
sudo tee /etc/systemd/system/dtunnel.service << EOF
[Unit]
Description=DTunnel Proxy Server
After=network.target

[Service]
Type=simple
User=dtunnel
ExecStart=/usr/local/bin/proxy --port 8080 --workers 8
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Habilitar e iniciar
sudo systemctl daemon-reload
sudo systemctl enable dtunnel
sudo systemctl start dtunnel

# Verificar status
sudo systemctl status dtunnel
```

## Verificação da Instalação

### Teste Completo
```bash
# 1. Verificar versão
proxy --help | head -2

# 2. Teste HTTP
proxy --port 8080 &
sleep 2
curl -I http://localhost:8080
kill %1

# 3. Teste HTTPS (se certificados configurados)
proxy --https --cert ~/.config/dtunnel/combined.pem --port 8443 &
sleep 2
curl -k -I https://localhost:8443
kill %1

# 4. Teste validação de token (deve falhar sem token válido)
proxy --token "test" --validate
```

### Logs e Monitoramento
```bash
# Executar com logs
proxy --port 8080 2>&1 | tee dtunnel.log

# Monitorar em tempo real
tail -f dtunnel.log
```

## Desinstalação

### Remover Executável
```bash
# Instalação local
rm ~/bin/proxy

# Instalação do sistema
sudo rm /usr/local/bin/proxy
```

### Remover Configurações
```bash
# Configurações do usuário
rm -rf ~/.config/dtunnel

# Configurações do sistema (se aplicável)
sudo rm -rf /etc/dtunnel
sudo rm -rf /var/log/dtunnel
sudo userdel dtunnel
```

### Remover Serviço Systemd
```bash
sudo systemctl stop dtunnel
sudo systemctl disable dtunnel
sudo rm /etc/systemd/system/dtunnel.service
sudo systemctl daemon-reload
```

## Próximos Passos

Após a instalação bem-sucedida:

1. Leia o README.md para entender o uso
2. Configure certificados SSL para produção
3. Ajuste as configurações conforme necessário
4. Configure monitoramento e logs
5. Implemente backup das configurações

Para suporte adicional, consulte a documentação completa ou abra uma issue no repositório do projeto.

