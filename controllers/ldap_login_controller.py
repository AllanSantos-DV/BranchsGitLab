"""
Controller para gerenciar a autenticação LDAP/AD
"""
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal

class LDAPAuthenticationThread(QThread):
    """Thread para realizar autenticação LDAP sem bloquear a UI"""
    
    # Sinais para comunicar resultado
    auth_success = pyqtSignal(str)  # username
    auth_failure = pyqtSignal(str)  # mensagem de erro
    
    def __init__(self, ldap_auth, ldap_params):
        super().__init__()
        self.ldap_auth = ldap_auth
        self.ldap_params = ldap_params
        
    def run(self):
        """Executa a autenticação em uma thread separada"""
        try:
            # Autenticar no LDAP
            success, message = self.ldap_auth.authenticate(
                server_url=self.ldap_params['ldap_server'],
                domain=self.ldap_params['domain'],
                username=self.ldap_params['username'],
                password=self.ldap_params['password'],
                use_ssl=self.ldap_params['use_ssl'],
                auth_method=self.ldap_params['auth_method']
            )
            
            if success:
                # Tentar integrar com GitLab
                gitlab_success, gitlab_message = self.ldap_auth.integrate_with_gitlab(
                    gitlab_url=self.ldap_params['gitlab_url']
                )
                
                if gitlab_success:
                    # Emitir sinal de sucesso com o nome de usuário
                    self.auth_success.emit(self.ldap_params['username'])
                else:
                    # Falha na integração com GitLab
                    self.auth_failure.emit(f"Autenticação LDAP bem-sucedida, mas falha na integração com GitLab: {gitlab_message}")
            else:
                # Falha na autenticação LDAP
                self.auth_failure.emit(message)
        except Exception as e:
            self.auth_failure.emit(f"Erro inesperado: {str(e)}")
        finally:
            # Sempre fechar a conexão LDAP, independente do resultado
            if self.ldap_auth:
                self.ldap_auth.close()


class LDAPLoginController:
    """
    Controller responsável pela lógica de autenticação LDAP/AD
    """
    
    def __init__(self, view, ldap_model, gitlab_api, parent_controller=None):
        """
        Inicializa o controller de login LDAP
        
        Args:
            view: View de login (LDAPLoginView ou LoginTabView)
            ldap_model: Modelo de autenticação LDAP
            gitlab_api: Modelo de API do GitLab
            parent_controller: Controller pai (AppController)
        """
        self.view = view
        self.ldap_model = ldap_model
        self.gitlab_api = gitlab_api
        self.parent = parent_controller
        self.auth_thread = None
        
        # Configurar o modelo LDAP para usar a API do GitLab
        self.ldap_model.gitlab_api = self.gitlab_api
        
        # Conectar sinais da view
        self.view.ldap_login_requested.connect(self.login_ldap)
        
    def login_ldap(self, ldap_params):
        """
        Realiza o login via LDAP/AD
        
        Args:
            ldap_params (dict): Dicionário com os parâmetros de autenticação LDAP
        """
        # Validações básicas
        if not ldap_params['ldap_server'] or not ldap_params['domain'] or not ldap_params['username'] or not ldap_params['password']:
            QMessageBox.warning(
                self.view, 
                "Erro de Login LDAP", 
                "Servidor LDAP, domínio, nome de usuário e senha são obrigatórios."
            )
            return
            
        if not ldap_params['gitlab_url']:
            QMessageBox.warning(
                self.view, 
                "Erro de Login LDAP", 
                "URL do GitLab é obrigatória para integração após autenticação LDAP."
            )
            return
        
        # Desabilitar botão de login e mostrar status
        self.view.set_ldap_login_button_enabled(False)
        self.view.set_ldap_login_status("Conectando ao servidor LDAP...")
        
        # Criar e iniciar thread de autenticação
        self.auth_thread = LDAPAuthenticationThread(self.ldap_model, ldap_params)
        self.auth_thread.auth_success.connect(self.on_login_success)
        self.auth_thread.auth_failure.connect(self.on_login_failure)
        self.auth_thread.finished.connect(self.on_thread_finished)
        self.auth_thread.start()
        
    def on_login_success(self, username):
        """Callback para login bem-sucedido"""
        self.parent.set_status(f"Logado como {username} via LDAP")
        self.parent.after_login_success(username)
        
    def on_login_failure(self, message):
        """Callback para falha no login"""
        self.view.set_ldap_login_status("")
        QMessageBox.critical(
            self.view, 
            "Erro de Login LDAP", 
            f"Não foi possível autenticar via LDAP: {message}"
        )
        
    def on_thread_finished(self):
        """Callback quando a thread termina"""
        self.view.set_ldap_login_button_enabled(True)
        self.auth_thread = None 