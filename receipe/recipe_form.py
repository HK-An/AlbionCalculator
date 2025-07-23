import os
import json
from util import Util
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox, QLineEdit, QSpinBox, QHBoxLayout, QMessageBox)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECIPE_FILE = os.path.join(BASE_DIR, '..', 'recipes.json')

def load_data(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

class IngredientRow(QWidget):
    def __init__(self, inventory_items, remove_callback, is_recipe, item_name):
        super().__init__()
        self.util = Util()
        self.is_recipe = is_recipe
        self.item_name = item_name

        self.setup_ui(inventory_items)

    def setup_ui(self, inventory_items):
        layout = QHBoxLayout()

        self.add_item_name_combo(layout, inventory_items)
        self.add_qty_spinbox(layout)
        self.add_inv_qty_spinbox(layout)
        self.add_remaining_qty_spinbox(layout)

        self.setLayout(layout)

    def get_value(self):
        return self.combo.currentText(), self.qty.value(), self.remaining_qty.value()

    def add_item_name_combo(self, layout, inventory_items):
        self.combo = QComboBox()
        self.combo.addItems(inventory_items)
        self.combo.setDisabled(not self.is_recipe)
        layout.addWidget(self.combo)

    def add_qty_spinbox(self, layout):
        self.qty = QSpinBox()
        self.qty.setMaximum(999999)
        self.qty.setHidden(not self.is_recipe)
        layout.addWidget(self.qty)

    def add_inv_qty_spinbox(self, layout):
        self.inv_qty = QSpinBox()
        self.inv_qty.setMaximum(999999)
        self.inv_qty.setDisabled(True)
        self.inv_qty.setHidden(self.is_recipe)

        item_data = self.util.get_item_from_inventory(self.item_name)
        if item_data:
            self.inv_qty.setValue(item_data.get('enchant', {}).get('0', {}).get('count', 0))

        layout.addWidget(self.inv_qty)

    def add_remaining_qty_spinbox(self, layout):
        self.remaining_qty = QSpinBox()
        self.remaining_qty.setMaximum(999999)
        layout.addWidget(self.remaining_qty)  
    
class RecipeForm(QWidget):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.lang = "ko"

        self.util = Util()
        self.isRecipe = title != "Crafting Manager"
        self.isHeader = False
        self.editing = False
        self.ingredient_rows = []
        self.inventory_items = self.load_inventory_items()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.add_item_name_combo(layout)
        self.add_recipe_name_input(layout)
        self.add_output_count_spinbox(layout)
        self.add_fee_spinbox(layout)
        self.add_ingredient_area(layout)
        self.add_buttons(layout)

        self.setLayout(layout)

        self.load_recipes(self.isRecipe)
        self.add_ingredient_row()
        self.connect_signals()

# Add UI start
    def add_item_name_combo(self, layout):
        layout.addWidget(QLabel(self.util.get_text_from_lang(self.lang, "label_item_name")))
        self.name_select = QComboBox()
        self.name_select.addItem("새로 입력")
        layout.addWidget(self.name_select)

    def add_recipe_name_input(self, layout):
        layout.addWidget(QLabel(self.util.get_text_from_lang(self.lang, "label_recipe_name")))
        self.recipe_name = QLineEdit()
        self.recipe_name.setPlaceholderText(self.util.get_text_from_lang(self.lang, "label_recipe_name"))
        layout.addWidget(self.recipe_name)

    def add_output_count_spinbox(self, layout):
        layout.addWidget(QLabel(self.util.get_text_from_lang(self.lang, "label_craft_count")))
        self.output_count = QSpinBox()
        self.output_count.setMaximum(99999)
        layout.addWidget(self.output_count)

    def add_fee_spinbox(self, layout):
        layout.addWidget(QLabel(self.util.get_text_from_lang(self.lang, "label_total_craft_fee")))
        self.fee = QSpinBox()
        self.fee.setMaximum(999999)
        layout.addWidget(self.fee)

    def add_ingredient_area(self, layout):
        layout.addWidget(QLabel(self.util.get_text_from_lang(self.lang, "label_ingredient_and_count")))
        self.ingredients_layout = QVBoxLayout()
        layout.addLayout(self.ingredients_layout)

    def add_buttons(self, layout):
        btn_layout = QHBoxLayout()
        self.btn_calculate = QPushButton(self.util.get_text_from_lang(self.lang, "btn_calculate"))
        self.btn_craft = QPushButton(self.util.get_text_from_lang(self.lang, "btn_craft"))
        btn_layout.addWidget(self.btn_calculate)
        btn_layout.addWidget(self.btn_craft)
        layout.addLayout(btn_layout)

    def connect_signals(self):
        self.name_select.currentIndexChanged.connect(self.select_changed)
        self.btn_craft.clicked.connect(self.do_craft)
        self.btn_calculate.clicked.connect(self.calculate_ingredient_count)
    # Add UI end
        
    def load_recipes(self, flag):
        self.recipes = load_data(RECIPE_FILE)
        self.name_select.blockSignals(True)
        self.name_select.clear()
        if flag:
            self.name_select.addItem(self.util.get_text_from_lang(self.lang, "combo_new"))
        else:
            self.name_select.addItem(self.util.get_text_from_lang(self.lang, "combo_not_selected"))
        for name in self.recipes:
            self.name_select.addItem(name)
        self.name_select.blockSignals(False)

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

    def add_ingredient_row(self, mat="", qty=1):
        def remove_row():
            row = self.sender()
            for i, widget in enumerate(self.ingredient_rows):
                if widget is row:
                    self.ingredients_layout.removeWidget(widget)
                    widget.setParent(None)
                    self.ingredient_rows.pop(i)
                    break
        self.set_header()
        row = IngredientRow(self.inventory_items, remove_row, self.isRecipe, mat)
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

    def do_craft(self):
        ret = QMessageBox.question(
                self,
                "일치하지 않음",
                self.util.get_text_from_lang("ko", "msg_craft_process"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
        if ret == QMessageBox.Yes:
            self.process_craft()

    def process_craft(self):
        ingredient_dict = {}
        for row in self.ingredient_rows:
            name, qty, remaining_qty = row.get_value()
            
            if name:
                ingredient_dict[name] = remaining_qty        

        # 재료 소비 및 fee 이동
        total_transfer_fee = 0
        for item, transfer_fee in self.util.consume_ingredients_and_transfer_fee(ingredient_dict, self.output_count.value()):
            total_transfer_fee += transfer_fee

        # 산출물 fee에 (입력된 수수료 + 재료에서 넘긴 fee) 합산
        # 즉, add_inventory의 fee값에 위 transfer_fee를 더해서 호출해야함
        final_fee = self.fee.value() + total_transfer_fee
        self.util.add_inventory(self.name_select.currentText(), self.output_count.value(), final_fee)

        # minus fee or price from the item

        self.initialize_after_crafting()
     
    def calculate_ingredient_count(self):
        count = self.output_count.value()
        for ingredient_row in self.ingredient_rows:
            ingredient_row.qty.setValue(ingredient_row.qty.value() * count)
        

    def initialize_after_crafting(self):
        self.output_count.setValue(0)
        self.fee.setValue(0)
        for ingredient_row in self.ingredient_rows:
            ingredient_row.remaining_qty.setValue(0)

        self.select_changed()

    def set_header(self): 
        if self.isHeader == False:
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(""))
            hbox.addWidget(QLabel("현재 인벤토리내 갯수"))
            hbox.addWidget(QLabel("제작 후 인벤토리내 갯수"))
            self.ingredients_layout.addLayout(hbox)
            self.isHeader = True