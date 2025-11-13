from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget)
from qfluentwidgets import SubtitleLabel, CardWidget, ComboBox, SpinBox, CheckBox, PushButton, TransparentToolButton
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt

from ui.components.autocompletion_combo_box import AutocompletionComboBox
from ui.components.foldable_card_widget import FoldableCardWidget
from ui.components.card_area import CardArea
from ui.components.card_slot import CardSlot

from core.ivtcontext import CONTEXT
from core.ivtenum import (WeaponPropertyType, EnemyMaterial, DamageType, SkillDebuff, AvailableCardSets, CardSet, CharacterPropertyType)
from core.ivtdps import DPSRequest
from core.ivtweapon import Weapon
from core.ivtcard import WeaponCardBase

class WeaponSelectCard(CardWidget):
    '''
    武器选择组件
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('weaponSelectCard')

        self.weaponLayout = QHBoxLayout(self)
        self.weaponLabel = QLabel("选择武器:")
        self.weaponSelectComboBox = AutocompletionComboBox()

        # 获取所有的武器名称并作为选项添加到下拉框中
        allWeapons = CONTEXT.getAllWeapons()
        weaponNames = [weapon.name for weapon in allWeapons]
        self.weaponSelectComboBox.addItems(weaponNames)

        self.weaponLayout.addWidget(self.weaponLabel)
        self.weaponLayout.addWidget(self.weaponSelectComboBox)
        self.setLayout(self.weaponLayout)

        self.weaponSelectComboBox.currentTextChanged.connect(self.onWeaponChanged)

        maxHeight = self.weaponSelectComboBox.sizeHint().height()
        self.setMaximumHeight(maxHeight + 40)

    def onWeaponChanged(self, weaponName):
        '''
        当选择的武器改变时调用此方法刷新所有相关组件
        '''
        weapon = CONTEXT.getWeaponByName(weaponName)
        if weapon:
            CONTEXT.uiSignals.weaponChanged.emit(weapon)
            request = DPSRequest(weapon, [None]*9)
            CONTEXT.triggerDpsCalculation(request)

    def afterInit(self):
        '''
        当所有组件都初始化、注册完成后再调用此方法刷新
        '''
        self.onWeaponChanged(self.weaponSelectComboBox.currentText())


    def getWeapon(self) -> Weapon:
        '''
        获取当前选择的武器
        '''
        weaponName = self.weaponSelectComboBox.currentText()
        weapon = CONTEXT.getWeaponByName(weaponName)
        return weapon

class WeaponPropertyCard(CardWidget):
    '''
    武器属性显示组件
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('weaponPropertyCard')
        
        self.contentLayout = QVBoxLayout(self)
        self.contentLayout.setSpacing(0)

        self.title = SubtitleLabel("武器属性")
        self.contentLayout.addWidget(self.title)

        # MOD提升统计方法选择
        self.dpsMethodLayout = QHBoxLayout()
        self.dpsMethodLabel = QLabel("MOD提升统计方法:")
        self.dpsMethodComboBox = ComboBox()
        self.dpsMethodComboBox.addItem("单次爆发伤害量")
        self.dpsMethodComboBox.addItem("单次爆发DPS")
        self.dpsMethodComboBox.addItem("平均DPS")
        self.dpsMethodComboBox.setCurrentIndex(0)
        self.dpsMethodLayout.addWidget(self.dpsMethodLabel)
        self.dpsMethodLayout.addWidget(self.dpsMethodComboBox)
        self.contentLayout.addLayout(self.dpsMethodLayout)
        self.dpsMethodComboBox.currentIndexChanged.connect(self._onDpsMethodChanged)

        self.propertyLayout = QVBoxLayout()
        self.contentLayout.addLayout(self.propertyLayout)
        self.contentLayout.addStretch(1)

        self.setFixedWidth(400)
        self.propertyLabels = {}

        signals = CONTEXT.uiSignals
        signals.dpsResultCompleted.connect(self._updateLabels)

    def _onDpsMethodChanged(self, index):
        '''
        当MOD提升统计方法改变时触发信号
        '''
        CONTEXT.uiSignals.dpsMethodChanged.emit(index)

    def _addPropertyLabel(self, name: str, value, tooltip=None):
        '''
        添加一个属性标签
        '''
        hLayout = QHBoxLayout()
        nameLabel = QLabel(f"{name}:", self)
        hLayout.addWidget(nameLabel)

        if tooltip:
            infoLabel = QLabel(self)
            infoLabel.setPixmap(FIF.INFO.icon().pixmap(16, 16))
            infoLabel.setToolTip(tooltip)
            hLayout.addWidget(infoLabel)

        valueLabel = QLabel(str(value), self)
        hLayout.addWidget(valueLabel)

        container = QWidget(self)
        container.setLayout(hLayout)

        self.propertyLayout.addWidget(container)
        self.propertyLabels[name] = container

    def _setPropertyValue(self, name: str, value):
        '''
        设置属性标签的值
        '''
        if name in self.propertyLabels:
            self.propertyLabels[name].setText(str(value))

    def _updateLabels(self, request: DPSRequest):
        '''
        当属性变化时，更新所有属性标签
        '''
        # 清空现有标签
        for i in reversed(range(self.propertyLayout.count())):
            widgetToRemove = self.propertyLayout.itemAt(i).widget()
            if widgetToRemove is not None:
                widgetToRemove.setParent(None)
        self.propertyLabels.clear()

        weapon = request.weapon

        self._addPropertyLabel('首发暴击伤害', request.firstCriticalDamage, tooltip='若暴击率超过100%则为下一等级暴击伤害')
        self._addPropertyLabel('首发非暴击伤害', request.firstUncriticalDamage, tooltip='若暴击率超过100%则为原等级暴击伤害')
        self._addPropertyLabel('单次爆发伤害量', request.magazineDamage, tooltip='单个弹匣造成的总伤害')
        self._addPropertyLabel('单次爆发DPS', request.magazineDps, tooltip='单个弹匣造成的每秒伤害')
        self._addPropertyLabel('平均DPS', request.averageDps, tooltip='计入换弹时间后的每秒伤害')

        damage = request.finalSnapshot.getTotalDamageArray().sum()
        self._addPropertyLabel('面板总伤害', damage, tooltip='武器面板伤害，计入魈鬼系列卡牌的元素转化')

        for weaponPropType in WeaponPropertyType:
            value = request.finalSnapshot.getPropertyValue(weaponPropType)
            if value != 0:
                self._addPropertyLabel(str(weaponPropType), value)

