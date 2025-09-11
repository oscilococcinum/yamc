from PySide6.QtWidgets import (
    QGraphicsSceneContextMenuEvent, QGraphicsSceneHoverEvent, QGraphicsTextItem, QGraphicsItem, QGraphicsRectItem,
    QLineEdit, QGraphicsProxyWidget, QGraphicsScene, QWidget
)
from PySide6.QtGui import QBrush, QColor, QFocusEvent, QFontMetrics, QFont, Qt
from PySide6.QtCore import QTimer, Signal
import solve
from ploting import *
import re
from numpy import array, linspace

ITEM_W, ITEM_H = 220, 60

class AutoResizeLineEdit(QLineEdit):
    focused: Signal = Signal()
    def __init__(self, text="", gparent=None):
        super().__init__(text)
        self.gparent: (QGraphicsItem | None) = gparent
        self.textChanged.connect(self.adjustSizeToText)
        self.adjustSizeToText()
        self.focused.connect(self.select_parent)

    def adjustSizeToText(self):
        fm = QFontMetrics(self.font())
        text_width = fm.horizontalAdvance(self.text())
        self.setFixedWidth(text_width + 10)

    def select_parent(self):
        if self.gparent:
            scene: QGraphicsScene = self.gparent.scene()
            scene.clearSelection()
            self.gparent.setSelected(True)
        else: pass

    def focusInEvent(self, event: QFocusEvent) -> None:
        super().focusInEvent(event)
        self.focused.emit()

        

class ExpressionItem(QGraphicsRectItem):
    instance_list: list = []
    var_dict: dict = {}

    def __init__(self, x, y, expr='', result='', varName='', desc=''):
        super().__init__(0, 0, 220, 30)
        type(self).instance_list.append(self)
        self.setPos(x, y)
        self.expr = expr
        self.result = result
        self.varName = varName
        self.description = desc

        self.setBrush(QBrush(QColor(230, 230, 250)))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable) # type: ignore
        #self.setAcceptHoverEvents(True)

        self.input_field = AutoResizeLineEdit('', self)
        self.input_field.setPlaceholderText("Enter expression")
        self.input_field.setFrame(False)

        self.result_label = QGraphicsTextItem("", self)
        self.result_label.setTextInteractionFlags(Qt.TextSelectableByMouse) # type: ignore

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
#        self.input_field.focused.connect(self.input_field.select_parent())
        
#    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent) -> None:
#        self.setSelected(True)
#        self.input_field.setFocus()
#        self.input_field.setReadOnly(False)
#        return super().hoverEnterEvent(event)
#
#    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
#        self.setSelected(False)
#        self.input_field.clearFocus()
#        self.input_field.setReadOnly(True)
#        return super().hoverLeaveEvent(event)

#    def set_selected(self):
#        scene: QGraphicsScene = self.scene()
#        scene.clearSelection()
#        self.setSelected(True)

    def move_result_label(self):
        fm = QFontMetrics(self.QlineEditProxy.font())
        text_width = fm.horizontalAdvance(self.input_field.text())
        self.result_label.setPos(text_width+25, 4)
        self.setRect(0, 0, text_width+20, 30)

    def rearrange_item(self):
        self.move_result_label()

    def insetr_expr(self):
        if self.varName:
            self.input_field.setText(f'{self.varName}={self.expr}')
        else:
            self.input_field.setText(f'{self.expr}')

    def contextMenuEvent(self, event: QGraphicsSceneContextMenuEvent) -> None:
        menu = self.input_field.createStandardContextMenu()
        menu.addSeparator()
        remove_action = menu.addAction("Delete Item")
        chosen = menu.exec(event.screenPos())
        if chosen == remove_action:
            try:
                if hasattr(self, "QlineEditProxy"):
                    type(self).instance_list.remove(self)
                    type(self).var_dict.pop(self.varName)
                    self.QlineEditProxy.setWidget(None) # type: ignore
                    self.QlineEditProxy.widget().deleteLater()
            except Exception:
                pass

            scene = self.scene()
            if scene: scene.removeItem(self)
            event.accept()
            return

        return super().contextMenuEvent(event)

    def _on_text_changed(self, _):
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
                self.expr = expr_str.strip()
                self.result = solve.generalEval(expr_str, type(self).var_dict)
            self.result_label.setPlainText(f"= {self.result}")
        except Exception as e:
            self.result_label.setPlainText(f"Error: {str(e)}")
    
    def recalculate_all(self):
        self.evaluate_expression()

    def save_file(self) -> str:
        stream = f'{type(self)};{self.pos()};{self.expr};{self.result};{self.varName};{self.description}'
        stream = stream.replace('\n', '')
        return stream

