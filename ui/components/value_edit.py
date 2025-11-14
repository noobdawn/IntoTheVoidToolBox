from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel
from qfluentwidgets import LineEdit

class ValueEdit(QWidget):
    """A custom widget for value editing with optional type, percentage, and threshold."""
    textChanged = pyqtSignal(str)

    def __init__(self, input_type='float', is_percentage=False, threshold=None, parent=None):
        super().__init__(parent)
        self.input_type = input_type
        self.is_percentage = is_percentage
        self.threshold = threshold

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.line_edit = LineEdit(self)
        
        # Add a container for the line edit and potential placeholder
        self.layout.addWidget(self.line_edit, 1)

        if self.is_percentage:
            self.percentage_label = QLabel('%', self)
            self.percentage_label.setAlignment(Qt.AlignCenter)
            # A bit of styling to make it look like part of the LineEdit
            self.percentage_label.setStyleSheet("""
                background-color: transparent;
                border: 1px solid #E0E0E0;
                border-left: none;
                padding-left: 5px;
                padding-right: 5px;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            """)
            self.line_edit.setStyleSheet("border-right: none; border-top-right-radius: 0px; border-bottom-right-radius: 0px;")
            self.layout.addWidget(self.percentage_label)

        self._setup_validator()
        self._setup_placeholder()
        
        self.line_edit.textChanged.connect(self.textChanged)

    def _setup_validator(self):
        if self.input_type == 'int':
            self.line_edit.setValidator(QIntValidator())
        elif self.input_type == 'float':
            # Allow for negative values and decimals
            validator = QDoubleValidator()
            validator.setNotation(QDoubleValidator.StandardNotation)
            self.line_edit.setValidator(validator)

    def _setup_placeholder(self):
        if self.threshold and isinstance(self.threshold, (list, tuple)) and len(self.threshold) == 2:
            min_val, max_val = self.threshold
            def _fmt(v):
                try:
                    n = float(v)
                except (TypeError, ValueError):
                    return str(v)
                s = f"{n:.2f}"
                return s.rstrip('0').rstrip('.') if '.' in s else s

            placeholder = f"范围: {_fmt(min_val)} ~ {_fmt(max_val)}"
            self.line_edit.setPlaceholderText(placeholder)

    def text(self):
        return self.line_edit.text()

    def setText(self, text):
        self.line_edit.setText(text)

    def clear(self):
        self.line_edit.clear()

    def setThreshold(self, threshold):
        self.threshold = threshold
        self._setup_placeholder()
