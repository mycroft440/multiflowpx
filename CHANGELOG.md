# CHANGELOG MultiFlowPX

Este documento detalha as modificações e melhorias implementadas no projeto MultiFlowPX.

## Versão 1.1.0 (29 de Julho de 2025)

### Melhorias no Código C++

*   **Gerenciamento de Clientes (`Server.h`, `Server.cpp`):**
    *   Implementado o método `cleanupInactiveClients()` na classe `Server` para remover clientes inativos do vetor `m_clients`, garantindo a liberação de recursos e evitando vazamentos de memória. Este método é chamado periodicamente no loop principal do servidor.
    *   Refatorado o uso de `std::make_shared` para a criação de objetos `Client`, promovendo uma alocação de memória mais eficiente e segura.

*   **Const-correctness (`Server.h`, `Server.cpp`):**
    *   Aplicado `const-correctness` a métodos como `isConnected()` e `getSocketFd()` na classe `Server`, indicando que esses métodos não modificam o estado do objeto. Isso melhora a segurança do código e permite otimizações do compilador.

*   **Sistema de Logging (`Logger.h`, `Server.cpp`, `main.cpp`):**
    *   Introduzida uma biblioteca de logging simples (`Logger.h`) baseada em macros (`LOG_INFO`, `LOG_WARNING`, `LOG_ERROR`).
    *   Substituídas as chamadas diretas a `std::cout` e `std::cerr` por essas macros de logging em `Server.cpp` e `main.cpp`, centralizando e padronizando a saída de logs com timestamps.

### Melhorias nos Scripts Python

*   **Integração com Systemd (`proxy_menu.py`, `multiflowpx.service`):**
    *   Criado um arquivo de serviço `systemd` (`multiflowpx.service`) para gerenciar o ciclo de vida do servidor proxy (iniciar, parar, reiniciar, verificar status).
    *   Refatorado o `proxy_menu.py` para utilizar comandos `systemctl` para interagir com o serviço `multiflowpx.service`, delegando o gerenciamento de processos ao `systemd` e tornando o serviço mais robusto e resiliente.
    *   Removidas as lógicas manuais de PID e arquivo de log do `proxy_menu.py`, uma vez que o `systemd` agora gerencia esses aspectos.
    *   Atualizada a função de desinstalação (`menu_uninstall`) para remover o serviço `systemd` e os arquivos relacionados.

*   **Validação de Entrada (`proxy_menu.py`):**
    *   Adicionada validação de entrada para as configurações numéricas (`port`, `workers`, `buffer_size`, `log_level`) nos submenus de configuração (`submenu_config_basic`, `submenu_config_advanced`), garantindo que apenas valores válidos sejam aceitos e prevenindo erros de conversão.

### Melhorias nos Scripts Shell

*   **Instalação de Dependências (`install.sh`, `instalar_deps_multiflowpx.py`):**
    *   Implementada uma lógica de fallback no `install.sh` para a instalação de dependências. Se o script Python (`instalar_deps_multiflowpx.py`) falhar ou o Python 3 não estiver disponível, o `install.sh` tentará instalar as dependências essenciais diretamente via gerenciador de pacotes do sistema (apt, yum, dnf).
    *   Aprimorada a robustez do processo de instalação, garantindo que o projeto possa ser compilado e executado mesmo em ambientes com configurações de Python não ideais.




