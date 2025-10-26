from PyQt5.QtCore import QObject, pyqtSignal
from pynput import keyboard
from .loader import load_cards, load_weapons, delete_riven_card

from .ivtdps import DPSRequest
from .ivtweapon import Weapon
from .ivtcard import WeaponCardRiven

class UISignals(QObject):
    '''
    全局UI使用的信号类
    '''
    weaponChanged = pyqtSignal(DPSRequest)
    deleteRivenCard = pyqtSignal(WeaponCardRiven)

class HotkeyListener(QObject):
    '''
    全局热键监听类
    '''
    homePressed = pyqtSignal()
    endPressed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.listener = keyboard.Listener(on_press=self.on_press)

    def on_press(self, key):
        if key == keyboard.Key.home:
            self.homePressed.emit()
        elif key == keyboard.Key.end:
            self.endPressed.emit()

    def start(self):
        self.listener.start()

    def stop(self):
        self.listener.stop()

class IVTContext:
    '''
    全局上下文类，保存全局状态和信号
    '''
    def __init__(self):
        self.uiSignals = UISignals()
        self.hotkeyListener = HotkeyListener()
        
        self.__allCards = load_cards()
        self.__allWeapons = load_weapons()


    def getAllCards(self):
        '''
        获取所有执行卡
        '''
        return self.__allCards
    
    def getAllWeapons(self):
        '''
        获取所有武器
        '''
        return self.__allWeapons
    
    def getWeaponByName(self, name: str):
        '''
        根据名称获取武器
        '''
        for weapon in self.__allWeapons:
            if weapon.name == name:
                return weapon
        return None
    
    def deleteRivenCard(self, card: WeaponCardRiven):
        '''
        删除混淆执行卡
        '''
        delete_riven_card(card)
        if card in self.__allCards['riven']:
            self.__allCards['riven'].remove(card)

CONTEXT = IVTContext()