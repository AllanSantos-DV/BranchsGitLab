"""
Controller para gerenciar a autenticação no GitLab
"""
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal

class AuthenticationThread(QThread):
    """Thread para realizar autenticação sem bloquear a UI"""
    
    # Sinais para comunicar resultado
    auth_success = pyqtSignal(str)  # username
    auth_failure = pyqtSignal(str)  # mensagem de erro
    
    def __init__(self, gitlab_api, url, username, token):
        super().__init__()
        self.gitlab_api = gitlab_api
        self.url = url
        self.username = username
        self.token = token
        
    def run(self):
        """Executa a autenticação em uma thread separada"""
        try:
            success, message = self.gitlab_api.login(self.url, self.token)
            
            if success:
                self.auth_success.emit(self.username)
            else:
                self.auth_failure.emit(message)
        except Exception as e:
            self.auth_failure.emit(f"Erro inesperado: {str(e)}")


class LoginController:
    """
    Controller responsável pela lógica de autenticação no GitLab
    """
    
    def __init__(self, view, model, parent_controller=None):
        """
        Inicializa o controller de login
        
        Args:
            view: View de login (LoginView ou LoginTabView)
            model: Modelo de API do GitLab (GitLabAPI)
            parent_controller: Controller pai (AppController)
        """
        self.view = view
        self.model = model
        self.parent = parent_controller
        self.auth_thread = None
        
        # Conectar sinais da view
        # Verificar o tipo de view e conectar ao sinal apropriado
        if hasattr(self.view, 'token_login_requested'):
            self.view.token_login_requested.connect(self.login)
        else:
            self.view.login_requested.connect(self.login)
        
    def login(self, url, username, token):
        """
        Realiza o login no GitLab
        
        Args:
            url (str): URL da instância do GitLab
            username (str): Nome de usuário
            token (str): Token de acesso
        """
        if not url or not token:
            QMessageBox.warning(
                self.view, 
                "Erro de Login", 
                "URL e token são obrigatórios para acessar o GitLab."
            )
            return
        
        # Desabilitar botão de login e mostrar status
        # Verificar o tipo de view para chamar o método correto
        if hasattr(self.view, 'set_token_login_button_enabled'):
            self.view.set_token_login_button_enabled(False)
            self.view.set_token_login_status("Conectando ao GitLab...")
        else:
            self.view.set_login_button_enabled(False)
            self.view.set_login_status("Conectando ao GitLab...")
        
        # Criar e iniciar thread de autenticação
        self.auth_thread = AuthenticationThread(self.model, url, username, token)
        self.auth_thread.auth_success.connect(self.on_login_success)
        self.auth_thread.auth_failure.connect(self.on_login_failure)
        self.auth_thread.finished.connect(self.on_thread_finished)
        self.auth_thread.start()
        
    def on_login_success(self, username):
        """Callback para login bem-sucedido"""
        self.parent.set_status(f"Logado como {username}")
        self.parent.after_login_success(username)
        
    def on_login_failure(self, message):
        """Callback para falha no login"""
        # Verificar o tipo de view para chamar o método correto
        if hasattr(self.view, 'set_token_login_status'):
            self.view.set_token_login_status("")
        else:
            self.view.set_login_status("")
            
        QMessageBox.critical(
            self.view, 
            "Erro de Login", 
            f"Não foi possível autenticar no GitLab: {message}"
        )
        
    def on_thread_finished(self):
        """Callback quando a thread termina"""
        # Verificar o tipo de view para chamar o método correto
        if hasattr(self.view, 'set_token_login_button_enabled'):
            self.view.set_token_login_button_enabled(True)
        else:
            self.view.set_login_button_enabled(True)
            
        self.auth_thread = None 