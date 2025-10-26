from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget)
from qfluentwidgets import SubtitleLabel, CardWidget, ComboBox, SpinBox, CheckBox, PushButton
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt

from ui.components.autocompletion_combo_box import AutocompletionComboBox
from ui.components.foldable_card_widget import FoldableCardWidget
from ui.components.card_area import CardArea

from core.ivtcontext import CONTEXT
from core.ivtenum import (WeaponPropertyType, EnemyMaterial, DamageType, SkillDebuff)
from core.ivtdps import DPSRequest

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
            request = DPSRequest(weapon, [])
            CONTEXT.uiSignals.weaponChanged.emit(request)

    def afterInit(self):
        '''
        当所有组件都初始化、注册完成后再调用此方法刷新
        '''
        self.onWeaponChanged(self.weaponSelectComboBox.currentText())

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

        self.propertyLayout = QVBoxLayout()
        self.contentLayout.addLayout(self.propertyLayout)
        self.contentLayout.addStretch(1)

        self.setFixedWidth(400)
        self.propertyLabels = {}

        signals = CONTEXT.uiSignals
        signals.weaponChanged.connect(self._updateLabels)

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
        当武器变化或者属性变化时，更新所有属性标签
        '''
        # 清空现有标签
        for i in reversed(range(self.propertyLayout.count())):
            widgetToRemove = self.propertyLayout.itemAt(i).widget()
            if widgetToRemove is not None:
                widgetToRemove.setParent(None)
        self.propertyLabels.clear()

        weapon = request.weapon

        self._addPropertyLabel('首发暴击伤害', 0, tooltip='若暴击率超过100%则为下一等级暴击伤害')
        self._addPropertyLabel('首发非暴击伤害', 1, tooltip='若暴击率超过100%则为原等级暴击伤害')
        self._addPropertyLabel('单次爆发伤害量', 0, tooltip='单个弹匣造成的总伤害')
        self._addPropertyLabel('单次爆发DPS', 0, tooltip='单个弹匣造成的每秒伤害')
        self._addPropertyLabel('平均DPS', 0, tooltip='计入换弹时间后的每秒伤害')

        damage = weapon.snapshot.getTotalDamageArray().sum()
        self._addPropertyLabel('面板总伤害', damage, tooltip='武器面板伤害，计入魈鬼系列卡牌的元素转化')

        for weaponPropType in WeaponPropertyType:
            value = weapon.snapshot.getPropertyValue(weaponPropType)
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
        self.materialComboBox.currentIndexChanged.connect(self.onTargetSettingChanged)

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
        self.armorSpinBox.valueChanged.connect(self.onTargetSettingChanged)

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
            checkbox.stateChanged.connect(self.onTargetSettingChanged)
            layout.addWidget(checkbox)
            layout.addStretch(1)
            layout.addWidget(spinbox)
            self.debuffLayout.addLayout(layout)
            self.debuffWidgets[damageType] = (checkbox, spinbox)
            spinbox.valueChanged.connect(self.onTargetSettingChanged)

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
            checkbox.stateChanged.connect(self.onTargetSettingChanged)

        contentLayout.addLayout(self.skillDebuffLayout)

        self.applyButton = PushButton(FIF.SAVE,'应用', self)
        self.applyButton.clicked.connect(self.onApplyClicked)

        contentLayout.addWidget(self.applyButton, alignment=Qt.AlignRight)

    def onApplyClicked(self):
        '''
        应用当前设置到靶标信息中
        '''
        # 隐藏应用按钮
        self.applyButton.setVisible(False)

    def onTargetSettingChanged(self):
        '''
        当靶标设置改变时调用此方法
        '''
        self.applyButton.setVisible(True)

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
        self.isMovingCheckBox.stateChanged.connect(self.onCharacterSettingChanged)
        self.isInAirLayout = QHBoxLayout()
        self.isInAirLabel = QLabel("空中")
        self.isInAirCheckBox = CheckBox()
        self.isInAirLayout.addWidget(self.isInAirLabel)
        self.isInAirLayout.addStretch(1)
        self.isInAirLayout.addWidget(self.isInAirCheckBox)
        contentLayout.addLayout(self.isInAirLayout)
        self.isInAirCheckBox.stateChanged.connect(self.onCharacterSettingChanged)

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
        self.skillStrengthSpinBox.valueChanged.connect(self.onCharacterSettingChanged)

        self.applyButton = PushButton(FIF.SAVE,'应用', self)
        self.applyButton.clicked.connect(self.onApplyClicked)
        contentLayout.addWidget(self.applyButton, alignment=Qt.AlignRight)



    def onCharacterSettingChanged(self):
        '''
        当角色设置改变时调用此方法
        '''
        self.applyButton.setVisible(True)
        pass

    def onApplyClicked(self):
        '''
        应用当前设置到角色信息中
        '''
        self.applyButton.setVisible(False)
        pass

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

        self.topLayout.addLayout(self.leftTopLayout)
        
        # 武器属性卡片
        self.weaponPropertyCard = WeaponPropertyCard(self)
        self.topLayout.addWidget(self.weaponPropertyCard)

        self.mainLayout.addLayout(self.topLayout)
        # 卡片选择区域
        self.cardSelectArea = CardArea(self)
        self.mainLayout.addWidget(self.cardSelectArea)

        self.weaponSelectCard.afterInit()
