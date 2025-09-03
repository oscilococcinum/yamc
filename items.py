from PySide6.QtWidgets import (
    QGraphicsTextItem, QGraphicsItem, QGraphicsRectItem,
    QLineEdit, QGraphicsProxyWidget,
)
from PySide6.QtGui import QBrush, QColor, QFontMetrics
from PySide6.QtCore import QTimer
import solve
import re

ITEM_W, ITEM_H = 220, 60

class AutoResizeLineEdit(QLineEdit):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.textChanged.connect(self.adjustSizeToText)
        self.adjustSizeToText()

    def adjustSizeToText(self):
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(self.text())
        # Add some padding
        self.setFixedWidth(text_width + 10)


class ExpressionItem(QGraphicsRectItem):
    instance_list = []
    var_dict: dict = {}

    def __init__(self, x, y):
        super().__init__(0, 0, 220, 30)
        type(self).instance_list.append(self)
        self.setPos(x, y)
        self.expr = ''
        self.result = ''
        self.varName = ''
        self.description = ''

        self.setBrush(QBrush(QColor(230, 230, 250)))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

        self.input_field = AutoResizeLineEdit()
        self.input_field.setPlaceholderText("Enter expression")
        self.input_field.setFrame(False)
        self.input_field.setWindowOpacity(80)

        self.result_label = QGraphicsTextItem("", self)

        self.QlineEditProxy = QGraphicsProxyWidget(self)
        self.QlineEditProxy.setWidget(self.input_field)
        self.QlineEditProxy.setPos(5, 5)

        self.input_field.returnPressed.connect(self.evaluate_expression)
        self.input_field.textChanged.connect(self.move_result_label)

        # NEW: Debounced live evaluation
        self._debounce = QTimer()
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(300)  # ms
        self._debounce.timeout.connect(self.evaluate_expression)
        self.input_field.textChanged.connect(self._on_text_changed)

    def move_result_label(self):
        fm = QFontMetrics(self.QlineEditProxy.font())
        text_width = fm.horizontalAdvance(self.input_field.text())
        self.result_label.setPos(text_width+25, 4)
        self.setRect(0, 0, text_width+20, 30)

    # Right-click → show the same context menu as QLineEdit, plus "Delete Item"
    def contextMenuEvent(self, event):
        # Ensure the text actions (undo/cut/copy/paste) apply to the line edit
        self.input_field.setFocus()
        # If click is over the edit, move caret near the click position
        try:
            wpos = self.input_field.mapFromGlobal(event.screenPos().toPoint())
            if self.input_field.rect().contains(wpos):
                if hasattr(self.input_field, "cursorPositionAt"):
                    self.input_field.setCursorPosition(self.input_field.cursorPositionAt(wpos))
        except Exception:
            pass

        # Build native-looking menu from the line edit, then append our action
        menu = self.input_field.createStandardContextMenu()
        menu.addSeparator()
        remove_action = menu.addAction("Delete Item")
        chosen = menu.exec(event.screenPos())
        if chosen == remove_action:
            # Cleanly detach embedded widget, then remove item from the scene
            try:
                if hasattr(self, "proxy") and self.QlineEditProxy and self.proxy.widget():
                    self.QlineEditProxy.widget().deleteLater()
                    self.QlineEditProxy.setWidget(None)
                    type(self).var_dict.pop(self.varName)
                    type(self).instance_list.remove(self)
            except Exception:
                pass
            scene = self.scene()
            if scene:
                scene.removeItem(self)
            event.accept()
            return
        # The standard actions already executed; consume the event
        event.accept()

    def _on_text_changed(self, _):
        # Skip if the user just cleared the field
        self._debounce.start()

    def evaluate_expression(self):
        expr_str = self.input_field.text().strip()
        if not expr_str:
            self.result_label.setPlainText("")
            return
        try:
            if re.search(r'=', expr_str):
                self.varName = expr_str.split('=')[0].strip()
                self.expr = expr_str.split('=')[1].strip()
                self.result = solve.generalEval(self.expr, type(self).var_dict)
                type(self).var_dict[self.varName] = self.result
            elif re.search(r'=.*#', expr_str):
                self.varName = expr_str.split('=')[0].strip()
                self.expr = expr_str.split('=')[1].strip().split('#')[0].strip()
                self.result = solve.generalEval(self.expr, type(self).var_dict)
                self.description = expr_str.split('=')[1].strip().split('#')[1].strip()
                type(self).var_dict[self.varName] = self.result
            else:
                self.result = solve.generalEval(expr_str, type(self).var_dict)
            self.result_label.setPlainText(f"= {self.result}")
#            self.var_name_label.setPlainText(f"{self.varName}")
        except Exception as e:
            self.result_label.setPlainText(f"Error: {str(e)}")