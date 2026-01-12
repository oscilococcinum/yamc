from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class plotWidget(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100, plotType: int = 1):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        if plotType == 2:
            self.axes = self.fig.add_subplot(111, projection='3d')
        else:
            self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
