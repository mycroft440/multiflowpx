#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import json
import time

# --- Constantes de Configuração ---
# Arquivo para salvar as configurações do proxy.
CONFIG_FILE = "/etc/multiflowpx/config.json"
# Caminho para o script de instalação. Usado para a opção de (re)instalar.
INSTALL_SCRIPT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "install.sh")

# --- Cores para o Terminal ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ProxyMenu:
    """
    Classe que gerencia o menu interativo para o MultiFlowPX Proxy Server.
    """

    def __init__(self):

        # Dicionário para armazenar as configurações atuais.
        self.config = self.load_config()

    # --- Funções Utilitárias ---

    def clear_screen(self):
        """Limpa a tela do terminal."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title):
        """Exibe um cabeçalho padronizado."""
        self.clear_screen()
        print(f"{Colors.HEADER}=================================================={Colors.ENDC}")
        print(f"{Colors.HEADER}      MultiFlowPX Proxy Server - {title}{Colors.ENDC}")
        print(f"{Colors.HEADER}=================================================={Colors.ENDC}\n")

    def check_root(self):
        """Verifica se o script está sendo executado como root."""
        if os.geteuid() != 0:
            print(f"{Colors.FAIL}Erro: Esta operação requer privilégios de root. Execute com 'sudo'.{Colors.ENDC}")
            input("\nPressione Enter para continuar...")
            return False
        return True

    def is_running(self):
        """Verifica se o processo do proxy está em execução."""
        return subprocess.run(["systemctl", "is-active", "--quiet", "multiflowpx.service"]).returncode == 0

    def load_config(self):
        """Carrega as configurações do arquivo JSON."""
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"{Colors.WARNING}Aviso: Não foi possível carregar o arquivo de configuração: {e}{Colors.ENDC}")
        # Retorna uma configuração padrão se o arquivo não existir ou for inválido.
        return {
            "mode": "ssh", "port": 8080, "host": "127.0.0.1:22", "sni": "example.com",
            "workers": 4, "buffer_size": 8192, "log_level": 1
        }

    def save_config(self):
        """Salva as configurações atuais no arquivo JSON."""
        if not self.check_root(): return
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"\n{Colors.GREEN}Configurações salvas com sucesso em {CONFIG_FILE}{Colors.ENDC}")
        except IOError as e:
            print(f"\n{Colors.FAIL}Erro ao salvar as configurações: {e}{Colors.ENDC}")

    # --- Funções de Gerenciamento do Proxy ---

    def start_proxy(self):
        """Inicia o processo do proxy com as configurações salvas."""
        if not self.check_root(): return
        if self.is_running():
            print(f"{Colors.WARNING}O proxy já está em execução.{Colors.ENDC}")
            return

        try:
            subprocess.run(["systemctl", "start", "multiflowpx.service"], check=True)
            print(f"{Colors.GREEN}Proxy iniciado com sucesso via systemd.{Colors.ENDC}")
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}Erro ao iniciar o proxy via systemd: {e}{Colors.ENDC}")

    def stop_proxy(self):
        """Para o processo do proxy."""
        if not self.check_root(): return
        if not self.is_running():
            print(f"{Colors.WARNING}O proxy não está em execução.{Colors.ENDC}")
            return

        try:
            subprocess.run(["systemctl", "stop", "multiflowpx.service"], check=True)
            print(f"{Colors.GREEN}Proxy parado com sucesso via systemd.{Colors.ENDC}")
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}Erro ao parar o proxy via systemd: {e}{Colors.ENDC}")

    # --- Menus ---

    def main_menu(self):
        """Exibe o menu principal."""
        while True:
            status = f"{Colors.GREEN}Ativo{Colors.ENDC}" if self.is_running() else f"{Colors.FAIL}Inativo{Colors.ENDC}"
            self.print_header(f"Menu Principal (Status: {status})")
            print("1. Instalar e Configurar Proxy")
            print("2. Iniciar/Parar Proxy")
            print("3. Reiniciar Proxy")
            print("4. Desinstalar Completamente")
            print("5. Ver Logs do Proxy")
            print("6. Ver Configurações Atuais")
            print("7. Sair")
            choice = input("\nEscolha uma opção: ")

            if choice == '1':
                self.menu_install_configure()
            elif choice == '2':
                if self.is_running():
                    self.stop_proxy()
                else:
                    self.start_proxy()
            elif choice == '3':
                self.print_header("Reiniciar Proxy")
                self.stop_proxy()
                time.sleep(1)
                self.start_proxy()
            elif choice == '4':
                self.menu_uninstall()
            elif choice == '5':
                self.view_logs()
            elif choice == '6':
                self.view_current_config()
            elif choice == '7':
                sys.exit(0)
            else:
                print(f"{Colors.FAIL}Opção inválida. Tente novamente.{Colors.ENDC}")
            
            if choice in ['2', '3', '4', '5', '6']:
                input("\nPressione Enter para voltar ao menu...")

    def menu_install_configure(self):
        """Menu para instalação e configuração."""
        while True:
            self.print_header("Instalar e Configurar")
            print("1. Instalar / Reinstalar Proxy (Executar install.sh)")
            print("2. Configuração Básica")
            print("3. Configuração Avançada")
            print("4. Salvar Configurações e Iniciar Proxy")
            print("5. Voltar ao Menu Principal")
            choice = input("\nEscolha uma opção: ")

            if choice == '1':
                self.install_script()
            elif choice == '2':
                self.submenu_config_basic()
            elif choice == '3':
                self.submenu_config_advanced()
            elif choice == '4':
                self.save_config()
                print("\nReiniciando o proxy para aplicar as novas configurações...")
                self.stop_proxy()
                time.sleep(1)
                self.start_proxy()
            elif choice == '5':
                break
            else:
                print(f"{Colors.FAIL}Opção inválida.{Colors.ENDC}")
            
            if choice in ['1', '2', '3', '4']:
                input("\nPressione Enter para continuar...")

    def submenu_config_basic(self):
        """Submenu para as configurações essenciais."""
        self.print_header("Configuração Básica")
        
        # Modo de Conexão
        self.config['mode'] = input(f"Modo de conexão [ssh, ssl, openvpn, v2ray] (atual: {self.config.get('mode')}): ") or self.config.get('mode')
        # Porta Local
        self.config['port'] = int(input(f"Porta de escuta local (atual: {self.config.get('port')}): ") or self.config.get('port'))
        # Host Remoto
        self.config['host'] = input(f"Host e porta remotos (ex: 127.0.0.1:22) (atual: {self.config.get('host')}): ") or self.config.get('host')
        # SNI
        self.config['sni'] = input(f"SNI (Server Name Indication) (atual: {self.config.get('sni')}): ") or self.config.get('sni')
        
        self.save_config()

    def submenu_config_advanced(self):
        """Submenu para configurações avançadas."""
        self.print_header("Configuração Avançada")

        # Workers
        self.config['workers'] = int(input(f"Número de workers (threads) (atual: {self.config.get('workers')}): ") or self.config.get('workers'))
        # Buffer Size
        self.config['buffer_size'] = int(input(f"Tamanho do buffer (bytes) (atual: {self.config.get('buffer_size')}): ") or self.config.get('buffer_size'))
        # Log Level
        self.config['log_level'] = int(input(f"Nível de log [0-3] (atual: {self.config.get('log_level')}): ") or self.config.get('log_level'))

        self.save_config()

    def install_script(self):
        """Executa o script de instalação."""
        self.print_header("Instalação")
        if not self.check_root(): return
        
        if not os.path.exists(INSTALL_SCRIPT_PATH):
            print(f"{Colors.FAIL}Erro: Script 'install.sh' não encontrado em '{INSTALL_SCRIPT_PATH}'.{Colors.ENDC}")
            return
            
        try:
            print(f"Executando {INSTALL_SCRIPT_PATH}...")
            # Dá permissão de execução e roda o script.
            subprocess.run(['chmod', '+x', INSTALL_SCRIPT_PATH], check=True)
            subprocess.run(['bash', INSTALL_SCRIPT_PATH], check=True)
            print(f"{Colors.GREEN}\nScript de instalação concluído com sucesso!{Colors.ENDC}")
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}\nOcorreu um erro durante a execução do script de instalação: {e}{Colors.ENDC}")

    def menu_uninstall(self):
        """Executa a desinstalação completa."""
        self.print_header("Desinstalar Completamente")
        if not self.check_root(): return

        print(f"{Colors.WARNING}AVISO: Esta ação removerá permanentemente o MultiFlowPX e todas as suas configurações.{Colors.ENDC}")
        confirm = input("Tem certeza que deseja continuar? [s/N]: ").lower()

        if confirm == 's':
            print("\nIniciando desinstalação...")
            self.stop_proxy()
            
            # Para e desabilita o serviço systemd
            try:
                subprocess.run(["systemctl", "stop", "multiflowpx.service"], check=False)
                subprocess.run(["systemctl", "disable", "multiflowpx.service"], check=False)
                print("Serviço systemd parado e desabilitado.")
            except Exception as e:
                print(f"{Colors.WARNING}Aviso: Erro ao parar/desabilitar serviço: {e}{Colors.ENDC}")
            
            files_to_remove = ["/usr/local/bin/proxy", "/usr/local/bin/proxy_menu", "/etc/systemd/system/multiflowpx.service", CONFIG_FILE]
            dirs_to_remove = [os.path.dirname(CONFIG_FILE)]

            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"Removido: {file_path}")
                    except OSError as e:
                        print(f"{Colors.FAIL}Erro ao remover {file_path}: {e}{Colors.ENDC}")
            
            for dir_path in dirs_to_remove:
                 if os.path.exists(dir_path) and not os.listdir(dir_path):
                    try:
                        os.rmdir(dir_path)
                        print(f"Removido diretório: {dir_path}")
                    except OSError as e:
                        print(f"{Colors.FAIL}Erro ao remover diretório {dir_path}: {e}{Colors.ENDC}")
            
            # Recarrega os daemons do systemd
            try:
                subprocess.run(["systemctl", "daemon-reload"], check=True)
                print("Daemons do systemd recarregados.")

            print(f"\n{Colors.GREEN}Desinstalação concluída.{Colors.ENDC}")
            # Sai do script após a desinstalação.
            sys.exit(0)
        else:
            print("\nDesinstalação cancelada.")

    def view_logs(self):
        """Exibe os logs do proxy em tempo real."""
        self.print_header("Logs do Proxy")
        try:
            print("Exibindo logs do serviço via journalctl. Pressione Ctrl+C para sair.")
            subprocess.run(["journalctl", "-u", "multiflowpx.service", "-f"])
        except KeyboardInterrupt:
            print("\nSaindo da visualização de logs.")
        except Exception as e:
            print(f"{Colors.FAIL}Erro ao visualizar logs: {e}{Colors.ENDC}")


if __name__ == "__main__":
    menu = ProxyMenu()
    try:
        menu.main_menu()
    except KeyboardInterrupt:
        print("\nSaindo do menu...")
        sys.exit(0)


    def view_current_config(self):
        """Exibe as configurações atuais do proxy."""
        self.print_header("Configurações Atuais")
        if not self.config:
            print(f"{Colors.WARNING}Nenhuma configuração carregada. Por favor, configure o proxy primeiro.{Colors.ENDC}")
            return
        
        print(json.dumps(self.config, indent=4))


