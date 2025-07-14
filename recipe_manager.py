import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit,
    QSpinBox, QTextEdit, QHBoxLayout, QPushButton, QMessageBox
)

RECIPE_FILE = "recipes.json"

def load_data(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class IngredientRow(QWidget):
    def __init__(self, inventory_items, remove_callback):
        super().__init__()
        layout = QHBoxLayout()
        self.combo = QComboBox()
        self.combo.setEditable(True)
        self.combo.addItems(inventory_items)
        self.qty = QSpinBox()
        self.qty.setMaximum(999999)
        self.btn_remove = QPushButton("-")
        self.btn_remove.clicked.connect(remove_callback)
        layout.addWidget(self.combo)
        layout.addWidget(self.qty)
        layout.addWidget(self.btn_remove)
        self.setLayout(layout)

    def get_value(self):
        return self.combo.currentText(), self.qty.value()


class RecipeManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("레시피")
        layout = QVBoxLayout()
        self.name_select = QComboBox()
        self.name_select.addItem("새로 입력")
        self.name_select.currentIndexChanged.connect(self.select_changed)
        self.load_recipes()
        layout.addWidget(QLabel("아이템명"))
        layout.addWidget(self.name_select)

        self.recipe_name = QLineEdit()
        self.recipe_name.setPlaceholderText("레시피명")
        self.output_count = QSpinBox()
        self.output_count.setMaximum(99999)
        self.ingredients_layout = QVBoxLayout()
        self.ingredient_rows = []
        self.btn_add_ingredient = QPushButton("+")
        self.btn_add_ingredient.clicked.connect(self.add_ingredient_row)
        self.inventory_items = self.load_inventory_items()

        layout.addWidget(QLabel("레시피명"))
        layout.addWidget(self.recipe_name)
        layout.addWidget(QLabel("제작산출갯수"))
        layout.addWidget(self.output_count)

        layout.addWidget(QLabel("재료와 수량"))
        layout.addLayout(self.ingredients_layout)
        layout.addWidget(self.btn_add_ingredient)

        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("저장")
        self.btn_save.clicked.connect(self.save_recipe)
        self.btn_edit = QPushButton("수정")
        self.btn_edit.clicked.connect(self.enable_edit)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_edit)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

        self.editing = False
        self.set_editable(True)
        self.add_ingredient_row()

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
        row.qty.setValue(qty)
        self.ingredient_rows.append(row)
        self.ingredients_layout.addWidget(row)

    def load_recipes(self):
        self.recipes = load_data(RECIPE_FILE)
        self.name_select.blockSignals(True)
        self.name_select.clear()
        self.name_select.addItem("새로 입력")
        for name in self.recipes:
            self.name_select.addItem(name)
        self.name_select.blockSignals(False)

    def load_inventory_items(self):
        try:
            items = load_data("material_data.json")
            return list(items.keys())
        except Exception:
            return []


    def set_editable(self, enable):
        self.recipe_name.setEnabled(enable)
        self.output_count.setEnabled(enable)
        # self.materials.setEnabled(enable)

    def select_changed(self):
        idx = self.name_select.currentIndex()
        if idx == 0:
            self.set_editable(True)
            self.recipe_name.setText("")
            self.output_count.setValue(1)
            # self.materials.setPlainText("")
            self.btn_edit.setEnabled(False)
        else:
            key = self.name_select.currentText()
            rec = self.recipes.get(key, {})
            self.recipe_name.setText(rec.get("name", key))
            self.output_count.setValue(rec.get("output_count", 1))
            mats = rec.get("materials", {})
            self.set_ingredients(mats)
            self.set_editable(False)
            self.btn_edit.setEnabled(True)

    def enable_edit(self):
        self.set_editable(True)
        self.editing = True

    def save_recipe(self):
        n = self.recipe_name.text()
        out_cnt = self.output_count.value()
        mats = self.get_ingredients()  # 동적 행 기반 dict

        recipes = load_data(RECIPE_FILE)
        recipes[n] = {
            "name": n,
            "output_count": out_cnt,
            "materials": mats
        }
        save_data(RECIPE_FILE, recipes)
        QMessageBox.information(self, "알림", "저장됨")
        self.load_recipes()
        idx = self.name_select.findText(n)
        self.name_select.setCurrentIndex(idx if idx >= 0 else 0)
        self.set_editable(False)
        self.editing = False
        self.btn_edit.setEnabled(True)

    def set_ingredients(self, ingredients_dict):
        for w in self.ingredient_rows:
            self.ingredients_layout.removeWidget(w)
            w.setParent(None)
        self.ingredient_rows = []
        for mat, qty in ingredients_dict.items():
            self.add_ingredient_row(mat, qty)
        if not ingredients_dict:
            self.add_ingredient_row()

    def get_ingredients(self):
        result = {}
        for row in self.ingredient_rows:
            mat, qty = row.get_value()
            if mat:
                result[mat] = qty
        return result
