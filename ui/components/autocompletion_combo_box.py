from PyQt5.QtWidgets import QCompleter
from PyQt5.QtCore import QStringListModel
from qfluentwidgets import EditableComboBox
from PyQt5.QtCore import Qt

class AutocompletionComboBox(EditableComboBox):
    """
    一个带有自动补全和搜索功能的组合框。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._string_list_model = QStringListModel(self)
        self._completer = QCompleter(self._string_list_model, self)
        self._completer.setFilterMode(Qt.MatchContains)
        self._completer.setMaxVisibleItems(10)
        self.setCompleter(self._completer)

        self.textChanged.connect(self._on_text_changed)
        self._completer.activated.connect(self.setCurrentText)

    def addItem(self, text: str, icon=None, userData=None):
        super().addItem(text, icon, userData)
        self._update_model()

    def addItems(self, texts):
        super().addItems(texts)
        self._update_model()

    def insertItem(self, index: int, text: str, icon=None, userData=None):
        super().insertItem(index, text, icon, userData)
        self._update_model()

    def insertItems(self, index: int, texts):
        super().insertItems(index, texts)
        self._update_model()

    def removeItem(self, index: int):
        super().removeItem(index)
        self._update_model()

    def clear(self):
        super().clear()
        self._update_model()

    def _update_model(self):
        """ 更新补全器的模型 """
        item_texts = [self.itemText(i) for i in range(self.count())]
        self._string_list_model.setStringList(item_texts)

    def _on_text_changed(self, text):
        """ 文本改变时，如果文本是来自补全项，则设置为当前项 """
        if text in self._string_list_model.stringList():
            self.setCurrentText(text)
