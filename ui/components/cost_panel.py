from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap, QPainter
from core.ivtcontext import CONTEXT

class CostPanel(QWidget):
    """
    显示执行卡电量
    """
    def __init__(self, pixmap_path, parent=None):
        super().__init__(parent)
        self.pixmap = QPixmap(pixmap_path)
        uiScale = CONTEXT.getUiScale()
        self.setFixedSize(int(66 * uiScale), int(25 * uiScale))

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.pixmap.isNull():
            painter.drawPixmap(self.rect(), self.pixmap)
        super().paintEvent(event)