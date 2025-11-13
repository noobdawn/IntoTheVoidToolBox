from PyQt5.QtWidgets import QWidget, QMenu, QMessageBox
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtCore import Qt
from core.ivtcard import WeaponCardBase

from .mini_card import MiniCard

from core.ivtcontext import CONTEXT
from core.ivtcard import WeaponCardSpecial, WeaponCardWithProperty
import json

class CardSlot(MiniCard):
    def __init__(self, slotIndex: int, isSpecial: bool, parent=None):
        super().__init__(None, parent)

        self.slotIndex = slotIndex
        self.card: WeaponCardBase | None = None
        self.backgroundPixmap = QPixmap('assets/ui/empty_frame.png')
        self.selectedPixmap = QPixmap('assets/ui/select_frame.png')
        self.isSpecial = isSpecial
        self.isSelected = False

    def setCard(self, card: WeaponCardBase):
        '''
        设置卡槽中的执行卡
        '''
        super().setCard(card)
        if card is None:
            self.backgroundPixmap = QPixmap('assets/ui/empty_frame.png')
        self.update()
        CONTEXT.uiSignals.weaponBuildRequestChanged.emit()

    def setSelected(self, selected: bool):
        '''
        设置卡槽选中状态
        '''
        self.isSelected = selected
        self.update()

    def mousePressEvent(self, event):
        '''
        选中卡槽
        '''
        if event.button() == Qt.LeftButton:
            CONTEXT.uiSignals.cardSlotSelected.emit(self.slotIndex)

    def contextMenuEvent(self, a0):
        '''
        右键卸载执行卡
        '''
        if self.card is not None:
            self.setCard(None)
            CONTEXT.uiSignals.weaponBuildRequestChanged.emit()

    def paintEvent(self, event):
        # 绘制空白背景或执行卡
        if self.card is None:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.drawPixmap(self.rect(), self.backgroundPixmap)
            painter.end()
        else:
            super().paintEvent(event)
        # 绘制选中边框
        if self.isSelected:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.drawPixmap(self.rect(), self.selectedPixmap)
            painter.end()