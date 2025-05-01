"""
View para a tela de merge de branches
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QCheckBox, QProgressBar, QComboBox,
                           QFrame, QListWidget, QListWidgetItem, QAbstractItemView,
                           QGroupBox, QMessageBox)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QIcon, QFont, QBrush
import sys
import os

class MergeBranchesView(QWidget):
    """
    View responsável pela interface de merge de branches
    """
    
    # Sinais
    merge_branches_requested = pyqtSignal(str, list, bool, bool)  # (source_branch, target_branches, delete_source, squash)
    back_to_projects_requested = pyqtSignal()  # Sinal para voltar
    
    def __init__(self, parent=None):
        """
        Inicializa a view de merge de branches
        
        Args:
            parent (QWidget): Widget pai
        """
        super().__init__(parent)
        self.init_ui()
        
    def get_resource_path(self, relative_path):
        """
        Obtém o caminho correto para um recurso, funciona tanto em desenvolvimento
        quanto após empacotado com PyInstaller
        """
        if getattr(sys, 'frozen', False):
            # Se estiver em um executável PyInstaller
            base_path = sys._MEIPASS
        else:
            # Se estiver em desenvolvimento
            base_path = os.path.abspath(".")
            
        return os.path.join(base_path, "resources", relative_path)
        
    def init_ui(self):
        """
        Inicializa a interface do usuário
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Título e informações do projeto
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #F0F5FF;
                border: 1px solid #D0E0FF;
                border-radius: 6px;
            }
        """)
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(15, 10, 15, 10)
        
        # Botão de voltar
        self.back_button = QPushButton("← Voltar")
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #4A7FC1;
                color: white;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2B5797;
            }
        """)
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(self._on_back_clicked)
        title_layout.addWidget(self.back_button)
        
        title_label = QLabel("Merge de Branches")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2B5797;")
        title_layout.addWidget(title_label)
        
        self.project_name_label = QLabel("")
        self.project_name_label.setStyleSheet("font-style: italic; color: #333333; font-weight: bold;")
        self.project_name_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(self.project_name_label, 1)
        
        layout.addWidget(title_frame)
        
        # Instruções
        instructions_label = QLabel("Selecione a branch de origem e as branches de destino para realizar o merge:")
        instructions_label.setStyleSheet("color: #555555; font-style: italic;")
        layout.addWidget(instructions_label)
        
        # Branch Source
        source_frame = QGroupBox("Branch de Origem (Source)")
        source_frame.setStyleSheet("""
            QGroupBox {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                margin-top: 10px;
            }
            QGroupBox::title {
                background-color: transparent;
                color: #2B5797;
                font-weight: bold;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px;
            }
        """)
        source_layout = QVBoxLayout(source_frame)
        
        source_description = QLabel("Selecione a branch que contém as alterações a serem mescladas:")
        source_description.setStyleSheet("color: #555555;")
        source_layout.addWidget(source_description)
        
        # Dropdown para source branch
        self.source_branch_combo = QComboBox()
        self.source_branch_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                padding: 3px 5px;
                min-height: 25px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid #CCCCCC;
            }
        """)
        source_layout.addWidget(self.source_branch_combo)
        
        layout.addWidget(source_frame)
        
        # Target Branches
        target_frame = QGroupBox("Branches de Destino (Target)")
        target_frame.setStyleSheet("""
            QGroupBox {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                margin-top: 10px;
            }
            QGroupBox::title {
                background-color: transparent;
                color: #2B5797;
                font-weight: bold;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px;
            }
        """)
        target_layout = QVBoxLayout(target_frame)
        
        target_description = QLabel("Selecione as branches que receberão as alterações (múltipla seleção):")
        target_description.setStyleSheet("color: #555555;")
        target_layout.addWidget(target_description)
        
        # Lista de target branches
        self.target_branches_list = QListWidget()
        self.target_branches_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.target_branches_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                background-color: #FFFFFF;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #F0F0F0;
            }
            QListWidget::item:selected {
                background-color: #E5F0FF;
                color: #000000;
            }
        """)
        target_layout.addWidget(self.target_branches_list)
        
        layout.addWidget(target_frame)
        
        # Opções adicionais
        options_frame = QGroupBox("Opções")
        options_frame.setStyleSheet("""
            QGroupBox {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                margin-top: 10px;
            }
            QGroupBox::title {
                background-color: transparent;
                color: #2B5797;
                font-weight: bold;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px;
            }
        """)
        options_layout = QVBoxLayout(options_frame)
        
        # Opção para squash commits
        self.squash_checkbox = QCheckBox("Combinar commits (squash)")
        self.squash_checkbox.setToolTip("Combina todos os commits em um único commit na branch de destino")
        self.squash_checkbox.setStyleSheet("color: #333333;")
        options_layout.addWidget(self.squash_checkbox)
        
        # Opção para deletar branch source após merge
        self.delete_source_checkbox = QCheckBox("Deletar branch de origem após merge bem-sucedido")
        self.delete_source_checkbox.setToolTip("Remove a branch de origem após o merge ser concluído com sucesso")
        self.delete_source_checkbox.setStyleSheet("color: #333333;")
        options_layout.addWidget(self.delete_source_checkbox)
        
        layout.addWidget(options_frame)
        
        # Status e progresso
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #FAFAFA;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)
        status_layout = QVBoxLayout(status_frame)
        status_layout.setContentsMargins(10, 8, 10, 8)
        status_layout.setSpacing(5)
        
        status_header = QHBoxLayout()
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #2B5797; font-weight: bold;")
        status_header.addWidget(self.status_label)
        
        status_layout.addLayout(status_header)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                background-color: #F5F5F5;
                color: #333333;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #2B5797;
            }
        """)
        status_layout.addWidget(self.progress_bar)
        
        self.progress_details = QLabel("")
        self.progress_details.setStyleSheet("color: #555555;")
        status_layout.addWidget(self.progress_details)
        
        layout.addWidget(status_frame)
        
        # Botões de ação
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Espaçador para alinhar os botões à direita
        button_layout.addStretch()
        
        # Botão para realizar merge
        self.merge_button = QPushButton("Realizar Merge")
        self.merge_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #666666;
            }
        """)
        self.merge_button.clicked.connect(self._on_merge_clicked)
        button_layout.addWidget(self.merge_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Inicialmente desabilitar o botão de merge
        self.merge_button.setEnabled(False)
        
    def _on_back_clicked(self):
        """
        Callback para quando o botão de voltar é clicado
        """
        self.back_to_projects_requested.emit()
    
    def _on_merge_clicked(self):
        """
        Callback para quando o botão de merge é clicado
        """
        source_branch = self.source_branch_combo.currentText()
        target_branches = self._get_selected_target_branches()
        delete_source = self.delete_source_checkbox.isChecked()
        squash = self.squash_checkbox.isChecked()
        
        if not source_branch:
            QMessageBox.warning(self, "Erro", "Selecione uma branch de origem.")
            return
            
        if not target_branches:
            QMessageBox.warning(self, "Erro", "Selecione pelo menos uma branch de destino.")
            return
            
        # Verificar se a source branch foi selecionada como target
        if source_branch in target_branches:
            QMessageBox.warning(
                self, 
                "Erro", 
                "A branch de origem não pode ser selecionada como destino."
            )
            return
            
        # Confirmar a operação
        message = f"Você está prestes a fazer merge de '{source_branch}' para {len(target_branches)} branch(es):\n\n"
        for i, branch in enumerate(target_branches, 1):
            message += f"{i}. {branch}\n"
            
        if delete_source:
            message += f"\nA branch de origem '{source_branch}' será excluída após os merges bem-sucedidos."
            
        if squash:
            message += "\n\nOs commits serão combinados (squash) durante o merge."
            
        message += "\n\nContinuar com a operação?"
        
        reply = QMessageBox.question(
            self, 
            "Confirmar Merge", 
            message, 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.merge_branches_requested.emit(source_branch, target_branches, delete_source, squash)
    
    def _get_selected_target_branches(self):
        """
        Retorna a lista de branches target selecionadas
        
        Returns:
            list: Lista de nomes de branches selecionadas
        """
        selected_items = self.target_branches_list.selectedItems()
        return [item.text() for item in selected_items]
    
    def set_project_name(self, project_name):
        """
        Define o nome do projeto na interface
        
        Args:
            project_name (str): Nome do projeto
        """
        self.project_name_label.setText(project_name)
    
    def set_branches(self, branches, protected_branches=None):
        """
        Configura as branches disponíveis na interface
        
        Args:
            branches (list): Lista de nomes de branches disponíveis
            protected_branches (list, optional): Lista de branches protegidas
        """
        if protected_branches is None:
            protected_branches = []
            
        # Filtrar branches protegidas para não aparecerem como source
        unprotected_branches = [b for b in branches if b not in protected_branches]
        
        # Configurar a combobox de source
        self.source_branch_combo.clear()
        for branch in sorted(unprotected_branches):
            self.source_branch_combo.addItem(branch)
            
        # Configurar a lista de target
        self.target_branches_list.clear()
        for branch in sorted(branches):
            # Adicionar todas as branches como possíveis targets
            item = QListWidgetItem(branch)
            
            # Se for protegida, destacar de alguma forma ou tornar não selecionável
            if branch in protected_branches:
                item.setForeground(QBrush(QColor("#999999")))
                item.setToolTip("Branch protegida")
            
            self.target_branches_list.addItem(item)
            
        # Conectar eventos para atualizar o estado do botão
        self.source_branch_combo.currentTextChanged.connect(self._update_button_state)
        self.target_branches_list.itemSelectionChanged.connect(self._update_button_state)
        
        # Atualizar o estado do botão
        self._update_button_state()
    
    def _update_button_state(self):
        """
        Atualiza o estado do botão de merge com base nas seleções
        """
        has_source = self.source_branch_combo.count() > 0
        selected_targets = len(self.target_branches_list.selectedItems()) > 0
        
        self.merge_button.setEnabled(has_source and selected_targets)
    
    def set_loading_state(self, is_loading, message=""):
        """
        Configura o estado de carregamento da tela
        
        Args:
            is_loading (bool): Se está em estado de carregamento
            message (str, optional): Mensagem a ser exibida
        """
        if is_loading:
            self.status_label.setText(message)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Modo indeterminado
            self.merge_button.setEnabled(False)
            self.back_button.setEnabled(False)
            self.source_branch_combo.setEnabled(False)
            self.target_branches_list.setEnabled(False)
            self.squash_checkbox.setEnabled(False)
            self.delete_source_checkbox.setEnabled(False)
        else:
            self.status_label.setText(message if message else "")
            self.progress_bar.setVisible(False)
            self.merge_button.setEnabled(True)
            self.back_button.setEnabled(True)
            self.source_branch_combo.setEnabled(True)
            self.target_branches_list.setEnabled(True)
            self.squash_checkbox.setEnabled(True)
            self.delete_source_checkbox.setEnabled(True)
            self._update_button_state()
    
    def prepare_progress(self, total_items):
        """
        Prepara a barra de progresso para o acompanhamento
        
        Args:
            total_items (int): Número total de itens a processar
        """
        self.progress_bar.setRange(0, total_items)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
    
    def update_progress(self, current_item, total_items, message=""):
        """
        Atualiza o progresso da operação
        
        Args:
            current_item (int): Número do item atual
            total_items (int): Número total de itens
            message (str, optional): Mensagem de progresso
        """
        self.progress_bar.setValue(current_item)
        if message:
            self.progress_details.setText(message) 