#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiFlowPX Proxy Server Manager
Sistema de gerenciamento para servidor proxy MultiFlowPX com interface CLI interativa.
"""

import os
import sys
import subprocess
import json
import time
import shutil
import re
from functools import wraps
from typing import Dict, List, Optional, Any

# --- Constantes de Configuração ---
CONFIG_FILE = "/etc/multiflowpx/config.json"
MIN_PORT = 1
MAX_PORT = 65535
DEFAULT_WORKERS = 4
DEFAULT_BUFFER_SIZE = 8192
MIN_LOG_LEVEL = 0
MAX_LOG_LEVEL = 2

# --- Cores para o Terminal ---
class Colors:
    """Classe para gerenciar cores ANSI do terminal."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# --- Decorators ---
def requires_root(func):
    """Decorator para métodos que requerem privilégios root."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.check_root():
            return None
        return func(self, *args, **kwargs)
    return wrapper

def requires_systemctl(func):
    """Decorator para métodos que requerem systemctl."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.service_manager.is_available():
            self._notify_systemctl_unavailable()
            return None
        return func(self, *args, **kwargs)
    return wrapper

class ConfigManager:
    """Gerencia as configurações do proxy."""
    
    def __init__(self):
        self.default_config = {
            "mode": [],
            "port": [],
            "host": "127.0.0.1:22",
            "sni": "example.com",
            "workers": DEFAULT_WORKERS,
            "buffer_size": DEFAULT_BUFFER_SIZE,
            "log_level": 1
        }
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Carrega as configurações do arquivo JSON de forma robusta."""
        config = self.default_config.copy()
        
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    loaded_config = json.load(f)
                    
                for key, default_value in self.default_config.items():
                    if key in loaded_config and isinstance(loaded_config[key], type(default_value)):
                        config[key] = loaded_config[key]
                    else:
                        print(f"{Colors.WARNING}[!] Aviso: Chave '{key}' ausente ou com tipo inválido. Usando valor padrão.{Colors.ENDC}")
        except (IOError, json.JSONDecodeError) as e:
            print(f"{Colors.WARNING}[!] Aviso: Não foi possível carregar configuração: {e}. Usando padrão.{Colors.ENDC}")
        
        # Validação adicional para listas
        for key in ['port', 'mode']:
            if not isinstance(config.get(key), list):
                config[key] = self.default_config[key]
        
        return config
    
    def save_config(self) -> bool:
        """Salva as configurações atuais no arquivo JSON."""
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"\n{Colors.GREEN}[✓] Configurações salvas com sucesso em {CONFIG_FILE}{Colors.ENDC}")
            return True
        except IOError as e:
            print(f"\n{Colors.FAIL}[!] Erro ao salvar as configurações: {e}{Colors.ENDC}")
            return False

class UIHelper:
    """Classe auxiliar para interface do usuário."""
    
    @staticmethod
    def clear_screen():
        """Limpa a tela do terminal."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def strip_ansi_codes(text: str) -> str:
        """Remove códigos ANSI para cálculo correto de largura."""
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    @staticmethod
    def pad_ansi_text(text: str, width: int) -> str:
        """Preenche texto com códigos ANSI para largura específica."""
        clean_text = UIHelper.strip_ansi_codes(text)
        padding_needed = width - len(clean_text)
        if padding_needed > 0:
            return text + ' ' * padding_needed
        return text
    
    @staticmethod
    def print_header(title: str):
        """Exibe um cabeçalho padronizado."""
        UIHelper.clear_screen()
        print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.CYAN}║{Colors.BOLD}           MULTIFLOWPX PROXY SERVER MANAGER                  {Colors.CYAN}║{Colors.ENDC}")
        print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════════╣{Colors.ENDC}")
        print(f"{Colors.CYAN}║  {Colors.HEADER}{title:^58}  {Colors.CYAN}║{Colors.ENDC}")
        print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")
    
    @staticmethod
    def print_divider():
        """Imprime um divisor visual."""
        print(f"{Colors.CYAN}{'─' * 64}{Colors.ENDC}")
    
    @staticmethod
    def validate_port(port_str: str) -> Optional[int]:
        """Valida e retorna uma porta ou None se inválida."""
        try:
            port = int(port_str)
            if MIN_PORT <= port <= MAX_PORT:
                return port
            print(f"\n{Colors.FAIL}[!] Porta deve estar entre {MIN_PORT} e {MAX_PORT}.{Colors.ENDC}")
        except ValueError:
            print(f"\n{Colors.FAIL}[!] Entrada inválida. Digite um número.{Colors.ENDC}")
        return None