class TargetSettingCard(FoldableCardWidget):
    '''
    目标设置
    '''
    def __init__(self, parent=None):
        super().__init__('靶标设置', parent)
        self.setObjectName('targetSettingCard')

        contentLayout = self.contentLayout()
        contentLayout.setSpacing(10)

        # 靶标材质选择
        self.materialLayout = QHBoxLayout()
        self.materialLabel = QLabel("靶标材质")
        self.materialComboBox = ComboBox()
        for material in EnemyMaterial:
            self.materialComboBox.addItem(str(material), userData=material)
        self.materialComboBox.setCurrentIndex(0)
        self.materialLayout.addWidget(self.materialLabel)
        self.materialLayout.addStretch(1)
        self.materialLayout.addWidget(self.materialComboBox)
        contentLayout.addLayout(self.materialLayout)
        self.materialComboBox.currentIndexChanged.connect(self._onTargetSettingChanged)

        # 护甲
        self.armorLayout = QHBoxLayout()
        self.armorLabel = QLabel("护甲")
        self.armorSpinBox = SpinBox()
        self.armorSpinBox.setRange(0, 9999)
        self.armorSpinBox.setValue(3430)
        self.armorInfoLabel = QLabel(self)
        self.armorInfoLabel.setPixmap(FIF.INFO.icon().pixmap(16, 16))
        self.armorInfoLabel.setToolTip("材质和护甲数值参考训练场中的120级虚空阿尔法")
        self.armorInfoLabel.setToolTipDuration(0)
        self.armorLayout.addWidget(self.armorLabel)
        self.armorLayout.addStretch(1)
        self.armorLayout.addWidget(self.armorInfoLabel)
        self.armorLayout.addWidget(self.armorSpinBox)
        contentLayout.addLayout(self.armorLayout)
        self.armorSpinBox.valueChanged.connect(self._onTargetSettingChanged)

        self.debuffLayout = QVBoxLayout()
        self.debuffLabel = QLabel("元素异常状态")
        self.debuffs = {
            DamageType.Cold: 9,
            DamageType.Electric: 10,
            DamageType.Virus: 10,
            DamageType.Fire: 1,
        }
        self.debuffWidgets = {}
        for damageType, maxValue in self.debuffs.items():
            layout = QHBoxLayout()
            checkbox = CheckBox(str(damageType))
            spinbox = SpinBox()
            spinbox.setRange(0, maxValue)
            spinbox.setEnabled(False)
            checkbox.stateChanged.connect(lambda state, s=spinbox: s.setEnabled(state))
            checkbox.stateChanged.connect(lambda state, s=spinbox: s.setValue(0) if not state else None)
            checkbox.stateChanged.connect(self._onTargetSettingChanged)
            layout.addWidget(checkbox)
            layout.addStretch(1)
            layout.addWidget(spinbox)
            self.debuffLayout.addLayout(layout)
            self.debuffWidgets[damageType] = (checkbox, spinbox)
            spinbox.valueChanged.connect(self._onTargetSettingChanged)

        contentLayout.addWidget(self.debuffLabel)
        contentLayout.addLayout(self.debuffLayout)

        # 技能易伤
        self.skillDebuffLayout = QVBoxLayout()
        self.skillDebuffLabel = QLabel("技能异常状态")
        self.skillDebuffLayout.addWidget(self.skillDebuffLabel)

        self.skillDebuffWidgets = {}
        for skillDebuff in SkillDebuff:
            checkbox = CheckBox(str(skillDebuff))
            self.skillDebuffLayout.addWidget(checkbox)
            self.skillDebuffWidgets[skillDebuff] = checkbox
            checkbox.stateChanged.connect(self._onTargetSettingChanged)

        contentLayout.addLayout(self.skillDebuffLayout)

        self.applyButton = PushButton(FIF.SAVE,'应用', self)
        self.applyButton.clicked.connect(self._onApplyClicked)

        contentLayout.addWidget(self.applyButton, alignment=Qt.AlignRight)

    def _onApplyClicked(self):
        '''
        应用当前设置到靶标信息中
        '''
        # 隐藏应用按钮
        self.applyButton.setVisible(False)
        CONTEXT.uiSignals.weaponBuildRequestChanged.emit()

    def _onTargetSettingChanged(self):
        '''
        当靶标设置改变时调用此方法
        '''
        self.applyButton.setVisible(True)

    def getElementDebuffInfo(self) -> list[tuple[DamageType, int]]:
        '''
        获取当前设置的元素异常状态信息
        '''
        elementDebuffInfo = []
        for damageType, (checkbox, spinbox) in self.debuffWidgets.items():
            if checkbox.isChecked():
                value = spinbox.value()
                elementDebuffInfo.append( (damageType, value) )
        return elementDebuffInfo
    
    def getSkillDebuff(self) -> list[tuple[SkillDebuff, int]]:
        '''
        获取当前设置的技能异常状态信息
        '''
        skillDebuffInfo = []
        for skillDebuff, checkbox in self.skillDebuffWidgets.items():
            if checkbox.isChecked():
                # 目前技能异常均为1
                skillDebuffInfo.append( (skillDebuff, 1) )
        return skillDebuffInfo
    
    def getMaterial(self) -> EnemyMaterial:
        '''
        获取当前选择的靶标材质
        '''
        return self.materialComboBox.currentData()
    
    def getArmor(self) -> float:
        '''
        获取当前设置的护甲值
        '''
        return self.armorSpinBox.value()

