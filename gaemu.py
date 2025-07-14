import sys
import datetime
import json
import os
from profit_manager import ProfitManager
from sale_register import SaleRegister
from inventory_manager import InventoryManager
from recipe_calc import RecipeCalc
from recipe_manager import RecipeManager
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton
    # , QTextEdit, QComboBox, QMessageBox, QSpinBox
)

DATA_FILE = "material_data.json"
RECIPE_FILE = "recipes.json"

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}

def save_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("제작 시뮬레이터")
        layout = QVBoxLayout()
        btn_inv = QPushButton("인벤토리")
        btn_recipe = QPushButton("레시피")
        btn_calc = QPushButton("제작비용계산")
        btn_sale = QPushButton("판매등록")
        btn_profit = QPushButton("수익 정산")

        btn_inv.clicked.connect(self.open_inventory)
        btn_recipe.clicked.connect(self.open_recipe)
        btn_calc.clicked.connect(self.open_calc)
        btn_sale.clicked.connect(self.open_sale)
        btn_profit.clicked.connect(self.open_profit)

        layout.addWidget(btn_inv)
        layout.addWidget(btn_recipe)
        layout.addWidget(btn_calc)
        layout.addWidget(btn_sale)
        layout.addWidget(btn_profit)
        self.setLayout(layout)

        self._inventory_window = None
        self._recipe_window = None
        self._calc_window = None
        self._sale_window = None
        self._profit_window = None

    def open_profit(self):
        self._profit_window = ProfitManager()
        self._profit_window.show()

    def open_inventory(self):
        self._inventory_window = InventoryManager()
        self._inventory_window.show()

    def open_recipe(self):
        self._recipe_window = RecipeManager()
        self._recipe_window.show()

    def open_calc(self):
        self._calc_window = RecipeCalc()
        self._calc_window.show()

    def open_sale(self):
        self._sale_window = SaleRegister()
        self._sale_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
