import sys
from PyQt6.QtWidgets import QApplication
import gui.main_widget as mwi


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_widget = mwi.MainWidget()
    sys.exit(app.exec())
