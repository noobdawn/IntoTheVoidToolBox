from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMenu, QMessageBox
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor
from PyQt5.QtCore import Qt, pyqtSignal

from .mini_card import MiniCard

from core.ivtcard import WeaponCardBase, WeaponCardCommon, WeaponCardRiven, WeaponCardWithProperty, WeaponCardSpecial
from core.ivtenum import Slot, SlotToString
from core.ivtcontext import CONTEXT

class SelectableMiniCard(MiniCard):
    '''
    显示可选择的执行卡的组件
    '''
    def __init__(self, card: WeaponCardBase, parent=None):
        super().__init__(card, parent)

        self.priority = 0.0

    def mousePressEvent(self, event):
        '''
        选中执行卡
        '''
        if event.button() == Qt.LeftButton:
            CONTEXT.uiSignals.miniCardSelected.emit(self.card)

    def setPriority(self, priority: float):
        self.priority = priority
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.priority != 0.0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            font = QFont()
            font.setPointSize(10)
            painter.setFont(font)
            if self.priority > 0.0:
                painter.setPen(QColor(255, 0, 0))
                painter.drawText(self.rect(), Qt.AlignCenter, f"{self.priority * 100:.1f}%")
            else:
                painter.setPen(QColor(0, 255, 0))
                painter.drawText(self.rect(), Qt.AlignCenter, f"{self.priority * 100:.1f}%")
            painter.end()