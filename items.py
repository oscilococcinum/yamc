from PySide6.QtWidgets import (
    QGraphicsSceneContextMenuEvent, QGraphicsTextItem, QGraphicsItem, QGraphicsRectItem,
    QLineEdit, QGraphicsProxyWidget, QGraphicsScene
)
from PySide6.QtGui import QBrush, QColor, QFocusEvent, QFontMetrics, Qt
from PySide6.QtCore import QTimer, Signal
from solve import Evaluate
from ploting import *
from matplotlib import cm

class QGraphicsTextLabel(QGraphicsTextItem):
    def __init__(self, text='', parent=None) -> None:
        super().__init__(text, parent)
        self.visibilityOverwriten: bool = False

    def overwriteVisibility(self, isOverwritten: bool) -> None:
        self.visibility_overwriten = isOverwritten

class AutoResizeLineEdit(QLineEdit):
    focused: Signal = Signal()
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

        

class ExpressionItem(QGraphicsRectItem):
    instanceList: list = []
    def __init__(self, x, y, expr='', result='', varName='', desc=''):
        super().__init__(0, 0, 220, 30)
        type(self).instanceList.append(self)
        self.setPos(x, y)
        self.expr = expr
        self.result = result
        self.lastVarName = ''
        self.varName = varName
        self.description = desc

        self.setBrush(QBrush(QColor(0, 0, 0, 0)))
        self.setPen(Qt.NoPen) # type: ignore
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable) # type: ignore

        self.inputField = AutoResizeLineEdit('', self)
        self.inputField.setPlaceholderText("Enter expression")
        self.inputField.setFrame(False)

        self.resultLabel = QGraphicsTextLabel("", self)
        self.resultLabel.setTextInteractionFlags(Qt.TextSelectableByMouse) # type: ignore

        self.inputFieldProxy = QGraphicsProxyWidget(self)
        self.inputFieldProxy.setWidget(self.inputField)
        self.inputFieldProxy.setPos(5, 5)

        self.inputField.returnPressed.connect(self.evaluateExpression)
        self.inputField.textChanged.connect(self.moveResultLabel)

        self.plot: (QGraphicsProxyWidget | None) = None
        self.plotProxy = QGraphicsProxyWidget(self)
        self.plotProxy.setFlags(QGraphicsItem.GraphicsItemFlag.ItemStacksBehindParent)

        self._debounce = QTimer()
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(300)  # ms
        self._debounce.timeout.connect(self.evaluateExpression)
        self.inputField.textChanged.connect(self._onTextChanged)
        
    def moveResultLabel(self):
        fm = QFontMetrics(self.inputFieldProxy.font())
        text_width = fm.horizontalAdvance(self.inputField.text())
        self.resultLabel.setPos(text_width+8, 2)
        self.setRect(0, 0, text_width+10, 30)

    def rearrangeItem(self):
        self.moveResultLabel()

    def insetrExpr(self):
        if self.varName:
            self.inputField.setText(f'{self.varName}={self.expr}')
        else:
            self.inputField.setText(f'{self.expr}')

    def contextMenuEvent(self, event: QGraphicsSceneContextMenuEvent) -> None:
        menu = self.inputField.createStandardContextMenu()
        menu.addSeparator()
        removeAction = menu.addAction("Delete Item")
        chosen = menu.exec(event.screenPos())
        if chosen == removeAction:
            try:
                if hasattr(self, "inputFieldProxy"):
                    type(self).instanceList.remove(self)
                    Evaluate.varDict.pop(self.varName)

                    self.inputFieldProxy.setWidget(None) # type: ignore
                    self.inputFieldProxy.widget().deleteLater()
            except Exception:
                pass

            scene = self.scene()
            if scene: scene.removeItem(self)
            event.accept()
            return

        return super().contextMenuEvent(event)

    def _onTextChanged(self, _):
        self._debounce.start()

    def evaluateExpression(self):
        expr_str = self.inputField.text().strip()
        if not expr_str:
            self.resultLabel.setPlainText("")
            return
        try:
            self.expr = expr_str.strip()
            evaluator = Evaluate(self.expr)
            self.result = evaluator.result
            self.varName = evaluator.varName
            self.itemType = evaluator.type
            self.resultLabel.setPlainText(f"= {self.result}")
            if evaluator.type == 'plotting2D':
                if self.plotProxy.isVisible():
                    self.plotProxy.hide()
                self.setup2DPlotter(evaluator)
                self.resultLabel.hide()
                self.resultLabel.overwriteVisibility(True)
            elif evaluator.type == 'plotting3D':
                if self.plotProxy.isVisible():
                    self.plotProxy.hide()
                self.setup3DPlotter(evaluator)
                self.resultLabel.hide()
                self.resultLabel.overwriteVisibility(True)
            else:
                if self.plot and self.plotProxy:
                    self.plotProxy.hide()
                self.resultLabel.show()
                self.resultLabel.overwriteVisibility(False)
        except Exception as e:
            self.resultLabel.setPlainText(f"Error: {str(e)}")

    def saveFile(self) -> str:
        stream = f'{type(self)};{self.pos()};{self.expr};{self.result};{self.varName};{self.description}'
        stream = stream.replace('\n', '')
        return stream

    def varNameExists(self):
        pass

    def setup2DPlotter(self, evaluator: Evaluate) -> None:
        self.plotProxy.show()
        self.plot = plotWidget(self, plotType=evaluator.type)
        self.plot.axes.cla()
        self.plot.axes.plot(evaluator.additionalData['X'], evaluator.result)
        self.plot.draw_idle()
        self.plotProxy.setWidget(self.plot)
        self.plotProxy.setPos(-60, -17)

    def setup3DPlotter(self, evaluator: Evaluate) -> None:
        self.plotProxy.show()
        self.plot = plotWidget(self, plotType=evaluator.type)
        self.plot.axes.cla()
        self.plot.axes.plot_surface(evaluator.additionalData['X'], evaluator.additionalData['Y'], evaluator.result, cmap=cm.magma) #type: ignore
        self.plot.draw_idle()
        self.plotProxy.setWidget(self.plot)
        self.plotProxy.setPos(-60, -17)

    def recalculateAll(self):
        self.evaluateExpression()