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
    QMessageBox,
    QMenu,
)

from timer import StudyTimer
from database import (
    add_subject,
    get_subjects,
    rename_subject,
    delete_subject,
)


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

        self.subject_list.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )

        self.subject_list.customContextMenuRequested.connect(
            self.show_subject_menu
        )

        for subject in self.subjects:
            self.add_subject_to_list(subject)

        sidebar_layout.addWidget(self.subject_list)

        self.add_button = QPushButton("+ Add Subject")
        self.add_button.clicked.connect(
            self.add_new_subject
        )

        sidebar_layout.addWidget(self.add_button)

        # timer content
        content = QFrame()
        content_layout = QVBoxLayout(content)

        self.subject_label = QLabel(
            "Select a subject"
        )

        self.subject_label.setObjectName(
            "currentSubject"
        )

        self.subject_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.time_label = QLabel(
            "00:00:00"
        )

        self.time_label.setObjectName(
            "timer"
        )

        self.time_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        self.start_button = QPushButton(
        "START"
        )

        self.start_button.setObjectName(
        "startButton"
        )

        self.start_button.clicked.connect(
        self.toggle_timer
        )

        self.pause_button = QPushButton(
        "PAUSE"
        )

        self.pause_button.setEnabled(False)

        self.pause_button.clicked.connect(
        self.toggle_pause
        )

        content_layout.addStretch()

        content_layout.addWidget(
            self.subject_label
        )

        content_layout.addWidget(
            self.time_label
        )

        content_layout.addSpacing(30)

        button_layout = QHBoxLayout()

        button_layout.addWidget(
        self.pause_button
        )

        button_layout.addWidget(
        self.start_button
        )

        content_layout.addLayout(
        button_layout
        )

        content_layout.addStretch()
        

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content)

        self.subject_list.currentItemChanged.connect(
            self.subject_changed
        )

    def setup_timer(self):
        self.ui_timer = QTimer(self)

        self.ui_timer.timeout.connect(
            self.update_timer_display
        )

        self.ui_timer.start(1000)

    # subjects management
    def add_subject_to_list(self, subject):
        item = QListWidgetItem(
            subject["name"]
        )

        item.setData(
            Qt.ItemDataRole.UserRole,
            subject["id"]
        )

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
            QMessageBox.warning(
                self,
                "Subject exists",
                "A subject with this name already exists."
            )

            return

        item = QListWidgetItem(name)

        item.setData(
            Qt.ItemDataRole.UserRole,
            subject_id
        )

        self.subject_list.addItem(item)

        self.subject_list.setCurrentItem(
            item
        )

    def show_subject_menu(self, position):
        item = self.subject_list.itemAt(position)

        if item is None:
            return

        menu = QMenu(self)

        rename_action = menu.addAction(
            "Rename"
        )

        delete_action = menu.addAction(
            "Delete"
        )

        action = menu.exec(
            self.subject_list.mapToGlobal(
                position
            )
        )

        if action == rename_action:
            self.rename_selected_subject()

        elif action == delete_action:
            self.delete_selected_subject()

    def rename_selected_subject(self):
        item = self.subject_list.currentItem()

        if item is None:
            return

        old_name = item.text()

        new_name, accepted = QInputDialog.getText(
            self,
            "Rename Subject",
            "New name:",
            text=old_name
        )

        if not accepted:
            return

        new_name = new_name.strip()

        if not new_name:
            return

        if new_name == old_name:
            return

        subject_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        try:
            rename_subject(
                subject_id,
                new_name
            )

        except Exception:
            QMessageBox.warning(
                self,
                "Subject exists",
                "A subject with this name already exists."
            )

            return

        item.setText(new_name)

        self.subject_label.setText(
            new_name
        )

    def delete_selected_subject(self):
        item = self.subject_list.currentItem()

        if item is None:
            return

        subject_id = item.data(
            Qt.ItemDataRole.UserRole
        )

        subject_name = item.text()

        answer = QMessageBox.question(
            self,
            "Delete Subject",
            (
                f"Delete '{subject_name}'?\n\n"
                "Your existing study history will be "
                "preserved."
            ),
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        delete_subject(subject_id)

        row = self.subject_list.row(item)

        self.subject_list.takeItem(row)

        self.subject_label.setText(
            "Select a subject"
        )

    def subject_changed(self, current, previous):
        if current is None:
            self.subject_label.setText(
                "Select a subject"
            )

            return

        self.subject_label.setText(
            current.text()
        )

    # timer management
    def toggle_timer(self):
        if not self.study_timer.running:

            current = (
                self.subject_list.currentItem()
            )

            if current is None:
                self.subject_label.setText(
                    "Select a subject first!"
                )

                return

            self.study_timer.start()

            self.subject_list.setEnabled(
                False
            )

            self.add_button.setEnabled(
                False
            )

            self.pause_button.setEnabled(
                True
            )

            self.start_button.setText(
                "STOP"
            )

        else:

            self.study_timer.stop()

            self.subject_list.setEnabled(
                True
            )

            self.add_button.setEnabled(
                True
            )

            self.pause_button.setEnabled(
                False
            )

            self.start_button.setText(
                "START"
            )

            self.time_label.setText(
                "00:00:00"
            )

    def toggle_pause(self):
        if not self.study_timer.running:
            return

        if not self.study_timer.paused:

            self.study_timer.pause()

            self.pause_button.setText(
                "RESUME"
            )

        else:

            self.study_timer.resume()

            self.pause_button.setText(
                "PAUSE"
            )

    # display time
    def update_timer_display(self):
        if not self.study_timer.running:
            return

        seconds = (
            self.study_timer.elapsed_seconds()
        )

        hours = seconds // 3600

        minutes = (
            seconds % 3600
        ) // 60

        seconds = seconds % 60

        self.time_label.setText(
            f"{hours:02}:{minutes:02}:{seconds:02}"
        )