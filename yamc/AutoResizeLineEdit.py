from PySide6.QtWidgets import QGraphicsItem, QLineEdit, QGraphicsScene
from PySide6.QtGui import  QFocusEvent, QFontMetrics
from PySide6.QtCore import Signal


class AutoResizeLineEdit(QLineEdit):
    focused: Signal = Signal()
    unfocused: Signal = Signal()
    def __init__(self, text="", gparent=None):
        super().__init__(text)
        self.gparent: (QGraphicsItem | None) = gparent
        self.setStyleSheet("""
            AutoResizeLineEdit {
                background: rgba(255, 255, 255, 0);  /* semi-transparent white */
                color: black;  /* fully visible text */
                border: 0px solid gray;
            }
        """)

        self.adjustSizeToText()
        self.textChanged.connect(self.adjustSizeToText)
        self.focused.connect(self.selectParent)

    def adjustSizeToText(self):
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(self.text())
        self.setFixedWidth(text_width + 10)

    def selectParent(self):
        if self.gparent:
            scene: QGraphicsScene = self.gparent.scene()
            scene.clearSelection()
            self.gparent.setSelected(True)
        else: pass

    def focusInEvent(self, event: QFocusEvent) -> None:
        super().focusInEvent(event)
        self.focused.emit()

    def focusOutEvent(self, event: QFocusEvent) -> None:
        super().focusOutEvent(event)
        self.unfocused.emit()