class CharacterSettingCard(FoldableCardWidget):
    '''
    角色设置
    '''
    def __init__(self, parent=None):
        super().__init__('角色设置', parent)
        self.setObjectName('characterSettingCard')

        contentLayout = self.contentLayout()
        contentLayout.setSpacing(10)

        # 角色运动状态
        self.moveStateLabel = QLabel("角色运动状态")
        self.isMovingLayout = QHBoxLayout()
        self.isMovingLabel = QLabel("移动中")
        self.isMovingCheckBox = CheckBox()
        self.isMovingLayout.addWidget(self.isMovingLabel)
        self.isMovingLayout.addStretch(1)
        self.isMovingLayout.addWidget(self.isMovingCheckBox)
        contentLayout.addLayout(self.isMovingLayout)
        self.isMovingCheckBox.stateChanged.connect(self._onCharacterSettingChanged)
        self.isInAirLayout = QHBoxLayout()
        self.isInAirLabel = QLabel("空中")
        self.isInAirCheckBox = CheckBox()
        self.isInAirLayout.addWidget(self.isInAirLabel)
        self.isInAirLayout.addStretch(1)
        self.isInAirLayout.addWidget(self.isInAirCheckBox)
        contentLayout.addLayout(self.isInAirLayout)
        self.isInAirCheckBox.stateChanged.connect(self._onCharacterSettingChanged)

        contentLayout.addSpacing(10)

        # 技能强度
        self.skillStrengthLayout = QHBoxLayout()
        self.skillStrengthLabel = QLabel("技能强度")
        self.skillStrengthSpinBox = SpinBox()
        self.skillStrengthSpinBox.setRange(0, 1000)
        self.skillStrengthSpinBox.setValue(100)
        self.skillStrengthLayout.addWidget(self.skillStrengthLabel)
        self.skillStrengthLayout.addStretch(1)
        self.skillStrengthLayout.addWidget(self.skillStrengthSpinBox)
        contentLayout.addLayout(self.skillStrengthLayout)
        self.skillStrengthSpinBox.valueChanged.connect(self._onCharacterSettingChanged)

        # 执行卡套装设置
        self.cardSetLayout = QVBoxLayout()
        self.cardSetLabel = QLabel("执行卡套装")
        self.cardSetLayout.addWidget(self.cardSetLabel)

        self.cardSetWidgets = []
        self.cardSetListLayout = QVBoxLayout()
        self.addCardSetButton = PushButton(FIF.ADD, '添加执行卡套装', self)
        self.addCardSetButton.clicked.connect(self._addCardSetRow)

        self.cardSetLayout.addLayout(self.cardSetListLayout)
        self.cardSetLayout.addWidget(self.addCardSetButton)
        contentLayout.addLayout(self.cardSetLayout)

        # 应用按钮
        self.applyButton = PushButton(FIF.SAVE,'应用', self)
        self.applyButton.clicked.connect(self._onApplyClicked)
        contentLayout.addWidget(self.applyButton, alignment=Qt.AlignRight)

    def _addCardSetRow(self):
        '''
        添加一行执行卡套装设置
        '''
        hLayout = QHBoxLayout()
        comboBox = ComboBox()
        for cs in AvailableCardSets:
            comboBox.addItem(str(cs), userData=cs)

        spinBox = SpinBox()
        spinBox.setRange(1, 10)

        removeButton = TransparentToolButton(FIF.DELETE, self)

        hLayout.addWidget(comboBox)
        hLayout.addWidget(spinBox)
        hLayout.addStretch(1)
        hLayout.addWidget(removeButton)

        self.cardSetListLayout.addLayout(hLayout)
        widgetTubple = (comboBox, spinBox, removeButton, hLayout)
        self.cardSetWidgets.append(widgetTubple)

        removeButton.clicked.connect(lambda: self._removeCardSetRow(widgetTubple))
        comboBox.currentIndexChanged.connect(self._onCharacterSettingChanged)
        spinBox.valueChanged.connect(self._onCharacterSettingChanged)
        
    def _removeCardSetRow(self, widgetTubple):
        '''
        删除一行执行卡套装设置
        '''
        comboBox, spinBox, removeButton, hLayout = widgetTubple
        # 从布局中移除
        while hLayout.count():
            item = hLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.cardSetListLayout.removeItem(hLayout)
        hLayout.deleteLater()
        self.cardSetWidgets.remove(widgetTubple)
        self._onCharacterSettingChanged()

    def _onCharacterSettingChanged(self):
        '''
        当角色设置改变时调用此方法
        '''
        self.applyButton.setVisible(True)

    def _onApplyClicked(self):
        '''
        应用当前设置到角色信息中
        '''
        self.applyButton.setVisible(False)
        CONTEXT.uiSignals.weaponBuildRequestChanged.emit()

    def getIsMoving(self) -> bool:
        '''
        获取角色是否移动
        '''
        return self.isMovingCheckBox.isChecked()
    
    def getIsInAir(self) -> bool:
        '''
        获取角色是否在空中
        '''
        return self.isInAirCheckBox.isChecked()
    
    def getCardSet(self) -> list[tuple[CardSet, int]]:
        '''
        获取当前选择的执行卡套装信息
        '''
        cardSetInfo = []
        for comboBox, spinBox, removeButton, hLayou in self.cardSetWidgets:
            cardSet = comboBox.currentData()
            count = spinBox.value()
            cardSetInfo.append( (cardSet, count) )
        return cardSetInfo
    
    def getSkillStrength(self) -> float:
        '''
        获取当前设置的技能强度
        '''
        return self.skillStrengthSpinBox.value()
    
