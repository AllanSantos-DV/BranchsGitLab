"""
Controller para gerenciar as branches do GitLab e repositório local
"""
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal
from utils.constants import PROTECTED_BRANCHES

class LoadBranchesThread(QThread):
    """Thread para carregar branches sem bloquear a UI"""
    
    # Sinais para comunicar resultado
    branches_loaded = pyqtSignal(list)  # lista de branches
    branches_failed = pyqtSignal(str)   # mensagem de erro
    
    def __init__(self, gitlab_api, project_id):
        super().__init__()
        self.gitlab_api = gitlab_api
        self.project_id = project_id
        
    def run(self):
        """Executa o carregamento de branches em uma thread separada"""
        try:
            success, branches = self.gitlab_api.get_branches(self.project_id)
            
            if success:
                self.branches_loaded.emit(branches)
            else:
                self.branches_failed.emit(branches)  # branches contém a mensagem de erro
        except Exception as e:
            self.branches_failed.emit(f"Erro inesperado: {str(e)}")


class DeleteBranchesThread(QThread):
    """Thread para remover branches sem bloquear a UI"""
    
    # Sinais para comunicar resultados
    branch_deleted = pyqtSignal(str, bool)  # (branch_name, success)
    branch_error = pyqtSignal(str, str)     # (branch_name, error_message)
    local_branch_deleted = pyqtSignal(str, bool)  # (branch_name, success)
    local_branch_error = pyqtSignal(str, str)     # (branch_name, error_message)
    all_finished = pyqtSignal(int, int, int, int)  # (remote_success, remote_errors, local_success, local_errors)
    
    def __init__(self, gitlab_api, git_repo, project_id, branch_names, delete_local=False):
        super().__init__()
        self.gitlab_api = gitlab_api
        self.git_repo = git_repo
        self.project_id = project_id
        self.branch_names = branch_names
        self.delete_local = delete_local
        
    def run(self):
        """Executa a remoção de branches em uma thread separada"""
        remote_success = 0
        remote_errors = 0
        local_success = 0
        local_errors = 0
        
        # Remover branches remotas
        for branch_name in self.branch_names:
            try:
                success, message = self.gitlab_api.delete_branch(self.project_id, branch_name)
                
                if success:
                    remote_success += 1
                    self.branch_deleted.emit(branch_name, True)
                else:
                    remote_errors += 1
                    self.branch_error.emit(branch_name, message)
            except Exception as e:
                remote_errors += 1
                self.branch_error.emit(branch_name, str(e))
        
        # Remover branches locais, se solicitado
        if self.delete_local and self.git_repo.is_valid():
            for branch_name in self.branch_names:
                try:
                    success, message = self.git_repo.delete_branch(branch_name)
                    
                    if success:
                        local_success += 1
                        self.local_branch_deleted.emit(branch_name, True)
                    else:
                        local_errors += 1
                        self.local_branch_error.emit(branch_name, message)
                except Exception as e:
                    local_errors += 1
                    self.local_branch_error.emit(branch_name, str(e))
        
        # Emitir sinal de finalização com estatísticas
        self.all_finished.emit(remote_success, remote_errors, local_success, local_errors)


