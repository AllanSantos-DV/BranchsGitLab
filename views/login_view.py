"""
View para a tela de login no GitLab
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QGroupBox, QFormLayout)
from PyQt6.QtCore import pyqtSignal, Qt

class LoginView(QWidget):
    """
    View responsável pela interface de login no GitLab
    """
    
    # Sinais
    login_requested = pyqtSignal(str, str, str)  # (url, username, token)
    
    def __init__(self, parent=None):
        """
        Inicializa a view de login
        
        Args:
            parent (QWidget): Widget pai
        """
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """
        Inicializa a interface do usuário
        """
        layout = QVBoxLayout()
        
        # Título
        title_label = QLabel("Login no GitLab com Token")
        title_label.setProperty("title", "true")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2B5797; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Informações explicativas
        info_label = QLabel(
            "Utilize seu token de acesso pessoal para se conectar ao GitLab. "
            "Você pode criar um token em seu perfil GitLab em Configurações → Tokens de Acesso."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #555555; margin-bottom: 15px; font-size: 13px;")
        layout.addWidget(info_label)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Campo de URL do GitLab
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://gitlab.com")
        self.url_input.setText("https://gitlab.com")
        self.url_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                color: #333333;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #2B5797;
            }
        """)
        form_layout.addRow("URL do GitLab:", self.url_input)
        
        # Campo de Usuário
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Seu nome de usuário")
        self.username_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                color: #333333;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #2B5797;
            }
        """)
        form_layout.addRow("Usuário:", self.username_input)
        
        # Campo de Token
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Seu token de acesso pessoal")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.token_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                color: #333333;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #2B5797;
            }
        """)
        form_layout.addRow("Token de Acesso:", self.token_input)
        
        form_group = QGroupBox("Credenciais")
        form_group.setStyleSheet("""
            QGroupBox {
                background-color: #F5F5F5;
                border: 1px solid #DDDDDD;
                border-radius: 6px;
                margin-top: 10px;
                font-weight: bold;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2B5797;
            }
            QLabel {
                color: #333333;
                font-weight: bold;
            }
        """)
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Status de login
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #2B5797; font-weight: bold; margin-top: 15px;")
        layout.addWidget(self.status_label)
        
        # Botão de Login
        self.login_button = QPushButton("Entrar")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #2B5797;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #1D3C6E;
            }
            QPushButton:disabled {
                background-color: #AAAAAA;
                color: #EEEEEE;
            }
        """)
        layout.addWidget(self.login_button)
        
        # Espaçador final
        layout.addStretch()
        
        # Conectar sinais
        self.login_button.clicked.connect(self._on_login_clicked)
        
        self.setLayout(layout)
        
    def _on_login_clicked(self):
        """
        Callback para quando o botão de login é clicado
        """
        url = self.url_input.text()
        username = self.username_input.text()
        token = self.token_input.text()
        
        self.login_requested.emit(url, username, token)
        
    def get_credentials(self):
        """
        Retorna as credenciais inseridas pelo usuário
        
        Returns:
            tuple: (url, username, token)
        """
        return (
            self.url_input.text(),
            self.username_input.text(),
            self.token_input.text()
        )
        
    def clear(self):
        """
        Limpa os campos de entrada
        """
        self.username_input.clear()
        self.token_input.clear()
        
    def set_url(self, url):
        """
        Define a URL do GitLab
        
        Args:
            url (str): URL para definir
        """
        self.url_input.setText(url)
        
    def set_username(self, username):
        """
        Define o nome de usuário
        
        Args:
            username (str): Nome de usuário para definir
        """
        self.username_input.setText(username)
        
    def set_login_status(self, message):
        """
        Define a mensagem de status de login
        
        Args:
            message (str): Mensagem de status
        """
        self.status_label.setText(message)
        
    def set_login_button_enabled(self, enabled):
        """
        Habilita ou desabilita o botão de login
        
        Args:
            enabled (bool): Se True, o botão estará habilitado
        """
        self.login_button.setEnabled(enabled)
        
        if not enabled:
            self.login_button.setText("Conectando...")
        else:
            self.login_button.setText("Entrar") 