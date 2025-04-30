"""
View para o diálogo de confirmação de exclusão de branches
"""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QScrollArea, QWidget, QCheckBox, QFrame, QDialogButtonBox,
                           QSizePolicy, QMessageBox)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QPalette

class DeleteConfirmationDialog(QDialog):
    """
    Diálogo para confirmar a exclusão de branches com funcionalidades de:
    - Altura máxima com scroll
    - Linhas alternadas (transparente/azul claro)
    - Botão para remover branches da seleção
    - Confirmação após rolar até o fim
    - Confirmação final explícita sobre irreversibilidade
    """
    
    # Sinais
    branch_removed = pyqtSignal(str)  # Emitido quando uma branch é removida da seleção
    
    def __init__(self, parent, branch_names, delete_local=False, resource_path_provider=None):
        """
        Inicializa o diálogo de confirmação
        
        Args:
            parent: Widget pai
            branch_names: Lista de nomes de branches para deletar
            delete_local: Se True, também deleta branches locais
            resource_path_provider: Função para obter caminhos de recursos
        """
        super().__init__(parent)
        self.branch_names = branch_names.copy()  # Cria uma cópia para manipulação segura
        self.delete_local = delete_local
        self.resource_path_provider = resource_path_provider
        self.branch_widgets = {}  # Rastreia os widgets de branch para manipulação
        self.init_ui()
        
    def init_ui(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("Confirmar Exclusão de Branches")
        self.setMinimumWidth(600)
        self.setMaximumHeight(500)
        self.setModal(True)
        
        main_layout = QVBoxLayout(self)
        
        # Texto de aviso
        local_text = " e localmente" if self.delete_local else ""
        warning_label = QLabel(f"<b>As branches a seguir serão removidas do GitLab{local_text}:</b>")
        warning_label.setStyleSheet("color: #333333; font-size: 14px;")
        main_layout.addWidget(warning_label)
        
        # Criar área de rolagem para a lista de branches
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
            }
        """)
        
        # Container para a lista de branches
        branches_container = QWidget()
        self.branches_layout = QVBoxLayout(branches_container)
        self.branches_layout.setContentsMargins(10, 10, 10, 10)
        self.branches_layout.setSpacing(0)
        
        # Adicionar cada branch à lista com cores alternadas
        self._populate_branches_list()
        
        self.scroll_area.setWidget(branches_container)
        main_layout.addWidget(self.scroll_area, 1)  # 1 = stretch
        
        # Adicionar checkbox de confirmação (inicialmente desabilitado)
        confirm_frame = QFrame()
        confirm_frame.setStyleSheet("""
            QFrame {
                background-color: #FFEBEB;
                border: 1px solid #FFCCCC;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        confirm_layout = QVBoxLayout(confirm_frame)
        
        self.scroll_warning = QLabel("Role até o final da lista para habilitar a confirmação")
        self.scroll_warning.setStyleSheet("color: #CC0000; font-weight: bold;")
        self.scroll_warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        confirm_layout.addWidget(self.scroll_warning)
        
        # Checkbox de confirmação
        self.confirm_checkbox = QCheckBox("Estou ciente que esta ação é irreversível e todas as branches selecionadas serão permanentemente excluídas")
        self.confirm_checkbox.setEnabled(False)
        confirm_layout.addWidget(self.confirm_checkbox)
        
        main_layout.addWidget(confirm_frame)
        
        # Botões de OK e Cancelar
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.ok_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setText("Confirmar Exclusão")
        self.ok_button.setEnabled(False)  # Inicialmente desabilitado
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        main_layout.addWidget(self.button_box)
        
        # Conectar sinais
        self.button_box.accepted.connect(self.on_accepted)
        self.button_box.rejected.connect(self.reject)
        
        # Habilitar confirmação quando o checkbox for marcado
        self.confirm_checkbox.stateChanged.connect(self._on_checkbox_changed)
        
        # Conectar evento de rolagem para verificar se chegou ao final
        self.scroll_area.verticalScrollBar().valueChanged.connect(self._check_scroll_position)
        
        # Se tiver poucas branches e não precisar de rolagem, habilitar direto
        if len(self.branch_names) < 10:
            self._enable_confirmation()
    
    def _populate_branches_list(self):
        """Popula a lista de branches no diálogo"""
        # Limpar layout existente
        while self.branches_layout.count():
            item = self.branches_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Limpar mapeamento de widgets
        self.branch_widgets = {}
        
        # Adicionar cada branch à lista com cores alternadas
        for i, branch_name in enumerate(self.branch_names):
            branch_frame = QFrame()
            branch_frame.setFrameShape(QFrame.Shape.StyledPanel)
            branch_frame.setFrameShadow(QFrame.Shadow.Plain)
            
            # Definir cores alternadas
            if i % 2 == 0:
                # Fundo transparente
                branch_frame.setStyleSheet("""
                    QFrame {
                        background-color: transparent;
                        border: none;
                        padding: 8px;
                    }
                """)
            else:
                # Fundo azul claro
                branch_frame.setStyleSheet("""
                    QFrame {
                        background-color: #F0F5FF;
                        border: none;
                        padding: 8px;
                    }
                """)
                
            branch_layout = QHBoxLayout(branch_frame)
            branch_layout.setContentsMargins(5, 5, 5, 5)
            
            # Label com o nome da branch
            branch_label = QLabel(branch_name)
            branch_label.setWordWrap(True)
            branch_layout.addWidget(branch_label)
            
            # Botão para remover da lista
            remove_button = QPushButton()
            if self.resource_path_provider:
                close_icon_path = self.resource_path_provider("close.png")
                remove_button.setIcon(QIcon(close_icon_path))
            else:
                # Fallback se não tiver provider de recursos
                remove_button.setText("X")
                
            remove_button.setToolTip("Remover da seleção")
            remove_button.setFixedSize(24, 24)
            remove_button.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                }
                QPushButton:hover {
                    background-color: #FFE0E0;
                    border-radius: 12px;
                }
            """)
            # Usar uma closure para preservar a referência ao branch_name
            remove_button.clicked.connect(lambda checked, name=branch_name: self._remove_branch(name))
            branch_layout.addWidget(remove_button)
            
            self.branches_layout.addWidget(branch_frame)
            self.branch_widgets[branch_name] = branch_frame
    
    def _on_checkbox_changed(self, state):
        """Manipula a mudança de estado do checkbox de confirmação"""
        self.ok_button.setEnabled(state == Qt.CheckState.Checked.value)
    
    def _check_scroll_position(self):
        """Verifica se a barra de rolagem chegou ao final"""
        # Verificar se a barra de rolagem está próxima do final
        scrollbar = self.scroll_area.verticalScrollBar()
        at_bottom = scrollbar.value() >= scrollbar.maximum() - 10
        
        if at_bottom:
            self._enable_confirmation()
    
    def _enable_confirmation(self):
        """Habilita o checkbox de confirmação quando apropriado"""
        # Habilitar o checkbox quando chegar ao final
        self.confirm_checkbox.setEnabled(True)
        self.scroll_warning.setText("Marque a caixa de confirmação para prosseguir")
        self.scroll_warning.setStyleSheet("color: #006600; font-weight: bold;")
    
    def _remove_branch(self, branch_name):
        """
        Remove uma branch da seleção
        
        Args:
            branch_name: Nome da branch a remover
        """
        if branch_name in self.branch_widgets:
            # Ocultar o widget
            self.branch_widgets[branch_name].setVisible(False)
            
            # Remover da lista
            if branch_name in self.branch_names:
                self.branch_names.remove(branch_name)
                
            # Remover do dicionário
            self.branch_widgets.pop(branch_name, None)
            
            # Emitir sinal
            self.branch_removed.emit(branch_name)
            
            # Se todas as branches foram removidas, fechar o diálogo
            if not self.branch_names:
                self.reject()
    
    def on_accepted(self):
        """Manipula o evento quando o botão 'Confirmar Exclusão' é clicado"""
        # Mostrar uma confirmação final
        final_message = (
            "ATENÇÃO: Esta ação é IRREVERSÍVEL!\n\n"
            "As branches selecionadas serão PERMANENTEMENTE EXCLUÍDAS.\n"
            "Não será possível recuperá-las após a exclusão.\n\n"
            "Tem certeza que deseja prosseguir?"
        )
        
        final_confirm = QMessageBox.warning(
            self,
            "Confirmação Final",
            final_message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # Botão padrão é "Não" para evitar cliques acidentais
        )
        
        if final_confirm == QMessageBox.StandardButton.Yes:
            self.accept()
        # Se o usuário cancelar na confirmação final, apenas retornar (não fechar o diálogo)
    
    def get_selected_branches(self):
        """
        Retorna a lista atual de branches selecionadas para exclusão
        
        Returns:
            list: Lista de nomes de branches
        """
        return self.branch_names.copy()  # Retorna uma cópia para evitar modificações externas 