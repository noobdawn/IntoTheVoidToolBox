from PyQt5.QtCore import QObject, pyqtSignal
from pynput import keyboard
from .loader import load_cards

class UISignals(QObject):
    '''
    全局UI使用的信号类
    '''
    weaponChanged = pyqtSignal()
    weaponCardChanged = pyqtSignal()

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


    def getAllCards(self):
        '''
        获取所有执行卡
        '''
        return self.__allCards

