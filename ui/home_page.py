import os
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QWidget
from qfluentwidgets import ScrollArea, CardWidget, SubtitleLabel, BodyLabel


class HomePage(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('homePage')
        self.vBoxLayout = QVBoxLayout(self)

        self.banner = QLabel(self)
        self.banner.setScaledContents(True)
        self.banner.setMaximumSize(800, 300)
        self.banner.setObjectName('banner')

        self.image_paths = self._load_image_paths('assets/images')
        self.current_image_index = 0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.next_image)

        self._init_layout()
        self._init_cards()

        if self.image_paths:
            self.timer.start(3000)  # Change image every 3 seconds
            self.next_image()

    def _load_image_paths(self, directory):
        paths = []
        if os.path.exists(directory):
            for file_name in os.listdir(directory):
                if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    paths.append(os.path.join(directory, file_name))
        return paths

    def next_image(self):
        if not self.image_paths:
            self.banner.setText("请在 assets/images 目录下添加图片")
            self.banner.setAlignment(Qt.AlignCenter)
            return

        pixmap = QPixmap(self.image_paths[self.current_image_index])
        self.banner.setPixmap(pixmap)
        self.current_image_index = (self.current_image_index + 1) % len(self.image_paths)

    def _init_layout(self):
        # self.vBoxLayout.setContentsMargins(36, 20, 36, 20)
        self.vBoxLayout.setSpacing(10)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.addWidget(self.banner)

    def _init_cards(self):
        # Combined info card
        info_card = CardWidget()
        info_card.setLayout(QVBoxLayout())
        info_card.layout().setContentsMargins(20, 10, 20, 10)
        info_card.layout().setSpacing(10)

        # Usage
        info_card.layout().addWidget(SubtitleLabel("使用方法"))
        info_card.layout().addWidget(BodyLabel(
            "1. 在自制混淆执行卡页面添加自定义的混淆执行卡。\n"
            "2. 在武器配卡页面选择武器，设置靶标和角色等环境因素。\n"
            "3. 下方即可预览每张执行卡在当前配装下的增幅效果。\n"
            "4. 选择不同的DPS统计方法进行比较，并装配执行卡查看最终伤害组成。\n"
        ))

        # Author
        info_card.layout().addWidget(SubtitleLabel("作者"))
        info_card.layout().addWidget(BodyLabel("noobdawn"))

        # GitHub
        info_card.layout().addWidget(SubtitleLabel("GitHub"))
        github_label = BodyLabel('<a href="https://github.com/noobdawn/IntoTheVoidToolBox">https://github.com/noobdawn/IntoTheVoidToolBox</a>')
        github_label.setOpenExternalLinks(True)
        info_card.layout().addWidget(github_label)

        self.vBoxLayout.addWidget(info_card)
