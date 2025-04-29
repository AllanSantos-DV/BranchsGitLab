"""
Constantes utilizadas pela aplicação
"""

# Estilos da aplicação
APP_STYLE = """
    QMainWindow, QWidget {
        background-color: #FFFFFF;
    }
    QLabel {
        color: #333333;
        font-weight: normal;
    }
    QLabel[title="true"] {
        font-size: 20px;
        font-weight: bold;
        color: #333333;
    }
    QListWidget {
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        padding: 5px;
        background-color: white;
        color: #333333;
    }
    QPushButton {
        border: 1px solid #999999;
        border-radius: 4px;
        padding: 8px;
        background-color: #2B5797;
        color: white;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #1D3C6E;
    }
    QPushButton[destructive="true"] {
        background-color: #C42B1C;
    }
    QPushButton[destructive="true"]:hover {
        background-color: #951500;
    }
    QPushButton:disabled {
        background-color: #CCCCCC;
        color: #888888;
    }
    QLineEdit {
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        padding: 8px;
        background-color: white;
        color: #333333;
    }
    QGroupBox {
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        margin-top: 2ex;
        padding: 15px;
        font-weight: bold;
        color: #333333;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top center;
        padding: 0 8px;
        color: #333333;
    }
    QCheckBox {
        color: #333333;
    }
    QTableWidget {
        border: 1px solid #CCCCCC;
        border-radius: 4px;
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
        padding: 4px;
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
        border-radius: 4px;
        background-color: #F5F5F5;
        color: #333333;
        text-align: center;
    }
    QProgressBar::chunk {
        background-color: #2B5797;
        width: 10px;
    }
    QFrame {
        background-color: #FFFFFF;
    }
""" 