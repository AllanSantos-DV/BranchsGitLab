#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Branches GitLab
----------------------------
Aplicação para gerenciar branches de múltiplos projetos no GitLab, 
permitindo a remoção segura de branches não utilizadas.

Autor: Allan
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
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
        self.setMinimumSize(800, 600)
        

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