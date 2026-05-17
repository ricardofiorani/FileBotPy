"""Preview widget showing new file names."""

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QStandardItemModel, QStandardItem
from PyQt6.QtWidgets import QTableView, QHeaderView


class PreviewWidget(QTableView):
    """Table widget showing only new file names."""

    def __init__(self):
        super().__init__()
        self._model = QStandardItemModel(self)
        self._model.setHorizontalHeaderLabels(["New Name"])
        self.setModel(self._model)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.setAlternatingRowColors(True)

    def set_mappings(self, mappings: list[tuple[str, str]]):
        """Set the preview mappings."""
        self._model.removeRows(0, self._model.rowCount())
        for old_path, new_path in mappings:
            if new_path:
                display_name = Path(new_path).name
                color = QColor(0, 128, 0)
            else:
                display_name = "No match found"
                color = QColor(255, 0, 0)

            item = QStandardItem(display_name)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            item.setForeground(color)
            item.setData(old_path, Qt.ItemDataRole.UserRole)
            item.setData(new_path, Qt.ItemDataRole.ToolTipRole)

            self._model.appendRow([item])

    def clear(self):
        """Clear all preview entries."""
        self._model.removeRows(0, self._model.rowCount())

    def get_mappings(self) -> list[tuple[str, str]]:
        """Get the current mappings."""
        mappings = []
        for row in range(self._model.rowCount()):
            item = self._model.item(row, 0)
            if item and item.text() != "No match found":
                old_path = item.data(Qt.ItemDataRole.UserRole)
                new_path = item.data(Qt.ItemDataRole.ToolTipRole)
                if old_path and new_path:
                    mappings.append((old_path, new_path))
        return mappings
