"""
View para a tela de gerenciamento de branches
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QListWidget, QListWidgetItem,
                           QCheckBox, QGroupBox, QProgressBar, QLineEdit,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QAbstractItemView)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QIcon, QFont

class BranchesView(QWidget):
    """
    View responsável pela interface de gerenciamento de branches
    """
    
    # Sinais
    delete_branches_requested = pyqtSignal(list, bool)  # (branches, delete_local)
    select_all_requested = pyqtSignal()
    deselect_all_requested = pyqtSignal()
    back_to_projects_requested = pyqtSignal()  # Novo sinal para voltar
    
    def __init__(self, parent=None):
        """
        Inicializa a view de branches
        
        Args:
            parent (QWidget): Widget pai
        """
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """
        Inicializa a interface do usuário
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)
        
        # Título e informações do projeto
        title_layout = QHBoxLayout()
        
        # Botão de voltar
        self.back_button = QPushButton("← Voltar")
        self.back_button.setFixedWidth(100)
        self.back_button.clicked.connect(self._on_back_clicked)
        title_layout.addWidget(self.back_button)
        
        title_label = QLabel("Gerenciar Branches")
        title_label.setProperty("title", "true")
        title_layout.addWidget(title_label)
        
        self.project_name_label = QLabel("")
        self.project_name_label.setStyleSheet("font-style: italic; color: #333333;")
        self.project_name_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        title_layout.addWidget(self.project_name_label, 1)
        
        title_widget = QWidget()
        title_widget.setLayout(title_layout)
        layout.addWidget(title_widget)
        
        # Repositório local
        repo_layout = QHBoxLayout()
        
        repo_label = QLabel("Repositório Local:")
        repo_label.setFixedWidth(120)
        self.repo_path_label = QLabel("Não selecionado")
        self.repo_path_label.setStyleSheet("font-style: italic; color: #333333;")
        
        repo_layout.addWidget(repo_label)
        repo_layout.addWidget(self.repo_path_label, 1)
        
        repo_widget = QWidget()
        repo_widget.setLayout(repo_layout)
        layout.addWidget(repo_widget)
        
        # Status e progresso
        status_layout = QVBoxLayout()
        status_layout.setSpacing(5)
        
        status_header = QHBoxLayout()
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #2B5797; font-weight: bold;")
        status_header.addWidget(self.status_label)
        
        status_header_widget = QWidget()
        status_header_widget.setLayout(status_header)
        status_layout.addWidget(status_header_widget)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        self.progress_details = QLabel("")
        self.progress_details.setStyleSheet("color: #555555;")
        status_layout.addWidget(self.progress_details)
        
        status_group = QWidget()
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Campo de filtro
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filtrar:")
        filter_label.setFixedWidth(60)
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filtrar branches por nome")
        self.filter_input.textChanged.connect(self._on_filter_changed)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input)
        
        filter_widget = QWidget()
        filter_widget.setLayout(filter_layout)
        layout.addWidget(filter_widget)
        
        # Tabela de branches
        self.branches_table = QTableWidget(0, 2)  # 0 linhas, 2 colunas (checkbox, nome)
        self.branches_table.setHorizontalHeaderLabels(["", "Nome da Branch"])
        self.branches_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.branches_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.branches_table.setColumnWidth(0, 30)  # Largura da coluna de checkbox
        self.branches_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.branches_table.setAlternatingRowColors(True)
        self.branches_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #CCCCCC;
                border-radius: 3px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
                color: #333333;
            }
            QHeaderView::section {
                background-color: #F0F0F0;
                padding: 5px;
                border: 1px solid #CCCCCC;
                color: #333333;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.branches_table)
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.select_all_button = QPushButton("Selecionar Todas")
        self.select_all_button.setFixedWidth(150)
        self.deselect_all_button = QPushButton("Desmarcar Todas")
        self.deselect_all_button.setFixedWidth(150)
        self.delete_button = QPushButton("Remover Selecionadas")
        self.delete_button.setProperty("destructive", "true")
        self.delete_button.setFixedWidth(180)
        
        buttons_layout.addWidget(self.select_all_button)
        buttons_layout.addWidget(self.deselect_all_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.delete_button)
        
        buttons_widget = QWidget()
        buttons_widget.setLayout(buttons_layout)
        layout.addWidget(buttons_widget)
        
        # Opções adicionais
        options_layout = QVBoxLayout()
        options_layout.setContentsMargins(10, 10, 10, 10)
        self.delete_local_checkbox = QCheckBox("Remover também branches locais (se disponíveis)")
        self.delete_local_checkbox.setStyleSheet("color: #333333;")
        options_layout.addWidget(self.delete_local_checkbox)
        
        options_group = QGroupBox("Opções")
        options_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
                color: #333333;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
        """)
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Conectar sinais
        self.select_all_button.clicked.connect(self._on_select_all_clicked)
        self.deselect_all_button.clicked.connect(self._on_deselect_all_clicked)
        self.delete_button.clicked.connect(self._on_delete_clicked)
        
        self.setLayout(layout)
        
    def _on_back_clicked(self):
        """Callback para quando o botão de voltar é clicado"""
        self.back_to_projects_requested.emit()
        
    def _on_filter_changed(self, text):
        """Callback para quando o texto do filtro muda"""
        # Filtrar branches com base no texto
        text = text.lower()
        for row in range(self.branches_table.rowCount()):
            item = self.branches_table.item(row, 1)  # Coluna do nome
            if not item:
                continue
                
            branch_name = item.text()
            matches = text == "" or text in branch_name.lower()
            self.branches_table.setRowHidden(row, not matches)
        
    def _on_select_all_clicked(self):
        """
        Callback para quando o botão de selecionar todas é clicado
        """
        self.select_all_requested.emit()
        
    def _on_deselect_all_clicked(self):
        """
        Callback para quando o botão de desmarcar todas é clicado
        """
        self.deselect_all_requested.emit()
        
    def _on_delete_clicked(self):
        """
        Callback para quando o botão de remover é clicado
        """
        selected_branches = self.get_selected_branches()
        delete_local = self.delete_local_checkbox.isChecked()
        
        if selected_branches:
            self.delete_branches_requested.emit(selected_branches, delete_local)
            
    def set_project_name(self, project_name):
        """
        Define o nome do projeto atual
        
        Args:
            project_name (str): Nome do projeto
        """
        self.project_name_label.setText(project_name)
        
    def set_repo_path(self, repo_path):
        """
        Define o caminho do repositório local
        
        Args:
            repo_path (str): Caminho do repositório
        """
        if repo_path:
            self.repo_path_label.setText(repo_path)
        else:
            self.repo_path_label.setText("Não selecionado")
            
    def set_loading_state(self, is_loading, message=""):
        """
        Define o estado de carregamento da view
        
        Args:
            is_loading (bool): Se True, mostra indicador de carregamento
            message (str): Mensagem de status (opcional)
        """
        self.progress_bar.setVisible(is_loading)
        self.status_label.setText(message if is_loading else "")
        self.progress_details.setText("")
        self.progress_details.setVisible(is_loading)
        
        # Habilitar/desabilitar controles
        self.select_all_button.setEnabled(not is_loading)
        self.deselect_all_button.setEnabled(not is_loading)
        self.delete_button.setEnabled(not is_loading)
        self.delete_local_checkbox.setEnabled(not is_loading)
        self.branches_table.setEnabled(not is_loading)
        self.filter_input.setEnabled(not is_loading)
        self.back_button.setEnabled(not is_loading)
        
    def prepare_progress(self, total_items):
        """
        Prepara a barra de progresso para exibir o progresso
        
        Args:
            total_items (int): Número total de itens
        """
        self.progress_bar.setRange(0, total_items)
        self.progress_bar.setValue(0)
        self.progress_count = 0
        
    def update_progress(self, message):
        """
        Atualiza o progresso e a mensagem
        
        Args:
            message (str): Mensagem de progresso
        """
        self.progress_count += 1
        self.progress_bar.setValue(self.progress_count)
        self.progress_details.setText(message)
            
    def clear_branches(self):
        """
        Limpa a lista de branches
        """
        self.branches_table.setRowCount(0)
        self.filter_input.clear()
        
    def add_branch(self, branch_name, is_protected=False):
        """
        Adiciona uma branch à lista
        
        Args:
            branch_name (str): Nome da branch
            is_protected (bool): Se a branch é protegida
        """
        row = self.branches_table.rowCount()
        self.branches_table.insertRow(row)
        
        # Checkbox
        checkbox_item = QTableWidgetItem()
        if is_protected:
            checkbox_item.setFlags(checkbox_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
        else:
            checkbox_item.setFlags(checkbox_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            checkbox_item.setCheckState(Qt.CheckState.Unchecked)
        self.branches_table.setItem(row, 0, checkbox_item)
        
        # Nome da branch
        name_item = QTableWidgetItem(branch_name)
        name_item.setData(Qt.ItemDataRole.UserRole, branch_name)
        
        if is_protected:
            name_item.setText(f"{branch_name} (protegida)")
            name_item.setForeground(QColor(128, 128, 128))  # Cinza
        else:
            name_item.setForeground(QColor(51, 51, 51))  # Cor escura para melhor legibilidade
            
        font = QFont()
        font.setPointSize(10)
        name_item.setFont(font)
        
        self.branches_table.setItem(row, 1, name_item)
        
    def get_selected_branches(self):
        """
        Retorna a lista de branches selecionadas
        
        Returns:
            list: Lista de nomes de branches selecionadas
        """
        selected_branches = []
        
        for row in range(self.branches_table.rowCount()):
            checkbox_item = self.branches_table.item(row, 0)
            name_item = self.branches_table.item(row, 1)
            
            if (checkbox_item and 
                checkbox_item.checkState() == Qt.CheckState.Checked and
                not self.branches_table.isRowHidden(row)):
                selected_branches.append(name_item.data(Qt.ItemDataRole.UserRole))
                
        return selected_branches
        
    def select_all_branches(self):
        """
        Seleciona todas as branches visíveis
        """
        for row in range(self.branches_table.rowCount()):
            if self.branches_table.isRowHidden(row):
                continue
                
            checkbox_item = self.branches_table.item(row, 0)
            if checkbox_item and checkbox_item.flags() & Qt.ItemFlag.ItemIsEnabled:
                checkbox_item.setCheckState(Qt.CheckState.Checked)
                
    def deselect_all_branches(self):
        """
        Desmarca todas as branches
        """
        for row in range(self.branches_table.rowCount()):
            checkbox_item = self.branches_table.item(row, 0)
            if checkbox_item:
                checkbox_item.setCheckState(Qt.CheckState.Unchecked) 