import subprocess
import sys
import os

def run_command(command):
    """
    Executa um comando no shell, exibe a saída em tempo real e verifica se há erros.
    """
    print(f"Executando: {' '.join(command)}")
    try:
        # Usando subprocess.run para mais controle e segurança
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        # Exibe a saída em tempo real
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        # Verifica o código de retorno ao final
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

def install_dependencies():
    """Instala as dependências de compilação necessárias para o projeto."""
    # Verifica se o script está sendo executado como root
    if os.geteuid() != 0:
        print("Este script precisa de privilégios de root para instalar pacotes.")
        print("Por favor, execute-o com 'sudo python3 instalar_deps_multiflowpx.py'")
        sys.exit(1)

    distro, id_like = get_distro_info()
    print(f"Distribuição Linux detectada: {distro}")

    packages = []
    manager = None

    # Determina o gerenciador de pacotes e a lista de pacotes
    if distro in ['ubuntu', 'debian'] or 'debian' in id_like:
        manager = "apt-get"
        packages = ["build-essential", "cmake", "libssl-dev", "libcurl4-openssl-dev", "libboost-all-dev"]
        if not run_command([manager, "update"]):
             print("Falha ao atualizar a lista de pacotes.", file=sys.stderr)
             sys.exit(1)
    elif distro in ['centos', 'fedora', 'rhel'] or 'rhel' in id_like or 'fedora' in id_like:
        if os.path.exists('/usr/bin/dnf'):
            manager = "dnf"
        else:
            manager = "yum"
        packages = ["gcc-c++", "make", "cmake", "openssl-devel", "libcurl-devel", "boost-devel"]
    else:
        print("Distribuição Linux não suportada automaticamente.", file=sys.stderr)
        print("Por favor, instale 'build-essential', 'cmake', e 'libssl-dev' (ou pacotes equivalentes) manualmente.", file=sys.stderr)
        sys.exit(1)

    print(f"\nInstalando os seguintes pacotes: {', '.join(packages)}")
    
    install_command = [manager, "install", "-y"] + packages
    
    if run_command(install_command):
        print("\nDependências instaladas com sucesso!")
    else:
        print("\nFalha ao instalar uma ou mais dependências. Verifique os erros acima.", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies()
