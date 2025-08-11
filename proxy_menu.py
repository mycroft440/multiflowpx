#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import json
import time
import shutil

# --- Constantes de Configuração ---
# Arquivo para salvar as configurações do proxy.
CONFIG_FILE = "/etc/multiflowpx/config.json"

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
    """Classe que gerencia o menu interativo para o MultiFlowPX Proxy Server."""

    def __init__(self):
        # O padrão de configuração é definido aqui para ser a fonte da verdade.
        self.default_config = {
            "mode": [],
            "port": [],
            "host": "127.0.0.1:22",
            "sni": "example.com",
            "workers": 4,
            "buffer_size": 8192,
            "log_level": 1
        }
        # Carrega a configuração de forma robusta.
        self.config = self.load_config()
        # VERIFICAÇÃO: Checa se o comando 'systemctl' está disponível no sistema.
        self.systemctl_path = shutil.which("systemctl")

    # --- Funções Utilitárias ---

    def _notify_systemctl_unavailable(self):
        """Informa ao usuário que o systemctl não está disponível."""
        print(f"\n{Colors.FAIL}[!] Erro: O comando 'systemctl' não foi encontrado.{Colors.ENDC}")
        print(f"{Colors.WARNING}Este script requer um sistema baseado em systemd (como a maioria das distribuições Linux).")
        print(f"As funções de gerenciamento de serviço estão desativadas.{Colors.ENDC}")

    def clear_screen(self):
        """Limpa a tela do terminal."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title):
        """Exibe um cabeçalho padronizado."""
        self.clear_screen()
        print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
        print(f"{Colors.CYAN}║{Colors.BOLD}           MULTIFLOWPX PROXY SERVER MANAGER                  {Colors.CYAN}║{Colors.ENDC}")
        print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════════╣{Colors.ENDC}")
        print(f"{Colors.CYAN}║  {Colors.HEADER}{title:^58}  {Colors.CYAN}║{Colors.ENDC}")
        print(f"{Colors.CYAN}╚══════════════════════════════════════════════════════════════╝{Colors.ENDC}\n")

    def print_divider(self):
        """Imprime um divisor visual."""
        print(f"{Colors.CYAN}{'─' * 64}{Colors.ENDC}")

    def check_root(self):
        """Verifica se o script está sendo executado como root."""
        if not hasattr(os, 'geteuid'):
            print(f"\n{Colors.WARNING}[!] Aviso: Não foi possível verificar privilégios de root em um sistema não-Unix.{Colors.ENDC}")
            return True
        if os.geteuid() != 0:
            print(f"\n{Colors.FAIL}[!] Erro: Esta operação requer privilégios de root. Execute com 'sudo'.{Colors.ENDC}")
            input("\n    Pressione Enter para continuar...")
            return False
        return True

    def is_running(self):
        """Verifica se o processo do proxy está em execução."""
        if not self.systemctl_path:
            return False
        return subprocess.run([self.systemctl_path, "is-active", "--quiet", "multiflowpx.service"]).returncode == 0

    def load_config(self):
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
                        print(f"{Colors.WARNING}[!] Aviso: Chave '{key}' ausente ou com tipo inválido no config.json. Usando valor padrão.{Colors.ENDC}")
        except (IOError, json.JSONDecodeError) as e:
            print(f"{Colors.WARNING}[!] Aviso: Não foi possível carregar o arquivo de configuração: {e}. Usando configuração padrão.{Colors.ENDC}")
        
        if not isinstance(config.get('port'), list):
            config['port'] = self.default_config['port']
        if not isinstance(config.get('mode'), list):
            config['mode'] = self.default_config['mode']
        return config

    def save_config(self):
        """Salva as configurações atuais no arquivo JSON."""
        if not self.check_root(): return
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"\n{Colors.GREEN}[✓] Configurações salvas com sucesso em {CONFIG_FILE}{Colors.ENDC}")
        except IOError as e:
            print(f"\n{Colors.FAIL}[!] Erro ao salvar as configurações: {e}{Colors.ENDC}")

    def find_install_script(self):
        """Detecta dinamicamente o script de instalação 'install.sh'."""
        potential_paths = ['/root/multiflowpx/install.sh', os.path.join(os.path.expanduser("~"), 'multiflowpx/install.sh'), './install.sh']
        for path in potential_paths:
            if os.path.isfile(path):
                print(f"{Colors.GREEN}[✓] Script de instalação encontrado em: {path}{Colors.ENDC}")
                return path
        return None

    # --- Funções auxiliares ---

    def _ask_ssl_domain(self):
        """Pergunta o domínio para emissão de certificado quando SSL for selecionado."""
        self.print_divider()
        print(f"{Colors.WARNING}CONFIGURAÇÃO DE CERTIFICADO SSL{Colors.ENDC}\n")
        print("Digite o seu domínio que é apontado para o seu servidor para")
        print("que se gere um certificado funcional para o mesmo.")
        self.print_divider()
        return input(f"{Colors.BOLD}Digite [exemplo: mycroft.multflowmanager.xyz]:{Colors.ENDC} ").strip()

    def _ask_for_install_port(self):
        """Pergunta e valida a porta principal durante a instalação."""
        self.print_divider()
        print(f"{Colors.BOLD}CONFIGURAÇÃO DA PORTA PRINCIPAL{Colors.ENDC}")
        while True:
            port_input = input(f"{Colors.BOLD}Digite a porta que deseja usar para o serviço: {Colors.ENDC}")
            try:
                new_port = int(port_input)
                if 1 <= new_port <= 65535:
                    return new_port
                else:
                    print(f"\n{Colors.FAIL}[!] Porta inválida. Por favor, digite um número entre 1 e 65535.{Colors.ENDC}")
            except ValueError:
                print(f"\n{Colors.FAIL}[!] Entrada inválida. Por favor, digite um número.{Colors.ENDC}")

    def _ask_for_protocols(self):
        """Pergunta e valida a combinação de protocolos. Reutilizável para instalação e alteração."""
        self.print_divider()
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
                # Se SSL for escolhido, pede o domínio.
                if 'ssl' in protocols:
                    domain = self._ask_ssl_domain()
                    if not domain:
                        print(f"\n{Colors.WARNING}[!] Domínio não informado. O SSL não será ativado.{Colors.ENDC}")
                        protocols.remove('ssl')
                    else:
                        # Define o SNI a partir do domínio informado
                        self.config["sni"] = domain
                return protocols
            else:
                print(f"\n{Colors.FAIL}[!] Opção inválida. Tente novamente.{Colors.ENDC}")

    # --- Funções de Gerenciamento do Proxy ---

    def start_proxy(self):
        """Inicia o processo do proxy com as configurações salvas."""
        if not self.systemctl_path:
            self._notify_systemctl_unavailable()
            return
        if not self.check_root(): return
        if self.is_running():
            print(f"\n{Colors.WARNING}[!] O proxy já está em execução.{Colors.ENDC}")
            return
        try:
            subprocess.run([self.systemctl_path, "start", "multiflowpx.service"], check=True)
            print(f"\n{Colors.GREEN}[✓] Proxy iniciado com sucesso via systemd.{Colors.ENDC}")
        except subprocess.CalledProcessError as e:
            print(f"\n{Colors.FAIL}[!] Erro ao iniciar o proxy via systemd: {e}{Colors.ENDC}")

    def stop_proxy(self):
        """Para o processo do proxy."""
        if not self.systemctl_path:
            self._notify_systemctl_unavailable()
            return
        if not self.check_root(): return
        if not self.is_running():
            print(f"\n{Colors.WARNING}[!] O proxy não está em execução.{Colors.ENDC}")
            return
        try:
            subprocess.run([self.systemctl_path, "stop", "multiflowpx.service"], check=True)
            print(f"\n{Colors.GREEN}[✓] Proxy parado com sucesso via systemd.{Colors.ENDC}")
        except subprocess.CalledProcessError as e:
            print(f"\n{Colors.FAIL}[!] Erro ao parar o proxy via systemd: {e}{Colors.ENDC}")

    # --- Menus ---

    def main_menu(self):
        """Exibe o menu principal."""
        while True:
            if self.systemctl_path:
                status_text = f"{Colors.GREEN}● ATIVO{Colors.ENDC}" if self.is_running() else f"{Colors.FAIL}○ INATIVO{Colors.ENDC}"
            else:
                status_text = f"{Colors.WARNING}N/A (systemd não encontrado){Colors.ENDC}"

            current_port = self.config.get("port", [])
            port_display = ", ".join(map(str, current_port)) if current_port else "Nenhuma"
            current_mode = self.config.get("mode", [])
            protocol_display = ", ".join([m.upper() for m in current_mode]) if current_mode else "Nenhum"

            self.clear_screen()
            print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗{Colors.ENDC}")
            print(f"{Colors.CYAN}║{Colors.BOLD}           MULTIFLOWPX PROXY SERVER MANAGER                  {Colors.CYAN}║{Colors.ENDC}")
            print(f"{Colors.CYAN}╠══════════════════════════════════════════════════════════════╣{Colors.ENDC}")
            print(f"{Colors.CYAN}║                                                              ║{Colors.ENDC}")
            print(f"{Colors.CYAN}║  {Colors.BOLD}Status do Serviço:{Colors.ENDC}  {status_text:<40}{Colors.CYAN}║{Colors.ENDC}")
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
                self.print_header("REINICIAR PROXY")
                self.stop_proxy()
                time.sleep(1)
                self.start_proxy()
            elif choice == '4':
                self.menu_uninstall()
            elif choice == '0':
                print(f"\n{Colors.GREEN}  Encerrando o sistema...{Colors.ENDC}\n")
                sys.exit(0)
            else:
                print(f"\n{Colors.FAIL}  [!] Opção inválida. Tente novamente.{Colors.ENDC}")
            
            if choice in ["1", "2", "3", "4"]:
                input(f"\n  {Colors.BOLD}Pressione Enter para voltar ao menu...{Colors.ENDC}")

    def submenu_configure_proxy(self):
        """Submenu para configurar o proxy (porta e protocolo)."""
        while True:
            self.print_header("CONFIGURAR PROXY")
            
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
                print(f"\n{Colors.FAIL}  [!] Opção inválida. Tente novamente.{Colors.ENDC}")
            input(f"\n  {Colors.BOLD}Pressione Enter para continuar...{Colors.ENDC}")

    def add_port(self):
        self.print_header("ADICIONAR PORTA")
        self.print_divider()
        current_ports = self.config.get('port', [])
        print(f"{Colors.BOLD}Portas atuais:{Colors.ENDC} {Colors.BLUE}{', '.join(map(str, current_ports)) if current_ports else 'Nenhuma'}{Colors.ENDC}\n")
        port_input = input(f"{Colors.BOLD}Digite a nova porta para adicionar:{Colors.ENDC} ")
        try:
            new_port = int(port_input)
            if 1 <= new_port <= 65535:
                if new_port not in self.config["port"]:
                    self.config["port"].append(new_port)
                    self.save_config()
                    print(f"\n{Colors.GREEN}[✓] Porta {new_port} adicionada com sucesso!{Colors.ENDC}")
                else:
                    print(f"\n{Colors.WARNING}[!] Porta {new_port} já existe.{Colors.ENDC}")
            else:
                print(f"\n{Colors.FAIL}[!] Porta inválida. Por favor, digite um número entre 1 e 65535.{Colors.ENDC}")
        except ValueError:
            print(f"\n{Colors.FAIL}[!] Entrada inválida. Por favor, digite um número.{Colors.ENDC}")

    def change_protocols(self):
        """Altera a combinação de protocolos em uso."""
        self.print_header("ALTERAR PROTOCOLO")
        current_modes = self.config.get('mode', [])
        print(f"{Colors.BOLD}Protocolos atuais:{Colors.ENDC} {Colors.BLUE}{', '.join(current_modes) if current_modes else 'Nenhum'}{Colors.ENDC}")
        
        new_protocols = self._ask_for_protocols()
        self.config['mode'] = new_protocols
        self.save_config()
        print(f"\n{Colors.GREEN}[✓] Protocolos alterados com sucesso!{Colors.ENDC}")

    def remove_port(self):
        self.print_header("REMOVER PORTA")
        self.print_divider()
        current_ports = self.config.get('port', [])
        if not current_ports:
            print(f"{Colors.WARNING}[!] Não há portas para remover.{Colors.ENDC}")
            return
        print(f"{Colors.BOLD}Portas atuais:{Colors.ENDC} {Colors.BLUE}{', '.join(map(str, current_ports))}{Colors.ENDC}\n")
        port_input = input(f"{Colors.BOLD}Digite a porta para remover:{Colors.ENDC} ")
        try:
            port_to_remove = int(port_input)
            if port_to_remove in self.config["port"]:
                self.config["port"].remove(port_to_remove)
                self.save_config()
                print(f"\n{Colors.GREEN}[✓] Porta {port_to_remove} removida com sucesso!{Colors.ENDC}")
            else:
                print(f"\n{Colors.WARNING}[!] Porta {port_to_remove} não encontrada.{Colors.ENDC}")
        except ValueError:
            print(f"\n{Colors.FAIL}[!] Entrada inválida. Por favor, digite um número.{Colors.ENDC}")

    def submenu_advanced_config(self):
        """Submenu para configurações avançadas."""
        while True:
            self.print_header("CONFIGURAÇÃO AVANÇADA")
            
            # ALTERAÇÃO: Textos do menu atualizados para maior clareza.
            print(f"{Colors.CYAN}┌──────────────────────────────────────────────────────────────┐{Colors.ENDC}")
            print(f"{Colors.CYAN}│                   PARÂMETROS AVANÇADOS                      │{Colors.ENDC}")
            print(f"{Colors.CYAN}├──────────────────────────────────────────────────────────────┤{Colors.ENDC}")
            print(f"{Colors.CYAN}│                                                              │{Colors.ENDC}")
            print(f"{Colors.CYAN}│  [{Colors.BOLD}1{Colors.ENDC}{Colors.CYAN}] Alterar destino do trafico do proxy                    │{Colors.ENDC}")
            print(f"{Colors.CYAN}│  [{Colors.BOLD}2{Colors.ENDC}{Colors.CYAN}] Alterar dominio do servidor e gerar novo certificado.  │{Colors.ENDC}")
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
                # ALTERAÇÃO: Chamada para o novo método renomeado e mais robusto.
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
                print(f"\n{Colors.FAIL}  [!] Opção inválida. Tente novamente.{Colors.ENDC}")
            input(f"\n  {Colors.BOLD}Pressione Enter para continuar...{Colors.ENDC}")

    def configure_host(self):
        # ALTERAÇÃO: Título do cabeçalho atualizado para consistência.
        self.print_header("ALTERAR DESTINO DO TRÁFEGO DO PROXY")
        self.print_divider()
        print(f"{Colors.BOLD}Host atual:{Colors.ENDC} {Colors.BLUE}{self.config['host']}{Colors.ENDC}\n")
        new_host = input(f"{Colors.BOLD}Digite o novo host (formato: IP:PORTA):{Colors.ENDC} ")
        if new_host:
            self.config["host"] = new_host
            self.save_config()
            print(f"\n{Colors.GREEN}[✓] Host configurado para {new_host}!{Colors.ENDC}")

    # ALTERAÇÃO: Método renomeado e com lógica aprimorada para reinstalar o SSL.
    def change_domain_and_reinstall_ssl(self):
        """Altera o domínio (SNI) e re-executa a instalação para gerar um novo certificado."""
        self.print_header("ALTERAR DOMÍNIO E GERAR CERTIFICADO")
        print(f"{Colors.BOLD}SNI (domínio) atual:{Colors.ENDC} {Colors.BLUE}{self.config['sni']}{Colors.ENDC}\n")
        print(f"{Colors.WARNING}Esta operação irá alterar o domínio do seu servidor e tentará")
        print(f"re-executar o script de instalação para gerar um novo certificado SSL.{Colors.ENDC}")
        
        confirm = input(f"{Colors.BOLD}Deseja continuar? (s/N):{Colors.ENDC} ").lower()
        if confirm not in ['s', 'sim', 'y', 'yes']:
            print(f"\n{Colors.WARNING}Operação cancelada.{Colors.ENDC}")
            return

        new_domain = self._ask_ssl_domain()
        if not new_domain:
            print(f"\n{Colors.WARNING}Nenhum domínio inserido. Operação cancelada.{Colors.ENDC}")
            return
        
        self.config["sni"] = new_domain
        self.save_config()
        print(f"\n{Colors.GREEN}[✓] Domínio (SNI) alterado para {new_domain}.{Colors.ENDC}")
        print(f"{Colors.WARNING}Iniciando a reinstalação para gerar o novo certificado...{Colors.ENDC}")
        
        install_script_path = self.find_install_script()
        if not install_script_path:
            print(f"{Colors.FAIL}[!] Erro: Script 'install.sh' não encontrado para gerar o certificado.{Colors.ENDC}")
            return
            
        try:
            subprocess.run(["/bin/bash", install_script_path], check=True)
            print(f"\n{Colors.GREEN}[✓] Script de instalação executado com sucesso para atualizar o certificado!{Colors.ENDC}")
        except subprocess.CalledProcessError as e:
            print(f"\n{Colors.FAIL}[!] Erro ao executar o script de instalação: {e}{Colors.ENDC}")
        except Exception as e:
            print(f"\n{Colors.FAIL}[!] Um erro inesperado ocorreu: {e}{Colors.ENDC}")

    def configure_workers(self):
        self.print_header("CONFIGURAR WORKERS")
        self.print_divider()
        print(f"{Colors.BOLD}Workers atuais:{Colors.ENDC} {Colors.BLUE}{self.config['workers']}{Colors.ENDC}\n")
        workers_input = input(f"{Colors.BOLD}Digite o número de workers:{Colors.ENDC} ")
        try:
            new_workers = int(workers_input)
            if new_workers > 0:
                self.config["workers"] = new_workers
                self.save_config()
                print(f"\n{Colors.GREEN}[✓] Workers configurados para {new_workers}!{Colors.ENDC}")
            else:
                print(f"\n{Colors.FAIL}[!] Número de workers deve ser maior que 0.{Colors.ENDC}")
        except ValueError:
            print(f"\n{Colors.FAIL}[!] Entrada inválida. Por favor, digite um número.{Colors.ENDC}")

    def configure_buffer_size(self):
        self.print_header("CONFIGURAR BUFFER SIZE")
        self.print_divider()
        print(f"{Colors.BOLD}Buffer size atual:{Colors.ENDC} {Colors.BLUE}{self.config['buffer_size']}{Colors.ENDC}\n")
        buffer_input = input(f"{Colors.BOLD}Digite o tamanho do buffer:{Colors.ENDC} ")
        try:
            new_buffer = int(buffer_input)
            if new_buffer > 0:
                self.config["buffer_size"] = new_buffer
                self.save_config()
                print(f"\n{Colors.GREEN}[✓] Buffer size configurado para {new_buffer}!{Colors.ENDC}")
            else:
                print(f"\n{Colors.FAIL}[!] Buffer size deve ser maior que 0.{Colors.ENDC}")
        except ValueError:
            print(f"\n{Colors.FAIL}[!] Entrada inválida. Por favor, digite um número.{Colors.ENDC}")

    def configure_log_level(self):
        self.print_header("CONFIGURAR LOG LEVEL")
        self.print_divider()
        print(f"{Colors.BOLD}Log level atual:{Colors.ENDC} {Colors.BLUE}{self.config['log_level']}{Colors.ENDC}\n")
        print(f"{Colors.BOLD}Níveis disponíveis:{Colors.ENDC} 0 (Silencioso), 1 (Normal), 2 (Verboso)\n")
        log_input = input(f"{Colors.BOLD}Digite o nível de log (0-2):{Colors.ENDC} ")
        try:
            new_log_level = int(log_input)
            if 0 <= new_log_level <= 2:
                self.config["log_level"] = new_log_level
                self.save_config()
                print(f"\n{Colors.GREEN}[✓] Log level configurado para {new_log_level}!{Colors.ENDC}")
            else:
                print(f"\n{Colors.FAIL}[!] Log level deve estar entre 0 e 2.{Colors.ENDC}")
        except ValueError:
            print(f"\n{Colors.FAIL}[!] Entrada inválida. Por favor, digite um número.{Colors.ENDC}")

    def run_install_script(self):
        """Encontra e executa o script de instalação."""
        self.print_header("INSTALAR/REINSTALAR MULTIFLOW PROXY")
        
        install_script_path = self.find_install_script()
        
        if not install_script_path:
            print(f"{Colors.FAIL}[!] Erro: Script 'install.sh' não encontrado.{Colors.ENDC}")
            print(f"{Colors.WARNING}Por favor, certifique-se de que o repositório foi clonado em /root/multiflowpx ou execute este menu a partir do diretório do projeto.{Colors.ENDC}")
            return

        install_port = self._ask_for_install_port()
        install_protocols = self._ask_for_protocols()
        
        print(f"\n{Colors.WARNING}Esta opção executará a instalação na porta {install_port} com os protocolos selecionados.{Colors.ENDC}")
        print(f"{Colors.WARNING}Isso pode sobrescrever configurações existentes.{Colors.ENDC}\n")
        
        confirm = input(f"{Colors.BOLD}Deseja continuar? (s/N):{Colors.ENDC} ").lower()
        if confirm in ['s', 'sim', 'y', 'yes']:
            if not self.check_root(): return
            try:
                self.config['port'] = [install_port]
                self.config['mode'] = install_protocols
                self.save_config()
                
                subprocess.run(["chmod", "+x", install_script_path], check=True)
                subprocess.run(["/bin/bash", install_script_path], check=True)
                print(f"\n{Colors.GREEN}[✓] Instalação concluída com sucesso!{Colors.ENDC}")
            except subprocess.CalledProcessError as e:
                print(f"\n{Colors.FAIL}[!] Erro durante a instalação: {e}{Colors.ENDC}")
            except Exception as e:
                print(f"\n{Colors.FAIL}[!] Um erro inesperado ocorreu: {e}{Colors.ENDC}")
        else:
            print(f"\n{Colors.WARNING}Instalação cancelada.{Colors.ENDC}")

    def menu_uninstall(self):
        """Menu para desinstalar o MultiFlowPX."""
        self.print_header("DESINSTALAR MULTIFLOWPX")
        print(f"{Colors.FAIL}ATENÇÃO: Esta operação removerá completamente o MultiFlowPX!{Colors.ENDC}")
        print(f"{Colors.WARNING}Isso incluirá:{Colors.ENDC}")
        print(f"  • Parar o serviço")
        print(f"  • Remover arquivos de configuração")
        print(f"  • Remover executáveis")
        print(f"  • Remover serviço systemd\n")
        
        confirm = input(f"{Colors.BOLD}Tem certeza que deseja desinstalar? (s/N):{Colors.ENDC} ").lower()
        if confirm in ['s', 'sim', 'y', 'yes']:
            self.uninstall()
        else:
            print(f"\n{Colors.WARNING}Desinstalação cancelada.{Colors.ENDC}")

    def uninstall(self):
        """Desinstala completamente o MultiFlowPX."""
        if not self.systemctl_path:
            self._notify_systemctl_unavailable()
            return
        if not self.check_root(): return
        
        try:
            print("Parando e desabilitando o serviço systemd...")
            subprocess.run([self.systemctl_path, "stop", "multiflowpx.service"], check=False, capture_output=True)
            subprocess.run([self.systemctl_path, "disable", "multiflowpx.service"], check=False, capture_output=True)
            
            files_to_remove = [
                "/etc/systemd/system/multiflowpx.service",
                "/usr/local/bin/multiflowpx_proxy",
                "/usr/local/bin/multiflowpx_menu",
                CONFIG_FILE
            ]
            
            print("Removendo arquivos...")
            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        print(f"  {Colors.GREEN}Removido:{Colors.ENDC} {file_path}")
                    except OSError as e:
                        print(f"  {Colors.FAIL}Erro ao remover {file_path}: {e}{Colors.ENDC}")

            config_dir = os.path.dirname(CONFIG_FILE)
            if os.path.exists(config_dir) and not os.listdir(config_dir):
                try:
                    os.rmdir(config_dir)
                    print(f"  {Colors.GREEN}Removido diretório vazio:{Colors.ENDC} {config_dir}")
                except OSError as e:
                    print(f"  {Colors.FAIL}Erro ao remover diretório {config_dir}: {e}{Colors.ENDC}")
            
            print("Recarregando o daemon do systemd...")
            subprocess.run([self.systemctl_path, "daemon-reload"], check=True)
            
            print(f"\n{Colors.GREEN}[✓] MultiFlowPX desinstalado com sucesso!{Colors.ENDC}")
            
        except Exception as e:
            print(f"\n{Colors.FAIL}[!] Erro durante a desinstalação: {e}{Colors.ENDC}")

if __name__ == "__main__":
    menu = ProxyMenu()
    menu.main_menu()
