"""
Constantes utilizadas pela aplicação
"""

# Estilos da aplicação
APP_STYLE = """
    QMainWindow, QWidget {
        background-color: #F5F5F5;
        color: #333333;
    }
    QLabel {
        color: #333333;
        font-weight: normal;
    }
    QLabel[title="true"] {
        font-size: 20px;
        font-weight: bold;
        color: #2B5797;
    }
    QListWidget {
        border: 1px solid #CCCCCC;
        border-radius: 6px;
        padding: 5px;
        background-color: white;
        color: #333333;
    }
    QPushButton {
        border: 1px solid #1D3C6E;
        border-radius: 5px;
        padding: 10px;
        background-color: #2B5797;
        color: white;
        font-weight: bold;
        font-size: 13px;
    }
    QPushButton:hover {
        background-color: #1D3C6E;
    }
    QPushButton[destructive="true"] {
        background-color: #C42B1C;
        border: 1px solid #951500;
    }
    QPushButton[destructive="true"]:hover {
        background-color: #951500;
    }
    QPushButton:disabled {
        background-color: #CCCCCC;
        color: #EEEEEE;
        border: 1px solid #BBBBBB;
    }
    QLineEdit {
        border: 1px solid #CCCCCC;
        border-radius: 5px;
        padding: 8px;
        background-color: white;
        color: #333333;
    }
    QLineEdit:focus {
        border: 1px solid #2B5797;
    }
    QGroupBox {
        border: 1px solid #CCCCCC;
        border-radius: 6px;
        margin-top: 2ex;
        padding: 15px;
        font-weight: bold;
        color: #333333;
        background-color: #FFFFFF;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 8px;
        color: #2B5797;
    }
    QCheckBox {
        color: #333333;
    }
    QComboBox {
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        padding: 5px;
        background-color: white;
        color: #333333;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: right;
        width: 20px;
        border-left: 1px solid #CCCCCC;
    }
    QTabWidget::pane {
        border: 1px solid #CCCCCC;
        background-color: white;
        border-radius: 6px;
    }
    QTabBar::tab {
        background-color: #E0E0E0;
        border: 1px solid #CCCCCC;
        border-bottom: none;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        padding: 10px 20px;
        margin-right: 3px;
        color: #333333;
        font-weight: bold;
    }
    QTabBar::tab:selected {
        background-color: #2B5797;
        color: white;
        border-bottom-color: #2B5797;
    }
    QTabBar::tab:hover:!selected {
        background-color: #D0D0D0;
    }
    QTabBar::tab:selected:hover {
        background-color: #1D3C6E;
    }
    QTableWidget {
        border: 1px solid #CCCCCC;
        border-radius: 6px;
        background-color: white;
        alternate-background-color: #F5F5F5;
        gridline-color: #DDDDDD;
    }
    QTableWidget::item {
        color: #333333;
        padding: 4px;
    }
    QHeaderView::section {
        background-color: #F0F0F0;
        padding: 8px;
        border: 1px solid #CCCCCC;
        font-weight: bold;
        color: #333333;
    }
    QToolButton {
        border: 1px solid #999999;
        border-radius: 4px;
        padding: 5px;
        background-color: #EEEEEE;
        color: #333333;
    }
    QToolButton:hover {
        background-color: #DDDDDD;
    }
    QScrollArea {
        border: none;
    }
    QProgressBar {
        border: 1px solid #CCCCCC;
        border-radius: 5px;
        background-color: #F5F5F5;
        color: #333333;
        text-align: center;
        height: 20px;
    }
    QProgressBar::chunk {
        background-color: #2B5797;
        border-radius: 3px;
    }
    QFrame {
        background-color: #FFFFFF;
    }
""" 