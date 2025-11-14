from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, 
                             QGridLayout, QSizePolicy)
from qfluentwidgets import (SubtitleLabel, CardWidget, ComboBox, SpinBox, CheckBox, 
                            PushButton, LineEdit, ScrollArea, TransparentToolButton,
                            MessageBox, StrongBodyLabel, InfoBar, InfoBarPosition, LineEdit)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt

from .components.value_edit import ValueEdit
from .components.riven_card_area import RivenCardArea
from .components.foldable_card_widget import FoldableCardWidget
from .components.autocompletion_combo_box import AutocompletionComboBox

from core.ivtcontext import CONTEXT
from core.ivtenum import (WeaponPropertyType, AvailableWeaponRivenProperties, WeaponRivenRange,
                          WeaponType, RivenRangeToString, WeaponRivenRangeParams, WeaponTypeToString, 
                          Slot, SlotToText)
from core.ivtcard import WeaponProperty, WeaponCardRiven, calculateRivenPropertyRange

class PropertyEditor(QWidget):
    """Widget for editing a single property."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(10)

        self.propertyTypeCombo = ComboBox(self)
        self.propertyValueEdit = ValueEdit(input_type='float', is_percentage=True, parent=self)
        self.removeButton = TransparentToolButton(FIF.REMOVE, self)

        self.layout.addWidget(StrongBodyLabel("属性:", self))
        self.layout.addWidget(self.propertyTypeCombo, 1)
        self.layout.addWidget(StrongBodyLabel("数值:", self))
        self.layout.addWidget(self.propertyValueEdit, 1)
        self.layout.addWidget(self.removeButton)

        self._initPropertyTypes()

    def _initPropertyTypes(self):
        for propType in AvailableWeaponRivenProperties:
            self.propertyTypeCombo.addItem(str(propType), userData=propType)

class RivenPage(QFrame):
    def __init__(self, context, parent=None):
        super().__init__(parent)
        self.context = context
        self.setObjectName('rivenPage')
        self.propertyEditors = []

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(10, 10, 10, 10)
        self.mainLayout.setSpacing(10)

        # Card 1: Basic Info
        self.basicInfoCard = FoldableCardWidget('基础信息', self)
        self.basicInfoLayout = self.basicInfoCard.contentLayout()
        
        self.nameLayout = QHBoxLayout()
        self.nameLabel = StrongBodyLabel('卡牌名称:', self)
        self.nameEdit = LineEdit(self)
        self.nameLayout.addWidget(self.nameLabel)
        self.nameLayout.addWidget(self.nameEdit)

        self.slotLayout = QHBoxLayout()
        self.slotLabel = StrongBodyLabel('极性:', self)
        self.slotCombo = ComboBox(self)
        self.slotLayout.addWidget(self.slotLabel)
        self.slotLayout.addWidget(self.slotCombo)

        self.weaponTypeLayout = QHBoxLayout()
        self.weaponTypeLabel = StrongBodyLabel('武器类型:', self)
        self.weaponCombo = AutocompletionComboBox()
        self.weaponTypeLayout.addWidget(self.weaponTypeLabel)
        self.weaponTypeLayout.addWidget(self.weaponCombo)

        self.rivenRangeLayout = QHBoxLayout()
        self.rivenRangeLabel = StrongBodyLabel('正负增益数量:', self)
        self.rivenRangeCombo = ComboBox(self)
        self.rivenRangeLayout.addWidget(self.rivenRangeLabel)
        self.rivenRangeLayout.addWidget(self.rivenRangeCombo)

        self.basicInfoLayout.addLayout(self.nameLayout)
        self.basicInfoLayout.addLayout(self.slotLayout)
        self.basicInfoLayout.addLayout(self.weaponTypeLayout)
        self.basicInfoLayout.addLayout(self.rivenRangeLayout)

        self.saveButton = PushButton(FIF.SAVE, '保存', self)
        self.basicInfoLayout.addWidget(self.saveButton, 0, Qt.AlignRight)

        # Card 2: Properties
        self.propertiesCard = FoldableCardWidget('属性', self)
        self.propertiesLayout = self.propertiesCard.contentLayout()
        self.addPropertyButton = PushButton(FIF.ADD, '添加属性', self)
        self.propertiesListLayout = QVBoxLayout()

        self.propertiesLayout.addLayout(self.propertiesListLayout)
        self.propertiesLayout.addWidget(self.addPropertyButton, 0)
        
        # Card 3: Card Area for preview
        self.cardArea = RivenCardArea(self)

        self.mainLayout.addWidget(self.basicInfoCard)
        self.mainLayout.addWidget(self.propertiesCard)
        self.mainLayout.addWidget(self.cardArea, 1) # Give it stretch factor

        self._initSlots()
        self._initWeaponTypes()
        self._initRivenRanges()
        self._initSignals()
        self.addPropertyEditor()
        self.addPropertyEditor()

    def _initRivenRanges(self):
        for rr in WeaponRivenRange:
            self.rivenRangeCombo.addItem(RivenRangeToString.get(rr, '未知'), userData=rr)
        self.rivenRangeCombo.setCurrentText(RivenRangeToString.get(WeaponRivenRange.PP))

    def _initWeaponTypes(self):
        allWeapons = CONTEXT.getAllWeapons()
        weaponNames = [weapon.name for weapon in allWeapons]
        self.weaponCombo.addItems(weaponNames)           
            

    def _initSlots(self):
        for slot in Slot:
            self.slotCombo.addItem(SlotToText.get(slot.value, '未知'), userData=slot)

    def _initSignals(self):
        self.addPropertyButton.clicked.connect(self.addPropertyEditor)
        self.saveButton.clicked.connect(self._saveCard)
        self.weaponCombo.currentIndexChanged.connect(self.recalculatePropertyRange)
        self.rivenRangeCombo.currentIndexChanged.connect(self.recalculatePropertyRange)

    def _saveCard(self):
        cardName = self.nameEdit.text()
        if not cardName:
            InfoBar.error('错误', '卡牌名称不能为空!', parent=self.window(), position=InfoBarPosition.TOP, duration=3000)
            return
        
        if CONTEXT.getCardByName(cardName):
            InfoBar.error('错误', f'卡牌名称 {cardName} 已存在，请使用不同的名称!', parent=self.window(), position=InfoBarPosition.TOP, duration=3000)
            return

        properties = []
        for editor in self.propertyEditors:
            propType = editor.propertyTypeCombo.currentData()
            propValueStr = editor.propertyValueEdit.text()
            
            if not propValueStr:
                InfoBar.error('错误', f'属性 {propType} 的数值不能为空!', parent=self.window(), position=InfoBarPosition.TOP, duration=3000)
                return
            
            try:
                propValue = float(propValueStr)
                properties.append(WeaponProperty.createModProperty(propType, propValue))
            except ValueError:
                InfoBar.error('错误', f'属性 {propType} 的数值无效!', parent=self.window(), position=InfoBarPosition.TOP, duration=3000)
                return

        if not properties:
            InfoBar.error('错误', '至少需要一个属性!', parent=self.window(), position=InfoBarPosition.TOP, duration=3000)
            return

        slot = self.slotCombo.currentData()
        weaponBaseName = self.weaponCombo.currentText()

        # 创建 CardRiven 对象
        newRivenCard = WeaponCardRiven(
            name=cardName,
            properties=properties,
            cost=15,
            slot=slot,
            weaponName=weaponBaseName
        )

        # 使用 data.cards 中的函数保存
        if CONTEXT.saveRivenCard(newRivenCard):
            InfoBar.success('成功', f'紫卡 {cardName} 已保存!', parent=self.window(), position=InfoBarPosition.TOP, duration=3000)
            # 触发 cardChanged 信号刷新卡牌区域
            CONTEXT.uiSignals.rivenCardChanged.emit(newRivenCard)
            # 清空输入
            self.nameEdit.clear()
            self.slotCombo.setCurrentIndex(0)
            self.weaponCombo.setCurrentText(WeaponTypeToString.get(WeaponType.Rifle))
            # 移除所有属性编辑器并添加一个默认的
            for editor in self.propertyEditors[:]:
                self.removePropertyEditor(editor)
            self.addPropertyEditor()
        else:
            InfoBar.error('保存失败', '保存紫卡时发生未知错误。', parent=self.window(), position=InfoBarPosition.TOP, duration=5000)

    def addPropertyEditor(self):
        if len(self.propertyEditors) >= 4:
            return
        
        editor = PropertyEditor(self)
        editor.removeButton.clicked.connect(lambda: self.removePropertyEditor(editor))
        editor.propertyTypeCombo.currentIndexChanged.connect(self.recalculatePropertyRange)
        self.propertiesListLayout.addWidget(editor)
        self.propertyEditors.append(editor)
        self.updateButtonsState()
        self.recalculatePropertyRange()

    def removePropertyEditor(self, editor):
        if len(self.propertyEditors) <= 1:
            return

        self.propertiesListLayout.removeWidget(editor)
        editor.deleteLater()
        self.propertyEditors.remove(editor)
        self.updateButtonsState()

    def updateButtonsState(self):
        self.addPropertyButton.setEnabled(len(self.propertyEditors) < 4)
        for editor in self.propertyEditors:
            editor.removeButton.setEnabled(len(self.propertyEditors) > 2)

    def recalculatePropertyRange(self):
        weaponBaseName = self.weaponCombo.currentText()
        weapon = CONTEXT.getWeaponByName(weaponBaseName)
        rivenRange = self.rivenRangeCombo.currentData()
        for editor in self.propertyEditors:
            propType = editor.propertyTypeCombo.currentData()
            if propType:
                minVal, maxVal = calculateRivenPropertyRange(propType, weapon.weaponType, rivenRange)
                editor.propertyValueEdit.setThreshold((minVal, maxVal))
