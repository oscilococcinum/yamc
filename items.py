from PySide6.QtWidgets import (
    QGraphicsTextItem, QGraphicsItem, QGraphicsRectItem,
    QLineEdit, QGraphicsProxyWidget,
)
from PySide6.QtGui import QBrush, QColor
from PySide6.QtCore import QTimer
import solve
import re

ITEM_W, ITEM_H = 220, 60

class ExpressionItem(QGraphicsRectItem):
    instance_list = []
    var_dict: dict = {}

    def __init__(self, x, y, width=ITEM_W, height=ITEM_H):
        super().__init__(0, 0, width, height)
        type(self).instance_list.append(self)
        self.setPos(x, y)
        self.expr = ''
        self.result = ''
        self.varName = ''
        self.description = ''

        self.setBrush(QBrush(QColor(230, 230, 250)))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter expression")

        self.result_label = QGraphicsTextItem("", self)
        self.result_label.setPos(10, 35)

        self.var_name_label = QGraphicsTextItem("", self)
        self.var_name_label.setPos(10, 20)

        self.proxy = QGraphicsProxyWidget(self)
        self.proxy.setWidget(self.input_field)
        self.proxy.setPos(10, 5)

        self.input_field.returnPressed.connect(self.evaluate_expression)

        # NEW: Debounced live evaluation
        self._debounce = QTimer()
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(300)  # ms
        self._debounce.timeout.connect(self.evaluate_expression)
        self.input_field.textChanged.connect(self._on_text_changed)

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
                if hasattr(self, "proxy") and self.proxy and self.proxy.widget():
                    self.proxy.widget().deleteLater()
                    self.proxy.setWidget(None)
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
            self.var_name_label.setPlainText(f"{self.varName}")
        except Exception as e:
            self.result_label.setPlainText(f"Error: {str(e)}")