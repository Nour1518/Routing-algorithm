
import sys

from PyQt6.QtWidgets import QApplication

from model.control_panel import ControlPanel


app = QApplication(sys.argv)

panel = ControlPanel()

panel.resize(
    300,
    500
)

panel.show()

sys.exit(
    app.exec()
)
