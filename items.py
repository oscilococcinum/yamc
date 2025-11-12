from PySide6.QtWidgets import (
    QGraphicsSceneContextMenuEvent, QGraphicsTextItem, QGraphicsItem, QGraphicsRectItem,
    QLineEdit, QGraphicsProxyWidget, QGraphicsScene
)
from PySide6.QtGui import QBrush, QColor, QFocusEvent, QFontMetrics, QAction, Qt
from PySide6.QtCore import QTimer, QSizeF, Signal
from latex import LatexWidget
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


class ExpressionItem(QGraphicsRectItem):
    instanceList: list = []
    def __init__(self, x, y, expr='', result='', lastVarName='', varName='', desc='', plotting=False, latexResult=False):
        super().__init__(0, 0, 220, 30)
        type(self).instanceList.append(self)
        self.setPos(x, y)
        self.expr: str = expr
        self.result: str = result
        self.lastVarName: str = lastVarName
        self.varName: str = varName
        self.description: str = desc
        self.plotting: bool = plotting
        self.latexResult: bool = latexResult
        self.evaluator = Evaluate()

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

        self.latex: LatexWidget = LatexWidget()
        self.latexProxy: QGraphicsProxyWidget = QGraphicsProxyWidget(self)
        if not latexResult:
            self.latexProxy.hide()
            self.latex.hide()
        self.latexProxy.setWidget(self.latex)

        self._debounce = QTimer()
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(300)  # ms
        self._debounce.timeout.connect(self.recalculateAll)

        self.inputField.textChanged.connect(self._onTextChanged)
        self.inputField.unfocused.connect(self.checkBlankItem)

    def checkVarNames(self):
        setVars: list = [inst.varName for inst in self.instanceList]
        memmoryVars: list = self.evaluator.varDict.keys()
        diff: list = list(set(setVars).symmetric_difference(set(memmoryVars)))
        for var in diff:
            self.evaluator.popVarName(var)

    def sortVars(self):
        self.instanceList = sorted(self.instanceList, key=lambda x: x.pos().y())

    def updatePlot(self):
        if self.plotting:
            self.evaluator.evalPlotData()
            self.setupPlotter(self.evaluator)

    def updateLatexSize(self):
        self.latex.adjustSize()

    def updateLatexPos(self):
        h:float = self.latex.size().height()/2
        self.latexProxy.setPos(self.resultLabel.x(), self.resultLabel.y() - h + 10)

    def moveResultLabel(self):
        fm = QFontMetrics(self.inputFieldProxy.font())
        text_width = fm.horizontalAdvance(self.inputField.text())
        self.resultLabel.setPos(text_width+8, 2)
        self.setRect(0, 0, text_width+10, 30)

    def rearrangeItem(self):
        self.moveResultLabel()

    def contextMenuEvent(self, event: QGraphicsSceneContextMenuEvent) -> None:
        menu = self.inputField.createStandardContextMenu()
        menu.addSeparator()

        removeAction = menu.addAction("Delete Item")

        plotAction: QAction = QAction('Plot', checkable=True)
        menu.addAction(plotAction)
        if self.plotting:
            plotAction.setChecked(True)
        else:
            plotAction.setChecked(False)

        latexAction: QAction = QAction('Latex', checkable=True)
        menu.addAction(latexAction)
        if self.latexResult:
            latexAction.setChecked(True)
        else:
            latexAction.setChecked(False)

        chosen = menu.exec(event.screenPos())
        scene = self.scene()
        for item in scene.selectedItems():
            if chosen == removeAction:
                try:
                    if hasattr(item, "inputFieldProxy"):
                        type(item).instanceList.remove(self)
                        Evaluate.varDict.pop(item.varName)

                        item.inputFieldProxy.setWidget(None) # type: ignore
                        item.inputFieldProxy.widget().deleteLater()
                except Exception:
                    pass
                scene = item.scene()
                if scene: scene.removeItem(item)
                event.accept()

            elif chosen == plotAction:
                try:
                    if item.plotting:
                        item.plotting = False
                        if item.plot and self.plotProxy:
                            item.plotProxy.hide()
                        item.resultLabel.show()
                        item.resultLabel.overwriteVisibility(False)
                    else:
                        item.plotting = True
                        item.plotProxy.show()
                        item.updatePlot()
                        item.resultLabel.hide()
                        item.resultLabel.overwriteVisibility(True)
                except Exception:
                    pass
                event.accept()

            elif chosen == latexAction:
                try:
                    if item.latexResult:
                        item.latexResult = False
                        item.latexProxy.hide()
                        item.latex.hide()
                        item.resultLabel.show()
                        item.resultLabel.overwriteVisibility(False)
                    else:
                        item.latexResult = True
                        item.latexProxy.show()
                        item.latex.show()
                        item.resultLabel.hide()
                        item.resultLabel.overwriteVisibility(True)
                except Exception:
                    pass
                event.accept()

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
            self.evaluator.eval(self.expr)
            self.result = self.evaluator.getResult()
            self.varName = self.evaluator.getVarName()
            self.resultLabel.setPlainText(f"= {self.result}")
            self.latex.setText(self.evaluator.getLatex()) 
        except Exception as e:
            self.resultLabel.setPlainText(f"Error: {str(e)}")

    def saveFile(self) -> str:
        if self.plotting:
            plt = "+"
        else:
            plt = ''
        stream = f'{type(self)};{self.pos()};{self.expr};{self.result};{self.lastVarName};{self.varName};{self.description};{plt}'
        stream = stream.replace('\n', '')
        return stream

    def setupPlotter(self, evaluator: Evaluate) -> None:
        self.plotProxy.show()
        self.plot = plotWidget(self, plotType=evaluator.getUnsingedSymsCount())
        self.plot.axes.cla()
        match evaluator.getUnsingedSymsCount():
            case 1:
                self.plot.axes.plot(evaluator.getAddData('X'), evaluator.getAddData('plotResult'))
            case 2:
                self.plot.axes.plot_surface(evaluator.getAddData('X'), evaluator.getAddData('Y'), evaluator.getAddData('plotResult'), cmap=cm.magma) #type: ignore
        self.plot.draw_idle()
        self.plotProxy.setWidget(self.plot)
        self.plotProxy.setPos(-60, -17)

    def recalculateAll(self):
        self.sortVars()
        self.evaluateExpression()
        self.checkVarNames()
        self.updateLatexSize()
        self.updateLatexPos()
        self.updatePlot()

    def insertExpr(self):
        if self.varName != 'None':
            self.inputField.setText(f'{self.varName}={self.expr}')
        else:
            self.inputField.setText(f'{self.expr}')

    def checkBlankItem(self) -> None:
        if not self.inputField.text():
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
            return