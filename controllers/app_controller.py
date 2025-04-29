"""
Controller principal da aplicação
"""
from PyQt6.QtWidgets import QMainWindow, QTabWidget, QStatusBar

from models.gitlab_api import GitLabAPI
from models.git_repo import GitRepo
from views.login_view import LoginView
from views.projects_view import ProjectsView
from views.branches_view import BranchesView
from controllers.login_controller import LoginController
from controllers.project_controller import ProjectController
from controllers.branch_controller import BranchController

class AppController:
    """
    Controller principal responsável por coordenar a aplicação
    """
    
    def __init__(self, main_window):
        """
        Inicializa o controller principal
        
        Args:
            main_window: Janela principal da aplicação (QMainWindow)
        """
        self.window = main_window
        self.setup_ui()
        self.setup_models()
        self.setup_controllers()
        
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
        self.login_view = LoginView()
        self.projects_view = ProjectsView()
        self.branches_view = BranchesView()
        
        # Conectar o sinal para voltar das branches para projetos
        self.branches_view.back_to_projects_requested.connect(self.show_projects)
        
    def setup_models(self):
        """
        Configura os models da aplicação
        """
        self.gitlab_api = GitLabAPI()
        self.git_repo = GitRepo()
        
    def setup_controllers(self):
        """
        Configura os controllers específicos
        """
        self.login_controller = LoginController(
            self.login_view,
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
        self.tab_widget.addTab(self.login_view, "Login")
        
    def show_projects(self):
        """
        Exibe a tela de projetos
        """
        self.tab_widget.clear()
        self.tab_widget.addTab(self.projects_view, "Projetos")
        
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
        Carrega as branches de um projeto e mostra a tela
        
        Args:
            project_id: ID do projeto no GitLab
            project_name: Nome do projeto
        """
        self.branch_controller.set_project(project_id, project_name)
        self.show_branches()
        
    def set_repo_path(self, repo_path):
        """
        Define o caminho do repositório local
        
        Args:
            repo_path (str): Caminho do repositório
        """
        self.branches_view.set_repo_path(repo_path) 