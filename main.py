#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Branches GitLab
----------------------------
Aplicação para gerenciar branches de múltiplos projetos no GitLab, 
permitindo a remoção segura de branches não utilizadas.

Autor: Allan
"""

import os
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow

from controllers.app_controller import AppController
from utils.constants import APP_STYLE


class MainWindow(QMainWindow):
    """
    Janela principal da aplicação
    """
    
    def __init__(self):
        """
        Inicializa a janela principal
        """
        super().__init__()
        self.setup_ui()
        
        # Inicializa o controller principal
        self.app_controller = AppController(self)
        
    def setup_ui(self):
        """
        Configura a interface da janela principal
        """
        self.setWindowTitle("Gerenciador de Branches GitLab")
        self.setMinimumSize(1000, 800)
        
        # Configurar ícone da aplicação
        self.setup_application_icon()
        
    def setup_application_icon(self):
        """
        Configura o ícone da aplicação
        """
        icon_path = self.get_resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
    
    def get_resource_path(self, relative_path):
        """
        Obtém o caminho correto para um recurso, funciona tanto em desenvolvimento
        quanto após empacotado com PyInstaller
        """
        if getattr(sys, 'frozen', False):
            # Se estiver em um executável PyInstaller
            base_path = sys._MEIPASS
        else:
            # Se estiver em desenvolvimento
            base_path = os.path.abspath(".")
            
        return os.path.join(base_path, "resources", relative_path)

def main():
    """
    Função principal da aplicação
    """
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Estilo moderno e consistente entre plataformas
    
    # Aplicar estilo personalizado
    app.setStyleSheet(APP_STYLE)
    
    # Criar e exibir janela principal
    window = MainWindow()
    window.show()
    
    # Executar o loop principal da aplicação
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 