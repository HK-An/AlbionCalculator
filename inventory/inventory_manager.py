import os
import json
import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QSpinBox, QMessageBox, QDoubleSpinBox
)
from inventory.crafting_manager import CraftingManager
from util import Util

CATEGORY_FILE = "category.json"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, '', 'material_data.json')

def load_data(filename):
    with open(filename, encoding="utf-8") as f:
        return json.load(f)

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_category_tree():
    with open(CATEGORY_FILE, encoding="utf-8") as f:
        return json.load(f)

def get_category_path_from_index(cat_tree, idx_list):
    names = []
    node = cat_tree
    for idx in idx_list:
        idx_str = str(idx)
        if idx_str in node:
            names.append(node[idx_str]["name"])
            node = node[idx_str].get("category", {})
        else:
            break
    return names

class InventoryManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("인벤토리")
        self.lang = "ko"
        self.util = Util(self.lang)

        self.cat_tree = load_category_tree()
        self.init_fields()
        self.setup_ui()
        self.load_materials()

    def init_fields(self):
        self.material_select = QComboBox()
        self.name = QLineEdit()
        self.key = QLineEdit()

        self.cat_box1 = QComboBox()
        self.cat_box2 = QComboBox()
        self.cat_box3 = QComboBox()
        self.cat_box4 = QComboBox()

        self.enchant = QComboBox()
        for i in range(5):
            self.enchant.addItem(str(i), i)

        self.buy_price = QSpinBox()
        self.buy_price.setMaximum(9999999)

        self.fee = QSpinBox()
        self.fee.setMaximum(9999999)

        self.count = QSpinBox()
        self.count.setMaximum(9999999)

        self.production_fee = QDoubleSpinBox()
        self.production_fee.setMaximum(9999999)

        self.market_price = QSpinBox()
        self.market_price_time = QLineEdit()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.add_material_selector(layout)
        self.add_name_input(layout)
        self.add_category_boxes(layout)
        self.add_enchant_section(layout)
        self.add_price_fields(layout)
        self.add_action_buttons(layout)

        self.setLayout(layout)

    def add_material_selector(self, layout):
        self.material_select.addItem(self.util.get_text_from_lang(self.lang, "combo_new"))
        self.material_select.currentIndexChanged.connect(self.load_selected_material)
        layout.addWidget(self.material_select)

    def add_name_input(self, layout):
        layout.addWidget(QLabel(self.util.get_text_from_lang(self.lang, "label_name")))
        layout.addWidget(self.name)
        layout.addWidget(QLabel("저장할키"))
        layout.addWidget(self.key)
        

    def add_category_boxes(self, layout):
        layout.addWidget(QLabel(self.util.get_text_from_lang(self.lang, "label_category")))
        cat_layout = QHBoxLayout()
        for box in [self.cat_box1, self.cat_box2, self.cat_box3, self.cat_box4]:
            box.currentIndexChanged.connect(self.update_category_boxes)
            cat_layout.addWidget(box)
        layout.addLayout(cat_layout)

    def add_enchant_section(self, layout):
        layout.addWidget(QLabel(self.util.get_text_from_lang(self.lang, "label_enchant")))
        layout.addWidget(self.enchant)

    def add_price_fields(self, layout):
        layout.addWidget(QLabel(self.util.get_text_from_lang(self.lang, "label_bought_price")))
        layout.addWidget(self.buy_price)

        layout.addWidget(QLabel(self.util.get_text_from_lang(self.lang, "label_fee")))
        layout.addWidget(self.fee)

        layout.addWidget(QLabel(self.util.get_text_from_lang(self.lang, "label_count")))
        layout.addWidget(self.count)

        layout.addWidget(QLabel(self.util.get_text_from_lang(self.lang, "label_price_per_production")))
        layout.addWidget(self.production_fee)

        layout.addWidget(QLabel(self.util.get_text_from_lang(self.lang, "label_market_price")))
        layout.addWidget(self.market_price)

        layout.addWidget(QLabel(self.util.get_text_from_lang(self.lang, "label_market_price_entered_time")))
        layout.addWidget(self.market_price_time)

    def add_action_buttons(self, layout):
        saveBtn = QPushButton(self.util.get_text_from_lang(self.lang, "btn_save"))
        saveBtn.clicked.connect(self.save_material)
        layout.addWidget(saveBtn)

        craftingBtn = QPushButton(self.util.get_text_from_lang(self.lang, "btn_craft"))
        craftingBtn.clicked.connect(self.open_crafting)
        layout.addWidget(craftingBtn)
    
    def open_crafting(self):
        self.crafting_manager = CraftingManager()
        self.crafting_manager.show()

