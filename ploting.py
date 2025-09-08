from PySide6.QtWidgets import QMainWindow, QApplication

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class plotWidget(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


# class MainWindow(QMainWindow):
# 
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
# 
#         # Create the maptlotlib FigureCanvas object,
#         # which defines a single set of axes as self.axes.
#         sc = plotWidget(self, width=5, height=4, dpi=100)
#         sc.axes.plot([0,1,2,3,4], [10,1,20,3,40])
#         self.setCentralWidget(sc)
#         sc.axes.plot([0,1,2,3,4], [0,1,2,3,4])
# 
#         self.show()
        
# if __name__=='__main__':
#     app = QApplication()
#     w = MainWindow()
#     app.exec()
