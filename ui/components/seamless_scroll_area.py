from qfluentwidgets import ScrollArea


class SeamlessScrollArea(ScrollArea):
    """
    无痕滚动区域，移除边框和背景色
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # 启用透明背景，移除边框
        self.enableTransparentBackground()
        
        # 设置样式，确保内容区域也是透明的
        self.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollArea > QWidget {
                background: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background: transparent;
            }
        """)