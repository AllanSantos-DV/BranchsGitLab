"""
View para a tela de listagem de projetos
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QListWidget, QListWidgetItem, QProgressBar,
                           QLineEdit, QScrollArea, QFrame, QGridLayout, QSizePolicy,
                           QToolButton, QSpacerItem)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon, QFont, QColor, QPalette, QLinearGradient, QBrush

class ProjectCard(QFrame):
    """Card para exibição de um projeto"""
    
    clicked = pyqtSignal(int, str)  # project_id, project_name
    
    def __init__(self, project_id, project_name, project_path, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.project_name = project_name
        self.project_path = project_path
        
        self.init_ui()
        
    def init_ui(self):
        """Inicializa a interface do card"""
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet("""
            ProjectCard {
                background-color: #F8F8F8;
                border: 1px solid #CCCCCC;
                border-radius: 10px;
                padding: 10px;
                margin: 8px;
            }
            ProjectCard:hover {
                background-color: #EFF5FB;
                border: 1px solid #A5C7FE;
            }
        """)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(150)
        self.setMaximumHeight(180)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Nome do projeto (estilizado)
        name_frame = QFrame()
        name_frame.setStyleSheet("""
            QFrame {
                background-color: #2B5797;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        name_layout = QVBoxLayout(name_frame)
        name_layout.setContentsMargins(10, 12, 10, 12)
        
        name_label = QLabel(self.project_name)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        name_label.setFont(font)
        name_label.setStyleSheet("color: white;")
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_layout.addWidget(name_label)
        
        layout.addWidget(name_frame)
        
        # Caminho do projeto
        path_frame = QFrame()
        path_frame.setStyleSheet("""
            QFrame {
                background-color: #F0F0F0;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        path_layout = QVBoxLayout(path_frame)
        path_layout.setContentsMargins(10, 5, 10, 5)
        
        path_label = QLabel(self.project_path)
        path_label.setStyleSheet("color: #555555;")
        path_label.setWordWrap(True)
        path_font = QFont()
        path_font.setPointSize(9)
        path_label.setFont(path_font)
        path_layout.addWidget(path_label)
        
        layout.addWidget(path_frame)
        
        # Botão de visualizar branches
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        view_button = QPushButton("Ver Branches")
        view_button.setStyleSheet("""
            QPushButton {
                background-color: #2B5797;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
                min-height: 25px;
            }
            QPushButton:hover {
                background-color: #1D3C6E;
            }
        """)
        view_button.setFixedWidth(120)
        view_button.clicked.connect(self.on_clicked)
        button_layout.addWidget(view_button)
        
        layout.addLayout(button_layout)
        
    def mousePressEvent(self, event):
        """Captura evento de clique no card"""
        super().mousePressEvent(event)
        self.on_clicked()
        
    def on_clicked(self):
        """Emite sinal de card clicado"""
        self.clicked.emit(self.project_id, self.project_name)

class ProjectsView(QWidget):
    """
    View responsável pela interface de listagem de projetos
    """
    
    # Sinais
    project_selected = pyqtSignal(int, str)  # (project_id, project_name)
    select_repo_requested = pyqtSignal()  # Solicita seleção de repositório local
    
    def __init__(self, parent=None):
        """
        Inicializa a view de projetos
        
        Args:
            parent (QWidget): Widget pai
        """
        super().__init__(parent)
        self.projects = []  # Armazena todos os projetos
        self.current_page = 0
        self.projects_per_page = 6  # Reduzido para mostrar cards maiores
        self.init_ui()
        
    def init_ui(self):
        """
        Inicializa a interface do usuário
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Título e botões
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #F0F5FF;
                border: 1px solid #D0E0FF;
                border-radius: 6px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        title_label = QLabel("Projetos Disponíveis")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2B5797;")
        header_layout.addWidget(title_label)
        
        spacer = QSpacerItem(20, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        header_layout.addItem(spacer)
        
        self.repo_button = QPushButton("Selecionar Repositório Local")
        self.repo_button.setStyleSheet("""
            QPushButton {
                background-color: #4A7FC1;
                color: white;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2B5797;
            }
        """)
        self.repo_button.setFixedWidth(200)
        header_layout.addWidget(self.repo_button)
        
        layout.addWidget(header_frame)
        
        # Status de carregamento
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                background-color: #FAFAFA;
            }
        """)
        self.status_layout = QHBoxLayout(status_frame)
        self.status_layout.setContentsMargins(10, 5, 10, 5)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #2B5797; font-weight: bold;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminado
        self.progress_bar.setVisible(False)
        
        self.status_layout.addWidget(self.status_label)
        self.status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(status_frame)
        
        # Campo de busca
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: #F7F7F7;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 5, 10, 5)
        
        search_label = QLabel("Buscar:")
        search_label.setStyleSheet("font-weight: bold;")
        search_label.setFixedWidth(60)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Filtrar por nome de projeto")
        self.search_input.setStyleSheet("""
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
        self.search_input.textChanged.connect(self.filter_projects)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        layout.addWidget(search_frame)
        
        # Grid de cards de projetos
        scroll_content = QWidget()
        self.projects_grid = QGridLayout(scroll_content)
        self.projects_grid.setSpacing(15)
        self.projects_grid.setContentsMargins(5, 5, 5, 5)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(scroll_content)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.scroll_area)
        
        # Paginação
        pagination_frame = QFrame()
        pagination_frame.setStyleSheet("""
            QFrame {
                background-color: #F0F5FF;
                border: 1px solid #D0E0FF;
                border-radius: 6px;
            }
        """)
        pagination_layout = QHBoxLayout(pagination_frame)
        pagination_layout.setContentsMargins(15, 10, 15, 10)
        
        self.prev_button = QPushButton("← Anterior")
        self.prev_button.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #888888;
            }
        """)
        self.prev_button.setFixedWidth(120)
        self.prev_button.clicked.connect(self.prev_page)
        
        self.page_label = QLabel("Página 1")
        self.page_label.setStyleSheet("font-weight: bold; color: #2B5797;")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.next_button = QPushButton("Próxima →")
        self.next_button.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #CCCCCC;
                color: #888888;
            }
        """)
        self.next_button.setFixedWidth(120)
        self.next_button.clicked.connect(self.next_page)
        
        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addStretch()
        pagination_layout.addWidget(self.next_button)
        
        layout.addWidget(pagination_frame)
        
        # Conectar sinais
        self.repo_button.clicked.connect(self._on_repo_clicked)
        
        self.setLayout(layout)
        
    def _on_repo_clicked(self):
        """
        Callback para quando o botão de selecionar repositório é clicado
        """
        self.select_repo_requested.emit()
    
    def _on_project_selected(self, project_id, project_name):
        """Callback para quando um projeto é selecionado"""
        self.project_selected.emit(project_id, project_name)
        
    def set_loading_state(self, is_loading, message=""):
        """
        Define o estado de carregamento da view
        
        Args:
            is_loading (bool): Se True, mostra indicador de carregamento
            message (str): Mensagem de status (opcional)
        """
        self.progress_bar.setVisible(is_loading)
        self.status_label.setText(message if is_loading else "")
        self.search_input.setEnabled(not is_loading)
        self.prev_button.setEnabled(not is_loading and self.current_page > 0)
        self.next_button.setEnabled(not is_loading and self.has_next_page())
        self.repo_button.setEnabled(not is_loading)
        
    def clear_projects(self):
        """
        Limpa a lista de projetos
        """
        # Limpar a grid de projetos
        for i in reversed(range(self.projects_grid.count())):
            widget = self.projects_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
                
        # Resetar a lista de projetos e paginação
        self.projects = []
        self.filtered_projects = []
        self.current_page = 0
        self.update_pagination()
        
    def add_project(self, project_id, project_name, project_path=None):
        """
        Adiciona um projeto à lista
        
        Args:
            project_id (int): ID do projeto no GitLab
            project_name (str): Nome do projeto
            project_path (str, optional): Caminho do projeto no GitLab
        """
        self.projects.append({
            'id': project_id,
            'name': project_name,
            'path': project_path or project_name
        })
        
        # Atualizar a visualização
        self.filter_projects(self.search_input.text())
        
    def filter_projects(self, search_text=""):
        """Filtra projetos com base no texto de busca"""
        search_text = search_text.lower()
        
        if search_text:
            self.filtered_projects = [
                p for p in self.projects 
                if search_text in p['name'].lower() or 
                   (p['path'] and search_text in p['path'].lower())
            ]
        else:
            self.filtered_projects = self.projects.copy()
            
        # Resetar para a primeira página
        self.current_page = 0
        self.update_pagination()
        self.display_current_page()
        
    def has_next_page(self):
        """Verifica se existe uma próxima página"""
        total_pages = (len(self.filtered_projects) + self.projects_per_page - 1) // self.projects_per_page
        return self.current_page < total_pages - 1
        
    def update_pagination(self):
        """Atualiza o estado dos controles de paginação"""
        total_projects = len(self.filtered_projects)
        total_pages = max(1, (total_projects + self.projects_per_page - 1) // self.projects_per_page)
        
        self.current_page = min(self.current_page, total_pages - 1)
        
        # Atualizar o texto da página atual
        page_text = f"Página {self.current_page + 1} de {total_pages}"
        if total_projects > 0:
            page_text += f" ({total_projects} projetos)"
        self.page_label.setText(page_text)
        
        # Habilitar/desabilitar botões de paginação
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.has_next_page())
        
    def display_current_page(self):
        """Exibe os projetos da página atual"""
        # Limpar a grid atual
        for i in reversed(range(self.projects_grid.count())):
            widget = self.projects_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
                
        # Calcular o intervalo de projetos a serem exibidos
        start_idx = self.current_page * self.projects_per_page
        end_idx = min(start_idx + self.projects_per_page, len(self.filtered_projects))
        
        # Se não houver projetos para exibir
        if start_idx >= len(self.filtered_projects):
            empty_frame = QFrame()
            empty_frame.setStyleSheet("""
                QFrame {
                    background-color: #F7F7F7;
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                }
            """)
            empty_layout = QVBoxLayout(empty_frame)
            
            empty_label = QLabel("Nenhum projeto encontrado.")
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #666666; font-size: 14px; font-weight: bold;")
            empty_layout.addWidget(empty_label)
            
            self.projects_grid.addWidget(empty_frame, 0, 0, 1, 2)
            return
            
        # Adicionar projetos à grid
        for i, idx in enumerate(range(start_idx, end_idx)):
            project = self.filtered_projects[idx]
            
            # Calcular posição na grid (2 colunas)
            row = i // 2
            col = i % 2
            
            # Criar e adicionar o card
            card = ProjectCard(
                project['id'], 
                project['name'], 
                project['path']
            )
            card.clicked.connect(self._on_project_selected)
            
            self.projects_grid.addWidget(card, row, col)
            
        # Adicionar espaço no final se necessário
        remaining_count = end_idx - start_idx
        if remaining_count % 2 != 0:
            spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.projects_grid.addItem(spacer, remaining_count // 2, 1)
        
    def next_page(self):
        """Avança para a próxima página"""
        if self.has_next_page():
            self.current_page += 1
            self.update_pagination()
            self.display_current_page()
        
    def prev_page(self):
        """Retorna para a página anterior"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_pagination()
            self.display_current_page()
        
    def get_selected_project(self):
        """
        Retorna o projeto selecionado
        
        Returns:
            tuple ou None: (project_id, project_name) se houver seleção, None caso contrário
        """
        # Não utilizado no novo layout de cards
        return None 