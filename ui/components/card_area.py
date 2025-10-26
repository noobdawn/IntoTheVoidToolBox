from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import ScrollArea, CardWidget, TitleLabel
from core.ivtcard import WeaponCardCommon, WeaponCardRiven, WeaponCardExclusive
from core.ivtenum import WeaponType,  SubWeaponType
from .mini_card import MiniCard
from .flow_layout import FlowLayout

from core.ivtcontext import CONTEXT
from core.ivtdps import DPSRequest

class CardArea(CardWidget):
    '''
    过滤并显示执行卡的区域
    '''

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("cardArea")

        self.mainLayout = QVBoxLayout(self)
        self.scrollArea = ScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidget = QWidget()
        self.flowLayout = FlowLayout(self.scrollAreaWidget)
        self.scrollAreaWidget.setLayout(self.flowLayout)
        self.scrollArea.setWidget(self.scrollAreaWidget)
        self.mainLayout.addWidget(self.scrollArea)

        CONTEXT.uiSignals.weaponChanged.connect(self._onWeaponChanged)

    def _init_cards(self, cards: list[WeaponCardCommon | WeaponCardRiven | WeaponCardExclusive]):
        '''
        初始化显示的执行卡
        '''
        for card in cards:
            miniCard = MiniCard(card, self)
            self.flowLayout.addWidget(miniCard)

    def _onWeaponChanged(self, dpsRequest : DPSRequest):
        '''
        处理武器更改事件，更新显示的执行卡
        '''
        # 清除现有的卡片
        while self.flowLayout.count():
            item = self.flowLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 根据武器类型过滤执行卡
        weaponType = dpsRequest.weapon.weaponType
        subWeaponType = dpsRequest.weapon.subWeaponType
        allCards = CONTEXT.getAllCards()
        filteredCards = []

        for card in allCards:
            if isinstance(card, WeaponCardCommon):
                if (card.weaponType == WeaponType.All):
                    filteredCards.append(card)
                elif (card.weaponType == weaponType and (card.subWeaponType == subWeaponType or card.subWeaponType == SubWeaponType.All)):
                    filteredCards.append(card)

        # 初始化显示的卡片
        self._init_cards(filteredCards)