class IntegrationItem(ExpressionItem):
    def __init__(self, x, y, expr='', result='', varName='', desc=''):
        super().__init__(x, y, expr, result, varName, desc)
        self.setPos(x, y)

        self.QlineEditProxy.setPos(10, 5)

        self.differential = AutoResizeLineEdit('dx', self)
        self.differential.setStyleSheet("""
            AutoResizeLineEdit {
                background: rgba(255, 255, 255, 0);  /* semi-transparent white */
                color: black;  /* fully visible text */
                border: 0px solid gray;
            }
        """)
        self.DifferentialQlineEditProxy = QGraphicsProxyWidget(self)
        self.DifferentialQlineEditProxy.setWidget(self.differential)
        self.DifferentialQlineEditProxy.setPos(15, 7)

        self.integralSign = QGraphicsTextItem("∫", self)
        self.integralSign.setPos(-2, 0)
        self.integralSign.setFont(QFont('DejaVuSans', 15))

        self.input_field.textChanged.connect(self.move_differential)
        self.differential.textChanged.connect(self.move_differential)
        self.input_field.textChanged.connect(self.move_result_label)
        self.differential.textChanged.connect(self.move_result_label)
        self.differential.textChanged.connect(self._on_text_changed)

    def move_differential(self):
        fm = QFontMetrics(self.QlineEditProxy.font())
        text_width = fm.horizontalAdvance(self.input_field.text())
        self.DifferentialQlineEditProxy.setPos(text_width+22, 7)
        fm01 = QFontMetrics(self.DifferentialQlineEditProxy.font())
        diff_text_width = fm01.horizontalAdvance(self.differential.text())
        self.setRect(0, 0, text_width+diff_text_width+30, 30)

    def move_result_label(self):
        fm = QFontMetrics(self.QlineEditProxy.font())
        text_width = fm.horizontalAdvance(self.input_field.text())
        fm01 = QFontMetrics(self.DifferentialQlineEditProxy.font())
        diff_text_width = fm01.horizontalAdvance(self.differential.text())
        self.result_label.setPos(text_width+diff_text_width+30, 4)
        self.setRect(0, 0, text_width+diff_text_width+30, 30)

    def rearrange_item(self):
        self.move_result_label()
        self.move_differential()

    def evaluate_expression(self):
        expr_str = self.input_field.text().strip()
        if not expr_str:
            self.result_label.setPlainText("")
            return
        try:
            if re.search(r'=', expr_str):
                self.varName = expr_str.split('=')[0].strip()
                self.expr = expr_str.split('=')[1].strip()
                self.result = solve.generalEval(self.expr, type(self).var_dict, 'integration', array([self.differential.text()]))
                type(self).var_dict[self.varName] = self.result
            elif re.search(r'=.*#', expr_str):
                self.varName = expr_str.split('=')[0].strip()
                self.expr = expr_str.split('=')[1].strip().split('#')[0].strip()
                self.result = solve.generalEval(self.expr, type(self).var_dict, 'integration', array([self.differential.text()]))
                self.description = expr_str.split('=')[1].strip().split('#')[1].strip()
                type(self).var_dict[self.varName] = self.result
            else:
                self.expr = expr_str.strip()
                self.result = solve.generalEval(expr_str, type(self).var_dict, 'integration', array([self.differential.text()]))
            self.result_label.setPlainText(f"= {self.result}")
        except Exception as e:
            self.result_label.setPlainText(f"Error: {str(e)}")