class ServiceManager:
    """Gerencia operações relacionadas ao serviço systemd."""
    
    def __init__(self):
        self.systemctl_path = shutil.which("systemctl")
    
    def is_available(self) -> bool:
        """Verifica se systemctl está disponível."""
        return bool(self.systemctl_path)
    
    def is_running(self) -> bool:
        """Verifica se o serviço está em execução."""
        if not self.systemctl_path:
            return False
        result = subprocess.run(
            [self.systemctl_path, "is-active", "--quiet", "multiflowpx.service"],
            capture_output=True
        )
        return result.returncode == 0
    
    def start(self) -> bool:
        """Inicia o serviço."""
        try:
            subprocess.run([self.systemctl_path, "start", "multiflowpx.service"], check=True)
            print(f"\n{Colors.GREEN}[✓] Proxy iniciado com sucesso via systemd.{Colors.ENDC}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n{Colors.FAIL}[!] Erro ao iniciar o proxy: {e}{Colors.ENDC}")
            return False
    
    def stop(self) -> bool:
        """Para o serviço."""
        try:
            subprocess.run([self.systemctl_path, "stop", "multiflowpx.service"], check=True)
            print(f"\n{Colors.GREEN}[✓] Proxy parado com sucesso via systemd.{Colors.ENDC}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n{Colors.FAIL}[!] Erro ao parar o proxy: {e}{Colors.ENDC}")
            return False
    
    def restart(self) -> bool:
        """Reinicia o serviço."""
        print(f"{Colors.WARNING}Reiniciando o serviço...{Colors.ENDC}")
        self.stop()
        time.sleep(1)
        return self.start()

