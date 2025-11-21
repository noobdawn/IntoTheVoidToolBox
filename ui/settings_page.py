import os
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QComboBox)
from qfluentwidgets import (ScrollArea, CardWidget, SubtitleLabel, BodyLabel, InfoBar, InfoBarPosition, SpinBox)
from qfluentwidgets import FluentIcon as FIF

from core.ivtcontext import CONTEXT
from core.ivtenum import SubWeaponType, SubWeaponTypeToString, SubWeaponTypeToMagazine

from .components.seamless_scroll_area import SeamlessScrollArea
from .components.foldable_card_widget import FoldableCardWidget

class UISettingsPage(FoldableCardWidget):

    def __init__(self, parent=None):
        super().__init__('界面设置', parent)
        self.setObjectName('uiSettingsPage')

        contentLayout = self.contentLayout()
        contentLayout.setSpacing(10)

        self.uiScaleLayout = QHBoxLayout()
        self.uiScaleLabel = BodyLabel("界面缩放:")
        self.uiScaleLayout.addWidget(self.uiScaleLabel)
        self.uiScaleComboBox = QComboBox()
        self.uiScaleComboBox.addItems(["50%", "75%", "100%", "125%", "150%"])
        self.uiScaleLayout.addWidget(self.uiScaleComboBox)

        contentLayout.addLayout(self.uiScaleLayout)

        currentScale = CONTEXT.getUiScale()
        if currentScale == 0.5:
            self.uiScaleComboBox.setCurrentText("50%")
        elif currentScale == 0.75:
            self.uiScaleComboBox.setCurrentText("75%")
        elif currentScale == 1.0:
            self.uiScaleComboBox.setCurrentText("100%")
        elif currentScale == 1.25:
            self.uiScaleComboBox.setCurrentText("125%")
        elif currentScale == 1.5:
            self.uiScaleComboBox.setCurrentText("150%")
        self.uiScaleComboBox.currentTextChanged.connect(self.onUIScaleChanged)


    def onUIScaleChanged(self, scale):
        # 浮动提示：需重启后才能生效
        # TODO
        InfoBar.success("界面缩放已更改", "请重启应用以应用新的界面缩放设置。", parent=self.window(), position=InfoBarPosition.TOP, duration=3000)
        if scale == "50%":
            CONTEXT.setUiScale(0.5)
        elif scale == "75%":
            CONTEXT.setUiScale(0.75)
        elif scale == "100%":
            CONTEXT.setUiScale(1.0)
        elif scale == "125%":
            CONTEXT.setUiScale(1.25)
        elif scale == "150%":
            CONTEXT.setUiScale(1.5)

class DPSSettingsPage(FoldableCardWidget):

    def __init__(self, parent=None):
        super().__init__('伤害计算', parent)
        self.setObjectName('dpsSettingsPage')

        contentLayout = self.contentLayout()
        contentLayout.setSpacing(10)

        self.equivalentLayout = QVBoxLayout()

        self.equivalentLabelLayout = QHBoxLayout()
        self.equivalentLabel = BodyLabel("弹匣容量等效")
        self.equivalentLabelLayout.addWidget(self.equivalentLabel)
        self.equivalentIcon = QLabel()
        self.equivalentIcon.setPixmap(FIF.INFO.icon().pixmap(16, 16))
        self.equivalentIcon.setToolTip("对于无弹药限制的武器类型，需设置其在DPS计算时的等效弹药容量")
        self.equivalentLabelLayout.addWidget(self.equivalentIcon)
        self.equivalentLayout.addLayout(self.equivalentLabelLayout)

        for subWeaponType in SubWeaponType:
            if subWeaponType == SubWeaponType.All:
                continue
            layout = QHBoxLayout()
            label = BodyLabel(f"{SubWeaponTypeToString[subWeaponType]}:")
            layout.addWidget(label)
            spinBox = SpinBox(self)
            spinBox.setRange(1, 200)
            value = CONTEXT.getSubWeaponTypeMagazine(subWeaponType)
            spinBox.setValue(value)
            spinBox.valueChanged.connect(lambda value, swt=subWeaponType: self.onEquivalentMagazineChanged(swt, value))
            layout.addWidget(spinBox)
            self.equivalentLayout.addLayout(layout)

        contentLayout.addLayout(self.equivalentLayout)

    def onEquivalentMagazineChanged(self, subWeaponType: SubWeaponType, magazine: int):
        CONTEXT.setSubWeaponTypeMagazine(subWeaponType, magazine)


class SettingsPage(QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('settingsPage')
        self.vBoxLayout = QVBoxLayout(self)

        self.scrollArea = SeamlessScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.DPSSettings = DPSSettingsPage(self)
        self.UISettings = UISettingsPage(self)

        self.containerWidget = QWidget()
        self.containerLayout = QVBoxLayout(self.containerWidget)
        self.containerLayout.setContentsMargins(10, 10, 10, 10)
        self.containerLayout.setSpacing(10)

        self.containerLayout.addWidget(self.UISettings)
        self.containerLayout.addWidget(self.DPSSettings)
        self.scrollArea.setWidget(self.containerWidget)
        self.vBoxLayout.addWidget(self.scrollArea)