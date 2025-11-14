from qfluentwidgets import FluentWindow, SubtitleLabel, setFont, NavigationItemPosition
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QApplication

from ui.home_page import HomePage
from ui.weapon_build_page import WeaponBuildPage
from ui.edit_riven_page import RivenPage
# from ui.config_page import ConfigPage

class MainWindow(FluentWindow):
    """
    主窗口
    """
    def __init__(self):
        super().__init__()

        self.setObjectName("mainWindow")
        self.setWindowTitle("《驱入虚空》工具箱")
        self.setWindowIcon(QIcon('assets/ico/intothevoid.ico'))
        self.resize(900, 600)

        # 在这里可以添加更多的UI组件和逻辑
        self.home_page = HomePage(self)
        self.weapon_build_page = WeaponBuildPage(self)
        self.edit_riven_page = RivenPage(self)
        # self.config_page = ConfigPage(self)

        self.home_page.setObjectName("homePage")
        self.weapon_build_page.setObjectName("weaponBuildPage")
        self.edit_riven_page.setObjectName("editRivenPage")
        # self.config_page.setObjectName("configPage")
        
        self.addSubInterface(self.home_page, FIF.HOME, "首页", position=NavigationItemPosition.TOP)
        self.addSubInterface(self.weapon_build_page, FIF.DEVELOPER_TOOLS, "武器配卡", position=NavigationItemPosition.TOP)
        self.addSubInterface(self.edit_riven_page, FIF.EDIT, "混淆执行卡", position=NavigationItemPosition.TOP)
        # self.addSubInterface(self.config_page, FIF.SETTING, "设置", position=NavigationItemPosition.BOTTOM)



    def show(self):
        return super().show()