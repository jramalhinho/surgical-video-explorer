import sys
from PyQt6.QtWidgets import QApplication
import gui.main_widget as mwi


def main():
    app = QApplication(sys.argv)
    main_widget = mwi.MainWidget()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

