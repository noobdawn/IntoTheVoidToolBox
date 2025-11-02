from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import ScrollArea, CardWidget, TitleLabel
from .selectable_mini_card import SelectableMiniCard
from .flow_layout import FlowLayout
import copy

from core.ivtcard import WeaponCardCommon, WeaponCardRiven, WeaponCardSpecial
from core.ivtenum import WeaponType,  SubWeaponType
from core.ivtweapon import Weapon
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
        CONTEXT.uiSignals.dpsResultCompleted.connect(self._onDPSResultCompleted)
        CONTEXT.uiSignals.cardSlotSelected.connect(self._onCardSlotSelected)

        self.weapon = None

    def _init_cards(self, cards: list[WeaponCardCommon | WeaponCardRiven | WeaponCardSpecial]):
        '''
        初始化显示的执行卡
        '''
        for card in cards:
            miniCard = SelectableMiniCard(card, self)
            self.flowLayout.addWidget(miniCard)

    def _onWeaponChanged(self, weapon : Weapon):
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
        self.weapon = weapon
        weaponType = weapon.weaponType
        subWeaponType = weapon.subWeaponType
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

    def _onDPSResultCompleted(self, request: DPSRequest):
        '''
        处理DPS计算结果完成事件，更新显示的执行卡
        '''
        # 查看是否还有执行卡空位
        slotIndex = -1
        for i in range(8):
            if request.cards[i] is None:
                slotIndex = i
                break
        cardWidgets = [self.flowLayout.itemAt(i).widget() for i in range(self.flowLayout.count())]
        if slotIndex == -1:
            for cardWidget in cardWidgets:
                cardWidget.setPriority(0.0)
        else:
            for cardWidget in cardWidgets:
                card = cardWidget.card
                # 判断该执行卡是否已经被装备
                if card in request.cards:
                    cardWidget.setPriority(0.0)
                    continue
                newRequest = copy.deepcopy(request)
                newRequest.cards[slotIndex] = card
                newRequest.calculate()
                priority = (newRequest.averageDps - request.averageDps) / request.averageDps
                cardWidget.setPriority(priority)
        # 重新排序显示的执行卡
        sortedCardWidgets = sorted(cardWidgets, key=lambda w: w.priority, reverse=True)
        for i in range(len(sortedCardWidgets)):
            self.flowLayout.removeWidget(sortedCardWidgets[i])
        for i in range(len(sortedCardWidgets)):
            self.flowLayout.addWidget(sortedCardWidgets[i])


    def _onCardSlotSelected(self, slotIndex: int):
        '''
        处理卡槽选中事件，更新显示的执行卡
        '''
        if self.weapon is None:
            return
        # 清除现有的卡片
        while self.flowLayout.count():
            item = self.flowLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        
        # 根据武器类型过滤执行卡
        weaponType = self.weapon.weaponType
        subWeaponType = self.weapon.subWeaponType
        allCards = CONTEXT.getAllCards()
        filteredCards = []

        for card in allCards:
            if slotIndex != 8 and isinstance(card, WeaponCardCommon):
                if (card.weaponType == WeaponType.All):
                    filteredCards.append(card)
                elif (card.weaponType == weaponType and (card.subWeaponType == subWeaponType or card.subWeaponType == SubWeaponType.All)):
                    filteredCards.append(card)
            elif slotIndex == 8 and isinstance(card, WeaponCardSpecial):
                if (card.weaponName == self.weapon.basename):
                    filteredCards.append(card)
                    
        # 初始化显示的卡片
        self._init_cards(filteredCards)

        if slotIndex != 8 and CONTEXT._lastDPSRequest is not None:
            self._onDPSResultCompleted(CONTEXT._lastDPSRequest)