from PySide6.QtWidgets import (
    QApplication, QGraphicsView, QGraphicsScene,
    QVBoxLayout, QWidget, QFileDialog
)
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt, QTimer
from items import *
import sys


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

            item.input_field.setText(text)
            QTimer.singleShot(0, lambda: (
                item.input_field.setFocus(),
                item.input_field.setCursorPosition(len(text))
            ))

            event.accept()
            return

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_1: # type: ignore
            global_pos = QCursor.pos()
            view_pos = self.mapFromGlobal(global_pos)
            if self.viewport().rect().contains(view_pos):
                scene_pos = self.mapToScene(view_pos)
            else:
                scene_pos = self.mapToScene(self.viewport().rect().center())
            x = scene_pos.x()
            y = scene_pos.y()

            item = IntegrationItem(x, y)
            scene.addItem(item)

            scene.clearSelection()
            item.setSelected(True)

            item.input_field.setText(text)
            QTimer.singleShot(0, lambda: (
                item.input_field.setFocus(),
                item.input_field.setCursorPosition(len(text))
            ))

            event.accept()
            return
        
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_Equal: # type: ignore
            for item in ExpressionItem.instance_list:
                item.recalculate_all()
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
                for item in ExpressionItem.instance_list:
                    file.write(f'{item.save_file()}\n')
            event.accept()
            return

        #TODO Add full suport for saving integrals and diffs, currntly dosent support saving differentials, and params for ploting
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_O: # type: ignore
            objDict: dict = {"<class 'items.ExpressionItem'>": ExpressionItem,
                             "<class 'items.IntegrationItem'>": IntegrationItem,
                             "<class 'items.DifferentiationItem'>": DifferentiationItem,
                             "<class 'items.PlotItem'>": PlotItem}
            
            file_path, _ = QFileDialog.getOpenFileName(
                parent=window,
                caption="Save File",
                dir="",
                filter="YAMC Files (*.yamc);;Text Files (*.txt);;All Files (*)"
            )

            with open(file_path, 'r') as file:
                for line in file:
                    parts = line.split(';')
                    cls = objDict[parts[0]]
                    point_match = re.search(r'QPointF\(([\d\.\-]+), ([\d\.\-]+)\)', parts[1])
                    x, y = float(point_match.group(1)), float(point_match.group(2)) # type: ignore
                    obj: ExpressionItem = cls(x, y, parts[2], parts[3], parts[4], parts[5])
                    scene.addItem(obj)
                    obj._debounce.start()
                    obj.rearrange_item()
                    obj.insetr_expr()
            event.accept()
            return

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_W: # type: ignore
            item: ExpressionItem
            for item in ExpressionItem.instance_list[:]:
                type(item).instance_list.remove(item)
                try:
                    type(item).var_dict.pop(item.varName)
                except: pass

                scene = item.scene()
                if scene: scene.removeItem(item)

                if item.childItems():
                    for child in item.childItems():
                        del child
                    del item
            event.accept()
            return
    
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_2: # type: ignore
            global_pos = QCursor.pos()
            view_pos = self.mapFromGlobal(global_pos)
            if self.viewport().rect().contains(view_pos):
                scene_pos = self.mapToScene(view_pos)
            else:
                scene_pos = self.mapToScene(self.viewport().rect().center())
            x = scene_pos.x()
            y = scene_pos.y()

            item = DifferentiationItem(x, y)
            scene.addItem(item)

            scene.clearSelection()
            item.setSelected(True)

            item.input_field.setText(text)
            QTimer.singleShot(0, lambda: (
                item.input_field.setFocus(),
                item.input_field.setCursorPosition(len(text))
            ))

            event.accept()
            return

        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_3: # type: ignore
            global_pos = QCursor.pos()
            view_pos = self.mapFromGlobal(global_pos)
            if self.viewport().rect().contains(view_pos):
                scene_pos = self.mapToScene(view_pos)
            else:
                scene_pos = self.mapToScene(self.viewport().rect().center())
            x = scene_pos.x()
            y = scene_pos.y()

            item = PlotItem(x, y)
            scene.addItem(item)

            scene.clearSelection()
            item.setSelected(True)

            item.input_field.setText(text)
            QTimer.singleShot(0, lambda: (
                item.input_field.setFocus(),
                item.input_field.setCursorPosition(len(text))
            ))

            event.accept()
            return
        
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key.Key_Period: # type: ignore
            selection: list[ExpressionItem] = scene.selectedItems() #type: ignore
            for i in selection:
                if i.result_label.isVisible():
                    i.result_label.hide()
                    i.result_label.overwrite_visibility(False)
                else:
                    i.result_label.show()
                    i.result_label.overwrite_visibility(True)
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