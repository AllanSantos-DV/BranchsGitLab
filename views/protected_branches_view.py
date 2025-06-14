"""
View para a tela de seleção de branches protegidas
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QCheckBox, QFrame, QScrollArea, QMessageBox, QSizePolicy, QLineEdit, QProgressBar)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

class ProtectedBranchesView(QWidget):
    """
    View responsável pela interface de seleção de branches protegidas
    """
    
    # Sinais
    branches_selected = pyqtSignal(list, bool)  # Lista de branches protegidas selecionadas, boolean para esconder protegidas
    back_to_projects_requested = pyqtSignal()
    protected_branches_selected_signal = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """
        Inicializa a view de branches protegidas
        
        Args:
            parent (QWidget): Widget pai
        """
        super().__init__(parent)
        self.selected_branches = []
        self.checkboxes = {}
        self.gitlab_protected_checkboxes = {}
        self.project_branches = []
        self.gitlab_protected_branches = []
        self.init_ui()

    def init_ui(self):
        """
        Inicializa a interface do usuário
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Título
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
        self.back_button = QPushButton("← Voltar para Projetos")
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
        self.back_button.setFixedWidth(180)
        self.back_button.clicked.connect(self._on_back_clicked)
        title_layout.addWidget(self.back_button)
        
        title_label = QLabel("Configurar Branches Protegidas")
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
        
        # Indicador de carregamento
        self.loading_frame = QFrame()
        self.loading_frame.setStyleSheet("""
            QFrame {
                background-color: #FFF8E1;
                border: 1px solid #FFE082;
                border-radius: 4px;
            }
        """)
        loading_layout = QVBoxLayout(self.loading_frame)
        loading_layout.setContentsMargins(15, 10, 15, 10)
        loading_layout.setSpacing(8)
        
        self.loading_label = QLabel("Carregando branches...")
        self.loading_label.setStyleSheet("color: #5D4037; font-weight: bold;")
        loading_layout.addWidget(self.loading_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #FFE082;
                border-radius: 4px;
                text-align: center;
                background-color: #FFFFFF;
            }
            QProgressBar::chunk {
                background-color: #FFA000;
                width: 20px;
            }
        """)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(0)  # Barra de progresso indeterminada
        loading_layout.addWidget(self.progress_bar)
        
        layout.addWidget(self.loading_frame)
        self.loading_frame.setVisible(False)  # Inicialmente oculto
        
        # Explicação
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFBEA;
                border: 1px solid #FFE082;
                border-radius: 4px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(15, 10, 15, 10)
        
        info_label = QLabel(
            "Selecione quais branches devem ser protegidas contra exclusão acidental. "
            "As branches já protegidas pelo GitLab não podem ser deselecionadas. "
            "Estas branches serão marcadas como protegidas e não poderão ser selecionadas para remoção."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #5D4037;")
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_frame)
        
        # Barra de busca
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #F7F7F7;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(10, 8, 10, 8)
        
        filter_label = QLabel("Filtrar:")
        filter_label.setStyleSheet("font-weight: bold;")
        filter_label.setFixedWidth(60)
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filtrar branches por nome")
        self.filter_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #CCCCCC;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #2B5797;
            }
        """)
        self.filter_input.textChanged.connect(self._on_filter_changed)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input)
        
        layout.addWidget(filter_frame)
        
        # Seção de Branches Protegidas pelo GitLab
        gitlab_protected_frame = QFrame()
        gitlab_protected_frame.setStyleSheet("""
            QFrame {
                background-color: #FFEBEE;
                border: 1px solid #FFCDD2;
                border-radius: 4px;
            }
        """)
        gitlab_protected_layout = QVBoxLayout(gitlab_protected_frame)
        gitlab_protected_layout.setContentsMargins(15, 10, 15, 10)
        gitlab_protected_layout.setSpacing(10)
        
        gitlab_protected_label = QLabel("Branches Protegidas pelo GitLab (não podem ser deselecionadas)")
        gitlab_protected_label.setStyleSheet("font-weight: bold; color: #B71C1C;")
        gitlab_protected_layout.addWidget(gitlab_protected_label)
        
        self.gitlab_protected_scroll = QScrollArea()
        self.gitlab_protected_scroll.setWidgetResizable(True)
        self.gitlab_protected_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.gitlab_protected_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.gitlab_protected_content = QWidget()
        self.gitlab_protected_layout = QVBoxLayout(self.gitlab_protected_content)
        self.gitlab_protected_layout.setContentsMargins(5, 5, 5, 5)
        self.gitlab_protected_layout.setSpacing(8)
        
        # Será preenchido dinamicamente
        self.gitlab_protected_layout.addStretch()
        self.gitlab_protected_scroll.setWidget(self.gitlab_protected_content)
        gitlab_protected_layout.addWidget(self.gitlab_protected_scroll)
        
        layout.addWidget(gitlab_protected_frame)
        
        # Seção de Branches do Repositório
        branches_frame = QFrame()
        branches_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
            }
        """)
        branches_layout = QVBoxLayout(branches_frame)
        branches_layout.setContentsMargins(15, 10, 15, 10)
        branches_layout.setSpacing(10)
        
        branches_label = QLabel("Branches do Repositório")
        branches_label.setStyleSheet("font-weight: bold; color: #2B5797;")
        branches_layout.addWidget(branches_label)
        
        self.branches_scroll = QScrollArea()
        self.branches_scroll.setWidgetResizable(True)
        self.branches_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.branches_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        self.branches_content = QWidget()
        self.branches_layout = QVBoxLayout(self.branches_content)
        self.branches_layout.setContentsMargins(5, 5, 5, 5)
        self.branches_layout.setSpacing(8)
        
        # Será preenchido dinamicamente
        self.branches_layout.addStretch()
        self.branches_scroll.setWidget(self.branches_content)
        branches_layout.addWidget(self.branches_scroll)
        
        layout.addWidget(branches_frame, 1)  # Dar mais espaço a esta seção
        
        # Opções adicionais
        options_frame = QFrame()
        options_frame.setStyleSheet("""
            QFrame {
                background-color: #F7F7F7;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)
        options_layout = QVBoxLayout(options_frame)
        options_layout.setContentsMargins(15, 10, 15, 10)
        options_layout.setSpacing(8)
        
        options_label = QLabel("Opções Adicionais")
        options_label.setStyleSheet("font-weight: bold; color: #2B5797;")
        options_layout.addWidget(options_label)
        
        self.hide_protected_checkbox = QCheckBox("Ocultar branches protegidas da visualização")
        self.hide_protected_checkbox.setChecked(True)  # Ativado por padrão
        self.hide_protected_checkbox.setStyleSheet("""
            QCheckBox {
                color: #333333;
                font-size: 12px;
                padding: 4px;
            }
            QCheckBox:hover {
                background-color: #F0F5FF;
                border-radius: 3px;
            }
        """)
        options_layout.addWidget(self.hide_protected_checkbox)
        
        layout.addWidget(options_frame)
        
        # Botões de ação
        buttons_frame = QFrame()
        buttons_frame.setStyleSheet("""
            QFrame {
                background-color: #F7F7F7;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(15, 10, 15, 10)
        
        self.select_all_button = QPushButton("Selecionar Todas")
        self.select_all_button.setStyleSheet("""
            QPushButton {
                background-color: #AAAAAA;
                color: #DDDDDD;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
        """)
        self.select_all_button.setEnabled(False)
        self.select_all_button.clicked.connect(self._select_all)
        
        self.deselect_all_button = QPushButton("Desmarcar Todas")
        self.deselect_all_button.setStyleSheet("""
            QPushButton {
                background-color: #AAAAAA;
                color: #DDDDDD;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
        """)
        self.deselect_all_button.setEnabled(False)
        self.deselect_all_button.clicked.connect(self._deselect_all)
        
        buttons_layout.addWidget(self.select_all_button)
        buttons_layout.addWidget(self.deselect_all_button)
        buttons_layout.addStretch()
        
        self.confirm_button = QPushButton("Confirmar e Continuar")
        self.confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #AAAAAA;
                color: #DDDDDD;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
        """)
        self.confirm_button.setEnabled(False)
        # Inicialmente desabilitado
        self.confirm_button.clicked.connect(self._on_confirm)
        buttons_layout.addWidget(self.confirm_button)
        
        layout.addWidget(buttons_frame)
        
        self.setLayout(layout)
        
    def set_project_name(self, project_name):
        """
        Define o nome do projeto atual
        
        Args:
            project_name (str): Nome do projeto
        """
        self.project_name_label.setText(project_name)
        
    def _on_filter_changed(self):
        """
        Filtra as branches exibidas com base no texto digitado
        """
        filter_text = self.filter_input.text().lower()
        
        # Filtrar branches protegidas pelo GitLab
        for branch_name, checkbox in self.gitlab_protected_checkboxes.items():
            checkbox.setVisible(filter_text in branch_name.lower())
        
        # Filtrar branches do repositório
        for branch_name, checkbox in self.checkboxes.items():
            checkbox.setVisible(filter_text in branch_name.lower())
    
    def _select_all(self):
        """
        Seleciona todas as branches visíveis que não são protegidas pelo GitLab
        """
        for checkbox in self.checkboxes.values():
            if checkbox.isVisible():
                checkbox.setChecked(True)
    
    def _deselect_all(self):
        """
        Desmarca todas as branches visíveis que não são protegidas pelo GitLab
        """
        for checkbox in self.checkboxes.values():
            if checkbox.isVisible():
                checkbox.setChecked(False)
            
    def _on_back_clicked(self):
        """Callback para quando o botão de voltar é clicado"""
        self._disable_all_buttons()
        self.back_to_projects_requested.emit()
        
    def _disable_all_buttons(self):
        """Desabilita todos os botões de ação"""
        self._disable_button_style(self.confirm_button)
        self._disable_button_style(self.select_all_button)
        self._disable_button_style(self.deselect_all_button)
        self.back_button.setEnabled(True)  # Manter o botão de voltar habilitado
        
    def _enable_action_buttons(self):
        """Habilita todos os botões de ação"""
        self._enable_confirm_button_style(self.confirm_button)
        self._enable_action_button_style(self.select_all_button)
        self._enable_action_button_style(self.deselect_all_button)
        
    def _disable_button_style(self, button):
        """Define o estilo de um botão desabilitado"""
        button.setEnabled(False)
        button.setStyleSheet("""
            QPushButton {
                background-color: #AAAAAA;
                color: #DDDDDD;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
        """)
        
    def _enable_action_button_style(self, button):
        """Define o estilo de um botão de ação habilitado"""
        button.setEnabled(True)
        button.setStyleSheet("""
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
        
    def _enable_confirm_button_style(self, button):
        """Define o estilo do botão de confirmação habilitado"""
        button.setEnabled(True)
        button.setStyleSheet("""
            QPushButton {
                background-color: #007E33;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #006129;
            }
        """)
        
    def _on_confirm(self):
        """
        Emite um sinal com as branches selecionadas
        """
        # Cria um dicionário seguro mesmo se não houver branches
        selected_branches = {
            'protected_by_gitlab': list(self.gitlab_protected_checkboxes.keys()),
            'protected_by_app': []
        }
        
        # Adiciona branches selecionadas apenas se existirem checkboxes
        if self.checkboxes:
            try:
                selected_branches['protected_by_app'] = [
                    branch_name for branch_name, checkbox in self.checkboxes.items()
                    if checkbox.isChecked()
                ]
            except RuntimeError:
                # Se ocorrer erro porque os checkboxes foram destruídos
                # (durante navegação rápida entre projetos)
                selected_branches['protected_by_app'] = []
        
        # Adicionar o estado do checkbox de ocultar branches protegidas
        selected_branches['hide_protected'] = self.hide_protected_checkbox.isChecked()
        
        self.protected_branches_selected_signal.emit(selected_branches)
    
    def set_branches(self, project_branches, gitlab_protected_branches):
        """
        Define as branches do projeto e as que são protegidas pelo GitLab
        
        Args:
            project_branches (list): Lista de todas as branches do projeto
            gitlab_protected_branches (list): Lista de branches protegidas pelo GitLab
        """
        self.project_branches = project_branches
        self.gitlab_protected_branches = gitlab_protected_branches
        
        # Limpar layouts existentes
        self._clear_layout(self.gitlab_protected_layout)
        self._clear_layout(self.branches_layout)
        
        # Adicionar branches protegidas pelo GitLab
        if gitlab_protected_branches:
            for branch_name in gitlab_protected_branches:
                checkbox = QCheckBox(branch_name)
                checkbox.setChecked(True)
                checkbox.setEnabled(False)  # Não pode ser deselecionada
                checkbox.setStyleSheet("""
                    QCheckBox {
                        color: #B71C1C;
                        font-size: 12px;
                        padding: 4px;
                        background-color: #FFEBEE;
                        border-radius: 3px;
                    }
                    QCheckBox:disabled {
                        color: #B71C1C;
                    }
                """)
                self.gitlab_protected_checkboxes[branch_name] = checkbox
                self.gitlab_protected_layout.addWidget(checkbox)
            self.gitlab_protected_layout.addStretch()
        else:
            # Caso não haja branches protegidas pelo GitLab
            no_branches_label = QLabel("Nenhuma branch protegida pelo GitLab encontrada")
            no_branches_label.setStyleSheet("color: #666666; font-style: italic;")
            self.gitlab_protected_layout.addWidget(no_branches_label)
            
            # Adicionar uma mensagem explicativa para usuários sem permissão
            if len(project_branches) > 0:
                info_label = QLabel(
                    "Nota: Isto pode ocorrer porque você não tem permissão para acessar as branches protegidas neste projeto. "
                    "Você ainda pode selecionar branches para proteção local no aplicativo."
                )
                info_label.setWordWrap(True)
                info_label.setStyleSheet("color: #FF9900; font-style: italic; margin-top: 5px;")
                self.gitlab_protected_layout.addWidget(info_label)
            
            self.gitlab_protected_layout.addStretch()
        
        # Adicionar branches do projeto (excluindo as já protegidas pelo GitLab)
        other_branches = [b for b in project_branches if b not in gitlab_protected_branches]
        
        if other_branches:
            for branch_name in other_branches:
                checkbox = QCheckBox(branch_name)
                # Não marcar nenhuma branch como selecionada por padrão
                checkbox.setChecked(False)
                checkbox.setStyleSheet("""
                    QCheckBox {
                        color: #333333;
                        font-size: 12px;
                        padding: 4px;
                    }
                    QCheckBox:hover {
                        background-color: #F0F5FF;
                        border-radius: 3px;
                    }
                """)
                self.checkboxes[branch_name] = checkbox
                self.branches_layout.addWidget(checkbox)
            self.branches_layout.addStretch()
            
            # Habilitar botões de ação já que há branches para selecionar
            self._enable_action_buttons()
        else:
            # Caso não haja outras branches além das protegidas pelo GitLab
            no_branches_label = QLabel("Nenhuma branch adicional encontrada")
            no_branches_label.setStyleSheet("color: #666666; font-style: italic;")
            self.branches_layout.addWidget(no_branches_label)
            self.branches_layout.addStretch()
            
            # Desabilitar botões de ação já que não há branches para selecionar
            self._disable_all_buttons()
            
            # Adiciona aviso sobre não haver branches para selecionar
            info_label = QLabel("Não há branches adicionais para proteger.")
            info_label.setStyleSheet("color: #B71C1C; font-weight: bold;")
            info_label.setWordWrap(True)
            self.branches_layout.addWidget(info_label)
    
    def _clear_layout(self, layout):
        """
        Remove todos os widgets de um layout
        
        Args:
            layout (QLayout): Layout a ser limpo
        """
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
    
    def get_selected_branches(self):
        """
        Retorna um dicionário com as branches selecionadas
        
        Returns:
            dict: Dicionário com as branches selecionadas
                {
                    'protected_by_gitlab': [...],  # Branches já protegidas pelo GitLab
                    'protected_by_app': [...]      # Branches protegidas pelo aplicativo
                }
        """
        protected_by_gitlab = list(self.gitlab_protected_checkboxes.keys())
        protected_by_app = []
        
        # Adiciona branches selecionadas apenas se existirem checkboxes
        if self.checkboxes:
            try:
                protected_by_app = [
                    branch_name for branch_name, checkbox in self.checkboxes.items()
                    if checkbox.isChecked()
                ]
            except RuntimeError:
                # Se ocorrer erro porque os checkboxes foram destruídos
                # (durante navegação rápida entre projetos)
                protected_by_app = []
        
        return {
            'protected_by_gitlab': protected_by_gitlab,
            'protected_by_app': protected_by_app
        }

    def disable_buttons_externally(self):
        """
        Método público para desabilitar os botões quando solicitado externamente
        por outras views
        """
        self._disable_all_buttons()
        
    def set_loading_state(self, is_loading, message="Carregando..."):
        """
        Exibe ou oculta o indicador de carregamento
        
        Args:
            is_loading (bool): True para mostrar o carregamento, False para ocultar
            message (str): Mensagem a ser exibida durante o carregamento
        """
        self.loading_frame.setVisible(is_loading)
        self.loading_label.setText(message)
        
        # Desabilitar os elementos interativos durante o carregamento
        if is_loading:
            self._disable_all_buttons()
            self.filter_input.setEnabled(False)
        else:
            self.filter_input.setEnabled(True)
            # Não reabilitamos os botões aqui - isso é feito no set_branches
        
    def clear_branches(self):
        """
        Limpa as branches das listas
        """
        # Limpar os dicionários de checkboxes
        self.checkboxes.clear()
        self.gitlab_protected_checkboxes.clear()
        
        # Limpar layouts
        self._clear_layout(self.gitlab_protected_layout)
        self._clear_layout(self.branches_layout)
        
        # Adicionar placeholders
        no_branches_label_gitlab = QLabel("Carregando branches protegidas...")
        no_branches_label_gitlab.setStyleSheet("color: #666666; font-style: italic;")
        self.gitlab_protected_layout.addWidget(no_branches_label_gitlab)
        self.gitlab_protected_layout.addStretch()
        
        no_branches_label = QLabel("Carregando branches do repositório...")
        no_branches_label.setStyleSheet("color: #666666; font-style: italic;")
        self.branches_layout.addWidget(no_branches_label)
        self.branches_layout.addStretch()
        
        # Desabilitar filtro e botões durante o carregamento
        self.filter_input.clear()
        self._disable_all_buttons() 