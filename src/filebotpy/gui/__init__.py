"""FileBotPy GUI module using PyQt6."""

__all__ = ["launch_gui"]


def launch_gui():
    """Launch the FileBotPy GUI application."""
    import sys
    from PyQt6.QtWidgets import QApplication
    from filebotpy.gui.app import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("FileBotPy")
    app.setApplicationVersion("0.1.0")
    app.setOrganizationName("FileBotPy")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
