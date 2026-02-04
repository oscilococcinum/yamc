from PySide6.QtWidgets import QGraphicsTextItem

class QGraphicsTextLabel(QGraphicsTextItem):
    def __init__(self, text='', parent=None) -> None:
        super().__init__(text, parent)
        self.visibilityOverwriten: bool = False

    def overwriteVisibility(self, isOverwritten: bool) -> None:
        self.visibility_overwriten = isOverwritten