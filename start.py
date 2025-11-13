import sys
from PyQt5.QtWidgets import QApplication, QSplashScreen
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


# QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

def main():
    app = QApplication(sys.argv)

    splash_pix = QPixmap('assets/splash/splash.jpg')
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.showMessage("正在启动...", Qt.AlignBottom | Qt.AlignCenter, Qt.white)
    splash.show()

    from ui.main_window import MainWindow
    main_window = MainWindow()
    splash.finish(main_window)
    main_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()