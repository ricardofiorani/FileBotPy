"""File list widget with drag-drop support."""

from pathlib import Path

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QStandardItemModel, QStandardItem, QIcon
from PyQt6.QtWidgets import QListView, QMenu


class FileListWidget(QListView):
    """List widget that accepts drag-dropped files."""

    files_changed = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self._model = QStandardItemModel(self)
        self.setModel(self._model)
        self.setAcceptDrops(True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Accept drag events with URLs."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        """Accept drag move events."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event: QDropEvent):
        """Handle dropped files/folders."""
        urls = event.mimeData().urls()
        for url in urls:
            if url.isLocalFile():
                path = Path(url.toLocalFile())
                if path.is_file():
                    self._add_file(path)
                elif path.is_dir():
                    for file in path.rglob("*"):
                        if file.is_file():
                            self._add_file(file)
        event.acceptProposedAction()
        self.files_changed.emit(self.get_files())

    def _add_file(self, path: Path):
        """Add a file to the list."""
        for row in range(self._model.rowCount()):
            if self._model.item(row).data(Qt.ItemDataRole.UserRole) == str(path):
                return

        item = QStandardItem(path.name)
        item.setData(str(path), Qt.ItemDataRole.UserRole)
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self._model.appendRow(item)

    def _show_context_menu(self, position):
        """Show context menu."""
        menu = QMenu(self)
        remove_action = menu.addAction("Remove Selected")
        clear_action = menu.addAction("Clear All")

        action = menu.exec(self.mapToGlobal(position))
        if action == remove_action:
            self._remove_selected()
        elif action == clear_action:
            self._clear_all()

    def _remove_selected(self):
        """Remove selected items."""
        indexes = self.selectedIndexes()
        for index in sorted(indexes, reverse=True):
            self._model.removeRow(index.row())
        self.files_changed.emit(self.get_files())

    def _clear_all(self):
        """Clear all items."""
        self._model.removeRows(0, self._model.rowCount())
        self.files_changed.emit(self.get_files())

    def get_files(self) -> list[str]:
        """Get list of file paths."""
        files = []
        for row in range(self._model.rowCount()):
            path = self._model.item(row).data(Qt.ItemDataRole.UserRole)
            if path:
                files.append(path)
        return files