class ProxyMenu:
    """Classe principal que gerencia o menu interativo para o MultiFlowPX Proxy Server."""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.service_manager = ServiceManager()
        self.ui = UIHelper()
        self.config = self.config_manager.config
    
    # --- Métodos de Verificação ---
    
    def check_root(self) -> bool:
        """Verifica se o script está sendo executado como root."""
        if not hasattr(os, 'geteuid'):
            print(f"\n{Colors.WARNING}[!] Aviso: Não foi possível verificar privilégios de root.{Colors.ENDC}")
            return True
        
        if os.geteuid() != 0:
            print(f"\n{Colors.FAIL}[!] Erro: Esta operação requer privilégios de root. Execute com 'sudo'.{Colors.ENDC}")
            input("\n    Pressione Enter para continuar...")
            return False
        return True
    
    def _notify_systemctl_unavailable(self):
        """Informa ao usuário que o systemctl não está disponível."""
        print(f"\n{Colors.FAIL}[!] Erro: O comando 'systemctl' não foi encontrado.{Colors.ENDC}")
        print(f"{Colors.WARNING}Este script requer um sistema baseado em systemd.")
        print(f"As funções de gerenciamento de serviço estão desativadas.{Colors.ENDC}")
    
    # --- Métodos de Entrada do Usuário ---
    
    def _ask_ssl_domain(self) -> str:
        """Pergunta o domínio para emissão de certificado quando SSL for selecionado."""
        self.ui.print_divider()
        print(f"{Colors.WARNING}CONFIGURAÇÃO DE CERTIFICADO SSL{Colors.ENDC}\n")
        print("Digite o seu domínio que é apontado para o seu servidor para")
        print("que se gere um certificado funcional para o mesmo.")
        self.ui.print_divider()
        return input(f"{Colors.BOLD}Digite [exemplo: mycroft.multflowmanager.xyz]:{Colors.ENDC} ").strip()
    
    def _ask_for_install_port(self) -> int:
        """Pergunta e valida a porta principal durante a instalação."""
        self.ui.print_divider()
        print(f"{Colors.BOLD}CONFIGURAÇÃO DA PORTA PRINCIPAL{Colors.ENDC}")
        
        while True:
            port_input = input(f"{Colors.BOLD}Digite a porta que deseja usar para o serviço: {Colors.ENDC}")
            port = self.ui.validate_port(port_input)
            if port:
                return port
    
    def _ask_for_protocols(self) -> List[str]:
        """Pergunta e valida a combinação de protocolos."""
        self.ui.print_divider()
        print(f"{Colors.BOLD}CONFIGURAÇÃO DOS PROTOCOLOS{Colors.ENDC}\n")
        
        protocol_map = {
            '1': (['ssh', 'openvpn', 'v2ray'], "ssh, openvpn, v2ray"),
            '2': (['ssh', 'openvpn', 'v2ray', 'ssl'], "ssh, openvpn, v2ray e ssl"),
            '3': (['ssh', 'v2ray'], "ssh e v2ray"),
            '4': (['ssh', 'openvpn'], "ssh e openvpn"),
            '5': (['ssh', 'ssl'], "ssh e ssl"),
            '6': (['ssh'], "Apenas SSH"),
            '7': (['openvpn'], "Apenas OpenVPN")
        }
        
        print("Em qual protocolo deseja utilizar o serviço?")
        for key, (_, text) in protocol_map.items():
            print(f"  [{Colors.BOLD}{key}{Colors.ENDC}] {text}")
        
        while True:
            choice = input(f"\n{Colors.BOLD}Escolha uma opção (1-7): {Colors.ENDC}")
            if choice in protocol_map:
                protocols, _ = protocol_map[choice]
                
                if 'ssl' in protocols:
                    domain = self._ask_ssl_domain()
                    if not domain:
                        print(f"\n{Colors.WARNING}[!] Domínio não informado. SSL não será ativado.{Colors.ENDC}")
                        protocols.remove('ssl')
                    else:
                        self.config["sni"] = domain
                
                return protocols
            else:
                print(f"\n{Colors.FAIL}[!] Opção inválida. Tente novamente.{Colors.ENDC}")
    
    def save_config(self) -> bool:
        """Salva as configurações com verificação de root."""
        if not self.check_root():
            return False
        return self.config_manager.save_config()
    
    # --- Métodos de Gerenciamento do Proxy ---
    
    @requires_systemctl
    @requires_root
    def start_proxy(self):
        """Inicia o processo do proxy."""
        if self.service_manager.is_running():
            print(f"\n{Colors.WARNING}[!] O proxy já está em execução.{Colors.ENDC}")
            return
        self.service_manager.start()
    
    @requires_systemctl
    @requires_root
    def stop_proxy(self):
        """Para o processo do proxy."""
        if not self.service_manager.is_running():
            print(f"\n{Colors.WARNING}[!] O proxy não está em execução.{Colors.ENDC}")
            return
        self.service_manager.stop()
    
    @requires_systemctl
    @requires_root
    def restart_proxy(self):
        """Reinicia o processo do proxy."""
        self.ui.print_header("REINICIAR PROXY")
        self.service_manager.restart()

    @requires_root
    @requires_systemctl
    def install_proxy_binaries(self):
        """Compila e instala o binário do proxy."""
        self.ui.print_header("INSTALAR BINÁRIOS DO PROXY")
        
        # Navegar para o diretório do projeto
        proxy_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "multiflowproxy")
        
        if not os.path.isdir(proxy_dir):
            print(f"{Colors.FAIL}[!] Erro: Diretório do proxy não encontrado em {proxy_dir}{Colors.ENDC}")
            return False

        print(f"{Colors.CYAN}Navegando para {proxy_dir}...{Colors.ENDC}")
        os.chdir(proxy_dir)

        # Limpar compilações anteriores
        if os.path.exists("build"):
            print(f"{Colors.WARNING}Removendo diretório de build existente...{Colors.ENDC}")
            shutil.rmtree("build")

        print(f"{Colors.CYAN}Criando diretório de compilação...{Colors.ENDC}")
        os.makedirs("build", exist_ok=True)
        os.chdir("build")

        print(f"{Colors.CYAN}Executando CMake...{Colors.ENDC}")
        if not self._run_command(["cmake", ".."]):
            print(f"{Colors.FAIL}[!] Erro: CMake falhou.{Colors.ENDC}")
            return False

        print(f"{Colors.CYAN}Compilando o projeto com make...{Colors.ENDC}")
        if not self._run_command(["make"]):
            print(f"{Colors.FAIL}[!] Erro: A compilação (make) falhou.{Colors.ENDC}")
            return False

        print(f"{Colors.CYAN}Instalando o binário 'proxy' em /usr/local/bin/multiflowpx_proxy...{Colors.ENDC}")
        # O nome do executável é 'proxy' conforme CMakeLists.txt
        if not self._run_command(["install", "-m", "755", "proxy", "/usr/local/bin/multiflowpx_proxy"]):
            print(f"{Colors.FAIL}[!] Erro: Falha ao instalar o binário.{Colors.ENDC}")
            return False
        
        print(f"{Colors.GREEN}[✓] Binário 'multiflowpx_proxy' instalado com sucesso!{Colors.ENDC}")
        return True

    @requires_root
    @requires_systemctl
    def install_systemd_service(self):
        """Instala e habilita o serviço systemd para o proxy."""
        self.ui.print_header("INSTALAR SERVIÇO SYSTEMD")
        
        service_file_content = """
[Unit]
Description=MultiFlowPX Proxy Server
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/multiflowpx_proxy
Restart=on-failure
User=root
Group=root

[Install]
WantedBy=multi-user.target
"""
        service_path = "/etc/systemd/system/multiflowpx.service"

        print(f"{Colors.CYAN}Criando arquivo de serviço systemd em {service_path}...{Colors.ENDC}")
        try:
            with open(service_path, "w") as f:
                f.write(service_file_content)
            print(f"{Colors.GREEN}[✓] Arquivo de serviço criado com sucesso!{Colors.ENDC}")
        except IOError as e:
            print(f"{Colors.FAIL}[!] Erro ao criar o arquivo de serviço: {e}{Colors.ENDC}")
            return False

        print(f"{Colors.CYAN}Recarregando systemd, habilitando e iniciando o serviço multiflowpx...{Colors.ENDC}")
        if not self._run_command([self.service_manager.systemctl_path, "daemon-reload"]):
            print(f"{Colors.FAIL}[!] Erro: Falha ao recarregar o systemd.{Colors.ENDC}")
            return False
        if not self._run_command([self.service_manager.systemctl_path, "enable", "multiflowpx.service"]):
            print(f"{Colors.FAIL}[!] Erro: Falha ao habilitar o serviço.{Colors.ENDC}")
            return False
        if not self._run_command([self.service_manager.systemctl_path, "start", "multiflowpx.service"]):
            print(f"{Colors.FAIL}[!] Erro: Falha ao iniciar o serviço.{Colors.ENDC}")
            return False

        print(f"{Colors.GREEN}[✓] Serviço multiflowpx instalado e iniciado com sucesso!{Colors.ENDC}")
        return True

    def _run_command(self, command: List[str]) -> bool:
        """Executa um comando de shell e retorna True em caso de sucesso, False caso contrário."""
        try:
            process = subprocess.run(command, check=True, capture_output=True, text=True)
            print(process.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print(f"{Colors.FAIL}[!] Comando falhou: {' '.join(command)}\n{e.stdout}\n{e.stderr}{Colors.ENDC}")
            return False
        except FileNotFoundError:
            print(f"{Colors.FAIL}[!] Erro: Comando '{command[0]}' não encontrado.{Colors.ENDC}")
            return False

    def full_install(self):
        """Executa a instalação completa do proxy: compilação e serviço."""
        self.ui.print_header("INSTALAÇÃO COMPLETA DO PROXY")
        if self.install_proxy_binaries():
            if self.install_systemd_service():
                print(f"\n{Colors.GREEN}Instalação completa do MultiFlowPX concluída com sucesso!{Colors.ENDC}")
                self.check_service_status()
            else:
                print(f"\n{Colors.FAIL}Instalação do serviço falhou.{Colors.ENDC}")
        else:
            print(f"\n{Colors.FAIL}Compilação e instalação do binário falharam.{Colors.ENDC}")

    @requires_systemctl
    def check_service_status(self):
        """Verifica e exibe o status do serviço multiflowpx."""
        self.ui.print_header("STATUS DO SERVIÇO")
        try:
            subprocess.run([self.service_manager.systemctl_path, "status", "multiflowpx.service"], check=False)
        except Exception as e:
            print(f"{Colors.FAIL}[!] Erro ao verificar status do serviço: {e}{Colors.ENDC}")

    def main_menu(self):
        """Exibe o menu principal e gerencia as opções."""
        while True:
            self.ui.print_header("MENU PRINCIPAL")
            
            status_text = f"{Colors.GREEN}ATIVO{Colors.ENDC}" if self.service_manager.is_running() else f"{Colors.FAIL}INATIVO{Colors.ENDC}"
            print(f"Status do Serviço: {status_text}\n")

            print(f"  [{Colors.BOLD}1{Colors.ENDC}] Iniciar Proxy")
            print(f"  [{Colors.BOLD}2{Colors.ENDC}] Parar Proxy")
            print(f"  [{Colors.BOLD}3{Colors.ENDC}] Reiniciar Proxy")
            print(f"  [{Colors.BOLD}4{Colors.ENDC}] Status do Serviço")
            self.ui.print_divider()
            print(f"  [{Colors.BOLD}5{Colors.ENDC}] Instalar/Reinstalar Proxy (Compilar e Configurar Serviço)")
            self.ui.print_divider()
            print(f"  [{Colors.BOLD}6{Colors.ENDC}] Adicionar Porta")
            print(f"  [{Colors.BOLD}7{Colors.ENDC}] Remover Porta")
            print(f"  [{Colors.BOLD}8{Colors.ENDC}] Alterar Protocolos")
            print(f"  [{Colors.BOLD}9{Colors.ENDC}] Configurar Host de Destino")
            print(f"  [{Colors.BOLD}10{Colors.ENDC}] Alterar Domínio (SNI) e Gerar Certificado SSL")
            self.ui.print_divider()
            print(f"  [{Colors.BOLD}0{Colors.ENDC}] Sair")
            self.ui.print_divider()

            choice = input(f"{Colors.BOLD}Escolha uma opção: {Colors.ENDC}").strip()

            if choice == "1":
                self.start_proxy()
            elif choice == "2":
                self.stop_proxy()
            elif choice == "3":
                self.restart_proxy()
            elif choice == "4":
                self.check_service_status()
            elif choice == "5":
                self.full_install()
            elif choice == "6":
                self.add_port()
            elif choice == "7":
                self.remove_port()
            elif choice == "8":
                self.change_protocols()
            elif choice == "9":
                self.configure_host()
            elif choice == "10":
                self.change_domain_and_reinstall_ssl()
            elif choice == "0":
                print(f"{Colors.GREEN}Saindo...{Colors.ENDC}")
                sys.exit(0)
            else:
                print(f"\n{Colors.FAIL}[!] Opção inválida. Tente novamente.{Colors.ENDC}")
            
            input("\n    Pressione Enter para continuar...")

if __name__ == "__main__":
    menu = ProxyMenu()
    menu.main_menu()
