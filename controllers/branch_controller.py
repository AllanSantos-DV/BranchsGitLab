"""
Controller para gerenciar as branches do GitLab e repositório local
"""
from PyQt6.QtWidgets import QMessageBox, QTreeWidgetItem
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from utils.constants import PROTECTED_BRANCHES

class LoadBranchesThread(QThread):
    """
    Thread para carregar branches do GitLab sem bloquear a interface
    """
    branches_loaded = pyqtSignal(list)  # Sinal emitido quando as branches são carregadas
    branches_failed = pyqtSignal(str)   # Sinal emitido em caso de falha
    
    def __init__(self, gitlab_api, project_id, parent=None):
        """
        Inicializa a thread
        
        Args:
            gitlab_api: Instância do GitLabAPI
            project_id: ID do projeto a ser carregado
            parent: Objeto pai
        """
        super().__init__(parent)
        self.gitlab_api = gitlab_api
        self.project_id = project_id
        
    def run(self):
        """Executa a thread para carregar as branches"""
        try:
            success, result = self.gitlab_api.get_branches(self.project_id)
            if success:
                self.branches_loaded.emit(result)
            else:
                self.branches_failed.emit(f"Erro ao carregar branches: {result}")
        except Exception as e:
            self.branches_failed.emit(f"Erro ao carregar branches: {str(e)}")


class DeleteBranchesThread(QThread):
    """
    Thread para deletar branches no GitLab sem bloquear a interface
    """
    branch_deleted = pyqtSignal(str)      # Sinal emitido quando uma branch é deletada
    branch_failed = pyqtSignal(str, str)  # Sinal emitido quando uma deleção falha
    all_completed = pyqtSignal()          # Sinal emitido quando todas as operações são concluídas
    
    def __init__(self, gitlab_api, project_id, branch_names, delete_local=False, git_repo=None, parent=None):
        """
        Inicializa a thread
        
        Args:
            gitlab_api: Instância do GitLabAPI
            project_id: ID do projeto
            branch_names: Lista de nomes de branches para deletar
            delete_local: Se True, também deleta branches locais
            git_repo: Instância do repositório Git (se delete_local for True)
            parent: Objeto pai
        """
        super().__init__(parent)
        self.gitlab_api = gitlab_api
        self.project_id = project_id
        self.branch_names = branch_names
        self.delete_local = delete_local
        self.git_repo = git_repo
        
    def run(self):
        """Executa a thread para deletar as branches"""
        for branch_name in self.branch_names:
            try:
                # Deletar branch remota primeiro
                self.gitlab_api.delete_branch(self.project_id, branch_name)
                
                # Deletar branch local se solicitado
                if self.delete_local and self.git_repo:
                    try:
                        self.git_repo.delete_branch(branch_name)
                    except Exception as e:
                        self.branch_failed.emit(branch_name, f"Branch remota deletada, mas falha ao deletar localmente: {str(e)}")
                        continue
                
                self.branch_deleted.emit(branch_name)
            except Exception as e:
                self.branch_failed.emit(branch_name, str(e))
                
        self.all_completed.emit()


