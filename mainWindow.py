from PySide6.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene,
    QVBoxLayout, QWidget
)
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt, QTimer
from items import *
import sys

ITEM_W, ITEM_H = 220, 60

class View(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus) # type: ignore
        self.setSceneRect(0, 0, 720, 1280)
    
    ### Keyboard key press event
    def keyPressEvent(self, event):
        focus_w = QApplication.focusWidget()
        if isinstance(focus_w, QLineEdit):
            super().keyPressEvent(event)
            return

        scene = self.scene()
        if scene and scene.selectedItems():
            super().keyPressEvent(event)
            return

        text = event.text()
        modifiers = event.modifiers()
        has_ctrl_alt_meta = bool(modifiers & (Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier))  # type: ignore

        if text and text.isprintable() and not has_ctrl_alt_meta:
            # Create a new item at the current mouse cursor position (scene coords)
            global_pos = QCursor.pos()
            view_pos = self.mapFromGlobal(global_pos)
            if self.viewport().rect().contains(view_pos):
                scene_pos = self.mapToScene(view_pos)
            else:
                # Fallback to view center if cursor is outside the view
                scene_pos = self.mapToScene(self.viewport().rect().center())
            x = scene_pos.x() - ITEM_W / 2
            y = scene_pos.y() - ITEM_H / 2


            item = ExpressionItem(x, y)
            scene.addItem(item)

            # Highlight/select the new item
            scene.clearSelection()
            item.setSelected(True)

            # Seed char and focus the editor (ensure caret is active)
            item.input_field.setText(text)
            # Defer focus to next event loop to ensure proxy is fully realized
            QTimer.singleShot(0, lambda: (
                item.input_field.setFocus(),
                item.input_field.setCursorPosition(len(text))
            ))

            event.accept()
            return

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_1: # type: ignore
            # Create a new item at the current mouse cursor position (scene coords)
            global_pos = QCursor.pos()
            view_pos = self.mapFromGlobal(global_pos)
            if self.viewport().rect().contains(view_pos):
                scene_pos = self.mapToScene(view_pos)
            else:
                # Fallback to view center if cursor is outside the view
                scene_pos = self.mapToScene(self.viewport().rect().center())
            x = scene_pos.x() - ITEM_W / 2
            y = scene_pos.y() - ITEM_H / 2


            item = IntegrationItem(x, y)
            scene.addItem(item)

            # Highlight/select the new item
            scene.clearSelection()
            item.setSelected(True)

            # Seed char and focus the editor (ensure caret is active)
            item.input_field.setText(text)
            # Defer focus to next event loop to ensure proxy is fully realized
            QTimer.singleShot(0, lambda: (
                item.input_field.setFocus(),
                item.input_field.setCursorPosition(len(text))
            ))

            event.accept()
            return
        
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Equal: # type: ignore
            ExpressionItem.recalculate_all()
            event.accept()
            return

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_2: # type: ignore
            # Create a new item at the current mouse cursor position (scene coords)
            global_pos = QCursor.pos()
            view_pos = self.mapFromGlobal(global_pos)
            if self.viewport().rect().contains(view_pos):
                scene_pos = self.mapToScene(view_pos)
            else:
                # Fallback to view center if cursor is outside the view
                scene_pos = self.mapToScene(self.viewport().rect().center())
            x = scene_pos.x() - ITEM_W / 2
            y = scene_pos.y() - ITEM_H / 2


            item = DifferentiationItem(x, y)
            scene.addItem(item)

            # Highlight/select the new item
            scene.clearSelection()
            item.setSelected(True)

            # Seed char and focus the editor (ensure caret is active)
            item.input_field.setText(text)
            # Defer focus to next event loop to ensure proxy is fully realized
            QTimer.singleShot(0, lambda: (
                item.input_field.setFocus(),
                item.input_field.setCursorPosition(len(text))
            ))

            event.accept()
            return

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_3: # type: ignore
            # Create a new item at the current mouse cursor position (scene coords)
            global_pos = QCursor.pos()
            view_pos = self.mapFromGlobal(global_pos)
            if self.viewport().rect().contains(view_pos):
                scene_pos = self.mapToScene(view_pos)
            else:
                # Fallback to view center if cursor is outside the view
                scene_pos = self.mapToScene(self.viewport().rect().center())
            x = scene_pos.x() - ITEM_W / 2
            y = scene_pos.y() - ITEM_H / 2


            item = PlotItem(x, y)
            scene.addItem(item)

            # Highlight/select the new item
            scene.clearSelection()
            item.setSelected(True)

            # Seed char and focus the editor (ensure caret is active)
            item.input_field.setText(text)
            # Defer focus to next event loop to ensure proxy is fully realized
            QTimer.singleShot(0, lambda: (
                item.input_field.setFocus(),
                item.input_field.setCursorPosition(len(text))
            ))

            event.accept()
            return
        super().keyPressEvent(event)


class mainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("yamc")
        self.setGeometry(0, 0, 1024, 768)

        layout = QVBoxLayout(self)

        self.view = View()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout.addWidget(self.view)

    def add_expression_item(self, x=50, y=50, seed_text=""):
        item = ExpressionItem(x, y)
        self.scene.addItem(item)
        # Highlight and focus when adding programmatically as well
        self.scene.clearSelection()
        item.setSelected(True)
        if seed_text:
            item.input_field.setText(seed_text)
        QTimer.singleShot(0, lambda: (
            item.input_field.setFocus(),
            item.input_field.setCursorPosition(len(item.input_field.text()))
        ))
        return item


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mainWindow()
    window.show()
    sys.exit(app.exec())