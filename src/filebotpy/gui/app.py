"""Main window for FileBotPy GUI."""

from pathlib import Path

from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QLabel,
    QStatusBar,
    QMessageBox,
    QMenuBar,
    QMenu,
    QDialog,
    QFormLayout,
    QLineEdit,
    QDialogButtonBox,
)
from PyQt6.QtGui import QAction

from filebotpy.gui.widgets import FileListWidget, PreviewWidget, ActionButtons
from filebotpy.gui.worker import MatchingWorker


class SettingsDialog(QDialog):
    """Dialog for configuring API keys."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.resize(400, 200)

        layout = QFormLayout(self)

        self.tmdb_key_edit = QLineEdit()
        self.tmdb_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.tmdb_key_edit.setPlaceholderText("Get key from themoviedb.org/settings/api")
        layout.addRow("TMDb API Key:", self.tmdb_key_edit)

        self.tvdb_key_edit = QLineEdit()
        self.tvdb_key_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.tvdb_key_edit.setPlaceholderText("Get key from thetvdb.com/api-information")
        layout.addRow("TheTVDB API Key:", self.tvdb_key_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_tmdb_key(self) -> str:
        return self.tmdb_key_edit.text().strip()

    def get_tvdb_key(self) -> str:
        return self.tvdb_key_edit.text().strip()

    def set_tmdb_key(self, key: str):
        self.tmdb_key_edit.setText(key)

    def set_tvdb_key(self, key: str):
        self.tvdb_key_edit.setText(key)


class MainWindow(QMainWindow):
    """Main application window with three-panel layout."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FileBotPy")
        self.resize(1200, 700)
        self._settings_org = "FileBotPy"
        self._settings_app = "FileBotPy"

        self._setup_ui()
        self._setup_worker()
        self._connect_signals()

    def _setup_ui(self):
        """Set up the main UI layout."""
        self._setup_menu()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(8, 8, 8, 8)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        left_panel = self._create_left_panel()
        center_panel = self._create_center_panel()
        right_panel = self._create_right_panel()

        splitter.addWidget(left_panel)
        splitter.addWidget(center_panel)
        splitter.addWidget(right_panel)

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 0)
        splitter.setStretchFactor(2, 2)

        main_layout.addWidget(splitter)

        self.statusBar().showMessage("Ready")

    def _setup_menu(self):
        """Set up the menu bar."""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("&File")
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._show_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _create_left_panel(self) -> QWidget:
        """Create the left panel with file list."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("Original Files")
        label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 4px;")
        layout.addWidget(label)

        self.file_list = FileListWidget()
        layout.addWidget(self.file_list)

        return panel

    def _create_center_panel(self) -> QWidget:
        """Create the center panel with action buttons."""
        panel = QWidget()
        panel.setFixedWidth(150)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(4, 0, 4, 0)
        layout.addStretch()

        self.action_buttons = ActionButtons()
        layout.addWidget(self.action_buttons)

        layout.addStretch()
        return panel

    def _create_right_panel(self) -> QWidget:
        """Create the right panel with preview."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel("Preview")
        label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 4px;")
        layout.addWidget(label)

        self.preview = PreviewWidget()
        layout.addWidget(self.preview)

        return panel

    def _get_settings(self):
        """Get QSettings instance."""
        from PyQt6.QtCore import QSettings
        return QSettings(self._settings_org, self._settings_app)

    def _load_api_keys(self) -> tuple[str, str]:
        """Load API keys from settings."""
        settings = self._get_settings()
        tmdb_key = settings.value("tmdb_api_key", "", type=str)
        tvdb_key = settings.value("tvdb_api_key", "", type=str)
        return tmdb_key, tvdb_key

    def _save_api_keys(self, tmdb_key: str, tvdb_key: str):
        """Save API keys to settings."""
        settings = self._get_settings()
        settings.setValue("tmdb_api_key", tmdb_key)
        settings.setValue("tvdb_api_key", tvdb_key)

    def _show_settings(self):
        """Show settings dialog."""
        dialog = SettingsDialog(self)
        tmdb_key, tvdb_key = self._load_api_keys()
        dialog.set_tmdb_key(tmdb_key)
        dialog.set_tvdb_key(tvdb_key)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._save_api_keys(dialog.get_tmdb_key(), dialog.get_tvdb_key())

    def _setup_worker(self):
        """Set up the background matching worker."""
        self.worker_thread = QThread()
        tmdb_key, tvdb_key = self._load_api_keys()
        self.worker = MatchingWorker(tmdb_api_key=tmdb_key, tvdb_api_key=tvdb_key)
        self.worker.moveToThread(self.worker_thread)

    def _connect_signals(self):
        """Connect UI signals."""
        self.action_buttons.match_clicked.connect(self._on_match_clicked)
        self.action_buttons.rename_clicked.connect(self._on_rename_clicked)
        self.action_buttons.refresh_clicked.connect(self._on_refresh_clicked)

        self.worker.match_complete.connect(self._on_match_complete)
        self.worker.error.connect(self._on_worker_error)
        self.worker.progress.connect(self._on_worker_progress)

    def _on_match_clicked(self):
        """Handle match button click."""
        files = self.file_list.get_files()
        if not files:
            QMessageBox.warning(self, "No Files", "Please add files to match.")
            return

        tmdb_key, tvdb_key = self._load_api_keys()
        if not tmdb_key and not tvdb_key:
            QMessageBox.information(
                self,
                "No API Keys",
                "No TMDb or TheTVDB API keys configured. Matches will use filename parsing only.\n\n"
                "Configure keys in File > Settings for best results.",
            )

        self.statusBar().showMessage("Matching files...")
        self.action_buttons.set_match_enabled(False)
        self.worker.set_api_keys(tmdb_key, tvdb_key)
        self.worker.set_files(files)
        self.worker_thread.start()
        QThread.msleep(100)
        self.worker.run()

    def _on_rename_clicked(self):
        """Handle rename button click."""
        mappings = self.preview.get_mappings()
        if not mappings:
            QMessageBox.warning(self, "No Matches", "No files to rename. Click Match first.")
            return

        self.statusBar().showMessage("Renaming files...")
        self.action_buttons.set_rename_enabled(False)

        renamed = 0
        errors = 0
        for old_path, new_path in mappings:
            try:
                old = Path(old_path)
                new = Path(new_path)
                new.parent.mkdir(parents=True, exist_ok=True)
                old.rename(new)
                renamed += 1
            except Exception as e:
                errors += 1
                self.statusBar().showMessage(f"Error: {e}")

        self.action_buttons.set_rename_enabled(True)
        QMessageBox.information(
            self,
            "Rename Complete",
            f"Renamed: {renamed}\nErrors: {errors}",
        )
        self.statusBar().showMessage("Ready")

    def _on_refresh_clicked(self):
        """Handle refresh/clear button click."""
        self.preview.clear()
        self.file_list._clear_all()
        self.statusBar().showMessage("Cleared")

    def _on_match_complete(self, mappings):
        """Handle match completion."""
        self.preview.set_mappings(mappings)
        self.worker_thread.quit()
        self.worker_thread.wait()
        self.action_buttons.set_match_enabled(True)
        self.statusBar().showMessage(f"Matched {len(mappings)} files")

    def _on_worker_error(self, error_msg):
        """Handle worker error."""
        self.worker_thread.quit()
        self.worker_thread.wait()
        self.action_buttons.set_match_enabled(True)
        QMessageBox.critical(self, "Error", error_msg)
        self.statusBar().showMessage("Error during matching")

    def _on_worker_progress(self, message):
        """Handle worker progress update."""
        self.statusBar().showMessage(message)
