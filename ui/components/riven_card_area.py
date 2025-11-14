from .card_area import CardArea
from .mini_card import MiniCard

from core.ivtcontext import CONTEXT
from core.ivtcard import WeaponCardRiven, WeaponCardCommon, WeaponCardSpecial

class RivenCardArea(CardArea):
    '''
    过滤并显示混淆执行卡的区域
    '''

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("rivenCardArea")
        
        CONTEXT.uiSignals.weaponChanged.disconnect(self._onWeaponChanged)
        CONTEXT.uiSignals.dpsResultCompleted.disconnect(self._onDPSResultCompleted)
        CONTEXT.uiSignals.cardSlotSelected.disconnect(self._onCardSlotSelected)
        CONTEXT.uiSignals.dpsMethodChanged.disconnect(self._onDpsMethodChanged)

        CONTEXT.uiSignals.rivenCardChanged.connect(self._onRivenCardChanged)
        self._onRivenCardChanged(None)

    def _onRivenCardChanged(self, card : WeaponCardRiven):
        '''
        处理混淆执行卡更改事件，更新显示的执行卡
        '''
        # 清除现有的卡片
        while self.flowLayout.count():
            item = self.flowLayout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 重新加载混淆执行卡
        allCards = CONTEXT.getAllCards()
        rivenCards = [card for card in allCards]
        self._init_cards(rivenCards)

    def _init_cards(self, cards: list[WeaponCardCommon | WeaponCardRiven | WeaponCardSpecial]):
        '''
        初始化显示的执行卡，仅显示混淆执行卡
        '''
        for card in cards:
            if isinstance(card, WeaponCardRiven):
                miniCard = MiniCard(card, self)
                self.flowLayout.addWidget(miniCard)