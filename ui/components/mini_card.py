from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QMenu, QMessageBox
from PyQt5.QtGui import QPixmap, QPainter, QFont, QColor
from PyQt5.QtCore import Qt, pyqtSignal

from .cost_panel import CostPanel

from core.ivtcard import WeaponCardBase, WeaponCardCommon, WeaponCardRiven, WeaponCardWithProperty, WeaponCardSpecial
from core.ivtenum import Slot, SlotToString
from core.ivtcontext import CONTEXT

class MiniCard(QWidget):
    '''
    显示执行卡的组件
    '''
    def __init__(self, card: WeaponCardBase, parent=None):
        super().__init__(parent)
        self.setFixedSize(124, 128)
        
        self.costPanel = CostPanel('assets/ui/costpanel.png', self)
        self.costLayout = QHBoxLayout(self.costPanel)
        self.costLayout.setContentsMargins(0, 0, 0, 0)
        self.costLayout.setSpacing(0)
        
        self.slotLabel = QLabel(self.costPanel)
        self.slotLabel.setFixedSize(30, 30)
        self.slotLabel.setScaledContents(True)
        self.costLayout.addWidget(self.slotLabel)

        self.costLabel = QLabel(self.costPanel)
        self.costLabel.setAlignment(Qt.AlignCenter)
        self.costLayout.addWidget(self.costLabel)

        self.nameLabel = QLabel(self)
        self.nameLabel.setAlignment(Qt.AlignCenter)
        self.nameLabel.setWordWrap(True)

        self.cardLayout = QVBoxLayout(self)
        self.cardLayout.setContentsMargins(5, 5, 5, 5)
        self.cardLayout.addWidget(self.costPanel, alignment=Qt.AlignTop | Qt.AlignHCenter)
        self.cardLayout.addStretch()
        self.cardLayout.addWidget(self.nameLabel)
        self.cardLayout.addStretch()
        self.setLayout(self.cardLayout)

        self.setCard(card)
        self.setActive(True)

    def setCard(self, card: WeaponCardBase):
        '''
        设置显示的执行卡
        '''
        self.card = card
        if card is not None:
            if isinstance(card, WeaponCardCommon):
                commonCard: WeaponCardCommon = card
                self.backgroundPath = 'assets/ui/frame_gold.png'
                if commonCard.isPrime:
                    self.backgroundPath = 'assets/ui/frame_prime.png'
            elif isinstance(card, WeaponCardRiven):
                self.backgroundPath = 'assets/ui/frame_riven.png'
            else:
                self.backgroundPath = 'assets/ui/frame_gold.png'
            self.backgroundPixmap = QPixmap(self.backgroundPath)

            self.costLabel.setText(str(card.cost) if card else "0")
            slotPixmapPath = f'assets/ui/{SlotToString[self.card.slot.value]}.png'
            slotPixmap = QPixmap(slotPixmapPath)
            self.slotLabel.setPixmap(slotPixmap)
            slotPixmapSize = self.slotLabel.size()
            self.slotLabel.setFixedHeight(20)
            self.slotLabel.setFixedWidth(20 * slotPixmap.width() // slotPixmap.height())

            self.nameLabel.setText(card.name)
            tooltipText = None
            if isinstance(card, WeaponCardSpecial):
                tooltipText = f'专属执行卡: 仅限武器 "{card.weaponName}" 使用'
            elif isinstance(card, WeaponCardWithProperty):
                propText = [str(prop) for prop in card.getPropertiesRef()]
                tooltipText = f'属性执行卡:\n' + '\n'.join(propText)
            if tooltipText:
                self.setToolTip(tooltipText)

            self.costPanel.show()
            self.slotLabel.show()
            self.nameLabel.show()
        else:
            # 无执行卡时显示空白
            self.backgroundPixmap = QPixmap()
            self.costPanel.hide()
            self.slotLabel.hide()
            self.nameLabel.hide()
            self.setToolTip("")
        self.update()

    def setActive(self, active: bool):
        '''
        设置执行卡是否可用
        '''
        self.isActive = active
        if active:
            if self.card is not None:  
                self.backgroundPixmap = QPixmap(self.backgroundPath)
            self.nameLabel.setStyleSheet("color: white; background-color: transparent;")
            self.costLabel.setStyleSheet("color: white; background-color: transparent;")
        else:
            if self.card is not None:
                self.backgroundPixmap = QPixmap(self.backgroundPath.replace('.png', '_gray.png'))
            self.nameLabel.setStyleSheet("color: gray; background-color: transparent;")
            self.costLabel.setStyleSheet("color: gray; background-color: transparent;")
        self.update()

    def paintEvent(self, event):
        """
        需自定义背景，故重写paintEvent
        """
        if not self.backgroundPixmap.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.drawPixmap(self.rect(), self.backgroundPixmap)
            painter.end()
        super().paintEvent(event)

    def contextMenuEvent(self, event):
        '''
        删除混淆执行卡
        '''
        if self.card is not None:
            if isinstance(self.card, WeaponCardRiven):
                menu = QMenu(self)
                deleteAction = menu.addAction("删除")
                action = menu.exec_(self.mapToGlobal(event.pos()))

                if action == deleteAction:
                    self._handleDeleteRivenCard()

    def _handleDeleteRivenCard(self):
        '''
        删除混淆执行卡
        '''
        reply = QMessageBox.question(self, '确认删除', 
                                     f'你确定要删除这张自定义混淆执行卡 "{self.card.name}" 吗?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            CONTEXT.deleteRivenCard(self.card)
            CONTEXT.uiSignals.rivenCardChanged.emit(self.card)