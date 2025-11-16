from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from qfluentwidgets import CardWidget, SubtitleLabel

class FoldableCardWidget(CardWidget):
    """
    可折叠的卡片组件。
    """

    def __init__(self, title: str, parent=None):
        super().__init__(parent)
        self.setObjectName('foldableCardWidget')

        self._is_expanded = True
        self._title_text = title

        # Main layout
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 8)
        self.main_layout.setSpacing(5)

        # Header
        self.header_widget = QWidget(self)
        self.header_widget.setObjectName('header')
        self.header_widget.setFixedHeight(50)
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(20, 10, 20, 10)
        self.header_layout.setSpacing(10)

        self.title_label = SubtitleLabel(self._title_text, self)
        self.toggle_label = QLabel("[展开]", self)
        self.toggle_label.setObjectName('toggleLabel')
        self.toggle_label.setStyleSheet("color: grey;")
        self.toggle_label.hide()

        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch(1)
        self.header_layout.addWidget(self.toggle_label)

        # Content
        self.content_widget = QWidget(self)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 0, 20, 0)
        self.content_layout.setSpacing(10)

        # Collapse label
        self.collapse_label_layout = QHBoxLayout()
        self.collapse_label_layout.setContentsMargins(0, 0, 20, 0)
        self.collapse_label = QLabel("[收起]", self)
        self.collapse_label.setObjectName('collapseLabel')
        self.collapse_label.setStyleSheet("color: grey;")
        self.collapse_label_layout.addStretch(1)
        self.collapse_label_layout.addWidget(self.collapse_label)

        # Add widgets to main layout
        self.main_layout.addWidget(self.header_widget)
        self.main_layout.addWidget(self.content_widget)
        self.main_layout.addLayout(self.collapse_label_layout)

        # Connect signals
        self.header_widget.mousePressEvent = self.toggle_expansion
        self.collapse_label.mousePressEvent = self.toggle_expansion

    def contentLayout(self) -> QVBoxLayout:
        """ Returns the layout of the content widget. """
        return self.content_layout

    def toggle_expansion(self, event=None):
        """ Toggles the expanded/collapsed state of the card. """
        self._is_expanded = not self._is_expanded
        self.content_widget.setVisible(self._is_expanded)
        self.collapse_label.setVisible(self._is_expanded)
        self.toggle_label.setVisible(not self._is_expanded)
        self.header_widget.setFixedHeight(50)
        self.adjustSize()
        if self.parentWidget():
            self.parentWidget().adjustSize()

    def expand(self, is_expanded=True):
        """ Sets the expanded state of the card. """
        if self._is_expanded == is_expanded:
            return
        self.toggle_expansion()

    def isExpanded(self) -> bool:
        """ Returns whether the card is expanded. """
        return self._is_expanded
