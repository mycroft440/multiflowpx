import subprocess
import sys
import os

def run_command(command):
    """
    Executa um comando no shell, exibe a saída em tempo real e verifica se há erros.
    """
    print(f"Executando: {' '.join(command)}")
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        if process.returncode != 0:
            print(f"Erro ao executar o comando. Código de saída: {process.returncode}", file=sys.stderr)
            return False
        return True

    except FileNotFoundError:
        print(f"Erro: Comando '{command[0]}' não encontrado. Verifique se está instalado e no PATH.", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}", file=sys.stderr)
        return False

def get_distro_info():
    """Detecta a distribuição Linux e o gerenciador de pacotes."""
    try:
        with open('/etc/os-release') as f:
            lines = f.readlines()
            info = {line.split('=')[0]: line.split('=')[1].strip().strip('"') for line in lines if '=' in line}
            distro_id = info.get('ID', '').lower()
            id_like = info.get('ID_LIKE', '').lower()
            return distro_id, id_like
    except FileNotFoundError:
        return 'unknown', ''

def install_system_dependencies():
    """Instala as dependências de compilação e python necessárias para o projeto."""
    if os.geteuid() != 0:
        print("Este script precisa de privilégios de root para instalar pacotes do sistema.")
        print("Por favor, execute-o com 'sudo python3 instalar_deps_multiflowpx.py'")
        sys.exit(1)

    distro, id_like = get_distro_info()
    print(f"Distribuição Linux detectada: {distro}")

    apt_packages = ["build-essential", "cmake", "libssl-dev", "libcurl4-openssl-dev", "libboost-all-dev", "python3-pip"]
    dnf_packages = ["gcc-c++", "make", "cmake", "openssl-devel", "libcurl-devel", "boost-devel", "python3-pip"]

    if distro in ['ubuntu', 'debian'] or 'debian' in id_like:
        manager = "apt-get"
        packages_to_install = apt_packages
        if not run_command([manager, "update"]):
             print("Falha ao atualizar a lista de pacotes.", file=sys.stderr)
             sys.exit(1)
    elif distro in ['centos', 'fedora', 'rhel'] or 'rhel' in id_like or 'fedora' in id_like:
        if os.path.exists('/usr/bin/dnf'):
            manager = "dnf"
        else:
            manager = "yum"
        packages_to_install = dnf_packages
    else:
        print("Distribuição Linux não suportada automaticamente para instalação de dependências do sistema.", file=sys.stderr)
        print("Por favor, instale 'build-essential', 'cmake', 'libssl-dev', 'libcurl4-openssl-dev', 'libboost-all-dev' e 'python3-pip' (ou pacotes equivalentes) manualmente.", file=sys.stderr)
        sys.exit(1)

    print(f"\nInstalando os seguintes pacotes do sistema: {', '.join(packages_to_install)}")
    
    install_command = [manager, "install", "-y"] + packages_to_install
    
    if run_command(install_command):
        print("\nDependências do sistema instaladas com sucesso!")
    else:
        print("\nFalha ao instalar uma ou mais dependências do sistema. Verifique os erros acima.", file=sys.stderr)
        sys.exit(1)

def install_python_dependencies():
    """Instala as dependências Python usando pip."""
    print("\nInstalando dependências Python via pip...")
    # Adicione aqui quaisquer pacotes Python específicos que o projeto precise
    # Exemplo: python_packages = ["requests", "PyYAML"]
    python_packages = [] # Por enquanto, nenhum pacote Python específico identificado

    if python_packages:
        pip_command = [sys.executable, "-m", "pip", "install"] + python_packages
        if run_command(pip_command):
            print("Dependências Python instaladas com sucesso!")
        else:
            print("Falha ao instalar uma ou mais dependências Python. Verifique os erros acima.", file=sys.stderr)
            sys.exit(1)
    else:
        print("Nenhuma dependência Python específica para instalar.")

if __name__ == "__main__":
    install_system_dependencies()
    install_python_dependencies()

