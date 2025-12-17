import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QTextEdit
)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QRect
from PyQt5.QtGui import QPainter, QColor



class ChatInput(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_widget = parent

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return and not event.modifiers():
            if self.parent_widget:
                self.parent_widget.handle_submit()
        else:
            super().keyPressEvent(event)


        # Chat Input Area (Layout for Input + Mic)
        self.input_layout = QHBoxLayout()
        
        self.chat_input = ChatInput(self)
        self.chat_input.setPlaceholderText("Type a command...")
        self.chat_input.setVisible(False)
        self.chat_input.setMaximumHeight(50)
        self.chat_input.setStyleSheet("""
            background-color: #2d2d2d;
            color: white;
            border-radius: 10px;
            border: 1px solid #3d3d3d;
            padding: 5px;
        """)

        self.mic_btn = QLabel("🎙️")
        self.mic_btn.setAlignment(Qt.AlignCenter)
        self.mic_btn.setVisible(False)
        self.mic_btn.setStyleSheet("""
            background-color: #3d3d3d;
            border-radius: 15px;
            padding: 5px;
            font-size: 16px;
        """)
        self.mic_btn.setFixedSize(30, 30)
        # Make the label clickable by simple event filter or custom class?
        # Let's just subclass QLabel or use a QPushButton with style.
        # Ideally QPushButton creates less hassle.
        
        # ... Switching to QPushButton for the mic ...
        pass

# COMPLETE REPLACEMENT for better structure

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QTextEdit, QHBoxLayout, QPushButton
)
from PyQt5.QtCore import Qt, QPoint, QPropertyAnimation, QRect, pyqtSignal

class FloatingAtom(QWidget):
    wake_signal = pyqtSignal()

    def __init__(self, on_submit=None, on_mic=None, wake_service=None):
        super().__init__()
        self.on_submit = on_submit
        self.on_mic = on_mic
        self.wake_service = wake_service

        # Window settings
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.radius = 60
        self.expanded = False
        self.drag_pos = QPoint()

        self.init_ui()
        
        # Setup Wake Word Bridge
        if self.wake_service:
            self.wake_signal.connect(self.handle_mic)
            self.wake_service.on_wake = self.wake_signal.emit
            self.wake_service.start_listening()

    def init_ui(self):
        self.setGeometry(100, 100, self.radius, self.radius)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Icon / Face
        self.icon = QLabel("🧠")
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setStyleSheet("font-size: 26px; color: white;")

        # Chat display (History)
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setVisible(False)
        self.chat_history.setStyleSheet("""
            background-color: #1e1e1e;
            color: #e0e0e0;
            border-radius: 10px;
            border: none;
            padding: 5px;
        """)

        # Input Area Container
        self.input_container = QWidget()
        self.input_container.setVisible(False)
        self.input_layout = QHBoxLayout(self.input_container)
        self.input_layout.setContentsMargins(0, 0, 0, 0)

        self.chat_input = ChatInput(self)
        self.chat_input.setPlaceholderText("Type...")
        self.chat_input.setMaximumHeight(40)
        self.chat_input.setStyleSheet("""
            background-color: #2d2d2d;
            color: white;
            border-radius: 10px;
            border: 1px solid #3d3d3d;
            padding: 5px;
        """)

        self.mic_btn = QPushButton("🎙️")
        self.mic_btn.setFixedSize(40, 40)
        self.mic_btn.clicked.connect(self.handle_mic)
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                border: none;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #ff4757;
            }
        """)

        self.input_layout.addWidget(self.chat_input)
        self.input_layout.addWidget(self.mic_btn)

        self.layout.addWidget(self.icon)
        self.layout.addWidget(self.chat_history)
        self.layout.addWidget(self.input_container)

        self.setLayout(self.layout)

    def handle_submit(self):
        text = self.chat_input.toPlainText().strip()
        if not text:
            return
        
        self.chat_input.clear()
        self.add_message("You", text)

        if self.on_submit:
            response = self.on_submit(text)
            self.add_message("Atom", response)

    def handle_mic(self):
        if self.on_mic:
            # We pass 'self' so the controller can call set_listening/add_message
            self.on_mic(self)

    def add_message(self, sender, text):
        color = "#3498db" if sender == "You" else "#2ecc71"
        self.chat_history.append(f'<b style="color:{color}">{sender}:</b> {text}')
        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )

    # Draw circular background
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if self.expanded:
            painter.setBrush(QColor(20, 20, 20, 240))
            painter.drawRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        else:
            painter.setBrush(QColor(30, 144, 255))
            painter.drawEllipse(0, 0, self.width(), self.height())
            painter.setPen(Qt.NoPen)

    # Drag handling
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    # Click expand / collapse
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            child = self.childAt(event.pos())
            # Do not toggle if clicking interactive elements
            if child in [self.chat_input, self.chat_history, self.mic_btn]:
                return
            self.toggle_expand()

    def toggle_expand(self):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)

        if not self.expanded:
            self.chat_history.setVisible(True)
            self.input_container.setVisible(True)
            
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(
                QRect(self.x(), self.y(), 350, 500)
            )
            self.expanded = True
        else:
            self.chat_history.setVisible(False)
            self.input_container.setVisible(False)
            
            self.animation.setStartValue(self.geometry())
            self.animation.setEndValue(
                QRect(self.x(), self.y(), self.radius, self.radius)
            )
            self.expanded = False

        self.animation.start()

    # Listening animation status
    def set_listening(self, listening=True):
        if listening:
            self.icon.setText("🎤")
            self.mic_btn.setStyleSheet("background-color: #ff4757; border-radius: 20px;")
        else:
            self.icon.setText("🧠")
            self.mic_btn.setStyleSheet("""
            QPushButton {
                background-color: #3d3d3d;
                border: none;
                border-radius: 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            """)

def start_ui(on_submit_callback=None, on_mic_callback=None, wake_service=None):
    app = QApplication(sys.argv)
    atom = FloatingAtom(on_submit=on_submit_callback, on_mic=on_mic_callback, wake_service=wake_service)
    atom.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start_ui()