#  category
    def update_category_boxes(self):
        node = self.cat_tree
        boxes = [self.cat_box1, self.cat_box2, self.cat_box3, self.cat_box4]
        idx_list = [box.currentData() for box in boxes]
        for depth, box in enumerate(boxes):
            # 하위 후보 갱신 전 block
            box.blockSignals(True)
            box.clear()
            box.addItem("")
            if node and isinstance(node, dict):
                print("[ category ]")
                for k in sorted(node.keys(), key=int):
                    print(node[k]["name"])
                    box.addItem(self.util.get_text_from_lang(self.lang, node[k]["name"]), int(k))
            # 현재 선택값 복구
            idx = idx_list[depth]
            if idx is not None and idx in [box.itemData(i) for i in range(box.count()) if box.itemData(i) is not None]:
                # 값이 있으면 복구
                for i in range(box.count()):
                    if box.itemData(i) == idx:
                        box.setCurrentIndex(i)
                        break
            else:
                box.setCurrentIndex(0)
            box.blockSignals(False)
            # 다음 노드 이동
            if box.currentIndex() > 0:
                node = node.get(str(box.currentData()), {}).get("category", {})
            else:
                node = None

    def get_selected_category_index(self):
        boxes = [self.cat_box1, self.cat_box2, self.cat_box3, self.cat_box4]
        idx_list = []
        for box in boxes:
            idx = box.currentData()
            if idx is not None:
                idx_list.append(idx)
            else:
                break
        return idx_list

    def set_category_boxes_by_index(self, idx_list):
        node = self.cat_tree
        boxes = [self.cat_box1, self.cat_box2, self.cat_box3, self.cat_box4]
        # 1단계(최상위) 후보는 무조건 채우기
        box = boxes[0]
        box.blockSignals(True)
        box.clear()
        box.addItem("")
        if isinstance(node, dict):
            for k in sorted(node.keys(), key=int):
                box.addItem(self.util.get_text_from_lang(self.lang, node[k]["name"]), int(k))
        if idx_list and len(idx_list) > 0:
            box.setCurrentIndex(idx_list[0] + 1)
            node = node.get(str(idx_list[0]), {}).get("category", {})
        else:
            box.setCurrentIndex(0)
            node = None
        box.blockSignals(False)
        # 2~4단계는 idx_list 기반으로만 후보 채움
        for i in range(1, 4):
            box = boxes[i]
            box.blockSignals(True)
            box.clear()
            box.addItem("")
            if node and isinstance(node, dict):
                for k in sorted(node.keys(), key=int):
                    box.addItem(self.util.get_text_from_lang(self.lang, node[k]["name"]), int(k))
            if idx_list and len(idx_list) > i:
                box.setCurrentIndex(idx_list[i] + 1)
                node = node.get(str(idx_list[i]), {}).get("category", {}) if node else None
            else:
                box.setCurrentIndex(0)
                node = None
            box.blockSignals(False)
#   cateogry end

    def load_materials(self):
        # material_data.json에서 불러오기
        try:
            raw = load_data(DATA_FILE)
        except:
            raw = {}
        self.materials = raw
        self.material_select.blockSignals(True)
        self.material_select.clear()
        self.material_select.addItem(self.util.get_text_from_lang(self.lang, "combo_new"))
        print("[ load item ]")
        for name in self.materials:
            print(name)
            self.material_select.addItem(self.util.get_text_from_lang(self.lang, name))
        self.material_select.blockSignals(False)
        self.update_category_boxes()

    def load_selected_material(self):
        idx = self.material_select.currentIndex()
        if idx == 0:  # 새로 입력
            self.name.setText("")
            self.set_category_boxes_by_index([])
            self.enchant.setCurrentIndex(0)
            self.buy_price.setValue(0)
            self.fee.setValue(0)
            self.count.setValue(0)
            self.market_price.setValue(0)
            self.market_price_time.setText("-")
        else:
            mat_name = self.material_select.currentText()
            key = self.util.get_key_from_lang(self.lang, mat_name)
            self.key.setText(key)
            meta = self.materials.get(key, {})
            # 카테고리
            cat_idx = meta.get("category", [])
            self.set_category_boxes_by_index(cat_idx)
            self.name.setText(mat_name)
            # 인첸트
            enchants = meta.get("enchant", {})
            ench_str = str(self.enchant.currentData()) if self.enchant.currentData() is not None else "0"
            mat = enchants.get(ench_str, {})
            self.buy_price.setValue(mat.get("buy_price", 0))
            self.fee.setValue(mat.get("fee", 0))
            self.count.setValue(mat.get("count", 0))
            self.production_fee.setValue(self.calculate_production_fee(mat.get("fee", 0), mat.get("count", 0)))
            self.market_price.setValue(mat.get("market_price", 0))
            t = mat.get("market_price_time", None)
            self.market_price_time.setText(str(t) if t else "-")
            
    def calculate_production_fee(self, fee, count):
        if fee == 0: return 0
        
        return fee/count
    
    def save_material(self):
        is_new = False
        materials = load_data(DATA_FILE)
        item_name = self.name.text()
        item_key = self.util.get_key_from_lang(self.lang, item_name)
        if item_key == None:
            item_key = self.key.text()
            is_new = True
        buy_price = self.buy_price.value()
        fee = self.fee.value()
        count = self.count.value()
        market_price = self.market_price.value()

        enchant = str(self.enchant.currentData())
        category_idx = self.get_selected_category_index()
        now = datetime.datetime.now().isoformat(sep=" ", timespec="seconds") if market_price else materials.get(item_key, {}).get("enchant", {}).get(enchant, {}).get("market_price_time")
        if not item_key:
            QMessageBox.warning(self, "경고", self.util.get_text_from_lang(self.lang, "msg_enter_ingredient_name"))
            return
        # 중복 체크
        if self.material_select.currentIndex() == 0 and item_key in materials:
            QMessageBox.warning(self, "경고", self.util.get_text_from_lang(self.lang, "msg_item_is_already_exists"))
            return
        # 구조 맞추기
        if item_key not in materials or not isinstance(materials[item_key], dict):
            materials[item_key] = {"category": category_idx, "enchant": {}}
        else:
            materials[item_key]["category"] = category_idx
        if "enchant" not in materials[item_key]:
            materials[item_key]["enchant"] = {}
        materials[item_key]["enchant"][enchant] = {
            "buy_price": buy_price,
            "fee": fee,
            "count": count,
            "market_price": market_price,
            "market_price_time": now
        }
        save_data(DATA_FILE, materials)
        if is_new:
            self.util.add_lang(self.lang, item_key, item_name)
        QMessageBox.information(self, "알림", "저장됨")
        self.load_materials()
        self.material_select.setCurrentText(item_name)
