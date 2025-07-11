"""
Controller para gerenciar as branches do GitLab e repositório local
"""
from PyQt6.QtWidgets import QMessageBox, QTreeWidgetItem, QDialog, QVBoxLayout, QHBoxLayout, QLabel
from PyQt6.QtWidgets import QPushButton, QScrollArea, QWidget, QCheckBox, QFrame, QDialogButtonBox, QSizePolicy
from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt, QSize
from PyQt6.QtGui import QIcon, QColor, QPalette
from models.gitlab_api import GitLabAPI
import time

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


class LoadProtectedBranchesThread(QThread):
    """
    Thread para carregar branches protegidas do GitLab sem bloquear a interface
    """
    protected_branches_loaded = pyqtSignal(bool, object)  # Sinal emitido com (sucesso, resultado)
    
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
        """Executa a thread para carregar as branches protegidas"""
        try:
            success, result = self.gitlab_api.get_protected_branches(self.project_id)
            self.protected_branches_loaded.emit(success, result)
        except Exception as e:
            self.protected_branches_loaded.emit(False, str(e))


class BranchController(QObject):
    """
    Controller responsável pelo gerenciamento de branches
    """
    
    status_updated = pyqtSignal(str)
    protected_branches_updated = pyqtSignal(list)  # Sinal emitido quando a lista de branches protegidas é atualizada
    
    def __init__(self, view, gitlab_api: GitLabAPI, git_repo_model, parent_controller=None):
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
        self.protected_branches = []
        self.gitlab_protected_branches = []
        
        # Por padrão, esconde branches protegidas da listagem
        self.hide_protected_branches = True
        
        # Conectar sinais
        self.view.delete_branches_requested.connect(self.delete_branches)
        self.view.select_all_requested.connect(self.view.select_all_branches)
        self.view.deselect_all_requested.connect(self.view.deselect_all_branches)
        
        if parent_controller:
            self.view.back_to_projects_requested.connect(parent_controller.show_projects)
    
    def set_hide_protected_branches(self, hide_protected):
        """
        Define se branches protegidas devem ser ocultadas da visualização
        
        Args:
            hide_protected: True para ocultar, False para mostrar
        """
        self.hide_protected_branches = hide_protected
        
        # Se já tem branches carregadas, atualizar a visualização
        if self.branches:
            branch_tree = self.organize_branches_in_tree(self.branches)
            self.view.setup_tree_view(branch_tree, self.is_branch_protected)
    
    def set_protected_branches(self, protected_branches):
        """
        Define a lista de branches protegidas manualmente pelo usuário
        
        Args:
            protected_branches (list): Lista de branches protegidas
        """
        self.protected_branches = protected_branches
        self.protected_branches_updated.emit(protected_branches)
        
        # Se já tem branches carregadas, atualizar a visualização
        if self.branches:
            branch_tree = self.organize_branches_in_tree(self.branches)
            self.view.setup_tree_view(branch_tree, self.is_branch_protected)
    
    def is_branch_protected(self, branch_name, branch_obj=None):
        """
        Verifica se uma branch é protegida baseada em seu nome, partes do caminho,
        ou flags de proteção do GitLab
        
        Args:
            branch_name: Nome da branch a ser verificada
            branch_obj: Objeto Branch do GitLab (opcional)
            
        Returns:
            bool: True se a branch for protegida, False caso contrário
        """
        # Verificar se a branch está protegida pelo GitLab
        if branch_obj and hasattr(branch_obj, 'protected') and branch_obj.protected:
            return True
            
        # Verificar se o nome exato da branch está na lista de protegidas
        if branch_name in self.protected_branches:
            return True
            
        # Dividir o nome da branch em partes pelo separador /
        path_parts = branch_name.split('/')
        
        # Verificar se qualquer parte do caminho está na lista de protegidas
        return any(part in self.protected_branches for part in path_parts)
    
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
            # Verificar se a branch está protegida pelo GitLab
            is_protected_by_gitlab = hasattr(branch, 'protected') and branch.protected
            
            # Se a opção de esconder branches protegidas estiver ativada, 
            # não incluir branches protegidas na árvore
            if hasattr(self, 'hide_protected_branches') and self.hide_protected_branches:
                if is_protected_by_gitlab or self.is_branch_protected(branch.name):
                    continue
            
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
        
        # Usar a view de confirmação de exclusão em vez de criar o diálogo no controller
        from views.delete_confirmation_dialog import DeleteConfirmationDialog
        
        # Criar e exibir o diálogo de confirmação
        dialog = DeleteConfirmationDialog(
            self.view,
            branch_names,
            delete_local,
            resource_path_provider=self.view.get_resource_path
        )
        
        # Se o usuário confirmar, prosseguir com a exclusão
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Obter a lista final de branches (pode ter sido modificada no diálogo)
            final_branches = dialog.get_selected_branches()
            if final_branches:
                self._start_branch_deletion(final_branches, delete_local)
    
    def _start_branch_deletion(self, branch_names, delete_local):
        """
        Inicia o processo de remoção das branches após confirmação
        
        Args:
            branch_names: Lista de nomes de branches para deletar
            delete_local: Se True, também deleta branches locais
        """
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
        
        # Recarregar a lista de branches
        self.load_branches()
        
        # SOLUÇÃO AGRESSIVA: Forçar atualização completa de todas as visualizações de branches
        if self.parent_controller:
            # 1. Atualizar o modelo principal no AppController
            if hasattr(self.parent_controller, 'current_project_id'):
                # Forçar recarregamento direto da API
                success, result = self.gitlab_api.get_branches(self.parent_controller.current_project_id)
                if success:
                    # Atualizar o modelo no AppController
                    self.parent_controller.project_branches = result
                    
                    # 2. Atualizar a view de merge explicitamente
                    if hasattr(self.parent_controller, 'merge_controller'):
                        # Configurar o controller de merge com os dados atualizados
                        branch_names = [b.name for b in result]
                        
                        # Garantir que a tab de merge tenha as branches atualizadas
                        self.parent_controller.merge_controller.set_project(
                            self.parent_controller.current_project_id,
                            self.parent_controller.current_project_name,
                            branch_names,
                            self.parent_controller.selected_protected_branches
                        )
                        
                        # 3. Forçar refresh do display
                        if hasattr(self.parent_controller.merge_controller.view, 'refresh_branches_display'):
                            # Forçar atualização da view de merge
                            self.parent_controller.merge_controller.view.refresh_branches_display()
                            
            # 4. Notificar o AppController para garantir
            if hasattr(self.parent_controller, 'update_merge_tab_branches'):
                self.parent_controller.update_merge_tab_branches()

    def _populate_tree(self, parent_item, branch_dict, is_protected_func, path=""):
        """
        Popula a árvore recursivamente
        
        Args:
            parent_item: Item pai da árvore
            branch_dict: Dicionário contendo a estrutura de branches
            is_protected_func: Função para verificar se uma branch é protegida
            path: Caminho acumulado
        """
        # Ordenar as chaves para manter a ordem alfabética
        sorted_keys = sorted(branch_dict.keys())
        
        for key in sorted_keys:
            # Pular a chave especial __branch
            if key == "__branch":
                continue
                
            value = branch_dict[key]
            current_path = path + "/" + key if path else key
            
            # Verificar se é uma folha (branch) ou um diretório
            is_branch = "__branch" in value
            
            if is_branch:
                branch = value["__branch"]
                is_protected = is_protected_func(branch.name, branch)
                branch_item = self._create_branch_item(parent_item, key, branch, is_protected)
            else:
                # É um diretório, criar item do diretório
                dir_item = self._create_branch_item(parent_item, key)
                
                # Processar recursivamente os itens deste diretório
                self._populate_tree(dir_item, value, is_protected_func, current_path)

    def get_protected_branches(self, project_id, callback):
        """
        Obtém a lista de branches protegidas pelo GitLab
        
        Args:
            project_id (int): ID do projeto
            callback (function): Função de callback a ser chamada quando as branches protegidas forem carregadas
        """
        # Criar e iniciar thread para carregamento seguro
        self.protected_branches_thread = LoadProtectedBranchesThread(self.gitlab_api, project_id, self)
        self.protected_branches_thread.protected_branches_loaded.connect(callback)
        self.protected_branches_thread.start()

    def set_gitlab_protected_branches(self, gitlab_protected_branches):
        """
        Define a lista de branches protegidas pelo GitLab
        
        Args:
            gitlab_protected_branches (list): Lista de branches protegidas pelo GitLab
        """
        self.gitlab_protected_branches = gitlab_protected_branches

    def is_gitlab_protected(self, branch_name):
        """
        Verifica se uma branch está protegida pelo GitLab
        
        Args:
            branch_name (str): Nome da branch
            
        Returns:
            bool: True se a branch estiver protegida pelo GitLab, False caso contrário
        """
        return branch_name in self.gitlab_protected_branches

    def update_branches_after_deletion(self):
        """
        Atualiza a lista de branches após a exclusão de branches
        """
        # Recarregar a lista de branches
        self.load_branches()
        
        # Notificar o controller pai para atualizar a aba de merge, se existir
        if self.parent_controller and hasattr(self.parent_controller, 'update_merge_tab_branches'):
            self.parent_controller.update_merge_tab_branches() 