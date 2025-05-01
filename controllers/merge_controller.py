"""
Controller para gerenciar as operações de merge de branches
"""
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal, QObject
import time

class MergeBranchesThread(QThread):
    """
    Thread para realizar operações de merge sem bloquear a interface
    """
    merge_started = pyqtSignal(str, str)  # (source_branch, target_branch)
    merge_completed = pyqtSignal(str, str, bool)  # (source_branch, target_branch, success)
    merge_error = pyqtSignal(str, str, str)  # (source_branch, target_branch, error_message)
    merge_skipped = pyqtSignal(str, str, str)  # (source_branch, target_branch, reason)
    all_completed = pyqtSignal(bool, list)  # (success, failed_merges)
    
    def __init__(self, gitlab_api, project_id, source_branch, target_branches, squash=False, parent=None):
        """
        Inicializa a thread
        
        Args:
            gitlab_api: Instância do GitLabAPI
            project_id: ID do projeto no GitLab
            source_branch: Nome da branch de origem
            target_branches: Lista de nomes de branches de destino
            squash: Se deve combinar commits em um único
            parent: Objeto pai
        """
        super().__init__(parent)
        self.gitlab_api = gitlab_api
        self.project_id = project_id
        self.source_branch = source_branch
        self.target_branches = target_branches
        self.squash = squash
        self.failed_merges = []
        self.skipped_merges = []
        self.terminated = False
        
    def run(self):
        """Executa a thread para realizar os merges sequencialmente"""
        overall_success = True
        current_index = 0
        total_branches = len(self.target_branches)
        
        for target_branch in self.target_branches:
            if self.terminated:
                break
                
            # Emitir sinal de início do merge
            self.merge_started.emit(self.source_branch, target_branch)
            current_index += 1
            
            # Verificar diferenças entre as branches
            success, has_diff, message = self.gitlab_api.check_branch_differences(
                self.project_id, self.source_branch, target_branch
            )
            
            if not success:
                # Erro ao verificar diferenças
                # Se a mensagem contiver algo relacionado a MR, pode ser que o merge possa continuar
                # Se contém "404", provavelmente significa que não há diferenças
                if "há um mr aberto" in message.lower() or "404" in message:
                    # Continuar com o merge, pois já existe um MR ou não há diferenças
                    if "404" in message:
                        reason = f"Não há diferenças significativas entre {self.source_branch} e {target_branch} (indicado por 404)"
                        self.merge_skipped.emit(self.source_branch, target_branch, reason)
                        self.skipped_merges.append((target_branch, reason))
                        self.merge_completed.emit(self.source_branch, target_branch, True)
                        continue
                else:
                    self.merge_error.emit(self.source_branch, target_branch, f"Erro ao verificar diferenças: {message}")
                    self.failed_merges.append((target_branch, f"Erro ao verificar diferenças: {message}"))
                    overall_success = False
                    continue
                
            if not has_diff:
                # Sem diferenças, não precisa de merge
                reason = f"Não há diferenças entre {self.source_branch} e {target_branch} (merge não necessário)"
                self.merge_skipped.emit(self.source_branch, target_branch, reason)
                self.skipped_merges.append((target_branch, reason))
                self.merge_completed.emit(self.source_branch, target_branch, True)
                continue
                
            # Verificar conflitos antes de tentar merge
            success, has_conflicts, message = self.gitlab_api.check_merge_conflicts(
                self.project_id, self.source_branch, target_branch
            )
            
            if not success:
                # Erro ao verificar conflitos
                # Se a mensagem indicar que o MR já foi mesclado, podemos considerar como sucesso
                # Se contém "404", provavelmente significa que não há conflitos
                if "já realizado" in message.lower() or "404" in message:
                    if "já realizado" in message.lower():
                        reason = f"Merge de {self.source_branch} para {target_branch} já foi realizado anteriormente"
                    else:
                        reason = f"Não há conflitos entre {self.source_branch} e {target_branch} (indicado por 404)"
                    
                    self.merge_skipped.emit(self.source_branch, target_branch, reason)
                    self.skipped_merges.append((target_branch, reason))
                    self.merge_completed.emit(self.source_branch, target_branch, True)
                    continue
                else:
                    self.merge_error.emit(self.source_branch, target_branch, f"Erro ao verificar conflitos: {message}")
                    self.failed_merges.append((target_branch, f"Erro ao verificar conflitos: {message}"))
                    overall_success = False
                    continue
                
            if has_conflicts:
                # Há conflitos, não pode fazer merge automático
                self.merge_error.emit(self.source_branch, target_branch, "Existem conflitos de merge que precisam ser resolvidos manualmente")
                self.failed_merges.append((target_branch, "Conflitos de merge detectados"))
                overall_success = False
                # Como foi especificado cancelar todo o processo em caso de conflito
                break
                
            # Realizar o merge
            success, message = self.gitlab_api.merge_branches(
                self.project_id, self.source_branch, target_branch, self.squash
            )
            
            if success:
                # Se a mensagem contiver "já realizado", considerar como um skip
                if "já realizado" in message.lower():
                    self.merge_skipped.emit(self.source_branch, target_branch, message)
                    self.skipped_merges.append((target_branch, message))
                
                self.merge_completed.emit(self.source_branch, target_branch, True)
            else:
                # Se a mensagem de erro contiver "404", provavelmente significa que não há conflitos/diferenças
                if "404" in message:
                    reason = f"Não há diferenças significativas entre {self.source_branch} e {target_branch} (indicado por 404)"
                    self.merge_skipped.emit(self.source_branch, target_branch, reason)
                    self.skipped_merges.append((target_branch, reason))
                    self.merge_completed.emit(self.source_branch, target_branch, True)
                else:
                    self.merge_error.emit(self.source_branch, target_branch, message)
                    self.failed_merges.append((target_branch, message))
                    overall_success = False
                
            # Pequena pausa para não sobrecarregar o servidor
            time.sleep(0.5)
            
        # Emitir sinal de conclusão geral
        self.all_completed.emit(overall_success, self.failed_merges)
        
    def terminate(self):
        """Termina a thread de forma segura"""
        self.terminated = True
        super().terminate()


