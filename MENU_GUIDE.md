MultiFlowPX Proxy Server

## 📋 Visão Geral

O menu interativo em Python (`proxy_menu.py`) fornece uma interface amigável para controlar o servidor proxy MultiFlowPX sem necessidade de memorizar comandos de linha de comando.

## 🚀 Como Executar

### Pré-requisitos
- Python 3.6 ou superior
- Executável `proxy` compilado no mesmo diretório
- Sistema Linux/Unix

### Execução
```bash
# Navegar para o diretório build
cd dtunnel_proxy/build

# Executar o menu
python3 proxy_menu.py

# Ou tornar executável e rodar diretamente
chmod +x proxy_menu.py
./proxy_menu.py
```

## 🎮 Interface do Menu

### Tela Principal
```
============================================================
    MultiFlowPX Proxy Server - Menu Interativo
    Versão: 1.2.6
    Autor: @DuTra01
============================================================

🔴 Status: SERVIDOR PARADO

📋 Configuração Atual:
   Porta: 8080
   Protocolo: HTTP
   Workers: 4
   Buffer Size: 4096 bytes
   SSH Port: 22
   OpenVPN Port: 1194
   V2Ray Port: 10086

📋 Menu Principal:
1. 🚀 Iniciar Servidor
2. 🛑 Parar Servidor
3. 🔄 Reiniciar Servidor
4. ⚙️  Configuração Básica
5. 🔧 Configuração Avançada
6. 💾 Salvar Configuração
7. 📂 Carregar Configuração
8. 📋 Ver Logs
9. 📖 Ajuda
0. 🚪 Sair

Escolha uma opção:
```

## 📖 Funcionalidades Detalhadas

### 1. 🚀 Iniciar Servidor
- **Função**: Inicia o servidor proxy com as configurações atuais
- **Comportamento**: 
  - Verifica se o servidor já está rodando
  - Constrói o comando com base nas configurações
  - Inicia o processo em background
  - Monitora a saída em tempo real
- **Exemplo de comando gerado**:
  ```bash
  ./proxy --port 8080 --workers 4 --buffer-size 4096 --ssh-port 22 --ulimit 65536 --http --openvpn-port 1194 --v2ray-port 10086
  ```

### 2. 🛑 Parar Servidor
- **Função**: Para o servidor proxy em execução
- **Comportamento**:
  - Verifica se o servidor está rodando
  - Envia sinal SIGTERM (terminação graceful)
  - Aguarda até 5 segundos para parada
  - Força parada com SIGKILL se necessário

### 3. 🔄 Reiniciar Servidor
- **Função**: Para e inicia novamente o servidor
- **Comportamento**:
  - Para o servidor atual (se rodando)
  - Aguarda 1 segundo
  - Inicia novamente com as configurações atuais

### 4. ⚙️ Configuração Básica
Permite configurar os parâmetros principais:

#### Porta do Servidor
- **Padrão**: 8080
- **Faixa**: 1-65535
- **Exemplo**: 9999

#### Protocolo
- **Opções**: HTTP (1) ou HTTPS (2)
- **HTTPS**: Requer caminho para certificado SSL
- **Exemplo**: `/path/to/certificate.pem`

#### Número de Workers
- **Padrão**: 4
- **Mínimo**: 1
- **Recomendado**: Número de CPUs

### 5. 🔧 Configuração Avançada
Permite configurar parâmetros específicos:

#### Buffer Size
- **Padrão**: 4096 bytes
- **Uso**: Tamanho do buffer para transferência de dados

#### Modo SSH Apenas
- **Padrão**: Não
- **Efeito**: Desabilita OpenVPN e V2Ray

#### Portas dos Protocolos
- **SSH Port**: Padrão 22
- **OpenVPN Port**: Padrão 1194
- **V2Ray Port**: Padrão 10086

#### Limite de Arquivos (ulimit)
- **Padrão**: 65536
- **Uso**: Número máximo de arquivos abertos

#### Mensagem de Resposta HTTP
- **Padrão**: `HTTP/1.1 200 OK\r\n\r\n`
- **Uso**: Resposta personalizada para requisições HTTP

### 6. 💾 Salvar Configuração
- **Função**: Salva as configurações atuais em arquivo JSON
- **Arquivo**: `proxy_config.json`
- **Localização**: Diretório atual
- **Formato**:
  ```json
  {
      "port": 8080,
      "workers": 4,
      "buffer_size": 4096,
      "ssh_port": 22,
      "openvpn_port": 1194,
      "v2ray_port": 10086,
      "ulimit": 65536,
      "use_https": false,
      "use_http": true,
      "ssh_only": false,
      "cert_path": "",
      "response_message": "HTTP/1.1 200 OK\\r\\n\\r\\n"
  }
  ```

### 7. 📂 Carregar Configuração
- **Função**: Carrega configurações de arquivo JSON
- **Arquivo**: `proxy_config.json`
- **Comportamento**: Sobrescreve configurações atuais

