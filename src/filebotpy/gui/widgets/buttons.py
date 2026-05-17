"""Action buttons widget."""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class ActionButtons(QWidget):
    """Widget with Match, Rename and Refresh/Clear buttons."""

    match_clicked = pyqtSignal()
    rename_clicked = pyqtSignal()
    refresh_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        self.match_button = QPushButton("Match")
        self.match_button.setMinimumHeight(50)
        self.match_button.setStyleSheet(
            "QPushButton { font-size: 16px; font-weight: bold; background-color: #4CAF50; color: white; border-radius: 4px; }"
            "QPushButton:hover { background-color: #45a049; }"
            "QPushButton:disabled { background-color: #cccccc; }"
        )
        self.match_button.clicked.connect(self.match_clicked.emit)
        layout.addWidget(self.match_button)

        self.rename_button = QPushButton("Rename")
        self.rename_button.setMinimumHeight(50)
        self.rename_button.setStyleSheet(
            "QPushButton { font-size: 16px; font-weight: bold; background-color: #2196F3; color: white; border-radius: 4px; }"
            "QPushButton:hover { background-color: #1976D2; }"
            "QPushButton:disabled { background-color: #cccccc; }"
        )
        self.rename_button.clicked.connect(self.rename_clicked.emit)
        layout.addWidget(self.rename_button)

        self.refresh_button = QPushButton("Refresh/Clear")
        self.refresh_button.setMinimumHeight(50)
        self.refresh_button.setStyleSheet(
            "QPushButton { font-size: 16px; font-weight: bold; background-color: #FF9800; color: white; border-radius: 4px; }"
            "QPushButton:hover { background-color: #F57C00; }"
            "QPushButton:disabled { background-color: #cccccc; }"
        )
        self.refresh_button.clicked.connect(self.refresh_clicked.emit)
        layout.addWidget(self.refresh_button)

    def set_match_enabled(self, enabled: bool):
        """Enable/disable match button."""
        self.match_button.setEnabled(enabled)

    def set_rename_enabled(self, enabled: bool):
        """Enable/disable rename button."""
        self.rename_button.setEnabled(enabled)
