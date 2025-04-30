"""
Controller principal da aplicação
"""
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QStatusBar, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot

from models.gitlab_api import GitLabAPI
from models.git_repo import GitRepo
from models.ldap_auth import LDAPAuth
from views.login_tab_view import LoginTabView
from views.projects_view import ProjectsView
from views.branches_view import BranchesView
from views.protected_branches_view import ProtectedBranchesView
from controllers.login_controller import LoginController
from controllers.ldap_login_controller import LDAPLoginController
from controllers.project_controller import ProjectController
from controllers.branch_controller import BranchController

class AppController(QObject):
    """
    Controller principal responsável por coordenar a aplicação
    """
    # Sinais para comunicação entre threads
    protected_branches_loaded_signal = pyqtSignal(list)
    branches_loaded_signal = pyqtSignal(list)
    
    def __init__(self, main_window):
        """
        Inicializa o controller principal
        
        Args:
            main_window: Janela principal da aplicação (QMainWindow)
        """
        super().__init__()
        self.window = main_window
        self.setup_ui()
        self.setup_models()
        self.setup_controllers()
        
        # Conectar sinais internos
        self.protected_branches_loaded_signal.connect(self._on_gitlab_protected_branches_loaded)
        self.branches_loaded_signal.connect(self._on_project_branches_loaded)
        
        # Iniciar na tela de login
        self.show_login()
        
    def setup_ui(self):
        """
        Configura os elementos da interface principal
        """
        # Widget principal (abas)
        self.tab_widget = QTabWidget()
        self.window.setCentralWidget(self.tab_widget)
        
        # Barra de status
        self.status_bar = QStatusBar()
        self.window.setStatusBar(self.status_bar)
        
        # Criar as views
        self.login_tab_view = LoginTabView()
        self.projects_view = ProjectsView()
        self.branches_view = BranchesView()
        self.protected_branches_view = ProtectedBranchesView()
        
        # Conectar sinais
        self.branches_view.back_to_projects_requested.connect(self.show_projects)
        self.protected_branches_view.back_to_projects_requested.connect(self.show_projects)
        self.protected_branches_view.branches_selected.connect(self._on_protected_branches_selected)
        self.protected_branches_view.protected_branches_selected_signal.connect(self._on_protected_branches_selected_dict)
        
        # Conectar sinal para desabilitar botões da protected_branches_view quando voltar da branches_view
        self.branches_view.disable_protected_branches_buttons_requested.connect(
            self.protected_branches_view.disable_buttons_externally
        )
        
    def setup_models(self):
        """
        Configura os models da aplicação
        """
        self.gitlab_api = GitLabAPI()
        self.git_repo = GitRepo()
        self.ldap_auth = LDAPAuth()
        
    def setup_controllers(self):
        """
        Configura os controllers específicos
        """
        # Controller de login com token
        self.login_controller = LoginController(
            self.login_tab_view,
            self.gitlab_api,
            self
        )
        
        # Controller de login LDAP
        self.ldap_login_controller = LDAPLoginController(
            self.login_tab_view,
            self.ldap_auth,
            self.gitlab_api,
            self
        )
        
        self.project_controller = ProjectController(
            self.projects_view,
            self.gitlab_api,
            self.git_repo,
            self
        )
        
        self.branch_controller = BranchController(
            self.branches_view,
            self.gitlab_api,
            self.git_repo,
            self
        )
        
    def show_login(self):
        """
        Exibe a tela de login
        """
        self.tab_widget.clear()
        self.tab_widget.addTab(self.login_tab_view, "Login")
        
    def show_projects(self):
        """
        Exibe a tela de projetos
        """
        self.tab_widget.clear()
        self.tab_widget.addTab(self.projects_view, "Projetos")
        
    def show_protected_branches(self, project_id, project_name):
        """
        Exibe a tela de configuração de branches protegidas
        
        Args:
            project_id: ID do projeto no GitLab
            project_name: Nome do projeto
        """
        self.current_project_id = project_id
        self.current_project_name = project_name
        self.protected_branches_view.set_project_name(project_name)
        
        # Limpar branches anteriores e mostrar indicador de carregamento
        self.protected_branches_view.clear_branches()
        self.protected_branches_view.set_loading_state(True, "Carregando branches protegidas...")
        
        self.tab_widget.clear()
        self.tab_widget.addTab(self.protected_branches_view, "Configurar Branches Protegidas")
        
        # Carregar dados utilizando threads seguras
        self._load_protected_branches()
        
    def _load_protected_branches(self):
        """Inicia o carregamento das branches protegidas pelo GitLab de forma segura"""
        def on_protected_branches_loaded(success, result):
            if success:
                # Emitir sinal para processar na thread principal
                self.protected_branches_loaded_signal.emit(result)
            else:
                # Verificar se é um erro de permissão (403 Forbidden)
                if "403" in str(result) or "Forbidden" in str(result) or "acesso negado" in str(result).lower():
                    # Se for um erro de permissão, apenas definir uma lista vazia de branches protegidas
                    # e seguir para o carregamento das branches normais
                    self.window.statusBar().showMessage("Usuário sem permissão para acessar branches protegidas. Carregando apenas branches normais.")
                    self.gitlab_protected_branches = []
                    
                    # Atualizar mensagem de carregamento
                    self.protected_branches_view.set_loading_state(True, "Carregando branches do projeto...")
                    
                    # Agora carregar todas as branches do projeto
                    def on_branches_loaded(success, result):
                        if success:
                            # Emitir sinal para processar na thread principal
                            self.branches_loaded_signal.emit(result)
                        else:
                            # Exibir mensagem de erro na thread principal
                            self.window.statusBar().showMessage(f"Erro ao carregar branches: {result}")
                            QMessageBox.critical(self.window, "Erro", f"Falha ao carregar branches: {result}")
                            # Esconder indicador de carregamento em caso de erro
                            self.protected_branches_view.set_loading_state(False)
                    
                    # Chamar diretamente a API para obter as branches
                    success, result = self.gitlab_api.get_branches(self.current_project_id)
                    on_branches_loaded(success, result)
                else:
                    # Outros tipos de erro - mostrar mensagem
                    self.window.statusBar().showMessage(f"Erro ao carregar branches protegidas: {result}")
                    QMessageBox.critical(self.window, "Erro", f"Falha ao carregar branches protegidas: {result}")
        
        # Iniciar o carregamento das branches protegidas pelo GitLab
        self.branch_controller.get_protected_branches(self.current_project_id, on_protected_branches_loaded)
    
    @pyqtSlot(list)
    def _on_gitlab_protected_branches_loaded(self, gitlab_protected_branches):
        """Slot chamado na thread principal quando as branches protegidas são carregadas"""
        self.gitlab_protected_branches = gitlab_protected_branches
        
        # Atualizar mensagem de carregamento
        self.protected_branches_view.set_loading_state(True, "Carregando todas as branches do projeto...")
        
        # Agora carregar todas as branches do projeto
        def on_branches_loaded(success, result):
            if success:
                # Emitir sinal para processar na thread principal
                self.branches_loaded_signal.emit(result)
            else:
                # Exibir mensagem de erro na thread principal
                self.window.statusBar().showMessage(f"Erro ao carregar branches: {result}")
                QMessageBox.critical(self.window, "Erro", f"Falha ao carregar branches: {result}")
                # Esconder indicador de carregamento em caso de erro
                self.protected_branches_view.set_loading_state(False)
        
        # Chamar diretamente a API para obter as branches
        success, result = self.gitlab_api.get_branches(self.current_project_id)
        on_branches_loaded(success, result)
    
    @pyqtSlot(list)
    def _on_project_branches_loaded(self, branches):
        """Slot chamado na thread principal quando as branches do projeto são carregadas"""
        # Extrair apenas os nomes das branches
        project_branches = [branch.name for branch in branches]
        
        # Esconder indicador de carregamento
        self.protected_branches_view.set_loading_state(False)
        
        # Verificar se temos acesso às branches protegidas
        if not hasattr(self, 'gitlab_protected_branches') or self.gitlab_protected_branches is None:
            self.gitlab_protected_branches = []
            self.window.statusBar().showMessage("Aviso: Sem acesso às branches protegidas. Mostrando apenas branches normais.")
        
        # Configurar as branches na view - mesmo sem branches protegidas, a view pode funcionar
        self.protected_branches_view.set_branches(project_branches, self.gitlab_protected_branches)
        
    def _on_protected_branches_selected(self, protected_branches, hide_protected):
        """
        Callback para quando as branches protegidas são selecionadas
        
        Args:
            protected_branches: Lista de branches selecionadas como protegidas
            hide_protected: True para esconder branches protegidas da visualização
        """
        # Configurar as branches protegidas no controlador
        self.branch_controller.set_protected_branches(protected_branches)
        
        # Configurar se as branches protegidas devem ser ocultadas
        self.branch_controller.set_hide_protected_branches(hide_protected)
        
        # Agora carregar a tela de branches
        self.branch_controller.set_project(self.current_project_id, self.current_project_name)
        self.show_branches()
        
    def _on_protected_branches_selected_dict(self, protected_branches_dict):
        """
        Callback para quando as branches protegidas são selecionadas (formato dicionário)
        
        Args:
            protected_branches_dict (dict): Dicionário com as branches protegidas
                {
                    'protected_by_gitlab': [...],  # Branches já protegidas pelo GitLab
                    'protected_by_app': [...]      # Branches protegidas pelo aplicativo
                    'hide_protected': bool         # Se deve ocultar branches protegidas
                }
        """
        # Extrair as branches protegidas pelo aplicativo
        protected_branches = protected_branches_dict.get('protected_by_app', [])
        
        # Combinar com as branches protegidas pelo GitLab
        gitlab_protected = protected_branches_dict.get('protected_by_gitlab', [])
        all_protected = protected_branches + gitlab_protected
        
        # Configurar as branches protegidas no controlador
        self.branch_controller.set_protected_branches(all_protected)
        
        # Configurar se as branches protegidas devem ser ocultadas
        # Usar o valor do checkbox, ou True como padrão se não estiver presente
        hide_protected = protected_branches_dict.get('hide_protected', True)
        self.branch_controller.set_hide_protected_branches(hide_protected)
        
        # Agora carregar a tela de branches
        self.branch_controller.set_project(self.current_project_id, self.current_project_name)
        self.show_branches()
        
    def show_branches(self):
        """
        Exibe a tela de branches
        """
        self.tab_widget.clear()
        self.tab_widget.addTab(self.branches_view, "Branches")
        
    def set_status(self, message):
        """
        Define a mensagem da barra de status
        
        Args:
            message (str): Mensagem a ser exibida
        """
        self.status_bar.showMessage(message)
        
    def after_login_success(self, username):
        """
        Ações a realizar após login bem-sucedido
        
        Args:
            username (str): Nome do usuário logado
        """
        # Carregar lista de projetos e mostrar a tela
        self.project_controller.load_projects()
        self.show_projects()
        
    def load_branches(self, project_id, project_name):
        """
        Carrega a tela de configuração de branches protegidas antes de mostrar as branches
        
        Args:
            project_id: ID do projeto no GitLab
            project_name: Nome do projeto
        """
        # Mostrar a tela de configuração de branches protegidas
        self.show_protected_branches(project_id, project_name)
        
    def set_repo_path(self, repo_path):
        """
        Define o caminho do repositório local
        
        Args:
            repo_path (str): Caminho do repositório
        """
        self.branches_view.set_repo_path(repo_path) 