class BranchController:
    """
    Controller responsável pela lógica de gerenciamento de branches
    """
    
    def __init__(self, view, gitlab_model, git_model, parent_controller=None):
        """
        Inicializa o controller de branches
        
        Args:
            view: View de branches (BranchesView)
            gitlab_model: Modelo de API do GitLab (GitLabAPI)
            git_model: Modelo de repositório Git (GitRepo)
            parent_controller: Controller pai (AppController)
        """
        self.view = view
        self.gitlab_api = gitlab_model
        self.git_repo = git_model
        self.parent = parent_controller
        
        self.current_project_id = None
        self.current_project_name = None
        self.branches_thread = None
        self.delete_thread = None
        
        # Conectar sinais da view
        self.view.select_all_requested.connect(self.select_all_branches)
        self.view.deselect_all_requested.connect(self.deselect_all_branches)
        self.view.delete_branches_requested.connect(self.delete_branches)
        self.view.back_to_projects_requested.connect(self.back_to_projects)
        
    def load_branches(self, project_id, project_name):
        """
        Carrega as branches do projeto selecionado
        
        Args:
            project_id: ID do projeto no GitLab
            project_name: Nome do projeto
        """
        self.current_project_id = project_id
        self.current_project_name = project_name
        
        # Mostrar informações do projeto
        self.view.set_project_name(project_name)
        self.view.set_loading_state(True, "Carregando branches...")
        
        # Criar e iniciar thread de carregamento
        self.branches_thread = LoadBranchesThread(self.gitlab_api, project_id)
        self.branches_thread.branches_loaded.connect(self.on_branches_loaded)
        self.branches_thread.branches_failed.connect(self.on_branches_failed)
        self.branches_thread.finished.connect(self.on_load_thread_finished)
        self.branches_thread.start()
    
    def on_branches_loaded(self, branches):
        """Callback para quando as branches são carregadas com sucesso"""
        self.view.clear_branches()
        
        for branch in branches:
            is_protected = branch.name in PROTECTED_BRANCHES
            self.view.add_branch(branch.name, is_protected)
        
        self.parent.set_status(f"Carregadas {len(branches)} branches")
    
    def on_branches_failed(self, error_message):
        """Callback para quando ocorre falha no carregamento das branches"""
        QMessageBox.critical(
            self.view, 
            "Erro", 
            f"Não foi possível obter a lista de branches: {error_message}"
        )
    
    def on_load_thread_finished(self):
        """Callback quando a thread de carregamento termina"""
        self.view.set_loading_state(False)
        self.branches_thread = None
            
    def select_all_branches(self):
        """
        Seleciona todas as branches não protegidas
        """
        self.view.select_all_branches()
        
    def deselect_all_branches(self):
        """
        Desmarca todas as branches
        """
        self.view.deselect_all_branches()
        
    def delete_branches(self, branch_names, delete_local):
        """
        Remove as branches selecionadas
        
        Args:
            branch_names: Lista de nomes de branches para remover
            delete_local: Se deve remover também branches locais
        """
        if not branch_names:
            QMessageBox.warning(
                self.view, 
                "Aviso", 
                "Nenhuma branch selecionada para remoção"
            )
            return
            
        # Verificar se existe repositório local configurado
        if delete_local and not self.git_repo.is_valid():
            confirm_dialog = QMessageBox.question(
                self.view,
                "Repositório Local Não Configurado",
                "Você marcou para remover branches locais, mas não selecionou um repositório válido. "
                "Deseja continuar apenas com a remoção remota?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm_dialog != QMessageBox.StandardButton.Yes:
                return
                
            delete_local = False
            
        # Pedir confirmação
        confirm_msg = f"Tem certeza que deseja remover {len(branch_names)} branches?"
        if delete_local:
            confirm_msg += " As branches serão removidas tanto no GitLab quanto no repositório local."
        else:
            confirm_msg += " As branches serão removidas apenas no GitLab."
            
        confirm_msg += "\n\nBranches selecionadas:\n- " + "\n- ".join(branch_names[:10])
        
        if len(branch_names) > 10:
            confirm_msg += f"\n... e mais {len(branch_names) - 10} branches"
            
        confirm_dialog = QMessageBox.question(
            self.view, 
            "Confirmar Remoção", 
            confirm_msg, 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm_dialog != QMessageBox.StandardButton.Yes:
            return
        
        # Mostrar progresso de remoção
        self.view.set_loading_state(True, "Removendo branches...")
        self.view.prepare_progress(len(branch_names))
        
        # Armazenar erros para exibir depois
        self.remote_errors = []
        self.local_errors = []
            
        # Criar e iniciar thread de remoção
        self.delete_thread = DeleteBranchesThread(
            self.gitlab_api,
            self.git_repo,
            self.current_project_id,
            branch_names,
            delete_local
        )
        self.delete_thread.branch_deleted.connect(self.on_branch_deleted)
        self.delete_thread.branch_error.connect(self.on_branch_error)
        self.delete_thread.local_branch_deleted.connect(self.on_local_branch_deleted)
        self.delete_thread.local_branch_error.connect(self.on_local_branch_error)
        self.delete_thread.all_finished.connect(self.on_delete_finished)
        self.delete_thread.finished.connect(self.on_delete_thread_finished)
        self.delete_thread.start()
        
    def on_branch_deleted(self, branch_name, success):
        """Callback quando uma branch remota é removida com sucesso"""
        self.view.update_progress(f"Removida branch remota: {branch_name}")
        
    def on_branch_error(self, branch_name, error_message):
        """Callback quando ocorre erro ao remover uma branch remota"""
        self.remote_errors.append(f"{branch_name}: {error_message}")
        self.view.update_progress(f"Erro ao remover branch remota: {branch_name}")
        
    def on_local_branch_deleted(self, branch_name, success):
        """Callback quando uma branch local é removida com sucesso"""
        self.view.update_progress(f"Removida branch local: {branch_name}")
        
    def on_local_branch_error(self, branch_name, error_message):
        """Callback quando ocorre erro ao remover uma branch local"""
        self.local_errors.append(f"{branch_name}: {error_message}")
        self.view.update_progress(f"Erro ao remover branch local: {branch_name}")
        
    def on_delete_finished(self, remote_success, remote_errors, local_success, local_errors):
        """Callback quando termina a remoção de todas as branches"""
        # Atualizar a lista de branches
        self.load_branches(self.current_project_id, self.current_project_name)
        
        # Exibir resultado
        result_msg = f"Processo concluído:\n- {remote_success} branches removidas do GitLab"
        if local_success or local_errors:
            result_msg += f"\n- {local_success} branches removidas do repositório local"
            
        if remote_errors or local_errors:
            result_msg += "\n\nErros encontrados:"
            
            if remote_errors:
                result_msg += f"\n\nErros no GitLab ({remote_errors}):\n"
                result_msg += "\n".join(self.remote_errors[:5])
                if len(self.remote_errors) > 5:
                    result_msg += f"\n... e mais {len(self.remote_errors) - 5} erros"
                    
            if local_errors:
                result_msg += f"\n\nErros locais ({local_errors}):\n"
                result_msg += "\n".join(self.local_errors[:5])
                if len(self.local_errors) > 5:
                    result_msg += f"\n... e mais {len(self.local_errors) - 5} erros"
                    
            QMessageBox.warning(self.view, "Resultado da Remoção", result_msg)
        else:
            QMessageBox.information(self.view, "Resultado da Remoção", result_msg)
            
    def on_delete_thread_finished(self):
        """Callback quando a thread de remoção termina"""
        self.view.set_loading_state(False)
        self.delete_thread = None

    def back_to_projects(self):
        """Retorna para a lista de projetos"""
        if self.parent:
            self.parent.show_projects() 