class MergeController(QObject):
    """
    Controller responsável pelo gerenciamento de operações de merge
    """
    
    status_updated = pyqtSignal(str)
    
    def __init__(self, view, gitlab_api, parent_controller=None):
        """
        Inicializa o controller
        
        Args:
            view: Instância da view de merge de branches
            gitlab_api: Instância do GitLabAPI
            parent_controller: Controller pai (opcional)
        """
        super().__init__()
        self.view = view
        self.gitlab_api = gitlab_api
        self.parent_controller = parent_controller
        
        self.current_project_id = None
        self.current_project_name = None
        self.merge_thread = None
        
        # Conectar sinais da view
        self.view.merge_branches_requested.connect(self._on_merge_requested)
        self.view.back_to_projects_requested.connect(self._on_back_requested)
        
    def set_project(self, project_id, project_name, branches, protected_branches):
        """
        Define o projeto atual e configura a view
        
        Args:
            project_id: ID do projeto no GitLab
            project_name: Nome do projeto
            branches: Lista de branches disponíveis
            protected_branches: Lista de branches protegidas
        """
        self.current_project_id = project_id
        self.current_project_name = project_name
        
        # Configurar a view com os dados do projeto
        self.view.set_project_name(project_name)
        self.view.set_branches(branches, protected_branches)
        
    def _on_merge_requested(self, source_branch, target_branches, delete_source, squash):
        """
        Callback para quando o usuário solicita o merge
        
        Args:
            source_branch: Nome da branch de origem
            target_branches: Lista de nomes de branches de destino
            delete_source: Se deve deletar a branch source após merge
            squash: Se deve combinar commits em um único
        """
        if not self.current_project_id:
            QMessageBox.warning(self.view, "Erro", "Nenhum projeto selecionado.")
            return
            
        # Iniciar o processo de merge
        self.view.set_loading_state(True, "Iniciando processo de merge...")
        self.view.prepare_progress(len(target_branches))
        
        # Salvar informações para uso após o merge (caso seja necessário deletar a branch source)
        self.source_branch = source_branch
        self.delete_source = delete_source
        
        # Criar e iniciar a thread de merge
        self.merge_thread = MergeBranchesThread(
            self.gitlab_api,
            self.current_project_id,
            source_branch,
            target_branches,
            squash
        )
        
        # Conectar sinais da thread
        self.merge_thread.merge_started.connect(self._on_merge_started)
        self.merge_thread.merge_completed.connect(self._on_merge_completed)
        self.merge_thread.merge_error.connect(self._on_merge_error)
        self.merge_thread.merge_skipped.connect(self._on_merge_skipped)
        self.merge_thread.all_completed.connect(self._on_all_merges_completed)
        
        # Iniciar a thread
        self.merge_thread.start()
        
    def _on_merge_started(self, source_branch, target_branch):
        """
        Callback para quando um merge específico é iniciado
        
        Args:
            source_branch: Nome da branch de origem
            target_branch: Nome da branch de destino
        """
        message = f"Realizando merge de '{source_branch}' para '{target_branch}'..."
        self.view.status_label.setText(message)
        if self.parent_controller:
            self.parent_controller.set_status(message)
        
    def _on_merge_completed(self, source_branch, target_branch, success):
        """
        Callback para quando um merge específico é concluído
        
        Args:
            source_branch: Nome da branch de origem
            target_branch: Nome da branch de destino
            success: Se o merge foi bem-sucedido
        """
        if success:
            message = f"Merge de '{source_branch}' para '{target_branch}' concluído com sucesso"
            self.view.progress_details.setText(message)
            if self.parent_controller:
                self.parent_controller.set_status(message)
        
    def _on_merge_error(self, source_branch, target_branch, error_message):
        """
        Callback para quando ocorre um erro em um merge específico
        
        Args:
            source_branch: Nome da branch de origem
            target_branch: Nome da branch de destino
            error_message: Mensagem de erro
        """
        message = f"Erro ao realizar merge de '{source_branch}' para '{target_branch}': {error_message}"
        self.view.progress_details.setText(message)
        if self.parent_controller:
            self.parent_controller.set_status(message)
        
    def _on_merge_skipped(self, source_branch, target_branch, reason):
        """
        Callback para quando um merge é pulado
        
        Args:
            source_branch: Nome da branch de origem
            target_branch: Nome da branch de destino
            reason: Razão pela qual o merge foi pulado
        """
        message = f"Merge de '{source_branch}' para '{target_branch}' pulado. Razão: {reason}"
        self.view.progress_details.setText(message)
        if self.parent_controller:
            self.parent_controller.set_status(message)
        
    def _on_all_merges_completed(self, overall_success, failed_merges):
        """
        Callback para quando todos os merges são concluídos
        
        Args:
            overall_success: Se todas as operações foram bem-sucedidas
            failed_merges: Lista de merges que falharam (target_branch, error_message)
        """
        self.view.set_loading_state(False)
        
        skipped_merges = getattr(self.merge_thread, 'skipped_merges', [])
        
        if overall_success:
            # Mensagem de sucesso, mencionando merges pulados se houver
            if skipped_merges:
                message = f"Todos os merges foram concluídos com sucesso! ({len(skipped_merges)} pulados)"
            else:
                message = "Todos os merges foram concluídos com sucesso!"
                
            self.view.status_label.setText(message)
            
            # Se solicitado, deletar a branch source
            if self.delete_source:
                if self.parent_controller:
                    # Usar a funcionalidade existente para deletar a branch
                    # Isso abrirá a tela de confirmação de deleção já existente
                    self.parent_controller.branch_controller.delete_branches(
                        [self.source_branch], False
                    )
                else:
                    QMessageBox.warning(
                        self.view, 
                        "Aviso", 
                        "Não foi possível iniciar o processo de deleção da branch de origem."
                    )
            else:
                # Mostrar mensagem de sucesso com detalhes sobre merges pulados
                if skipped_merges:
                    details = "Detalhes dos merges pulados:\n\n"
                    for target_branch, reason in skipped_merges:
                        details += f"• {target_branch}: {reason}\n"
                    
                    QMessageBox.information(
                        self.view, 
                        "Sucesso", 
                        f"{message}\n\n{details}"
                    )
                else:
                    QMessageBox.information(
                        self.view, 
                        "Sucesso", 
                        "Todos os merges foram concluídos com sucesso!"
                    )
                    
                self._on_back_requested()
        else:
            # Criar mensagem detalhada com os erros e merges pulados
            error_message = "Alguns merges não puderam ser concluídos:\n\n"
            for target_branch, error in failed_merges:
                error_message += f"• {target_branch}: {error}\n"
                
            if skipped_merges:
                error_message += "\nMerges pulados:\n"
                for target_branch, reason in skipped_merges:
                    error_message += f"• {target_branch}: {reason}\n"
                
            QMessageBox.warning(self.view, "Erro", error_message)
        
    def _on_back_requested(self):
        """
        Callback para quando o usuário solicita voltar à tela de seleção de projetos
        """
        if self.merge_thread and self.merge_thread.isRunning():
            reply = QMessageBox.question(
                self.view,
                "Operação em Andamento",
                "Há uma operação de merge em andamento. Deseja interrompê-la?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.merge_thread.terminate()
                self.merge_thread.wait()
            else:
                return
        
        if self.parent_controller:
            self.parent_controller.show_projects() 