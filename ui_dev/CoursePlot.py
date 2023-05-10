from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as \
    FigureCanvas
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=100)
        axes = fig.add_subplot(111)
        super().__init__(fig)