class CardSlotCard(CardWidget):
    '''
    显示9个卡槽信息的组件
    '''
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('cardSlotCard')
        
        self.gridLayout = QHBoxLayout(self)
        self.gridLayout.setSpacing(10)

        self.cardSlots = []
        for i in range(9):
            cardSlot = CardSlot(i, i==8, self)
            self.gridLayout.addWidget(cardSlot)
            self.cardSlots.append(cardSlot)

        CONTEXT.uiSignals.cardSlotSelected.connect(self._onCardSlotSelected)
        CONTEXT.uiSignals.miniCardSelected.connect(self._onCardSelected)

    def _onCardSlotSelected(self, slotIndex: int):
        '''
        当卡槽被选中时调用此方法
        '''
        for i in range(9):
            self.cardSlots[i].setSelected(i == slotIndex)

    def _onCardSelected(self, card):
        '''
        当执行卡被选中时调用此方法
        '''
        selectedIndex = -1
        for i in range(9):
            if self.cardSlots[i].isSelected:
                selectedIndex = i
                break
        if selectedIndex != -1:
            self.cardSlots[selectedIndex].setCard(card)
            self.cardSlots[selectedIndex].setSelected(False)
            # 执行卡发生变化，触发DPS计算
            CONTEXT.uiSignals.weaponBuildRequestChanged.emit()

    def getCards(self) -> list[WeaponCardBase]:
        '''
        获取当前卡槽中的所有执行卡
        '''
        cards = []
        for cardSlot in self.cardSlots:
            # 要不要处理专属卡，暂不确定
            cards.append(cardSlot.card)
        return cards

