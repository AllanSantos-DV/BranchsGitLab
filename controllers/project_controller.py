"""
Controller para gerenciar os projetos do GitLab
"""
from PyQt6.QtWidgets import QMessageBox, QFileDialog
from PyQt6.QtCore import QThread, pyqtSignal

class LoadProjectsThread(QThread):
    """Thread para carregar projetos sem bloquear a UI"""
    
    # Sinais para comunicar resultado
    projects_loaded = pyqtSignal(list)  # lista de projetos
    projects_failed = pyqtSignal(str)   # mensagem de erro
    
    def __init__(self, gitlab_api):
        super().__init__()
        self.gitlab_api = gitlab_api
        
    def run(self):
        """Executa o carregamento de projetos em uma thread separada"""
        try:
            success, projects = self.gitlab_api.get_projects()
            
            if success:
                self.projects_loaded.emit(projects)
            else:
                self.projects_failed.emit(projects)  # projects contém a mensagem de erro
        except Exception as e:
            self.projects_failed.emit(f"Erro inesperado: {str(e)}")


class ProjectController:
    """
    Controller responsável pela lógica de gerenciamento de projetos
    """
    
    def __init__(self, view, gitlab_model, git_model, parent_controller=None):
        """
        Inicializa o controller de projetos
        
        Args:
            view: View de projetos (ProjectsView)
            gitlab_model: Modelo de API do GitLab (GitLabAPI)
            git_model: Modelo de repositório Git (GitRepo)
            parent_controller: Controller pai (AppController)
        """
        self.view = view
        self.gitlab_api = gitlab_model
        self.git_repo = git_model
        self.parent = parent_controller
        self.projects_thread = None
        
        # Conectar sinais da view
        self.view.project_selected.connect(self.select_project)
        self.view.select_repo_requested.connect(self.select_repository)
        
    def load_projects(self):
        """
        Carrega a lista de projetos do GitLab
        """
        # Mostrar mensagem de carregamento
        self.view.set_loading_state(True, "Carregando projetos...")
        
        # Criar e iniciar thread de carregamento
        self.projects_thread = LoadProjectsThread(self.gitlab_api)
        self.projects_thread.projects_loaded.connect(self.on_projects_loaded)
        self.projects_thread.projects_failed.connect(self.on_projects_failed)
        self.projects_thread.finished.connect(self.on_thread_finished)
        self.projects_thread.start()
    
    def on_projects_loaded(self, projects):
        """Callback para quando os projetos são carregados com sucesso"""
        self.view.clear_projects()
        for project in projects:
            self.view.add_project(
                project.id, 
                project.name, 
                project.path_with_namespace
            )
        
        self.parent.set_status(f"Carregados {len(projects)} projetos")
    
    def on_projects_failed(self, error_message):
        """Callback para quando ocorre falha no carregamento dos projetos"""
        QMessageBox.critical(
            self.view, 
            "Erro", 
            f"Não foi possível obter a lista de projetos: {error_message}"
        )
    
    def on_thread_finished(self):
        """Callback quando a thread termina"""
        self.view.set_loading_state(False)
        self.projects_thread = None
            
    def select_project(self, project_id, project_name):
        """
        Seleciona um projeto para gerenciar branches
        
        Args:
            project_id: ID do projeto no GitLab
            project_name: Nome do projeto
        """
        self.parent.load_branches(project_id, project_name)
        
    def select_repository(self):
        """
        Seleciona um repositório Git local
        """
        repo_path = QFileDialog.getExistingDirectory(
            self.view, 
            "Selecionar Repositório Git", 
            "", 
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not repo_path:
            return
            
        # Verificar se o diretório é um repositório Git válido
        if not self.git_repo.open(repo_path):
            QMessageBox.warning(
                self.view, 
                "Repositório Inválido", 
                "O diretório selecionado não é um repositório Git válido."
            )
            return
            
        self.parent.set_repo_path(repo_path)
        self.parent.set_status(f"Repositório Git local configurado: {repo_path}") 