from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QInputDialog,
)

from timer import StudyTimer
from database import add_subject, get_subjects


class Dashboard(QWidget):
    def __init__(self, subjects):
        super().__init__()

        self.subjects = subjects
        self.study_timer = StudyTimer()

        self.setWindowTitle("study-mode")
        self.resize(900, 600)

        self.build_ui()
        self.setup_timer()

    def build_ui(self):
        main_layout = QHBoxLayout(self)

        # subjects sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)

        title = QLabel("SUBJECTS")
        title.setObjectName("sectionTitle")

        sidebar_layout.addWidget(title)

        self.subject_list = QListWidget()

        for subject in self.subjects:
            self.add_subject_to_list(subject)

        sidebar_layout.addWidget(self.subject_list)

        self.add_button = QPushButton("+ Add Subject")
        self.add_button.clicked.connect(self.add_new_subject)

        sidebar_layout.addWidget(self.add_button)

        # timer content
        content = QFrame()
        content_layout = QVBoxLayout(content)

        self.subject_label = QLabel("Select a subject")
        self.subject_label.setObjectName("currentSubject")

        self.subject_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.time_label = QLabel("00:00:00")
        self.time_label.setObjectName("timer")

        self.time_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.start_button = QPushButton("START")
        self.start_button.setObjectName("startButton")

        self.start_button.clicked.connect(self.toggle_timer)

        content_layout.addStretch()
        content_layout.addWidget(self.subject_label)
        content_layout.addWidget(self.time_label)
        content_layout.addSpacing(30)
        content_layout.addWidget(self.start_button)
        content_layout.addStretch()

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

        self.subject_list.currentItemChanged.connect(
            self.subject_changed
        )

    def setup_timer(self):
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_timer_display)
        self.ui_timer.start(1000)

    # subject addition and selection
    def add_subject_to_list(self, subject):
        item = QListWidgetItem(subject["name"])
        item.setData(Qt.ItemDataRole.UserRole, subject["id"])

        self.subject_list.addItem(item)

    def add_new_subject(self):
        name, accepted = QInputDialog.getText(
            self,
            "Add Subject",
            "Subject name:"
        )

        if not accepted:
            return

        name = name.strip()

        if not name:
            return

        try:
            subject_id = add_subject(name)

        except Exception:
            self.subject_label.setText(
                "Subject already exists!"
            )
            return

        item = QListWidgetItem(name)
        item.setData(
            Qt.ItemDataRole.UserRole,
            subject_id
        )

        self.subject_list.addItem(item)

        self.subject_list.setCurrentItem(item)

    def subject_changed(self, current, previous):
        if current is None:
            self.subject_label.setText(
                "Select a subject"
            )
            return

        self.subject_label.setText(
            current.text()
        )

    # timer lock
    def toggle_timer(self):
        if not self.study_timer.running:

            current = self.subject_list.currentItem()

            if current is None:
                self.subject_label.setText(
                    "Select a subject first!"
                )
                return

            self.study_timer.start()

            # lock subject selection
            self.subject_list.setEnabled(False)

            # lock adding subjects
            self.add_button.setEnabled(False)

            self.start_button.setText("STOP")

        else:

            self.study_timer.stop()

            # unlock subject selection
            self.subject_list.setEnabled(True)

            # unlock adding subjects
            self.add_button.setEnabled(True)

            self.start_button.setText("START")
            self.time_label.setText("00:00:00")

    # timer display
    def update_timer_display(self):
        if not self.study_timer.running:
            return

        seconds = self.study_timer.elapsed_seconds()

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        self.time_label.setText(
            f"{hours:02}:{minutes:02}:{seconds:02}"
        )