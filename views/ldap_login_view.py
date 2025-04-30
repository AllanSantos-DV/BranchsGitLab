"""
View para a tela de login LDAP/Active Directory
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QGroupBox, QFormLayout,
                           QCheckBox, QComboBox, QTabWidget, QSplitter)
from PyQt6.QtCore import pyqtSignal, Qt

class LDAPLoginView(QWidget):
    """
    View responsável pela interface de login LDAP/AD para GitLab
    """
    
    # Sinais
    ldap_login_requested = pyqtSignal(dict)  # dict com todos os parâmetros LDAP
    
    def __init__(self, parent=None):
        """
        Inicializa a view de login LDAP
        
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
        title_layout = QHBoxLayout()
        title_label = QLabel("Login via LDAP/Active Directory")
        title_label.setProperty("title", "true")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2B5797; margin-bottom: 10px;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Informações explicativas
        info_label = QLabel(
            "Use suas credenciais LDAP/Active Directory para autenticar no GitLab. "
            "O sistema tentará autenticar no servidor LDAP e depois acessar o GitLab."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #555555; margin-bottom: 15px; font-size: 13px;")
        layout.addWidget(info_label)
        
        # Formulário GitLab
        gitlab_form_layout = QFormLayout()
        gitlab_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Campo de URL do GitLab
        self.gitlab_url_input = QLineEdit()
        self.gitlab_url_input.setPlaceholderText("https://gitlab.example.com")
        gitlab_form_layout.addRow("URL do GitLab:", self.gitlab_url_input)
        
        gitlab_group = QGroupBox("Configuração do GitLab")
        gitlab_group.setStyleSheet("""
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
        """)
        gitlab_group.setLayout(gitlab_form_layout)
        layout.addWidget(gitlab_group)
        
        # Formulário LDAP
        ldap_form_layout = QFormLayout()
        ldap_form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        # Campo de Servidor LDAP
        self.ldap_server_input = QLineEdit()
        self.ldap_server_input.setPlaceholderText("ldap.example.com")
        ldap_form_layout.addRow("Servidor LDAP:", self.ldap_server_input)
        
        # Campo de Domínio
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("example.com")
        ldap_form_layout.addRow("Domínio:", self.domain_input)
        
        # Campo de Usuário LDAP
        self.ldap_username_input = QLineEdit()
        self.ldap_username_input.setPlaceholderText("Seu nome de usuário LDAP")
        ldap_form_layout.addRow("Usuário:", self.ldap_username_input)
        
        # Campo de Senha LDAP
        self.ldap_password_input = QLineEdit()
        self.ldap_password_input.setPlaceholderText("Sua senha LDAP")
        self.ldap_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        ldap_form_layout.addRow("Senha:", self.ldap_password_input)
        
        # Configurações adicionais
        extra_layout = QHBoxLayout()
        
        # Método de Autenticação
        self.auth_method_combo = QComboBox()
        self.auth_method_combo.addItems(["SIMPLE", "NTLM", "GSSAPI"])
        self.auth_method_combo.setCurrentIndex(0)
        self.auth_method_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right;
                width: 20px;
                border-left: 1px solid #CCCCCC;
            }
        """)
        ldap_form_layout.addRow("Método Auth:", self.auth_method_combo)
        
        # Checkbox SSL
        self.use_ssl_checkbox = QCheckBox("Usar SSL")
        self.use_ssl_checkbox.setChecked(True)
        self.use_ssl_checkbox.setStyleSheet("""
            QCheckBox {
                color: #333333;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
        """)
        extra_layout.addWidget(self.use_ssl_checkbox)
        
        # Adicionar layout extra
        ldap_form_layout.addRow("Opções:", extra_layout)
        
        ldap_group = QGroupBox("Configuração LDAP/AD")
        ldap_group.setStyleSheet("""
            QGroupBox {
                background-color: #F5F5F5;
                border: 1px solid #DDDDDD;
                border-radius: 6px;
                margin-top: 15px;
                font-weight: bold;
                padding: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2B5797;
            }
        """)
        ldap_group.setLayout(ldap_form_layout)
        layout.addWidget(ldap_group)
        
        # Status de login
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #2B5797; font-weight: bold; margin-top: 15px;")
        layout.addWidget(self.status_label)
        
        # Botão de Login
        self.login_button = QPushButton("Autenticar via LDAP")
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #007E33;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #006129;
            }
            QPushButton:disabled {
                background-color: #AAAAAA;
                color: #EEEEEE;
            }
        """)
        self.login_button.clicked.connect(self._on_login_clicked)
        layout.addWidget(self.login_button)
        
        # Espaçador final
        layout.addStretch()
        
        self.setLayout(layout)
        
    def _on_login_clicked(self):
        """
        Callback para quando o botão de login LDAP é clicado
        """
        # Coletar todos os dados do formulário
        ldap_params = {
            'gitlab_url': self.gitlab_url_input.text(),
            'ldap_server': self.ldap_server_input.text(),
            'domain': self.domain_input.text(),
            'username': self.ldap_username_input.text(),
            'password': self.ldap_password_input.text(),
            'use_ssl': self.use_ssl_checkbox.isChecked(),
            'auth_method': self.auth_method_combo.currentText()
        }
        
        # Emitir sinal com todos os parâmetros
        self.ldap_login_requested.emit(ldap_params)
        
    def set_status(self, message):
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
            self.login_button.setText("Autenticar via LDAP")
    
    def clear_password(self):
        """
        Limpa o campo de senha por segurança
        """
        self.ldap_password_input.clear() 