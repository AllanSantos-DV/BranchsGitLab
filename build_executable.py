#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para criar um executável standalone da aplicação Gerenciador de Branches GitLab
Utiliza PyInstaller para empacotar a aplicação com todas as dependências
"""

import os
import sys
import shutil
import subprocess
import glob
from pathlib import Path

def check_pyinstaller():
    """Verifica se o PyInstaller está instalado e instala se necessário."""
    try:
        import PyInstaller
        print("PyInstaller já está instalado.")
        return True
    except ImportError:
        print("PyInstaller não encontrado. Instalando...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("PyInstaller instalado com sucesso.")
            return True
        except subprocess.CalledProcessError:
            print("Erro ao instalar PyInstaller. Por favor, instale manualmente com: pip install pyinstaller")
            return False

def clean_directories():
    """Limpa os diretórios build e dist se existirem."""
    directories = ['build', 'dist']
    for directory in directories:
        if os.path.exists(directory):
            print(f"Limpando diretório: {directory}")
            shutil.rmtree(directory)
    
    # Remover arquivos .spec
    for spec_file in glob.glob("*.spec"):
        print(f"Removendo arquivo .spec: {spec_file}")
        os.remove(spec_file)

def check_icon_file():
    """Verifica se o arquivo de ícone existe e cria um aviso se não existir."""
    icon_path = "resources/icon.ico"
    if not os.path.exists(icon_path):
        print(f"AVISO: Arquivo de ícone '{icon_path}' não encontrado!")
        print("O executável será gerado sem um ícone personalizado.")
        print("Para adicionar um ícone, crie um arquivo .ico na pasta resources.")
        return False
    return True

def check_resources():
    """Verifica se os arquivos de recursos necessários existem."""
    required_resources = [
        'resources/open.png', 
        'resources/closed.png'
    ]
    
    missing_resources = []
    for resource in required_resources:
        if not os.path.exists(resource):
            missing_resources.append(resource)
    
    if missing_resources:
        print("AVISO: Os seguintes recursos estão faltando:")
        for resource in missing_resources:
            print(f" - {resource}")
        print("Estes recursos são necessários para o funcionamento correto da aplicação.")
        return False
    
    print("Todos os recursos necessários foram encontrados.")
    return True

def list_resources():
    """Lista detalhadamente todos os recursos na pasta resources."""
    if not os.path.exists("resources"):
        print("ERRO: A pasta 'resources' não foi encontrada!")
        return False
    
    print("\n=== Verificação detalhada de recursos ===")
    resources_path = os.path.abspath("resources")
    print(f"Pasta de recursos: {resources_path}")
    
    files = os.listdir(resources_path)
    if not files:
        print("AVISO: A pasta 'resources' está vazia!")
        return False
    
    print(f"Total de arquivos encontrados: {len(files)}")
    for file in files:
        file_path = os.path.join(resources_path, file)
        file_size = os.path.getsize(file_path) / 1024  # Tamanho em KB
        print(f" - {file} ({file_size:.2f} KB) - {os.path.abspath(file_path)}")
    
    return True

def build_executable():
    """Constrói o executável usando PyInstaller."""
    app_name = "GerenciadorBranchesGitLab"
    main_file = "main.py"
    
    # Verificar se o arquivo principal existe
    if not os.path.exists(main_file):
        print(f"Arquivo principal '{main_file}' não encontrado!")
        return False
    
    # Verificar se o ícone existe
    has_icon = check_icon_file()
    
    # Verificar recursos necessários
    check_resources()
    
    # Listar recursos detalhadamente
    list_resources()
    
    # Obter caminho absoluto para resources
    resources_path = os.path.abspath("resources")
    
    # Formato do separador para --add-data
    # No Windows: usar ponto e vírgula (;)
    # No Linux/Mac: usar dois pontos (:)
    separator = ";" if sys.platform.startswith("win") else ":"
    add_data_arg = f"{resources_path}{separator}resources"
    
    print(f"\nArgumento --add-data que será usado: {add_data_arg}")
    
    # Definir os argumentos do PyInstaller
    pyinstaller_args = [
        "--name=" + app_name,
        "--onefile",               # Empacotar tudo em um único executável
        "--windowed",              # Não mostrar console para aplicações GUI
        "--clean",                 # Limpar dados de compilação anteriores
        "--noconfirm",             # Não perguntar sobre sobrescrever
        f"--add-data={add_data_arg}",  # Incluir recursos
    ]
    
    # Adicionar o ícone apenas se existir
    if has_icon:
        icon_path = os.path.abspath("resources/icon.ico")
        pyinstaller_args.append(f"--icon={icon_path}")
    
    # Adicionar imports ocultos e o arquivo principal
    pyinstaller_args.extend([
        "--hidden-import=PyQt6",   # Garantir que PyQt6 seja incluído
        "--hidden-import=python-gitlab",
        "--hidden-import=gitpython",
        main_file
    ])
    
    # Construir o comando
    cmd = [sys.executable, "-m", "PyInstaller"] + pyinstaller_args
    
    print("\nIniciando o build do executável...")
    print(f"Comando: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print(f"Executável criado com sucesso em: dist/{app_name}.exe")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erro ao criar o executável: {e}")
        return False

def cleanup_after_build():
    """Limpa arquivos e diretórios após o build bem-sucedido."""
    # Remover diretório build
    if os.path.exists("build"):
        print("Removendo diretório 'build'...")
        shutil.rmtree("build")
    
    # Remover arquivos .spec
    for spec_file in glob.glob("*.spec"):
        print(f"Removendo arquivo .spec: {spec_file}")
        os.remove(spec_file)
    
    print("Limpeza pós-build concluída.")

def main():
    print("=== Gerador de Executável - Gerenciador de Branches GitLab ===")
    
    # Verificar PyInstaller
    if not check_pyinstaller():
        return
    
    # Limpar diretórios antes de iniciar
    clean_directories()
    
    # Construir executável
    if build_executable():
        # Limpar após o build
        cleanup_after_build()
        print("Processo concluído com sucesso.")
    else:
        print("Falha ao gerar o executável.")

if __name__ == "__main__":
    main() 