#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiFlowPX Menu Interface
Interface CLI interativa para o MultiFlowPX Proxy Server Manager.
"""

import os
import sys
import time
import re
from typing import Dict, List, Optional, Any

# Importar módulo core
from multiflowpx_core import (
    ConfigManager, ServiceManager, InstallManager,
    check_root, validate_port, validate_host_format,
    CONFIG_FILE, MIN_PORT, MAX_PORT, DEFAULT_WORKERS,
    DEFAULT_BUFFER_SIZE, MIN_LOG_LEVEL, MAX_LOG_LEVEL
)

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
    def get_valid_port(prompt: str) -> Optional[int]:
        """Solicita e valida entrada de porta do usuário."""
        port_input = input(prompt)
        port = validate_port(port_input)
        if not port:
            print(f"\n{Colors.FAIL}[!] Porta inválida. Deve estar entre {MIN_PORT} e {MAX_PORT}.{Colors.ENDC}")
        return port
    
    @staticmethod
    def print_success(message: str):
        """Exibe mensagem de sucesso."""
        print(f"\n{Colors.GREEN}[✓] {message}{Colors.ENDC}")
    
    @staticmethod
    def print_error(message: str):
        """Exibe mensagem de erro."""
        print(f"\n{Colors.FAIL}[!] {message}{Colors.ENDC}")
    
    @staticmethod
    def print_warning(message: str):
        """Exibe mensagem de aviso."""
        print(f"\n{Colors.WARNING}[!] {message}{Colors.ENDC}")
    
    @staticmethod
    def confirm_action(message: str) -> bool:
        """Solicita confirmação do usuário."""
        response = input(f"{Colors.BOLD}{message} (s/N):{Colors.ENDC} ").lower()
        return response in ['s', 'sim', 'y', 'yes']

class ProxyMenu:
    """Classe principal que gerencia o menu interativo para o MultiFlowPX Proxy Server."""

    def __init__(self):
        self.config_manager = ConfigManager()
        self.service_manager = ServiceManager()
        self.install_manager = InstallManager()
        self.ui = UIHelper()
    
    def _check_root_access(self) -> bool:
        """Verifica acesso root e exibe mensagem se necessário."""
        if not check_root():
            self.ui.print_error("Esta operação requer privilégios de root. Execute com 'sudo'.")
            input("\n    Pressione Enter para continuar...")
            return False
        return True
    
    def _notify_systemctl_unavailable(self):
        """Informa ao usuário que o systemctl não está disponível."""
        self.ui.print_error("O comando 'systemctl' não foi encontrado.")
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
            port = self.ui.get_valid_port(f"{Colors.BOLD}Digite a porta que deseja usar para o serviço: {Colors.ENDC}")
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
                        self.ui.print_warning("Domínio não informado. SSL não será ativado.")
                        protocols.remove('ssl')
                    else:
                        self.config_manager.set_sni(domain)
                
                return protocols
            else:
                self.ui.print_error("Opção inválida. Tente novamente.")
    
    # --- Métodos de Gerenciamento do Proxy ---
    
    def start_proxy(self):
        """Inicia o processo do proxy."""
        if not self._check_root_access():
            return
        
        if not self.service_manager.is_available():
            self._notify_systemctl_unavailable()
            return
        
        if self.service_manager.is_running():
            self.ui.print_warning("O proxy já está em execução.")
            return
        
        if self.service_manager.start():
            self.ui.print_success("Proxy iniciado com sucesso via systemd.")
        else:
            self.ui.print_error("Erro ao iniciar o proxy.")
    
    def stop_proxy(self):
        """Para o processo do proxy."""
        if not self._check_root_access():
            return
        
        if not self.service_manager.is_available():
            self._notify_systemctl_unavailable()
            return
        
        if not self.service_manager.is_running():
            self.ui.print_warning("O proxy não está em execução.")
            return
        
        if self.service_manager.stop():
            self.ui.print_success("Proxy parado com sucesso via systemd.")
        else:
            self.ui.print_error("Erro ao parar o proxy.")
    
    def restart_proxy(self):
        """Reinicia o processo do proxy."""
        self.ui.print_header("REINICIAR PROXY")
        
        if not self._check_root_access():
            return
        
        if not self.service_manager.is_available():
            self._notify_systemctl_unavailable()
            return
        
        print(f"{Colors.WARNING}Reiniciando o serviço...{Colors.ENDC}")
        if self.service_manager.restart():
            self.ui.print_success("Proxy reiniciado com sucesso.")
        else:
            self.ui.print_error("Erro ao reiniciar o proxy.")
    
    # --- Métodos de Configuração ---
    
    def add_port(self):
        """Adiciona uma nova porta à configuração."""
        self.ui.print_header("ADICIONAR PORTA")
        self.ui.print_divider()
        
        config = self.config_manager.get_config()
        current_ports = config.get('port', [])
        print(f"{Colors.BOLD}Portas atuais:{Colors.ENDC} {Colors.BLUE}{', '.join(map(str, current_ports)) if current_ports else 'Nenhuma'}{Colors.ENDC}\n")
        
        port = self.ui.get_valid_port(f"{Colors.BOLD}Digite a nova porta para adicionar:{Colors.ENDC} ")
        
        if port:
            if self.config_manager.add_port(port):
                if self.config_manager.save_config():
                    self.ui.print_success(f"Porta {port} adicionada com sucesso!")
                else:
                    self.ui.print_error("Erro ao salvar as configurações.")
            else:
                self.ui.print_warning(f"Porta {port} já existe.")
    
    def remove_port(self):
        """Remove uma porta da configuração."""
        self.ui.print_header("REMOVER PORTA")
        self.ui.print_divider()
        
        config = self.config_manager.get_config()
        current_ports = config.get('port', [])
        
        if not current_ports:
            self.ui.print_warning("Não há portas para remover.")
            return
        
        print(f"{Colors.BOLD}Portas atuais:{Colors.ENDC} {Colors.BLUE}{', '.join(map(str, current_ports))}{Colors.ENDC}\n")
        port = self.ui.get_valid_port(f"{Colors.BOLD}Digite a porta para remover:{Colors.ENDC} ")
        
        if port:
            if self.config_manager.remove_port(port):
                if self.config_manager.save_config():
                    self.ui.print_success(f"Porta {port} removida com sucesso!")
                else:
                    self.ui.print_error("Erro ao salvar as configurações.")
            else:
                self.ui.print_warning(f"Porta {port} não encontrada.")
    
    def change_protocols(self):
        """Altera a combinação de protocolos em uso."""
        self.ui.print_header("ALTERAR PROTOCOLO")
        
        config = self.config_manager.get_config()
        current_modes = config.get('mode', [])
        print(f"{Colors.BOLD}Protocolos atuais:{Colors.ENDC} {Colors.BLUE}{', '.join(current_modes) if current_modes else 'Nenhum'}{Colors.ENDC}")
        
        new_protocols = self._ask_for_protocols()
        self.config_manager.set_protocols(new_protocols)
        
        if self.config_manager.save_config():
            self.ui.print_success("Protocolos alterados com sucesso!")
        else:
            self.ui.print_error("Erro ao salvar as configurações.")
    
    def configure_host(self):
        """Configura o host de destino do tráfego."""
        self.ui.print_header("ALTERAR DESTINO DO TRÁFEGO DO PROXY")
        self.ui.print_divider()
        
        config = self.config_manager.get_config()
        print(f"{Colors.BOLD}Host atual:{Colors.ENDC} {Colors.BLUE}{config['host']}{Colors.ENDC}\n")
        new_host = input(f"{Colors.BOLD}Digite o novo host (formato: IP:PORTA):{Colors.ENDC} ").strip()
        
        if new_host:
            if not validate_host_format(new_host):
                self.ui.print_error("Formato de host inválido. Use IP:PORTA")
                return
            
            self.config_manager.set_host(new_host)
            if self.config_manager.save_config():
                self.ui.print_success(f"Host configurado para {new_host}!")
            else:
                self.ui.print_error("Erro ao salvar as configurações.")
    
    def change_domain_and_reinstall_ssl(self):
        """Altera o domínio (SNI) e re-executa a instalação para gerar novo certificado."""
        self.ui.print_header("ALTERAR DOMÍNIO E GERAR CERTIFICADO")
        
        config = self.config_manager.get_config()
        print(f"{Colors.BOLD}SNI (domínio) atual:{Colors.ENDC} {Colors.BLUE}{config['sni']}{Colors.ENDC}\n")
        print(f"{Colors.WARNING}Esta operação irá alterar o domínio do seu servidor e tentará")
        print(f"re-executar o script de instalação para gerar um novo certificado SSL.{Colors.ENDC}")
        
        if not self.ui.confirm_action("Deseja continuar?"):
            self.ui.print_warning("Operação cancelada.")
            return
        
        new_domain = self._ask_ssl_domain()
        if not new_domain:
            self.ui.print_warning("Nenhum domínio inserido. Operação cancelada.")
            return
        
        self.config_manager.set_sni(new_domain)
        if self.config_manager.save_config():
            self.ui.print_success(f"Domínio (SNI) alterado para {new_domain}.")
            print(f"{Colors.WARNING}Iniciando a reinstalação para gerar o novo certificado...{Colors.ENDC}")
            self._run_install_script_internal()
        else:
            self.ui.print_error("Erro ao salvar as configurações.")
    
    def configure_workers(self):
        """Configura o número de workers."""
        self.ui.print_header("CONFIGURAR WORKERS")
        self.ui.print_divider()
        
        config = self.config_manager.get_config()
        print(f"{Colors.BOLD}Workers atuais:{Colors.ENDC} {Colors.BLUE}{config['workers']}{Colors.ENDC}\n")
        workers_input = input(f"{Colors.BOLD}Digite o número de workers:{Colors.ENDC} ")
        
        try:
            new_workers = int(workers_input)
            if new_workers > 0:
                self.config_manager.set_workers(new_workers)
                if self.config_manager.save_config():
                    self.ui.print_success(f"Workers configurados para {new_workers}!")
                else:
                    self.ui.print_error("Erro ao salvar as configurações.")
            else:
                self.ui.print_error("Número de workers deve ser maior que 0.")
        except ValueError:
            self.ui.print_error("Entrada inválida. Digite um número.")
    
    def configure_buffer_size(self):
        """Configura o tamanho do buffer."""
        self.ui.print_header("CONFIGURAR BUFFER SIZE")
        self.ui.print_divider()
        
        config = self.config_manager.get_config()
        print(f"{Colors.BOLD}Buffer size atual:{Colors.ENDC} {Colors.BLUE}{config['buffer_size']}{Colors.ENDC}\n")
        buffer_input = input(f"{Colors.BOLD}Digite o tamanho do buffer:{Colors.ENDC} ")
        
        try:
            new_buffer = int(buffer_input)
            if new_buffer > 0:
                self.config_manager.set_buffer_size(new_buffer)
                if self.config_manager.save_config():
                    self.ui.print_success(f"Buffer size configurado para {new_buffer}!")
                else:
                    self.ui.print_error("Erro ao salvar as configurações.")
            else:
                self.ui.print_error("Buffer size deve ser maior que 0.")
        except ValueError:
            self.ui.print_error("Entrada inválida. Digite um número.")
    
    def configure_log_level(self):
        """Configura o nível de log."""
        self.ui.print_header("CONFIGURAR LOG LEVEL")
        self.ui.print_divider()
        
        config = self.config_manager.get_config()
        print(f"{Colors.BOLD}Log level atual:{Colors.ENDC} {Colors.BLUE}{config['log_level']}{Colors.ENDC}\n")
        print(f"{Colors.BOLD}Níveis disponíveis:{Colors.ENDC} 0 (Silencioso), 1 (Normal), 2 (Verboso)\n")
        
        log_input = input(f"{Colors.BOLD}Digite o nível de log (0-2):{Colors.ENDC} ")
        
        try:
            new_log_level = int(log_input)
            if MIN_LOG_LEVEL <= new_log_level <= MAX_LOG_LEVEL:
                self.config_manager.set_log_level(new_log_level)
                if self.config_manager.save_config():
                    self.ui.print_success(f"Log level configurado para {new_log_level}!")
                else:
                    self.ui.print_error("Erro ao salvar as configurações.")
            else:
                self.ui.print_error(f"Log level deve estar entre {MIN_LOG_LEVEL} e {MAX_LOG_LEVEL}.")
        except ValueError:
            self.ui.print_error("Entrada inválida. Digite um número.")
    
    # --- Métodos de Instalação/Desinstalação ---
    
    def _run_install_script_internal(self) -> bool:
        """Executa o script de instalação (método interno)."""
        install_script_path = self.install_manager.find_install_script()
        
        if not install_script_path:
            self.ui.print_error("Script 'install.sh' não encontrado.")
            return False
        
        self.ui.print_success(f"Script de instalação encontrado em: {install_script_path}")
        
        if self.install_manager.run_install_script(install_script_path):
            self.ui.print_success("Script de instalação executado com sucesso!")
            return True
        else:
            self.ui.print_error("Erro ao executar o script de instalação.")
            return False
    
    def run_install_script(self):
        """Encontra e executa o script de instalação com configuração inicial."""
        self.ui.print_header("INSTALAR/REINSTALAR MULTIFLOW PROXY")
        
        install_script_path = self.install_manager.find_install_script()
        
        if not install_script_path:
            self.ui.print_error("Script 'install.sh' não encontrado.")
            print(f"{Colors.WARNING}Certifique-se de que o repositório foi clonado corretamente.{Colors.ENDC}")
            return
        
        self.ui.print_success(f"Script de instalação encontrado em: {install_script_path}")
        
        install_port = self._ask_for_install_port()
        install_protocols = self._ask_for_protocols()
        
        print(f"\n{Colors.WARNING}Esta opção executará a instalação na porta {install_port} com os protocolos selecionados.")
        print(f"Isso pode sobrescrever configurações existentes.{Colors.ENDC}\n")
        
        if self.ui.confirm_action("Deseja continuar?"):
            if not self._check_root_access():
                return
            
            self.config_manager.config['port'] = [install_port]
            self.config_manager.set_protocols(install_protocols)
            self.config_manager.save_config()
            
            self._run_install_script_internal()
        else:
            self.ui.print_warning("Instalação cancelada.")
    
    def uninstall(self):
        """Desinstala completamente o MultiFlowPX."""
        if not self._check_root_access():
            return
        
        if not self.service_manager.is_available():
            self._notify_systemctl_unavailable()
            print(f"{Colors.WARNING}Continuando com a desinstalação sem systemd...{Colors.ENDC}")
        
        print("Iniciando desinstalação...")
        success, messages = self.install_manager.uninstall(self.service_manager)
        
        for message in messages:
            if "Erro" in message:
                print(f"  {Colors.FAIL}{message}{Colors.ENDC}")
            else:
                print(f"  {Colors.GREEN}{message}{Colors.ENDC}")
        
        if success:
            self.ui.print_success("MultiFlowPX desinstalado com sucesso!")
        else:
            self.ui.print_error("Desinstalação concluída com erros.")
    
    # --- Menus ---
    
    def main_menu(self):
        """Exibe o menu principal."""
        while True:
            # Preparar informações de status
            config = self.config_manager.get_config()
            
            if self.service_manager.is_available():
                status_text = f"{Colors.GREEN}● ATIVO{Colors.ENDC}" if self.service_manager.is_running() else f"{Colors.FAIL}○ INATIVO{Colors.ENDC}"
            else:
                status_text = f"{Colors.WARNING}N/A (systemd não encontrado){Colors.ENDC}"
            
            current_port = config.get("port", [])
            port_display = ", ".join(map(str, current_port)) if current_port else "Nenhuma"
            current_mode = config.get("mode", [])
            protocol_display = ", ".join([m.upper() for m in current_mode]) if current_mode else "Nenhum"
            
            # Usar o método pad_ansi_text para alinhamento correto
            status_padded = self.ui.pad_ansi_text(status_text, 40)
            
            self.ui.clear_screen()
            print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
            print(f"{Colors.CYAN}║{Colors.BOLD}           MULTIFLOWPX PROXY SERVER MANAGER                  {Colors.CYAN}║{Colors.ENDC}")
            print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════════╣{Colors.ENDC}")
            print(f"{Colors.CYAN}║                                                              ║{Colors.ENDC}")
            print(f"{Colors.CYAN}║  {Colors.BOLD}Status do Serviço:{Colors.ENDC}  {status_padded}{Colors.CYAN}║{Colors.ENDC}")
            print(f"{Colors.CYAN}║  {Colors.BOLD}Porta(s) Ativa(s):{Colors.ENDC}  {Colors.BLUE}{port_display:<39}{Colors.CYAN}║{Colors.ENDC}")
            print(f"{Colors.CYAN}║  {Colors.BOLD}Protocolo(s):{Colors.ENDC}       {Colors.BLUE}{protocol_display:<39}{Colors.CYAN}║{Colors.ENDC}")
            print(f"{Colors.CYAN}║                                                              ║{Colors.ENDC}")
            print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════════╣{Colors.ENDC}")
            print(f"{Colors.CYAN}║                      MENU PRINCIPAL                         ║{Colors.ENDC}")
            print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════════╣{Colors.ENDC}")
            print(f"{Colors.CYAN}║                                                              ║{Colors.ENDC}")
            print(f"{Colors.CYAN}║  [{Colors.BOLD}1{Colors.ENDC}{Colors.CYAN}] Instalar/Reinstalar MultiFlow Proxy                   ║{Colors.ENDC}")
            print(f"{Colors.CYAN}║  [{Colors.BOLD}2{Colors.ENDC}{Colors.CYAN}] Configurar Proxy                                       ║{Colors.ENDC}")
            print(f"{Colors.CYAN}║  [{Colors.BOLD}3{Colors.ENDC}{Colors.CYAN}] Reiniciar Proxy                                        ║{Colors.ENDC}")
            print(f"{Colors.CYAN}║  [{Colors.BOLD}4{Colors.ENDC}{Colors.CYAN}] Desinstalar Completamente                             ║{Colors.ENDC}")
            print(f"{Colors.CYAN}║                                                              ║{Colors.ENDC}")
            print(f"{Colors.CYAN}║  [{Colors.BOLD}0{Colors.ENDC}{Colors.CYAN}] Sair                                                   ║{Colors.ENDC}")
            print(f"{Colors.CYAN}║                                                              ║{Colors.ENDC}")
            print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}")
            
            choice = input(f"\n  {Colors.BOLD}Escolha uma opção:{Colors.ENDC} ")
            
            if choice == '1':
                self.run_install_script()
            elif choice == '2':
                self.submenu_configure_proxy()
            elif choice == '3':
                self.restart_proxy()
            elif choice == '4':
                self.menu_uninstall()
            elif choice == '0':
                print(f"\n{Colors.GREEN}  Encerrando o sistema...{Colors.ENDC}\n")
                sys.exit(0)
            else:
                self.ui.print_error("Opção inválida. Tente novamente.")
            
            if choice in ["1", "2", "3", "4"]:
                input(f"\n  {Colors.BOLD}Pressione Enter para voltar ao menu...{Colors.ENDC}")
    
    def submenu_configure_proxy(self):
        """Submenu para configurar o proxy."""
        while True:
            self.ui.print_header("CONFIGURAR PROXY")
            
            print(f"{Colors.CYAN}┌──────────────────────────────────────────────────────────────┐{Colors.ENDC}")
            print(f"{Colors.CYAN}│                    OPÇÕES DE CONFIGURAÇÃO                   │{Colors.ENDC}")
            print(f"{Colors.CYAN}├──────────────────────────────────────────────────────────────┤{Colors.ENDC}")
            print(f"{Colors.CYAN}│                                                              │{Colors.ENDC}")
            print(f"{Colors.CYAN}│  [{Colors.BOLD}1{Colors.ENDC}{Colors.CYAN}] Adicionar porta                                        │{Colors.ENDC}")
            print(f"{Colors.CYAN}│  [{Colors.BOLD}2{Colors.ENDC}{Colors.CYAN}] Alterar protocolo                                      │{Colors.ENDC}")
            print(f"{Colors.CYAN}│  [{Colors.BOLD}3{Colors.ENDC}{Colors.CYAN}] Remover porta                                          │{Colors.ENDC}")
            print(f"{Colors.CYAN}│  [{Colors.BOLD}4{Colors.ENDC}{Colors.CYAN}] Configuração avançada                                  │{Colors.ENDC}")
            print(f"{Colors.CYAN}│                                                              │{Colors.ENDC}")
            print(f"{Colors.CYAN}│  [{Colors.BOLD}0{Colors.ENDC}{Colors.CYAN}] Voltar ao menu principal                              │{Colors.ENDC}")
            print(f"{Colors.CYAN}│                                                              │{Colors.ENDC}")
            print(f"{Colors.CYAN}└──────────────────────────────────────────────────────────────┘{Colors.ENDC}")
            
            choice = input(f"\n  {Colors.BOLD}Escolha uma opção:{Colors.ENDC} ")
            
            if choice == '1':
                self.add_port()
            elif choice == '2':
                self.change_protocols()
            elif choice == '3':
                self.remove_port()
            elif choice == '4':
                self.submenu_advanced_config()
            elif choice == '0':
                break
            else:
                self.ui.print_error("Opção inválida. Tente novamente.")
            
            input(f"\n  {Colors.BOLD}Pressione Enter para continuar...{Colors.ENDC}")
    
    def submenu_advanced_config(self):
        """Submenu para configurações avançadas."""
        while True:
            self.ui.print_header("CONFIGURAÇÃO AVANÇADA")
            
            print(f"{Colors.CYAN}┌──────────────────────────────────────────────────────────────┐{Colors.ENDC}")
            print(f"{Colors.CYAN}│                   PARÂMETROS AVANÇADOS                      │{Colors.ENDC}")
            print(f"{Colors.CYAN}├──────────────────────────────────────────────────────────────┤{Colors.ENDC}")
            print(f"{Colors.CYAN}│                                                              │{Colors.ENDC}")
            print(f"{Colors.CYAN}│  [{Colors.BOLD}1{Colors.ENDC}{Colors.CYAN}] Alterar destino do tráfego do proxy                   │{Colors.ENDC}")
            print(f"{Colors.CYAN}│  [{Colors.BOLD}2{Colors.ENDC}{Colors.CYAN}] Alterar domínio do servidor e gerar novo certificado  │{Colors.ENDC}")
            print(f"{Colors.CYAN}│  [{Colors.BOLD}3{Colors.ENDC}{Colors.CYAN}] Configurar número de workers                           │{Colors.ENDC}")
            print(f"{Colors.CYAN}│  [{Colors.BOLD}4{Colors.ENDC}{Colors.CYAN}] Configurar tamanho do buffer                           │{Colors.ENDC}")
            print(f"{Colors.CYAN}│  [{Colors.BOLD}5{Colors.ENDC}{Colors.CYAN}] Configurar nível de log                                │{Colors.ENDC}")
            print(f"{Colors.CYAN}│                                                              │{Colors.ENDC}")
            print(f"{Colors.CYAN}│  [{Colors.BOLD}0{Colors.ENDC}{Colors.CYAN}] Voltar ao menu anterior                                │{Colors.ENDC}")
            print(f"{Colors.CYAN}│                                                              │{Colors.ENDC}")
            print(f"{Colors.CYAN}└──────────────────────────────────────────────────────────────┘{Colors.ENDC}")
            
            choice = input(f"\n  {Colors.BOLD}Escolha uma opção:{Colors.ENDC} ")
            
            if choice == '1':
                self.configure_host()
            elif choice == '2':
                self.change_domain_and_reinstall_ssl()
            elif choice == '3':
                self.configure_workers()
            elif choice == '4':
                self.configure_buffer_size()
            elif choice == '5':
                self.configure_log_level()
            elif choice == '0':
                break
            else:
                self.ui.print_error("Opção inválida. Tente novamente.")
            
            input(f"\n  {Colors.BOLD}Pressione Enter para continuar...{Colors.ENDC}")
    
    def menu_uninstall(self):
        """Menu para desinstalar o MultiFlowPX."""
        self.ui.print_header("DESINSTALAR MULTIFLOWPX")
        
        print(f"{Colors.FAIL}ATENÇÃO: Esta operação removerá completamente o MultiFlowPX!{Colors.ENDC}")
        print(f"{Colors.WARNING}Isso incluirá:{Colors.ENDC}")
        print(f"  • Parar o serviço")
        print(f"  • Remover arquivos de configuração")
        print(f"  • Remover executáveis")
        print(f"  • Remover serviço systemd\n")
        
        if self.ui.confirm_action("Tem certeza que deseja desinstalar?"):
            self.uninstall()
        else:
            self.ui.print_warning("Desinstalação cancelada.")


def main():
    """Função principal para iniciar o menu."""
    try:
        menu = ProxyMenu()
        menu.main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Programa interrompido pelo usuário.{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}Erro crítico: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
