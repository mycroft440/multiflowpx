#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiFlowPX Core Module
Módulo principal contendo a lógica de negócio do MultiFlowPX Proxy Server.
"""

import os
import json
import subprocess
import shutil
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

# --- Decorators ---
def requires_root(func):
    """Decorator para métodos que requerem privilégios root."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not check_root():
            return None
        return func(self, *args, **kwargs)
    return wrapper

def requires_systemctl(func):
    """Decorator para métodos que requerem systemctl."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.systemctl_path:
            return None
        return func(self, *args, **kwargs)
    return wrapper

# --- Funções Auxiliares ---
def check_root() -> bool:
    """Verifica se o script está sendo executado como root."""
    if not hasattr(os, 'geteuid'):
        return True
    return os.geteuid() == 0

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
        except (IOError, json.JSONDecodeError):
            pass
        
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
            return True
        except IOError:
            return False
    
    def add_port(self, port: int) -> bool:
        """Adiciona uma porta à configuração."""
        if port not in self.config["port"]:
            self.config["port"].append(port)
            return True
        return False
    
    def remove_port(self, port: int) -> bool:
        """Remove uma porta da configuração."""
        if port in self.config["port"]:
            self.config["port"].remove(port)
            return True
        return False
    
    def set_protocols(self, protocols: List[str]):
        """Define os protocolos."""
        self.config['mode'] = protocols
    
    def set_host(self, host: str):
        """Define o host de destino."""
        self.config["host"] = host
    
    def set_sni(self, sni: str):
        """Define o SNI (domínio)."""
        self.config["sni"] = sni
    
    def set_workers(self, workers: int):
        """Define o número de workers."""
        self.config["workers"] = workers
    
    def set_buffer_size(self, buffer_size: int):
        """Define o tamanho do buffer."""
        self.config["buffer_size"] = buffer_size
    
    def set_log_level(self, log_level: int):
        """Define o nível de log."""
        self.config["log_level"] = log_level
    
    def get_config(self) -> Dict[str, Any]:
        """Retorna a configuração atual."""
        return self.config.copy()

class ServiceManager:
    """Gerencia operações relacionadas ao serviço systemd."""
    
    def __init__(self):
        self.systemctl_path = shutil.which("systemctl")
        self.service_name = "multiflowpx.service"
    
    def is_available(self) -> bool:
        """Verifica se systemctl está disponível."""
        return bool(self.systemctl_path)
    
    def is_running(self) -> bool:
        """Verifica se o serviço está em execução."""
        if not self.systemctl_path:
            return False
        result = subprocess.run(
            [self.systemctl_path, "is-active", "--quiet", self.service_name],
            capture_output=True
        )
        return result.returncode == 0
    
    @requires_systemctl
    def start(self) -> bool:
        """Inicia o serviço."""
        try:
            subprocess.run([self.systemctl_path, "start", self.service_name], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    @requires_systemctl
    def stop(self) -> bool:
        """Para o serviço."""
        try:
            subprocess.run([self.systemctl_path, "stop", self.service_name], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    @requires_systemctl
    def restart(self) -> bool:
        """Reinicia o serviço."""
        try:
            subprocess.run([self.systemctl_path, "restart", self.service_name], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    @requires_systemctl
    def disable(self) -> bool:
        """Desabilita o serviço."""
        try:
            subprocess.run([self.systemctl_path, "disable", self.service_name], 
                         check=False, capture_output=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    @requires_systemctl
    def daemon_reload(self) -> bool:
        """Recarrega o daemon do systemd."""
        try:
            subprocess.run([self.systemctl_path, "daemon-reload"], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

class InstallManager:
    """Gerencia operações de instalação e desinstalação."""
    
    @staticmethod
    def find_install_script() -> Optional[str]:
        """Detecta dinamicamente o script de instalação 'install.sh'."""
        potential_paths = [
            '/root/multiflowpx/install.sh',
            os.path.join(os.path.expanduser("~"), 'multiflowpx/install.sh'),
            './install.sh'
        ]
        
        for path in potential_paths:
            if os.path.isfile(path):
                return path
        return None
    
    @staticmethod
    def run_install_script(script_path: str) -> bool:
        """Executa o script de instalação."""
        try:
            subprocess.run(["chmod", "+x", script_path], check=True)
            subprocess.run(["/bin/bash", script_path], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
        except Exception:
            return False
    
    @staticmethod
    def uninstall(service_manager: ServiceManager) -> tuple[bool, List[str]]:
        """
        Desinstala completamente o MultiFlowPX.
        Retorna (sucesso, lista_de_mensagens)
        """
        messages = []
        
        try:
            # Parar e desabilitar serviço
            if service_manager.is_available():
                service_manager.stop()
                service_manager.disable()
                messages.append("Serviço parado e desabilitado")
            
            # Arquivos para remover
            files_to_remove = [
                "/etc/systemd/system/multiflowpx.service",
                "/usr/local/bin/multiflowpx_proxy",
                "/usr/local/bin/multiflowpx_menu",
                CONFIG_FILE
            ]
            
            # Remover arquivos
            for file_path in files_to_remove:
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                        messages.append(f"Removido: {file_path}")
                    except OSError as e:
                        messages.append(f"Erro ao remover {file_path}: {e}")
            
            # Remover diretório de configuração se vazio
            config_dir = os.path.dirname(CONFIG_FILE)
            if os.path.exists(config_dir) and not os.listdir(config_dir):
                try:
                    os.rmdir(config_dir)
                    messages.append(f"Removido diretório: {config_dir}")
                except OSError as e:
                    messages.append(f"Erro ao remover diretório {config_dir}: {e}")
            
            # Recarregar daemon
            if service_manager.is_available():
                service_manager.daemon_reload()
                messages.append("Daemon recarregado")
            
            return True, messages
            
        except Exception as e:
            messages.append(f"Erro crítico: {e}")
            return False, messages

def validate_port(port_value: Any) -> Optional[int]:
    """Valida se um valor é uma porta válida."""
    try:
        port = int(port_value)
        if MIN_PORT <= port <= MAX_PORT:
            return port
    except (ValueError, TypeError):
        pass
    return None

def validate_host_format(host: str) -> bool:
    """Valida o formato de host (IP:PORTA)."""
    parts = host.split(':')
    if len(parts) != 2:
        return False
    
    try:
        port = int(parts[1])
        return MIN_PORT <= port <= MAX_PORT
    except ValueError:
        return False
