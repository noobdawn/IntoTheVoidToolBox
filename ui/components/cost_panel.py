from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap, QPainter

class CostPanel(QWidget):
    """
    显示执行卡电量
    """
    def __init__(self, pixmap_path, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap(pixmap_path)
        self.setFixedSize(66, 25)

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.pixmap.isNull():
            painter.drawPixmap(self.rect(), self.pixmap)
        super().paintEvent(event)