### 8. 📋 Ver Logs
- **Função**: Mostra logs do servidor em tempo real
- **Comportamento**:
  - Monitora a saída do processo do proxy
  - Exibe logs com prefixo `[PROXY]`
  - Pressione Ctrl+C para voltar ao menu
- **Exemplo de saída**:
  ```
  [PROXY] Starting MultiFlowPX Proxy Server...
  [PROXY] MultiFlowPX Proxy Server v1.2.6
  [PROXY] Author: @DuTra01
  [PROXY] Server running (HTTP) on port 8080
  [PROXY] Workers: 4
  ```

### 9. 📖 Ajuda
- **Função**: Exibe informações detalhadas sobre o menu
- **Conteúdo**:
  - Descrição de cada opção
  - Protocolos suportados
  - Dicas de uso

### 0. 🚪 Sair
- **Função**: Encerra o menu
- **Comportamento**:
  - Para o servidor se estiver rodando
  - Limpa recursos
  - Encerra o script

## 🎯 Indicadores Visuais

### Status do Servidor
- 🟢 **SERVIDOR RODANDO**: Servidor ativo com PID
- 🔴 **SERVIDOR PARADO**: Servidor não está executando

### Mensagens de Feedback
- ✅ **Sucesso**: Operação realizada com êxito
- ❌ **Erro**: Problema encontrado
- ⚠️ **Aviso**: Informação importante
- 🔄 **Processando**: Operação em andamento

## ⌨️ Atalhos e Dicas

### Navegação
- **Enter**: Confirma entrada vazia (usa valor padrão)
- **Ctrl+C**: Cancela operação atual
- **Números**: Seleciona opção do menu

### Configuração Rápida
1. Execute o menu: `python3 proxy_menu.py`
2. Configure básico: Opção 4
3. Inicie servidor: Opção 1
4. Monitore logs: Opção 8

### Uso Avançado
1. Configure avançado: Opção 5
2. Salve configuração: Opção 6
3. Para desenvolvimento: Use porta > 1024
4. Para produção: Configure HTTPS com certificado

## 🔧 Personalização

### Modificar Configurações Padrão
Edite o arquivo `proxy_menu.py` na seção:
```python
self.current_config = {
    "port": 8080,        # Sua porta padrão
    "workers": 4,        # Número de workers
    # ... outras configurações
}
```

### Adicionar Novas Opções
1. Adicione nova entrada no menu principal
2. Implemente a função correspondente
3. Adicione tratamento no loop principal

### Customizar Interface
- Modifique emojis e cores
- Altere mensagens de feedback
- Ajuste layout da tela

## 🐛 Solução de Problemas

### Erro: "Executável 'proxy' não encontrado"
- **Causa**: Script não está no diretório correto
- **Solução**: Execute no diretório `build` onde está o executável

### Erro: "Permission denied" na porta
- **Causa**: Porta < 1024 requer privilégios de root
- **Solução**: Use porta > 1024 ou execute com sudo

### Erro: "Address already in use"
- **Causa**: Porta já está sendo usada
- **Solução**: Mude a porta ou pare o processo que está usando

### Menu não responde
- **Causa**: Processo travado
- **Solução**: Pressione Ctrl+C para forçar saída

### Logs não aparecem
- **Causa**: Servidor não está rodando
- **Solução**: Inicie o servidor primeiro (opção 1)

## 📚 Exemplos de Uso

### Configuração Básica para Desenvolvimento
```
1. Execute: python3 proxy_menu.py
2. Opção 4 (Configuração Básica)
3. Porta: 8080
4. Protocolo: 1 (HTTP)
5. Workers: 4
6. Opção 1 (Iniciar Servidor)
```

### Configuração HTTPS para Produção
```
1. Execute: python3 proxy_menu.py
2. Opção 4 (Configuração Básica)
3. Porta: 443
4. Protocolo: 2 (HTTPS)
5. Certificado: /etc/ssl/certs/server.pem
6. Opção 6 (Salvar Configuração)
7. Opção 1 (Iniciar Servidor)
```

### Modo SSH Apenas
```
1. Execute: python3 proxy_menu.py
2. Opção 5 (Configuração Avançada)
3. SSH apenas: s (sim)
4. SSH Port: 22
5. Opção 1 (Iniciar Servidor)
```

## 🔄 Integração com Scripts

### Automação
O menu pode ser integrado com scripts usando entrada programática:
```bash
# Iniciar servidor automaticamente
echo "1" | python3 proxy_menu.py

# Configurar e iniciar
echo -e "4\n9999\n1\n4\n1" | python3 proxy_menu.py
```

### Monitoramento
```bash
# Verificar se servidor está rodando
ps aux | grep proxy

# Monitorar logs
tail -f proxy.log
```

Este guia fornece uma visão completa do menu interativo, permitindo uso eficiente e personalização conforme necessário.

