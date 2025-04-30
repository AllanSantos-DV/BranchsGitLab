"""
View integrada para múltiplos métodos de login
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import pyqtSignal

from views.login_view import LoginView
from views.ldap_login_view import LDAPLoginView

class LoginTabView(QWidget):
    """
    View que integra múltiplos métodos de login através de abas
    """
    
    # Sinais
    token_login_requested = pyqtSignal(str, str, str)  # (url, username, token)
    ldap_login_requested = pyqtSignal(dict)  # dict com todos os parâmetros LDAP
    
    def __init__(self, parent=None):
        """
        Inicializa a view de login com abas
        
        Args:
            parent (QWidget): Widget pai
        """
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """
        Inicializa a interface de usuário
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Criar o widget de abas
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #CCCCCC;
                background-color: white;
                border-radius: 6px;
            }
            QTabBar::tab {
                background-color: #E0E0E0;
                border: 1px solid #CCCCCC;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 10px 20px;
                margin-right: 3px;
                color: #333333;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: #2B5797;
                color: white;
                border-bottom-color: #2B5797;
            }
            QTabBar::tab:hover:!selected {
                background-color: #D0D0D0;
            }
            QTabBar::tab:selected:hover {
                background-color: #1D3C6E;
            }
        """)
        
        # Criar view de login por token
        self.token_login_view = LoginView()
        self.token_login_view.login_requested.connect(self._on_token_login_requested)
        
        # Criar view de login LDAP
        self.ldap_login_view = LDAPLoginView()
        self.ldap_login_view.ldap_login_requested.connect(self._on_ldap_login_requested)
        
        # Adicionar abas
        self.tab_widget.addTab(self.token_login_view, "Token de Acesso")
        self.tab_widget.addTab(self.ldap_login_view, "LDAP/Active Directory")
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
    
    def _on_token_login_requested(self, url, username, token):
        """
        Repassa o sinal de login por token
        """
        self.token_login_requested.emit(url, username, token)
    
    def _on_ldap_login_requested(self, ldap_params):
        """
        Repassa o sinal de login LDAP
        """
        self.ldap_login_requested.emit(ldap_params)
        
    def set_token_login_status(self, message):
        """
        Define a mensagem de status na aba de login por token
        
        Args:
            message (str): Mensagem de status
        """
        self.token_login_view.set_login_status(message)
    
    def set_ldap_login_status(self, message):
        """
        Define a mensagem de status na aba de login LDAP
        
        Args:
            message (str): Mensagem de status
        """
        self.ldap_login_view.set_status(message)
    
    def set_token_login_button_enabled(self, enabled):
        """
        Habilita ou desabilita o botão de login por token
        
        Args:
            enabled (bool): Se True, o botão estará habilitado
        """
        self.token_login_view.set_login_button_enabled(enabled)
    
    def set_ldap_login_button_enabled(self, enabled):
        """
        Habilita ou desabilita o botão de login LDAP
        
        Args:
            enabled (bool): Se True, o botão estará habilitado
        """
        self.ldap_login_view.set_login_button_enabled(enabled)
        
    def clear(self):
        """
        Limpa os campos de entrada
        """
        self.token_login_view.clear()
        self.ldap_login_view.clear_password() 