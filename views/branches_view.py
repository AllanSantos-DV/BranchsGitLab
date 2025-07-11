"""
View para a tela de gerenciamento de branches
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QCheckBox, QProgressBar, QLineEdit,
                           QFrame, QTreeWidget, QTreeWidgetItem, QMenu,
                           QHeaderView, QAbstractItemView)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QColor, QIcon, QFont, QBrush, QAction
import sys
import os

class BranchesView(QWidget):
    """
    View responsável pela interface de gerenciamento de branches
    """
    
    # Sinais
    delete_branches_requested = pyqtSignal(list, bool)  # (branches, delete_local)
    select_all_requested = pyqtSignal()
    deselect_all_requested = pyqtSignal()
    back_to_projects_requested = pyqtSignal()  # Novo sinal para voltar
    disable_protected_branches_buttons_requested = pyqtSignal()  # Novo sinal para desabilitar botões em protected_branches_view
    
    def __init__(self, parent=None):
        """
        Inicializa a view de branches
        
        Args:
            parent (QWidget): Widget pai
        """
        super().__init__(parent)
        self.branch_icon = None
        self.branch_selected_icon = None
        self.lock_icon = None
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
        
        # Carregar ícones utilizados na interface
        self._load_icons()
        
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
        
        title_label = QLabel("Gerenciar Branches")
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
        
        # Repositório local
        repo_frame = QFrame()
        repo_frame.setStyleSheet("""
            QFrame {
                background-color: #F7F7F7;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)
        repo_layout = QHBoxLayout(repo_frame)
        repo_layout.setContentsMargins(10, 8, 10, 8)
        
        repo_label = QLabel("Repositório Local:")
        repo_label.setStyleSheet("font-weight: bold;")
        repo_label.setFixedWidth(120)
        self.repo_path_label = QLabel("Não selecionado")
        self.repo_path_label.setStyleSheet("font-style: italic; color: #333333;")
        
        repo_layout.addWidget(repo_label)
        repo_layout.addWidget(self.repo_path_label, 1)
        
        layout.addWidget(repo_frame)
        
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
        
        # Campo de filtro
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
        
        # Adicionar botões de ícone para expandir/recolher
        # Verificar se os ícones foram carregados no método _load_icons
        expand_icon_path = self.get_resource_path("expand.png")
        minimize_icon_path = self.get_resource_path("minimize.png")
        
        if os.path.exists(expand_icon_path):
            self.expand_icon = QIcon(expand_icon_path)
        else:
            self.expand_icon = QIcon()
            print(f"AVISO: Ícone de expandir não encontrado: {expand_icon_path}")
            
        if os.path.exists(minimize_icon_path):
            self.minimize_icon = QIcon(minimize_icon_path)
        else:
            self.minimize_icon = QIcon()
            print(f"AVISO: Ícone de minimizar não encontrado: {minimize_icon_path}")
            
        # Botão para expandir tudo
        self.expand_all_button = QPushButton()
        self.expand_all_button.setIcon(self.expand_icon)
        self.expand_all_button.setToolTip("Expandir Tudo")
        self.expand_all_button.setFixedSize(32, 32)
        self.expand_all_button.setStyleSheet("""
            QPushButton {
                background-color: #F0F5FF;
                border: 1px solid #D0E0FF;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #D0E0FF;
            }
            QPushButton:pressed {
                background-color: #B0D0FF;
            }
        """)
        self.expand_all_button.clicked.connect(self._expand_all)
        
        # Botão para recolher tudo
        self.collapse_all_button = QPushButton()
        self.collapse_all_button.setIcon(self.minimize_icon)
        self.collapse_all_button.setToolTip("Recolher Tudo")
        self.collapse_all_button.setFixedSize(32, 32)
        self.collapse_all_button.setStyleSheet("""
            QPushButton {
                background-color: #F0F5FF;
                border: 1px solid #D0E0FF;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #D0E0FF;
            }
            QPushButton:pressed {
                background-color: #B0D0FF;
            }
        """)
        self.collapse_all_button.clicked.connect(self._collapse_all)
        
        # Organizar o layout: primeiro os ícones, depois o filtro
        filter_layout.addWidget(self.expand_all_button)
        filter_layout.addWidget(self.collapse_all_button)
        
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
        
        # Árvore de branches (substitui a tabela)
        tree_frame = QFrame()
        tree_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #CCCCCC;
                border-radius: 4px;
            }
        """)
        tree_layout = QVBoxLayout(tree_frame)
        tree_layout.setContentsMargins(5, 5, 5, 5)
        
        self.branches_tree = QTreeWidget()
        self.branches_tree.setHeaderLabels(["Nome da Branch", "Status"])
        self.branches_tree.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.branches_tree.setAlternatingRowColors(True)
        self.branches_tree.setAnimated(True)
        self.branches_tree.setExpandsOnDoubleClick(True)
        self.branches_tree.setAllColumnsShowFocus(True)
        self.branches_tree.setUniformRowHeights(True)
        self.branches_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.branches_tree.customContextMenuRequested.connect(self._show_context_menu)
        self.branches_tree.setFrameShape(QFrame.Shape.NoFrame)
        self.branches_tree.setIndentation(20)
        
        # O estilo será aplicado no método _set_tree_icons
        
        # Ajustar tamanho das colunas
        self.branches_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.branches_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.branches_tree.header().setDefaultSectionSize(150)
        self.branches_tree.header().setStretchLastSection(False)
        
        tree_layout.addWidget(self.branches_tree)
        layout.addWidget(tree_frame, 1)  # Dar mais espaço à árvore
        
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
        buttons_layout.setContentsMargins(10, 8, 10, 8)
        
        self.select_all_button = QPushButton("Selecionar Todas")
        self.select_all_button.setStyleSheet("""
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
        self.select_all_button.setFixedWidth(150)
        
        self.deselect_all_button = QPushButton("Desmarcar Todas")
        self.deselect_all_button.setStyleSheet("""
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
        self.deselect_all_button.setFixedWidth(150)
        
        self.delete_button = QPushButton("Remover Selecionadas")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #C42B1C;
                color: white;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #951500;
            }
        """)
        self.delete_button.setFixedWidth(180)
        
        # Adicionar na ordem: selecionar, desmarcar, remover
        buttons_layout.addWidget(self.select_all_button)
        buttons_layout.addWidget(self.deselect_all_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.delete_button)
        
        layout.addWidget(buttons_frame)
        
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
        
        options_title = QLabel("Opções")
        options_title.setStyleSheet("color: #2B5797; font-weight: bold; font-size: 12px;")
        options_layout.addWidget(options_title)
        
        self.delete_local_checkbox = QCheckBox("Remover também branches locais (se disponíveis)")
        self.delete_local_checkbox.setStyleSheet("color: #333333;")
        options_layout.addWidget(self.delete_local_checkbox)
        
        layout.addWidget(options_frame)
        
        # Conectar sinais
        self.select_all_button.clicked.connect(self._on_select_all_clicked)
        self.deselect_all_button.clicked.connect(self._on_deselect_all_clicked)
        self.delete_button.clicked.connect(self._on_delete_clicked)
        
        # Conectar evento de seleção para atualizar ícones
        self.branches_tree.itemSelectionChanged.connect(self._update_selection_icons)
        
        self.setLayout(layout)
    
    def _load_icons(self):
        """Carrega todos os ícones utilizados na interface"""
        # Ícones para expansão da árvore
        closed_icon_path = self.get_resource_path("closed.png")
        open_icon_path = self.get_resource_path("open.png")
        
        if os.path.exists(closed_icon_path) and os.path.exists(open_icon_path):
            self.closed_icon = QIcon(closed_icon_path)
            self.open_icon = QIcon(open_icon_path)
        else:
            print(f"AVISO: Ícones de expansão não encontrados: {closed_icon_path}, {open_icon_path}")
            
        # Ícone para branches não selecionadas
        branch_icon_path = self.get_resource_path("branch.png")
        if os.path.exists(branch_icon_path):
            self.branch_icon = QIcon(branch_icon_path)
        else:
            # Criar um ícone padrão para branches
            print(f"AVISO: Ícone de branch não encontrado: {branch_icon_path}, criando um ícone padrão")
            self.branch_icon = self._create_default_branch_icon(False)
            
        # Ícone para branches selecionadas
        branch_selected_path = self.get_resource_path("branch_selected.png")
        if os.path.exists(branch_selected_path):
            self.branch_selected_icon = QIcon(branch_selected_path)
        else:
            # Criar um ícone padrão para branches selecionadas
            print(f"AVISO: Ícone de branch selecionada não encontrado: {branch_selected_path}, criando um ícone padrão")
            self.branch_selected_icon = self._create_default_branch_icon(True)
            
        # Ícone para branches protegidas
        lock_icon_path = self.get_resource_path("lock.png")
        if os.path.exists(lock_icon_path):
            self.lock_icon = QIcon(lock_icon_path)
        else:
            # Criar um ícone padrão para branches protegidas
            print(f"AVISO: Ícone de proteção não encontrado: {lock_icon_path}, criando um ícone padrão")
            self.lock_icon = self._create_default_lock_icon()
            
    def _create_default_branch_icon(self, selected):
        """Cria um ícone padrão para branches a partir de elementos básicos
        
        Args:
            selected (bool): Se True, cria um ícone para branch selecionada
            
        Returns:
            QIcon: Ícone criado
        """
        from PyQt6.QtGui import QPainter, QPixmap, QPen, QPolygon, QColor
        from PyQt6.QtCore import QPoint, Qt
        
        # Criar um pixmap vazio
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Criar um pintor
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Definir cor de acordo com o estado (selecionado ou não)
        if selected:
            branch_color = QColor("#2B5797")  # Azul mais escuro para selecionado
            painter.setBrush(QColor("#D0E8FF"))  # Fundo azul claro para selecionado
        else:
            branch_color = QColor("#333333")  # Cinza escuro para não selecionado
            painter.setBrush(Qt.GlobalColor.transparent)  # Sem fundo
        
        # Desenhar um símbolo de bifurcação simples
        pen = QPen(branch_color)
        pen.setWidth(1)
        painter.setPen(pen)
        
        # Desenhar um círculo de fundo se selecionado
        if selected:
            painter.drawEllipse(1, 1, 14, 14)
        
        # Desenhar uma linha vertical
        painter.setPen(QPen(branch_color, 2))
        painter.drawLine(8, 3, 8, 13)
        
        # Desenhar uma linha horizontal
        painter.drawLine(8, 8, 13, 8)
        
        # Desenhar uma marca de check se selecionado
        if selected:
            painter.setPen(QPen(branch_color, 2))
            points = [QPoint(4, 8), QPoint(6, 10), QPoint(11, 5)]
            painter.drawPolyline(QPolygon(points))
        
        painter.end()
        
        return QIcon(pixmap)
    
    def _create_default_lock_icon(self):
        """Cria um ícone padrão para branches protegidas
        
        Returns:
            QIcon: Ícone de cadeado criado
        """
        from PyQt6.QtGui import QPainter, QPixmap, QPen, QColor
        from PyQt6.QtCore import QRectF, Qt
        
        # Criar um pixmap vazio
        pixmap = QPixmap(16, 16)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        # Criar um pintor
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Definir cor
        lock_color = QColor("#B22222")  # Vermelho escuro
        
        # Desenhar um cadeado simples
        pen = QPen(lock_color)
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(QColor(255, 220, 220, 128))  # Vermelho claro com transparência
        
        # Corpo do cadeado
        painter.drawRoundedRect(QRectF(4, 7, 8, 7), 1, 1)
        
        # Arco do cadeado
        painter.drawArc(5, 3, 6, 8, 0, 180 * 16)
        
        painter.end()
        
        return QIcon(pixmap)
    
    def _show_context_menu(self, position):
        """Mostra o menu de contexto ao clicar com o botão direito em uma branch"""
        item = self.branches_tree.itemAt(position)
        if not item:
            return
            
        # Verificar se é uma branch e não um diretório
        branch_data = item.data(0, Qt.ItemDataRole.UserRole)
        if not branch_data or not branch_data.get('is_leaf', False):
            return
            
        # Criar menu
        menu = QMenu(self)
        
        # Ação para selecionar
        select_action = QAction("Selecionar", self)
        select_action.triggered.connect(lambda: self._select_item(item, True))
        menu.addAction(select_action)
        
        # Ação para desmarcar
        deselect_action = QAction("Desmarcar", self)
        deselect_action.triggered.connect(lambda: self._select_item(item, False))
        menu.addAction(deselect_action)
        
        # Separador
        menu.addSeparator()
        
        # Ação para deletar (se não for protegida)
        if not branch_data.get('is_protected', False):
            delete_action = QAction("Remover", self)
            delete_action.triggered.connect(lambda: self._delete_single_branch(branch_data.get('name', '')))
            menu.addAction(delete_action)
        
        # Expandir/Colapsar
        menu.addSeparator()
        if item.childCount() > 0:
            if item.isExpanded():
                collapse_action = QAction("Colapsar", self)
                collapse_action.triggered.connect(item.setExpanded)
                menu.addAction(collapse_action)
            else:
                expand_action = QAction("Expandir", self)
                expand_action.triggered.connect(lambda: item.setExpanded(True))
                menu.addAction(expand_action)
                
            expand_all_action = QAction("Expandir Tudo", self)
            expand_all_action.triggered.connect(lambda: self._expand_recursive(item, True))
            menu.addAction(expand_all_action)
            
            collapse_all_action = QAction("Colapsar Tudo", self)
            collapse_all_action.triggered.connect(lambda: self._expand_recursive(item, False))
            menu.addAction(collapse_all_action)
            
        # Mostrar menu
        menu.exec(self.branches_tree.viewport().mapToGlobal(position))
    
    def _select_item(self, item, selected):
        """Seleciona ou desmarca um item da árvore"""
        if item is None:
            return
            
        # Obter dados da branch
        branch_data = item.data(0, Qt.ItemDataRole.UserRole)
        if branch_data and branch_data.get('is_leaf', False):
            item.setSelected(selected)
        
        # Aplicar recursivamente a todos os filhos
        for i in range(item.childCount()):
            self._select_item(item.child(i), selected)
    
    def _expand_recursive(self, item, expand):
        """Expande ou colapsa um item e todos os seus filhos recursivamente"""
        if item is None:
            return
            
        item.setExpanded(expand)
        
        for i in range(item.childCount()):
            self._expand_recursive(item.child(i), expand)
    
    def _delete_single_branch(self, branch_name):
        """Remove uma única branch"""
        if branch_name:
            self.delete_branches_requested.emit([branch_name], self.delete_local_checkbox.isChecked())
        
    def _on_back_clicked(self):
        """Callback para quando o botão de voltar é clicado"""
        self._disable_all_buttons()
        self.disable_protected_branches_buttons_requested.emit()  # Emite sinal para desabilitar botões em protected_branches_view
        self.back_to_projects_requested.emit()
    
    def _disable_all_buttons(self):
        """Desabilita todos os botões de ação"""
        self._disable_button_style(self.select_all_button)
        self._disable_button_style(self.deselect_all_button)
        self._disable_delete_button_style(self.delete_button)
        
    def _disable_button_style(self, button):
        """Define o estilo de um botão desabilitado"""
        button.setEnabled(False)
        button.setStyleSheet("""
            QPushButton {
                background-color: #AAAAAA;
                color: #DDDDDD;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
            }
        """)
        
    def _disable_delete_button_style(self, button):
        """Define o estilo do botão de deletar desabilitado"""
        button.setEnabled(False)
        button.setStyleSheet("""
            QPushButton {
                background-color: #AAAAAA;
                color: #DDDDDD;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
            }
        """)
    
    def _on_filter_changed(self, text):
        """Callback para quando o texto do filtro muda"""
        self._filter_tree_items(self.branches_tree.invisibleRootItem(), text.lower())
    
    def _filter_tree_items(self, parent_item, filter_text):
        """Filtra os itens da árvore recursivamente"""
        any_visible = False
        
        for i in range(parent_item.childCount()):
            child = parent_item.child(i)
            item_text = child.text(0).lower()
            
            # Verificar filhos primeiro (para diretórios)
            child_visible = self._filter_tree_items(child, filter_text)
            
            # Verificar o item atual
            is_visible = filter_text == "" or filter_text in item_text
            
            # Um item é visível se ele próprio ou algum de seus filhos corresponder ao filtro
            child.setHidden(not (is_visible or child_visible))
            
            any_visible = any_visible or is_visible or child_visible
        
        return any_visible
            
    def _on_select_all_clicked(self):
        """Callback para quando o botão de selecionar todas é clicado"""
        if not self.select_all_button.isEnabled():
            return
            
        # Primeiro expandir todos os itens
        self.branches_tree.expandAll()
            
        # Depois selecionar todas as branches
        self.select_all_requested.emit()
        
    def _on_deselect_all_clicked(self):
        """Callback para quando o botão de desmarcar todas é clicado"""
        self.deselect_all_requested.emit()
        
    def _on_delete_clicked(self):
        """Callback para quando o botão de remover é clicado"""
        selected_branches = self.get_selected_branches()
        delete_local = self.delete_local_checkbox.isChecked()
        
        if selected_branches:
            self.delete_branches_requested.emit(selected_branches, delete_local)
            
    def set_project_name(self, project_name):
        """Define o nome do projeto atual"""
        self.project_name_label.setText(project_name)
        
    def set_repo_path(self, repo_path):
        """Define o caminho do repositório local"""
        if repo_path:
            self.repo_path_label.setText(repo_path)
        else:
            self.repo_path_label.setText("Não selecionado")
            
    def set_loading_state(self, is_loading, message=""):
        """Define o estado de carregamento da view"""
        self.progress_bar.setVisible(is_loading)
        self.status_label.setText(message if is_loading else "")
        self.progress_details.setText("")
        self.progress_details.setVisible(is_loading)
        
        # Habilitar/desabilitar controles
        self.select_all_button.setEnabled(not is_loading)
        self.deselect_all_button.setEnabled(not is_loading)
        self.delete_button.setEnabled(not is_loading)
        self.delete_local_checkbox.setEnabled(not is_loading)
        self.branches_tree.setEnabled(not is_loading)
        self.filter_input.setEnabled(not is_loading)
        self.back_button.setEnabled(not is_loading)
        
        # Atualizar estilos visuais dos botões de acordo com o estado
        if is_loading:
            self._disable_button_style(self.select_all_button)
            self._disable_button_style(self.deselect_all_button)
            self._disable_delete_button_style(self.delete_button)
        else:
            # Quando terminar o carregamento, atualizar o estado dos botões baseado nas branches disponíveis
            self._update_buttons_state()
            
            # Garantir que o botão de desmarcar esteja ativo se houver qualquer item na árvore
            if self.branches_tree.topLevelItemCount() > 0:
                self.deselect_all_button.setEnabled(True)
                self.deselect_all_button.setStyleSheet("""
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
    
    def prepare_progress(self, total_items):
        """Prepara a barra de progresso para exibir o progresso"""
        self.progress_bar.setRange(0, total_items)
        self.progress_bar.setValue(0)
        self.progress_count = 0
        
    def update_progress(self, message):
        """Atualiza o progresso e a mensagem"""
        self.progress_count += 1
        self.progress_bar.setValue(self.progress_count)
        self.progress_details.setText(message)
            
    def clear_branches(self):
        """Limpa a árvore de branches"""
        self.branches_tree.clear()
        self.filter_input.clear()
        
        # Desabilitar botões quando a lista é limpa
        self.select_all_button.setEnabled(False)
        self.deselect_all_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        
        # Aplicar estilo visual de desabilitado
        self._disable_button_style(self.select_all_button)
        self._disable_button_style(self.deselect_all_button)
        self._disable_delete_button_style(self.delete_button)
    
    def _create_branch_item(self, parent, name, branch=None, is_protected=False):
        """
        Cria um item de branch ou diretório na árvore
        
        Args:
            parent: Item pai
            name: Nome do item
            branch: Objeto de branch (se for uma branch)
            is_protected: Se a branch é protegida
        
        Returns:
            QTreeWidgetItem: Novo item criado
        """
        item = QTreeWidgetItem(parent)
        item.setText(0, name)
        
        # Se for uma branch (folha), adicionar dados e estilo
        if branch:
            # Armazenar informações úteis no item
            item.setData(0, Qt.ItemDataRole.UserRole, {
                'name': branch.name,
                'is_leaf': True,
                'is_protected': is_protected
            })
            
            # Definir texto e estilo da segunda coluna
            if is_protected:
                item.setText(1, "Protegida")
                item.setForeground(1, QBrush(QColor("#B22222")))  # Vermelho escuro
                item.setForeground(0, QBrush(QColor("#666666")))  # Cinza para o nome
                
                # Ícone de cadeado para branches protegidas
                if self.lock_icon:
                    item.setIcon(0, self.lock_icon)
                
                # Desabilitar seleção para branches protegidas
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                
                # Adicionar estilo para mostrar que não é selecionável
                item.setBackground(0, QBrush(QColor("#F8F8F8")))
                item.setBackground(1, QBrush(QColor("#F8F8F8")))
            else:
                item.setText(1, "Normal")
                item.setForeground(1, QBrush(QColor("#006400")))  # Verde escuro
                item.setForeground(0, QBrush(QColor("#333333")))  # Cor normal para o nome
                
                # Ícone folha para branches normais
                if self.branch_icon:
                    item.setIcon(0, self.branch_icon)
                
                # Tornar visualmente mais claro que é selecionável
                item.setToolTip(0, "Clique para selecionar esta branch")
                item.setToolTip(1, "Branch disponível para remoção")
        else:
            # É um diretório
            item.setData(0, Qt.ItemDataRole.UserRole, {
                'is_leaf': False,
                'name': name
            })
            # Estilizar nomes de diretórios
            font = item.font(0)
            font.setBold(True)
            item.setFont(0, font)
            item.setForeground(0, QBrush(QColor("#2B5797")))  # Azul para diretórios
        
        return item
            
    def setup_tree_view(self, branch_tree, is_protected_func):
        """
        Configura a visualização em árvore com a estrutura de branches
        
        Args:
            branch_tree: Estrutura de árvore das branches
            is_protected_func: Função para verificar se uma branch é protegida
        """
        self.clear_branches()
        
        # Use o método do controller para popular a árvore, se existir
        if hasattr(is_protected_func, '_populate_tree'):
            is_protected_func._populate_tree(self.branches_tree.invisibleRootItem(), branch_tree, is_protected_func)
        else:
            # Caso contrário, use o método interno
            self._populate_tree(self.branches_tree.invisibleRootItem(), branch_tree, is_protected_func)
        
        # Aplicar ícones de expandir/recolher via CSS
        self._set_tree_icons()
        
        # Aplicar ícones de seleção iniciais
        self._update_selection_icons()
        
        # Verificar se existem branches não protegidas e atualizar estado dos botões
        self._update_buttons_state()
        
        # Garantir que o botão de desmarcar todas esteja sempre ativado quando há items
        if self.branches_tree.topLevelItemCount() > 0:
            self.deselect_all_button.setEnabled(True)
            self.deselect_all_button.setStyleSheet("""
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
    
    def _populate_tree(self, parent_item, branch_dict, is_protected_func, path=""):
        """
        Popula a árvore recursivamente
        
        Args:
            parent_item: Item pai da árvore
            branch_dict: Dicionário contendo a estrutura de branches
            is_protected_func: Função para verificar se uma branch é protegida
            path: Caminho acumulado
        """
        # Separar chaves em 2 grupos: diretórios/branches dentro de pastas e branches na raiz
        folder_keys = []
        root_branch_keys = []
        
        for key in branch_dict.keys():
            # Pular a chave especial __branch
            if key == "__branch":
                continue
                
            value = branch_dict[key]
            # Verificar se é uma folha (branch) ou um diretório
            is_branch = "__branch" in value
            
            if is_branch and not path:  # Branch na raiz
                root_branch_keys.append(key)
            else:  # Diretório ou branch dentro de pasta
                folder_keys.append(key)
        
        # Ordenar as chaves em cada grupo para manter a ordem alfabética
        folder_keys.sort()
        root_branch_keys.sort()
        
        # Primeiro processar pastas e branches dentro de pastas
        for key in folder_keys:
            value = branch_dict[key]
            current_path = path + "/" + key if path else key
            
            # Verificar se é uma folha (branch) ou um diretório
            is_branch = "__branch" in value
            
            if is_branch:
                branch = value["__branch"]
                is_protected = is_protected_func(branch.name)
                branch_item = self._create_branch_item(parent_item, key, branch, is_protected)
            else:
                # É um diretório, criar item do diretório
                dir_item = self._create_branch_item(parent_item, key)
                
                # Processar recursivamente os itens deste diretório
                self._populate_tree(dir_item, value, is_protected_func, current_path)
        
        # Depois processar branches na raiz (sem pastas)
        for key in root_branch_keys:
            value = branch_dict[key]
            branch = value["__branch"]
            is_protected = is_protected_func(branch.name)
            branch_item = self._create_branch_item(parent_item, key, branch, is_protected)

    def _set_tree_icons(self):
        """Define os ícones de expandir/recolher na árvore"""
        closed_icon_path = self.get_resource_path("closed.png")
        open_icon_path = self.get_resource_path("open.png")
        
        # Converter caminhos para usar somente /
        closed_icon_path = closed_icon_path.replace('\\', '/')
        open_icon_path = open_icon_path.replace('\\', '/')
        
        if os.path.exists(closed_icon_path.replace('/', '\\')) and os.path.exists(open_icon_path.replace('/', '\\')):
            # Armazenar referências aos ícones, mesmo que não sejam usados programaticamente
            # isso pode ser útil para uso futuro
            self.closed_icon = QIcon(closed_icon_path)
            self.open_icon = QIcon(open_icon_path)
            
            # Aplicar estilo corrigido ao QTreeWidget para os branches
            self.branches_tree.setStyleSheet(f"""
                QTreeWidget {{
                    background-color: white;
                    alternate-background-color: #F8F8F8;
                    border: none;
                    outline: none;
                }}
                QTreeWidget::item {{
                    padding: 6px;
                    min-height: 28px;
                    border-bottom: 1px solid #EEEEEE;
                    color: #333333;
                    margin: 2px 0;
                    border-radius: 3px;
                }}
                QTreeWidget::item:selected {{
                    background-color: #D0E8FF;
                    color: #2B5797;
                    border: 1px solid #A9CCF3;
                    font-weight: bold;
                }}
                QTreeWidget::item:hover:!selected {{
                    background-color: #F0F5FF;
                }}
                QTreeWidget::item:selected:hover {{
                    background-color: #BBD9FF;
                }}
                QHeaderView::section {{
                    background-color: #F0F0F0;
                    padding: 8px 5px;
                    border: 1px solid #CCCCCC;
                    color: #333333;
                    font-weight: bold;
                }}
                QTreeWidget::branch {{
                    background: transparent;
                }}
                QTreeWidget::branch:selected {{
                    background-color: #D0E8FF;
                }}
                /* Apenas um único ícone para expandir/recolher */
                QTreeWidget::branch:has-children:!has-siblings:closed,
                QTreeWidget::branch:closed:has-children:has-siblings {{
                    border-image: none;
                    image: url({closed_icon_path});
                }}
                QTreeWidget::branch:open:has-children:!has-siblings,
                QTreeWidget::branch:open:has-children:has-siblings {{
                    border-image: none;
                    image: url({open_icon_path});
                }}
                /* Correção específica para garantir que não haja faixas pretas na seleção */
                QTreeWidget::branch:adjoins-item:selected {{
                    background-color: #D0E8FF;
                }}
                QTreeWidget::branch:has-siblings:adjoins-item:selected {{
                    background-color: #D0E8FF;
                }}
                QTreeWidget::branch:has-siblings:!adjoins-item:selected {{
                    background-color: #D0E8FF;
                }}
            """)
        else:
            print(f"AVISO: Ícones não encontrados: {closed_icon_path}, {open_icon_path}")
    
    def _update_selection_icons(self):
        """Atualiza os ícones das branches baseado no estado de seleção"""
        def update_item_icons(parent):
            for i in range(parent.childCount()):
                item = parent.child(i)
                
                # Verificar se é uma branch (folha)
                data = item.data(0, Qt.ItemDataRole.UserRole)
                if data and data.get('is_leaf', True) and not data.get('is_protected', False):
                    # Se for uma branch não protegida, atualizar ícone baseado na seleção
                    if item.isSelected() and self.branch_selected_icon:
                        item.setIcon(0, self.branch_selected_icon)
                        
                        # Não precisamos definir background aqui, pois o QTreeWidget::branch:selected
                        # e QTreeWidget::item:selected já são aplicados automaticamente
                    elif not item.isSelected() and self.branch_icon:
                        item.setIcon(0, self.branch_icon)
                        # Limpar fundos personalizados se houver
                        item.setBackground(0, QBrush())
                        item.setBackground(1, QBrush())
                
                # Processar recursivamente os filhos
                update_item_icons(item)
        
        # Iniciar o processamento a partir da raiz
        update_item_icons(self.branches_tree.invisibleRootItem())

    def get_selected_branches(self):
        """
        Retorna a lista de branches selecionadas
        
        Returns:
            list: Lista de nomes de branches selecionadas
        """
        selected_branches = []
        
        # Função recursiva para encontrar todos os itens selecionados
        def collect_selected(parent):
            for i in range(parent.childCount()):
                item = parent.child(i)
                
                # Verificar os dados do item
                data = item.data(0, Qt.ItemDataRole.UserRole)
                if data and data.get('is_leaf', False) and item.isSelected():
                    selected_branches.append(data.get('name', ''))
                
                # Verificar filhos recursivamente
                collect_selected(item)
        
        # Iniciar a busca a partir da raiz invisível
        collect_selected(self.branches_tree.invisibleRootItem())
        
        return selected_branches
        
    def select_all_branches(self):
        """Seleciona todas as branches não protegidas"""
        # Desmarcar tudo primeiro
        self.branches_tree.clearSelection()
        
        # Função recursiva para selecionar itens não protegidos
        def select_if_not_protected(parent):
            for i in range(parent.childCount()):
                item = parent.child(i)
                
                # Verificar os dados do item
                data = item.data(0, Qt.ItemDataRole.UserRole)
                if data and data.get('is_leaf', False) and not data.get('is_protected', False):
                    item.setSelected(True)
                
                # Aplicar recursivamente aos filhos
                select_if_not_protected(item)
        
        # Iniciar a seleção a partir da raiz invisível
        select_if_not_protected(self.branches_tree.invisibleRootItem())
        
        # Atualizar os ícones de seleção
        self._update_selection_icons()
                
    def deselect_all_branches(self):
        """Desmarca todas as branches"""
        self.branches_tree.clearSelection()
        
        # Atualizar os ícones de seleção
        self._update_selection_icons()
    
    def _count_deletable_branches(self):
        """
        Conta o número de branches que podem ser deletadas (não protegidas)
        
        Returns:
            int: Número de branches não protegidas
        """
        deletable_count = 0
        
        # Função recursiva para contar branches não protegidas
        def count_branches(parent):
            nonlocal deletable_count
            for i in range(parent.childCount()):
                item = parent.child(i)
                
                # Verificar os dados do item
                data = item.data(0, Qt.ItemDataRole.UserRole)
                if data and data.get('is_leaf', False) and not data.get('is_protected', False):
                    deletable_count += 1
                
                # Verificar filhos recursivamente
                count_branches(item)
        
        # Iniciar a contagem a partir da raiz invisível
        count_branches(self.branches_tree.invisibleRootItem())
        
        return deletable_count
    
    def _update_buttons_state(self):
        """
        Atualiza o estado dos botões de acordo com a presença de branches deletáveis
        """
        has_deletable_branches = self._count_deletable_branches() > 0
        
        self.select_all_button.setEnabled(has_deletable_branches)
        self.delete_button.setEnabled(has_deletable_branches)
        self.deselect_all_button.setEnabled(has_deletable_branches)
        
        if not has_deletable_branches:
            self.select_all_button.setStyleSheet("""
                QPushButton {
                    background-color: #AAAAAA;
                    color: #DDDDDD;
                    border-radius: 4px;
                    padding: 6px;
                    font-weight: bold;
                }
            """)
            self.delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #AAAAAA;
                    color: #DDDDDD;
                    border-radius: 4px;
                    padding: 6px;
                    font-weight: bold;
                }
            """)
            self.deselect_all_button.setStyleSheet("""
                QPushButton {
                    background-color: #AAAAAA;
                    color: #DDDDDD;
                    border-radius: 4px;
                    padding: 6px;
                    font-weight: bold;
                }
            """)
        else:
            self.select_all_button.setStyleSheet("""
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
            self.delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #C42B1C;
                    color: white;
                    border-radius: 4px;
                    padding: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #951500;
                }
            """)
            self.deselect_all_button.setStyleSheet("""
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
        
    def _expand_all(self):
        """Expande todos os items da árvore"""
        self.branches_tree.expandAll()
        
    def _collapse_all(self):
        """Recolhe todos os items da árvore"""
        self.branches_tree.collapseAll() 