class DifferentiationItem(ExpressionItem):
    def __init__(self, x, y, expr='', result='', varName='', desc=''):
        super().__init__(x, y, expr, result, varName, desc)
        self.setPos(x, y)
        self.setRect(0, 0, 20, 30)

        self.QlineEditProxy.setPos(20, 5)

        self.differential = AutoResizeLineEdit('dx', self)
        self.differential.setFont(QFont('DejaVu Sans', 8))
        self.differential.setFrame(False)
        self.differential.setStyleSheet("""
            AutoResizeLineEdit {
                background: rgba(255, 255, 255, 0);  /* semi-transparent white */
                color: black;  /* fully visible text */
                border: 0px solid gray;
            }
        """)

        self.DifferentialQlineEditProxy = QGraphicsProxyWidget(self)
        self.DifferentialQlineEditProxy.setWidget(self.differential)
        self.DifferentialQlineEditProxy.setPos(0, 10)

        self.integralSign = QGraphicsTextItem("d", self)
        self.integralSign.setPos(0, 0)
        self.integralSign.setFont(QFont('DejaVu Sans', 8))

        self.input_field.textChanged.connect(self.move_result_label)
        self.differential.textChanged.connect(self.move_result_label)
        self.differential.textChanged.connect(self.move_input_field)
        self.differential.textChanged.connect(self._on_text_changed)

    def move_result_label(self):
        fm = QFontMetrics(self.QlineEditProxy.font())
        text_width = fm.horizontalAdvance(self.input_field.text())
        fm01 = QFontMetrics(self.DifferentialQlineEditProxy.font())
        diff_text_width = fm01.horizontalAdvance(self.differential.text())
        self.result_label.setPos(text_width+diff_text_width+20, 4)
        self.setRect(0, 0, text_width+diff_text_width+20, 30)

    def move_input_field(self):
        fm = QFontMetrics(self.QlineEditProxy.font())
        text_width = fm.horizontalAdvance(self.input_field.text())
        fm01 = QFontMetrics(self.DifferentialQlineEditProxy.font())
        diff_text_width = fm01.horizontalAdvance(self.differential.text())
        self.QlineEditProxy.setPos(diff_text_width+5, 4)
        self.setRect(0, 0, diff_text_width+text_width+20, 30)

    def rearrange_item(self):
        self.move_result_label()
        self.move_input_field()

    def evaluate_expression(self):
        expr_str = self.input_field.text().strip()
        if not expr_str:
            self.result_label.setPlainText("")
            return
        try:
            if re.search(r'=', expr_str):
                self.varName = expr_str.split('=')[0].strip()
                self.expr = expr_str.split('=')[1].strip()
                self.result = solve.generalEval(self.expr, type(self).var_dict, 'differentiation', array([self.differential.text()]))
                type(self).var_dict[self.varName] = self.result
            elif re.search(r'=.*#', expr_str):
                self.varName = expr_str.split('=')[0].strip()
                self.expr = expr_str.split('=')[1].strip().split('#')[0].strip()
                self.result = solve.generalEval(self.expr, type(self).var_dict, 'differentiation', array([self.differential.text()]))
                self.description = expr_str.split('=')[1].strip().split('#')[1].strip()
                type(self).var_dict[self.varName] = self.result
            else:
                self.expr = expr_str.strip()
                self.result = solve.generalEval(expr_str, type(self).var_dict, 'differentiation', array([self.differential.text()]))
            self.result_label.setPlainText(f"= {self.result}")
        except Exception as e:
            self.result_label.setPlainText(f"Error: {str(e)}")

class PlotItem(ExpressionItem):
    def __init__(self, x, y, expr='', result='', varName='', desc=''):
        super().__init__(x, y, expr, result, varName, desc)
        self.setPos(x, y)

        self.result_label.setVisible(False)

        self.plot = plotWidget(self)
        self.PlotProxy = QGraphicsProxyWidget(self)

        self.plot_parameters = AutoResizeLineEdit("[0, 100, 100]", self)
        self.PlotParametersProxy = QGraphicsProxyWidget(self)
        self.PlotParametersProxy.setWidget(self.plot_parameters)
        self.PlotParametersProxy.setPos(0, -20)

        self.params = eval(self.plot_parameters.displayText())
        self.xmin: float=self.params[0]
        self.xmax: float=self.params[1]
        self.sampling: int=self.params[2]
        self.domian = linspace(self.xmin, self.xmax, self.sampling)

        self.input_field.textChanged.connect(self.move_result_label)
        self.plot_parameters.textChanged.connect(self.update_params)
        self._debounce.timeout.connect(self.plot_expression)

    def evaluate_expression(self):
        expr_str = self.input_field.text().strip()
        if not expr_str:
            self.result_label.setPlainText("")
            return
        try:
            if re.search(r'=', expr_str):
                self.varName = expr_str.split('=')[0].strip()
                self.expr = expr_str.split('=')[1].strip()
                self.result = solve.generalEval(self.expr, type(self).var_dict, 'ploting', self.domian)
                type(self).var_dict[self.varName] = self.result
            elif re.search(r'=.*#', expr_str):
                self.varName = expr_str.split('=')[0].strip()
                self.expr = expr_str.split('=')[1].strip().split('#')[0].strip()
                self.result = solve.generalEval(self.expr, type(self).var_dict, 'ploting', self.domian)
                self.description = expr_str.split('=')[1].strip().split('#')[1].strip()
                type(self).var_dict[self.varName] = self.result
            else:
                self.expr = expr_str.strip()
                self.result = solve.generalEval(expr_str, type(self).var_dict, 'ploting', self.domian)
            self.result_label.setPlainText(f"= {self.result}")
        except Exception as e:
            self.result_label.setPlainText(f"Error: {str(e)}")

    def plot_expression(self):
        self.plot.axes.cla()
        self.plot.axes.plot(self.domian, self.result)
        self.plot.axes.set_xlim(self.xmin, self.xmax)
        self.plot.draw_idle()
        self.PlotProxy.setWidget(self.plot)
        self.PlotProxy.setPos(0, 30)

    def update_params(self):
        self.params = eval(self.plot_parameters.displayText())
        self.xmin: float=self.params[0]
        self.xmax: float=self.params[1]
        self.sampling: int=self.params[2]
        self.domian = linspace(self.xmin, self.xmax, self.sampling)

    def recalculate_all(self):
        self.evaluate_expression()
        self.update_params()
        self.plot_expression()