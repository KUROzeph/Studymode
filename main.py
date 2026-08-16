import sys

from PySide6.QtWidgets import QApplication

from database import initialize_database, get_subjects
from menu import Dashboard


def main():
    initialize_database()

    subjects = get_subjects()

    app = QApplication(sys.argv)

    window = Dashboard(subjects)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()