from PySide6.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene,
    QVBoxLayout, QWidget, QFileDialog
)
from PySide6.QtGui import QCursor, QBrush, QColor
from PySide6.QtCore import Qt, QTimer
from solve import Evaluate
from items import ExpressionItem
import sys
import re


class View(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus) # type: ignore
        self.setSceneRect(0, 0, 720, 1280)

    def keyPressEvent(self, event):
        scene = self.scene()
        text = event.text()
        modifiers = event.modifiers()
        has_ctrl_alt_meta = bool(modifiers & (Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier))  # type: ignore

        if text and text.isprintable() and not has_ctrl_alt_meta and not scene.focusItem():
            global_pos = QCursor.pos()
            view_pos = self.mapFromGlobal(global_pos)
            if self.viewport().rect().contains(view_pos):
                scene_pos = self.mapToScene(view_pos)
            else:
                scene_pos = self.mapToScene(self.viewport().rect().center())
            x = scene_pos.x()
            y = scene_pos.y()
            item = ExpressionItem(x, y)
            scene.addItem(item)
            scene.clearSelection()
            item.setSelected(True)
            item.inputField.setText(text)
            QTimer.singleShot(0, lambda: (
                item.inputField.setFocus(),
                item.inputField.setCursorPosition(len(text))
            ))
            event.accept()
            return

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Equal: # type: ignore
            for item in ExpressionItem.instanceList:
                item.recalculateAll()
            event.accept()
            return

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_S: # type: ignore

            file_path, _ = QFileDialog.getSaveFileName(
                parent=window,
                caption="Save File",
                dir="",
                filter="YAMC Files (*.yamc);;Text Files (*.txt);;All Files (*)"
            )
            with open(file_path, 'w') as file:
                for item in ExpressionItem.instanceList:
                    file.write(f'{item.saveFile()}\n')
            event.accept()
            return

        #TODO Add full suport for saving integrals and diffs, currntly dosent support saving differentials, and params for ploting
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_O: # type: ignore
            objDict: dict = {"<class 'items.ExpressionItem'>": ExpressionItem}

            file_path, _ = QFileDialog.getOpenFileName(
                parent=window,
                caption="Save File",
                dir="",
                filter="YAMC Files (*.yamc);;Text Files (*.txt);;All Files (*)"
            )

            with open(file_path, 'r') as file:
                for line in file:
                    parts = line.split(';')
                    parts = [x.replace('\n', '') for x in parts]
                    cls = objDict[parts[0]]
                    point_match = re.search(r'QPointF\(([\d\.\-]+), ([\d\.\-]+)\)', parts[1])
                    x, y = float(point_match.group(1)), float(point_match.group(2)) # type: ignore
                    obj: ExpressionItem = cls(x, y, parts[2], parts[3], parts[4], parts[5] ,parts[6] ,bool(parts[7]) )
                    scene.addItem(obj)
                    obj._debounce.start()
                    obj.rearrangeItem()
                    obj.insetrExpr()
            event.accept()
            return

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_W: # type: ignore
            item: ExpressionItem
            for item in ExpressionItem.instanceList[:]:
                type(item).instanceList.remove(item)
                try:
                    Evaluate.varDict.pop(item.varName)
                except: pass

                scene = item.scene()
                if scene: scene.removeItem(item)

                if item.childItems():
                    for child in item.childItems():
                        del child
                    del item
            event.accept()
            return

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key.Key_Period: # type: ignore
            selection: list[ExpressionItem] = scene.selectedItems() #type: ignore
            for i in selection:
                if i.resultLabel.isVisible():
                    i.resultLabel.hide()
                    i.resultLabel.overwriteVisibility(False)
                else:
                    i.resultLabel.show()
                    i.resultLabel.overwriteVisibility(True)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mainWindow()
    window.show()
    sys.exit(app.exec())
