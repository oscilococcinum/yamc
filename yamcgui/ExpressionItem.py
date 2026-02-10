from PySide6.QtWidgets import QGraphicsItem, QGraphicsRectItem, QGraphicsProxyWidget, QGraphicsSceneContextMenuEvent
from PySide6.QtGui import QBrush, QColor, QFontMetrics, QAction, Qt
from PySide6.QtCore import QTimer
#from matplotlib import cm
from yamcgui.LatexWidget import LatexWidget
#from yamcgui.PlotWidget import PlotWidget
from yamcgui.QGraphicsTextLabel import QGraphicsTextLabel
from yamcgui.AutoResizeLineEdit import AutoResizeLineEdit
from yamcsolve.Equation import VisType
from yamcsolve.SymPySolver import EquationLike
from yamcsolve.ActiveSolvers import ActiveSolver


class ExpressionItem(QGraphicsRectItem):
    instances: dict[int, 'ExpressionItem'] = {}
    def __init__(self, x: float, y: float) -> None:
        super().__init__(0, 0, 220, 30)
        self.setPos(x, y)
        self._id: int = ActiveSolver.getFreeId()
        self._equation: EquationLike = ActiveSolver.getEquation(self.getId())
        type(self).instances[self.getId()] = self

        self.setBrush(QBrush(QColor(0, 0, 0, 0)))
        self.setPen(Qt.PenStyle.NoPen)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)

        self.inputField = AutoResizeLineEdit('', self)
        self.inputField.setPlaceholderText("Enter expression")
        self.inputField.setFrame(False)

        self.resultLabel = QGraphicsTextLabel("", self)
        self.resultLabel.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

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
        self.latexProxy.hide()
        self.latex.hide()
        self.latexProxy.setWidget(self.latex)

        self._debounce = QTimer()
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(300)
        self._debounce.timeout.connect(self.evaluateExpression)

        self.inputField.textChanged.connect(self._onTextChanged)
        self.inputField.unfocused.connect(self.checkBlankItem)

    def getId(self) -> int:
        return self._id
    
    def getEquation(self) -> EquationLike:
        return self._equation

    def _onTextChanged(self) -> None:
        self._debounce.start()

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
        if self.getEquation().getVisType() == VisType.Plot:
            plotAction.setChecked(True)
        else:
            plotAction.setChecked(False)

        latexAction: QAction = QAction('Latex', checkable=True)
        menu.addAction(latexAction)
        if self.getEquation().getVisType() == VisType.Latex:
            latexAction.setChecked(True)
        else:
            latexAction.setChecked(False)

        AlignVAction = menu.addAction("Align Vertycaly")
        menu.addAction(AlignVAction)
        AlignHAction = menu.addAction("Align Horizontally")
        menu.addAction(AlignHAction)

        chosen = menu.exec(event.screenPos())
        scene = self.scene()

        selection:list['ExpressionItem'] = [i for i in ExpressionItem.instances.values() if i.isSelected()]
        for item in selection:
            if chosen == removeAction:
                try:
                    if hasattr(item, "inputFieldProxy"):
                        type(item).instances.pop(item.getId())
                        ActiveSolver.popEquation(item.getId())

                        item.inputFieldProxy.setWidget(None) # type: ignore
                        item.inputFieldProxy.widget().deleteLater()
                except Exception:
                    pass
                scene = item.scene()
                if scene: scene.removeItem(item)
                event.accept()

            elif chosen == plotAction:
                try:
                    if ActiveSolver.getEquation(self.getId()).getVisType() == VisType.Plot:
                        ActiveSolver.getEquation(self.getId()).setVisType(VisType.Text)
                        if item.plot and self.plotProxy:
                            item.plotProxy.hide()
                        item.resultLabel.show()
                        item.resultLabel.overwriteVisibility(False)
                    elif ActiveSolver.getEquation(self.getId()).getVisType() != VisType.Plot:
                        ActiveSolver.getEquation(self.getId()).setVisType(VisType.Plot)
                        item.plotProxy.show()
#                        item.updatePlot()
                        item.resultLabel.hide()
                        item.resultLabel.overwriteVisibility(True)
                except Exception:
                    pass
                event.accept()

            elif chosen == latexAction:
                try:
                    if ActiveSolver.getEquation(self.getId()).getVisType() == VisType.Latex:
                        ActiveSolver.getEquation(self.getId()).setVisType(VisType.Text)
                        item.latexProxy.hide()
                        item.latex.hide()
                        item.resultLabel.show()
                        item.resultLabel.overwriteVisibility(False)
                    elif ActiveSolver.getEquation(self.getId()).getVisType() != VisType.Latex:
                        ActiveSolver.getEquation(self.getId()).setVisType(VisType.Latex)
                        item.latexProxy.show()
                        item.latex.show()
                        item.resultLabel.hide()
                        item.resultLabel.overwriteVisibility(True)
                except Exception:
                    pass
                event.accept()

            elif chosen == AlignVAction:
                try:
                    if item is not self:
                        item.setX(self.pos().x())
                except Exception:
                    pass
                event.accept()

            elif chosen == AlignHAction:
                try:
                    if item is not self:
                        item.setY(self.pos().y())
                except Exception:
                    pass
                event.accept()

        return super().contextMenuEvent(event)

    def evaluateExpression(self):
        expr_str = self.inputField.text().strip()
        if not expr_str:
            self.resultLabel.setPlainText("")
            return
        try:
            ActiveSolver.addEquation(self.getId(), expr_str)
            ActiveSolver.evalEq(self.getId())
            solverResult: str = ActiveSolver.getEquation(self.getId()).getResultStream()
            self.resultLabel.setPlainText(f"= {solverResult}")
            #self.latex.setText(self.evaluator.getLatex()) 
        except Exception as e:
            self.resultLabel.setPlainText(f"Error: {str(e)}")

#    def saveFile(self) -> str:
#        if self.plotting:
#            plt = "+"
#        else:
#            plt = ''
#        stream = f'{type(self)};{self.pos()};{self.expr};{self.result};{self.lastVarName};{self.varName};{self.description};{plt}'
#        stream = stream.replace('\n', '')
#        return stream

#    def setupPlotter(self, evaluator: Solver) -> None:
#        self.plotProxy.show()
#        self.plot = PlotWidget(self, plotType=evaluator.getUnsingedSymsCount())
#        self.plot.axes.cla()
#        match evaluator.getUnsingedSymsCount():
#            case 1:
#                self.plot.axes.plot(evaluator.getAddData('X'), evaluator.getAddData('plotResult'))
#            case 2:
#                self.plot.axes.plot_surface(evaluator.getAddData('X'), evaluator.getAddData('Y'), evaluator.getAddData('plotResult'), cmap=cm.magma) #type: ignore
#        self.plot.draw_idle()
#        self.plotProxy.setWidget(self.plot)
#        self.plotProxy.setPos(-60, -17)

    def checkBlankItem(self) -> None:
        if not self.inputField.text():
            try:
                if hasattr(self, "inputFieldProxy"):
                    type(self).instances.pop(self.getId())
                    ActiveSolver.popEquation(self.getId())

                    self.inputFieldProxy.setWidget(None) # type: ignore
                    self.inputFieldProxy.widget().deleteLater()
            except Exception:
                pass
            scene = self.scene()
            if scene: scene.removeItem(self)
            return
