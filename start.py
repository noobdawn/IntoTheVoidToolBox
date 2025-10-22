import sys
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

def main():
    from core.ivtproperty import WeaponPropertySnapshot

    s0 = WeaponPropertySnapshot([], False)
    import copy
    s1 = copy.deepcopy(s0)
    s1.test()
    s0.print()
    s1.print()

    pass

if __name__ == "__main__":
    main()