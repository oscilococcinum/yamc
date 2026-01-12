from PySide6.QtWidgets import QGraphicsScene, QVBoxLayout, QWidget
from yamc.View import View

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("yamc")
        self.setGeometry(0, 0, 1024, 768)

        layout = QVBoxLayout(self)

        self.view = View()
        self.scene = QGraphicsScene()
        self.view.setScene(self.scene)
        layout.addWidget(self.view)