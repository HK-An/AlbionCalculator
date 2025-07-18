import os
import json
from util import Util
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox, QLineEdit, QSpinBox)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECIPE_FILE = os.path.join(BASE_DIR, '..', 'recipes.json')

def load_data(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)
    
class IngredientRow(QWidget):
    def __init__(self, inventory_items, remove_callback):
        super().__init__()
        layout = QHBoxLayout()
        self.combo = QComboBox()
        # self.combo.setEditable(True)
        self.combo.addItems(inventory_items)
        self.qty = QSpinBox()
        self.qty.setMaximum(999999)
        # self.btn_remove = QPushButton("-")
        # self.btn_remove.clicked.connect(remove_callback)
        layout.addWidget(self.combo)
        layout.addWidget(self.qty)
        # layout.addWidget(self.btn_remove)
        self.setLayout(layout)

    def get_value(self):
        return self.combo.currentText(), self.qty.value()
    
class RecipeForm(QWidget):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        # self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        # self.setLayout(layout)

        self.isRecipe = title != "Crafting Manager"

        self.name_select = QComboBox()
        self.recipe_name = QLineEdit()
        self.output_count = QSpinBox()
        self.ingredients_layout = QVBoxLayout()
        self.fee = QSpinBox()
        btn_layout = QHBoxLayout()
        self.btn_craft = QPushButton("제작하기")


        self.name_select.addItem("새로 입력")
        self.name_select.currentIndexChanged.connect(self.select_changed)
        self.load_recipes(self.isRecipe)
        

        self.recipe_name.setPlaceholderText("레시피명")
        self.output_count.setMaximum(99999)
        self.ingredient_rows = []
        self.inventory_items = self.load_inventory_items()

        self.btn_craft.clicked.connect(self.add_inventory)
        
        layout.addWidget(QLabel("아이템명"))
        layout.addWidget(self.name_select)
        layout.addWidget(QLabel("레시피명"))
        layout.addWidget(self.recipe_name)
        layout.addWidget(QLabel("제작산출갯수"))
        layout.addWidget(self.output_count)
        layout.addWidget(QLabel("제작수수료"))
        layout.addWidget(self.fee)
        layout.addWidget(QLabel("재료와 수량"))
        layout.addLayout(self.ingredients_layout)
        btn_layout.addWidget(self.btn_craft)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.editing = False
        self.add_ingredient_row()
        self.util = Util()
        

    def select_changed(self):
        idx = self.name_select.currentIndex()
        if idx == 0:
            self.clear_ingredients()
        else:
            key = self.name_select.currentText()
            rec = self.recipes.get(key, {})
            self.recipe_name.setText(rec.get("name", key))
            self.output_count.setValue(rec.get("output_count", 1))
            mats = rec.get("materials", {})
            self.set_ingredients(mats)
            # self.btn_edit.setEnabled(True)

    def load_recipes(self, flag):
        self.recipes = load_data(RECIPE_FILE)
        self.name_select.blockSignals(True)
        self.name_select.clear()
        if flag:
            self.name_select.addItem("새로 입력")
        else:
            self.name_select.addItem("선택안함")
        for name in self.recipes:
            self.name_select.addItem(name)
        self.name_select.blockSignals(False)

    def add_ingredient_row(self, mat="", qty=1):
        def remove_row():
            row = self.sender()
            for i, widget in enumerate(self.ingredient_rows):
                if widget is row:
                    self.ingredients_layout.removeWidget(widget)
                    widget.setParent(None)
                    self.ingredient_rows.pop(i)
                    break
        row = IngredientRow(self.inventory_items, remove_row)
        if mat:
            idx = row.combo.findText(mat)
            if idx >= 0:
                row.combo.setCurrentIndex(idx)
        row.combo.addItem(mat)
        row.qty.setValue(qty)
        self.ingredient_rows.append(row)
        self.ingredients_layout.addWidget(row)
    
    def load_inventory_items(self):
        try:
            items = load_data("material_data.json")
            return list(items.keys())
        except Exception:
            return []
        
    def set_ingredients(self, ingredients_dict):
        for w in self.ingredient_rows:
            self.ingredients_layout.removeWidget(w)
            w.setParent(None)
        self.ingredient_rows = []
        for mat, qty in ingredients_dict.items():
            self.add_ingredient_row(mat, qty)
        if not ingredients_dict:
            self.add_ingredient_row()

    def clear_ingredients(self):
        self.recipe_name.setText("")
        self.output_count.setValue(0)
        self.set_ingredients({})
        # self.btn_edit.setEnabled(False)

    def add_inventory(self):
        self.util.add_inventory(self.name_select.currentText(), self.output_count.value())
        # Util.getIndexByNameFromMaterialJson(self.name_select.currentText())
        # print("count->",self.output_count.value())
        # print("fee->", self.fee.value())

        # for ingredient_row in self.ingredient_rows:
            # Util.getIndexByNameFromMaterialJson(ingredient_row.combo.currentText())