class WeaponBuildPage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('weaponBuildPage')

        # 主布局
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(10, 10, 10, 10)
        self.mainLayout.setSpacing(10)

        # 上方布局
        self.topLayout = QHBoxLayout()
        self.topLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.setSpacing(10)

        # 左上方布局
        self.leftTopLayout = QVBoxLayout()
        self.leftTopLayout.setContentsMargins(0, 0, 0, 0)
        self.leftTopLayout.setSpacing(10)

        # 武器选择卡片
        self.weaponSelectCard = WeaponSelectCard(self)
        self.leftTopLayout.addWidget(self.weaponSelectCard)
        
        # 目标设置卡片
        self.targetSettingCard = TargetSettingCard(self)
        self.leftTopLayout.addWidget(self.targetSettingCard)

        # 角色设置卡片
        self.characterSettingCard = CharacterSettingCard(self)
        self.leftTopLayout.addWidget(self.characterSettingCard)

        # 卡槽显示卡片
        self.cardSlotCard = CardSlotCard(self)
        self.leftTopLayout.addWidget(self.cardSlotCard)

        self.topLayout.addLayout(self.leftTopLayout)
        
        # 武器属性卡片
        self.weaponPropertyCard = WeaponPropertyCard(self)
        self.topLayout.addWidget(self.weaponPropertyCard)

        self.mainLayout.addLayout(self.topLayout)
        # 卡片选择区域
        self.cardSelectArea = CardArea(self)
        self.mainLayout.addWidget(self.cardSelectArea)

        self.weaponSelectCard.afterInit()

        CONTEXT.uiSignals.weaponBuildRequestChanged.connect(self._onWeaponBuildRequestChanged)


    def _onWeaponBuildRequestChanged(self):
        '''
        当配卡请求发生变化时调用此方法，主要是构建并填充DPSRequest，然后发起计算
        '''
        weapon = self.weaponSelectCard.getWeapon()
        cards = self.cardSlotCard.getCards()
        dpsRequest = DPSRequest(weapon, cards)
        # 移动状态
        dpsRequest.moveState.isMoving = self.characterSettingCard.getIsMoving()
        dpsRequest.moveState.isInAir = self.characterSettingCard.getIsInAir()
        # 执行卡套装
        cardSets = self.characterSettingCard.getCardSet()
        for cardSet, count in cardSets:
            dpsRequest.cardSetInfo.setCardSetCount(cardSet, count)
        # 技能强度
        skillStrength = self.characterSettingCard.getSkillStrength()
        dpsRequest.characterInfo.setCharacterProperty(CharacterPropertyType.SkillStrength, skillStrength)
        # 靶标信息
        targetMaterial = self.targetSettingCard.getMaterial()
        armor = self.targetSettingCard.getArmor()
        dpsRequest.targetInfo.material = targetMaterial
        dpsRequest.targetInfo.armor = armor
        # 元素异常状态
        elementDeuffInfo = self.targetSettingCard.getElementDebuffInfo()
        for damageType, value in elementDeuffInfo:
            dpsRequest.targetInfo.addConstantElementDebuff(damageType, value)
        # 技能异常
        skillDebuffInfo = self.targetSettingCard.getSkillDebuff()
        for skillDebuff, value in skillDebuffInfo:
            dpsRequest.targetInfo.addSkillDebuff(skillDebuff, value)
        # 通知计算完成
        CONTEXT.triggerDpsCalculation(dpsRequest)


