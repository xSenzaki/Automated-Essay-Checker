import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QGridLayout
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtCore import Qt
from aes_backend import AESBackend

class EssayGrader(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 700)
        self.setWindowTitle('Essay Grader')

        layout = QVBoxLayout()

        # HEADER
        header = QLabel("Automated Essay Checker")
        header.setFont(QFont("Helvetica", 14))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # REFERENCE ESSAY (PROMPT)
        self.reference_label = QLabel('Reference Essay:')
        layout.addWidget(self.reference_label)
        self.reference_essay = QTextEdit()
        self.reference_essay.setFixedHeight(200)
        layout.addWidget(self.reference_essay)

        # STUDENT ESSAY (INPUT)
        self.student_label = QLabel('Student Essay:')
        layout.addWidget(self.student_label)
        self.student_essay = QTextEdit()
        self.student_essay.setFixedHeight(200)
        layout.addWidget(self.student_essay)

        grid = QGridLayout()

        # SUBMIT BUTTON
        self.submit_button = QPushButton('Submit')
        self.submit_button.setStyleSheet(
            '''
            QPushButton {
                background-color: #007bff;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-family: Helvetica;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            '''
        )
        self.submit_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.submit_button.clicked.connect(self.submit_essay)
        grid.addWidget(self.submit_button, 0, 0)

        # RESET BUTTON
        self.reset_button = QPushButton('Reset')
        self.reset_button.setStyleSheet(
            '''
            QPushButton {
                background-color: #FF0000;
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-family: Helvetica;
            }
            QPushButton:hover {
                background-color: #8B0000;
            }
            '''
        )
        self.reset_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.reset_button.clicked.connect(self.reset_essay)
        grid.addWidget(self.reset_button, 0, 1)

        layout.addLayout(grid)

        self.score_label = QLabel()
        self.score_label.setFont(QFont("Helvetica", 14))
        layout.addWidget(self.score_label)

        self.setLayout(layout)

    def submit_essay(self):
        # Get the text from the reference and student essays
        reference_essay = self.reference_essay.toPlainText()
        student_essay = self.student_essay.toPlainText()
        
        # Create an instance of the AESBackend
        backend = AESBackend()
        
        # Grade the essay using the backend
        content_score = backend.evaluate_content(reference_essay, student_essay)
        organization_score = backend.evaluate_organization(reference_essay, student_essay)
        grammar_mechanics_score = backend.evaluate_grammar_mechanics(student_essay)
        word_choice_score = backend.evaluate_word_choice(student_essay)
        total_score = backend.grade_essay(reference_essay, student_essay)
        
        # Display the scores in the score label
        self.score_label.setText(
            f"Total Essay Score: {round(total_score)} / 50\n"
            f"Content Score: {round(content_score)} / 25\n"
            f"Organization Score: {round(organization_score)} / 10\n"
            f"Grammar/Mechanics Score: {round(grammar_mechanics_score)} / 10\n"
            f"Word Choice Score: {round(word_choice_score)} / 5"
        )
        
        # CENTER ALIGN THE SCORE LABEL
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def reset_essay(self):
        # Clear the text in the reference and student essays
        self.reference_essay.clear()
        self.student_essay.clear()
        
        # Clear the score label
        self.score_label.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    grader = EssayGrader()
    grader.show()
    sys.exit(app.exec())