class BranchController(QObject):
    """
    Controller responsável pelo gerenciamento de branches
    """
    # Lista de branches protegidas está definida em utils/constants.py
    
    status_updated = pyqtSignal(str)
    
    def __init__(self, view, gitlab_api, git_repo_model, parent_controller=None):
        """
        Inicializa o controller
        
        Args:
            view: Instância da view de branches
            gitlab_api: Instância do GitLabAPI
            git_repo_model: Instância do GitRepositoryModel
            parent_controller: Controller pai (opcional)
        """
        super().__init__()
        self.view = view
        self.gitlab_api = gitlab_api
        self.git_repo_model = git_repo_model
        self.parent_controller = parent_controller
        
        self.current_project_id = None
        self.current_project_name = None
        self.branches = []
        
        # Conectar sinais
        self.view.delete_branches_requested.connect(self.delete_branches)
        self.view.select_all_requested.connect(self.view.select_all_branches)
        self.view.deselect_all_requested.connect(self.view.deselect_all_branches)
        
        if parent_controller:
            self.view.back_to_projects_requested.connect(parent_controller.show_projects)
    
    def is_branch_protected(self, branch_name):
        """
        Verifica se uma branch é protegida baseada em seu nome ou partes do caminho
        
        Args:
            branch_name: Nome da branch a ser verificada
            
        Returns:
            bool: True se a branch for protegida, False caso contrário
        """
        # Verificar se o nome exato da branch está na lista de protegidas
        if branch_name in PROTECTED_BRANCHES:
            return True
            
        # Dividir o nome da branch em partes pelo separador /
        path_parts = branch_name.split('/')
        
        # Verificar se qualquer parte do caminho está na lista de protegidas
        return any(part in PROTECTED_BRANCHES for part in path_parts)
    
    def organize_branches_in_tree(self, branches):
        """
        Organiza as branches em uma estrutura de árvore para melhor visualização
        
        Args:
            branches: Lista de objetos Branch
            
        Returns:
            dict: Estrutura de árvore onde as chaves são partes do caminho e os valores são
                 dicionários ou branches (quando é uma folha)
        """
        tree = {}
        
        for branch in branches:
            path_parts = branch.name.split('/')
            current_level = tree
            
            # Percorrer cada parte do caminho para criar a estrutura de árvore
            for i, part in enumerate(path_parts):
                # Se estamos na última parte do caminho, armazenar a branch
                if i == len(path_parts) - 1:
                    # Verificar se já existe um diretório com este nome
                    if part in current_level and "__branch" not in current_level[part]:
                        # Se existe mas não tem branch, adicionar a branch
                        current_level[part]["__branch"] = branch
                    else:
                        # Caso contrário, criar uma nova entrada
                        current_level[part] = {"__branch": branch}
                else:
                    # Se não estamos na última parte, criar um nível de diretório se não existir
                    if part not in current_level:
                        current_level[part] = {}
                    
                    # Mover para o próximo nível de diretório
                    current_level = current_level[part]
        
        return tree
    
    def set_project(self, project_id, project_name):
        """
        Define o projeto atual e carrega suas branches
        
        Args:
            project_id: ID do projeto no GitLab
            project_name: Nome do projeto
        """
        self.current_project_id = project_id
        self.current_project_name = project_name
        self.view.set_project_name(project_name)
        self.view.set_repo_path(self.git_repo_model.repo_path if self.git_repo_model.is_initialized() else None)
        
        self.load_branches()
    
    def load_branches(self):
        """Carrega as branches do projeto atual"""
        if not self.current_project_id:
            self.status_updated.emit("Nenhum projeto selecionado")
            return
            
        self.view.set_loading_state(True, "Carregando branches...")
        self.view.clear_branches()
        
        # Criar e iniciar thread
        self.load_thread = LoadBranchesThread(self.gitlab_api, self.current_project_id)
        self.load_thread.branches_loaded.connect(self.on_branches_loaded)
        self.load_thread.branches_failed.connect(self.on_branches_failed)
        self.load_thread.finished.connect(lambda: self.view.set_loading_state(False))
        
        self.load_thread.start()
    
    def on_branches_loaded(self, branches):
        """
        Callback para quando as branches são carregadas com sucesso
        
        Args:
            branches: Lista de objetos Branch
        """
        self.branches = branches
        
        # Organizar branches em uma estrutura de árvore para visualização
        branch_tree = self.organize_branches_in_tree(branches)
        
        # Configurar a visualização de árvore
        self.view.setup_tree_view(branch_tree, self.is_branch_protected)
        
        self.status_updated.emit(f"Carregadas {len(branches)} branches")
    
    def on_branches_failed(self, error_message):
        """
        Callback para quando ocorre uma falha ao carregar branches
        
        Args:
            error_message: Mensagem de erro
        """
        QMessageBox.critical(self.view, "Erro", error_message)
        self.status_updated.emit("Falha ao carregar branches")
    
    def delete_branches(self, branch_names, delete_local=False):
        """
        Deleta as branches selecionadas
        
        Args:
            branch_names: Lista de nomes de branches para deletar
            delete_local: Se True, também deleta branches locais
        """
        if not branch_names:
            QMessageBox.information(self.view, "Aviso", "Nenhuma branch selecionada para remoção.")
            return
        
        # Filtrar branches protegidas (verificação extra de segurança)
        protected_branches = [name for name in branch_names if self.is_branch_protected(name)]
        branch_names = [name for name in branch_names if not self.is_branch_protected(name)]
        
        if protected_branches:
            protected_names = "\n".join(protected_branches)
            QMessageBox.warning(
                self.view, 
                "Branches Protegidas", 
                f"As seguintes branches protegidas foram ignoradas:\n\n{protected_names}"
            )
            
        if not branch_names:
            return  # Todas as branches eram protegidas
        
        # Confirmar com o usuário
        branch_list = "\n".join(branch_names)
        local_message = " e localmente" if delete_local else ""
        response = QMessageBox.question(
            self.view,
            "Confirmar Exclusão",
            f"Tem certeza que deseja remover as seguintes branches do GitLab{local_message}?\n\n{branch_list}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if response != QMessageBox.StandardButton.Yes:
            return
            
        # Preparar barra de progresso
        total_branches = len(branch_names)
        self.view.prepare_progress(total_branches)
        self.view.set_loading_state(True, "Removendo branches...")
        
        # Criar e iniciar thread
        git_repo = self.git_repo_model if delete_local and self.git_repo_model.is_initialized() else None
        self.delete_thread = DeleteBranchesThread(
            self.gitlab_api, 
            self.current_project_id, 
            branch_names, 
            delete_local, 
            git_repo
        )
        
        self.delete_thread.branch_deleted.connect(self._on_branch_deleted)
        self.delete_thread.branch_failed.connect(self._on_branch_failed)
        self.delete_thread.all_completed.connect(self._on_delete_completed)
        
        self.delete_thread.start()
    
    def _on_branch_deleted(self, branch_name):
        """
        Callback para quando uma branch é deletada com sucesso
        
        Args:
            branch_name: Nome da branch deletada
        """
        self.view.update_progress(f"Removida: {branch_name}")
    
    def _on_branch_failed(self, branch_name, error):
        """
        Callback para quando ocorre um erro ao deletar uma branch
        
        Args:
            branch_name: Nome da branch
            error: Mensagem de erro
        """
        self.view.update_progress(f"Falha ao remover {branch_name}: {error}")
    
    def _on_delete_completed(self):
        """Callback para quando todas as operações de deleção são concluídas"""
        self.view.set_loading_state(False)
        QMessageBox.information(self.view, "Concluído", "Operação de remoção finalizada.")
        self.load_branches()  # Recarregar a lista de branches 