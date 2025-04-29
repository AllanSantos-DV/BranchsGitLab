"""
View para a tela de seleção de branches protegidas
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                           QCheckBox, QFrame, QScrollArea, QMessageBox, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

class ProtectedBranchesView(QWidget):
    """
    View responsável pela interface de seleção de branches protegidas
    """
    
    # Sinais
    branches_selected = pyqtSignal(list, bool)  # Lista de branches protegidas selecionadas, boolean para esconder protegidas
    back_to_projects_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Inicializa a view de branches protegidas
        
        Args:
            parent (QWidget): Widget pai
        """
        super().__init__(parent)
        self.selected_branches = []
        self.suggested_branches = [
            'master', 'main', 'staging', 'homologacao', 'homolog', 'homologation',
            'integrations', 'uat', 'develop', 'developer', 'development',
            'release', 'hotfix', 'production'
        ]
        self.checkboxes = {}
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
            "Estas branches serão marcadas como protegidas e não poderão ser selecionadas para remoção."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #5D4037;")
        info_layout.addWidget(info_label)
        
        layout.addWidget(info_frame)
        
        # Checkboxes para as branches sugeridas
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
        
        branches_label = QLabel("Branches Padrão")
        branches_label.setStyleSheet("font-weight: bold; color: #2B5797;")
        branches_layout.addWidget(branches_label)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(5, 5, 5, 5)
        scroll_layout.setSpacing(8)
        
        # Criar checkboxes para cada branch sugerida
        for branch_name in self.suggested_branches:
            checkbox = QCheckBox(branch_name)
            checkbox.setChecked(True)  # Todas marcadas por padrão
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
            scroll_layout.addWidget(checkbox)
        
        scroll_layout.addStretch()
        scroll_area.setWidget(scroll_content)
        branches_layout.addWidget(scroll_area)
        
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
        self.select_all_button.clicked.connect(self._select_all)
        
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
        self.deselect_all_button.clicked.connect(self._deselect_all)
        
        buttons_layout.addWidget(self.select_all_button)
        buttons_layout.addWidget(self.deselect_all_button)
        buttons_layout.addStretch()
        
        self.confirm_button = QPushButton("Confirmar e Continuar")
        self.confirm_button.setStyleSheet("""
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
        
    def _select_all(self):
        """Seleciona todas as branches sugeridas"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)
            
    def _deselect_all(self):
        """Desmarca todas as branches sugeridas"""
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)
            
    def _on_back_clicked(self):
        """Callback para quando o botão de voltar é clicado"""
        self.back_to_projects_requested.emit()
        
    def _on_confirm(self):
        """Callback para quando o botão de confirmar é clicado"""
        # Coletar branches selecionadas
        selected_branches = [
            name for name, checkbox in self.checkboxes.items()
            if checkbox.isChecked()
        ]
        
        if not selected_branches:
            response = QMessageBox.question(
                self,
                "Confirmar Configuração",
                "Nenhuma branch foi selecionada como protegida. Isso pode levar à remoção acidental de branches importantes. Tem certeza que deseja continuar?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if response != QMessageBox.StandardButton.Yes:
                return
        
        # Emitir sinal com a lista de branches selecionadas
        self.branches_selected.emit(selected_branches, self.hide_protected_checkbox.isChecked()) 