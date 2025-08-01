import json
import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QSpinBox, QMessageBox
)

DATA_FILE = "material_data.json"
CATEGORY_FILE = "category.json"

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
        layout = QVBoxLayout()

        # 재료 선택
        self.material_select = QComboBox()
        self.material_select.addItem("새로 입력")
        self.material_select.currentIndexChanged.connect(self.load_selected_material)
        layout.addWidget(self.material_select)

        # 이름 입력
        self.name = QLineEdit()
        layout.addWidget(QLabel("이름"))
        layout.addWidget(self.name)

        # 카테고리 콤보박스 4단계
        self.cat_box1 = QComboBox()
        self.cat_box2 = QComboBox()
        self.cat_box3 = QComboBox()
        self.cat_box4 = QComboBox()
        for box in [self.cat_box1, self.cat_box2, self.cat_box3, self.cat_box4]:
            box.currentIndexChanged.connect(self.update_category_boxes)
        cat_layout = QHBoxLayout()
        for box in [self.cat_box1, self.cat_box2, self.cat_box3, self.cat_box4]:
            cat_layout.addWidget(box)
        layout.addWidget(QLabel("카테고리"))
        layout.addLayout(cat_layout)

        # 인첸트, 가격 등 기타 필드
        self.enchant = QComboBox()
        for i in range(5): self.enchant.addItem(str(i), i)
        self.buy_price = QSpinBox()
        self.fee = QSpinBox()
        self.count = QSpinBox()
        self.market_price = QSpinBox()
        self.market_price_time = QLineEdit()
        layout.addWidget(QLabel("인첸트"))
        layout.addWidget(self.enchant)
        layout.addWidget(QLabel("구매가"))
        layout.addWidget(self.buy_price)
        layout.addWidget(QLabel("수수료"))
        layout.addWidget(self.fee)
        layout.addWidget(QLabel("수량"))
        layout.addWidget(self.count)
        layout.addWidget(QLabel("시장가"))
        layout.addWidget(self.market_price)
        layout.addWidget(QLabel("시장가입력시각"))
        layout.addWidget(self.market_price_time)

        # 버튼
        btn = QPushButton("저장")
        btn.clicked.connect(self.save_material)
        layout.addWidget(btn)

        self.setLayout(layout)
        self.cat_tree = load_category_tree()
        self.load_materials()

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
                for k in sorted(node.keys(), key=int):
                    box.addItem(node[k]["name"], int(k))
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
    # def update_category_boxes(self):
    #     node = self.cat_tree
    #     boxes = [self.cat_box1, self.cat_box2, self.cat_box3, self.cat_box4]
    #     idx_list = []
    #     # 1~4단계 현재 선택값 저장
    #     for box in boxes:
    #         idx = box.currentData()
    #         idx_list.append(idx)
    #     # 1단계(최상위) 후보는 항상 채우기
    #     box = boxes[0]
    #     sel_idx = box.currentIndex()
    #     box.blockSignals(True)
    #     box.clear()
    #     box.addItem("")
    #     if isinstance(node, dict):
    #         for k in sorted(node.keys(), key=int):
    #             box.addItem(node[k]["name"], int(k))
    #     box.blockSignals(False)
    #     # 선택값 복구
    #     if sel_idx > 0 and sel_idx < box.count():
    #         box.setCurrentIndex(sel_idx)
    #     else:
    #         box.setCurrentIndex(0)
    #     # 하위단계
    #     for depth in range(1, 4):
    #         prev = boxes[depth - 1]
    #         prev_idx = prev.currentData()
    #         node = node.get(str(prev_idx), {}).get("category", {}) if prev_idx is not None and node else None
    #         box = boxes[depth]
    #         sel_idx = box.currentIndex()
    #         box.blockSignals(True)
    #         box.clear()
    #         box.addItem("")
    #         if node and isinstance(node, dict):
    #             for k in sorted(node.keys(), key=int):
    #                 box.addItem(node[k]["name"], int(k))
    #         box.blockSignals(False)
    #         if sel_idx > 0 and sel_idx < box.count():
    #             box.setCurrentIndex(sel_idx)
    #         else:
    #             box.setCurrentIndex(0)
    # def update_category_boxes(self):
    #     # 단계별 카테고리 후보 갱신
    #     node = self.cat_tree
    #     boxes = [self.cat_box1, self.cat_box2, self.cat_box3, self.cat_box4]
    #     for depth, box in enumerate(boxes):
    #         prev_idx = box.currentData()
    #         box.blockSignals(True)
    #         box.clear()
    #         box.addItem("")
    #         if isinstance(node, dict):
    #             for k in sorted(node.keys(), key=int):
    #                 box.addItem(node[k]["name"], int(k))
    #         box.blockSignals(False)
    #         # 다음 단계로 진입
    #         if box.currentIndex() > 0:
    #             idx = box.currentData()
    #             node = node.get(str(idx), {}).get("category", {})
    #         else:
    #             # 하위박스 초기화
    #             for b in boxes[depth+1:]:
    #                 b.blockSignals(True)
    #                 b.clear()
    #                 b.addItem("")
    #                 b.blockSignals(False)
    #             break

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

    # def set_category_boxes_by_index(self, idx_list):
    #     node = self.cat_tree
    #     boxes = [self.cat_box1, self.cat_box2, self.cat_box3, self.cat_box4]
    #     for i, idx in enumerate(idx_list):
    #         box = boxes[i]
    #         box.blockSignals(True)
    #         box.clear()
    #         box.addItem("")
    #         if isinstance(node, dict):
    #             for k in sorted(node.keys(), key=int):
    #                 box.addItem(node[k]["name"], int(k))
    #         box.setCurrentIndex(idx + 1)  # 0: ""(공백), 1: 0번 index ...
    #         box.blockSignals(False)
    #         # 다음 단계로 진입
    #         node = node.get(str(idx), {}).get("category", {})
    #     # 나머지 하위는 공백으로 초기화
    #     for j in range(len(idx_list), 4):
    #         boxes[j].blockSignals(True)
    #         boxes[j].clear()
    #         boxes[j].addItem("")
    #         boxes[j].blockSignals(False)
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
                box.addItem(node[k]["name"], int(k))
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
                    box.addItem(node[k]["name"], int(k))
            if idx_list and len(idx_list) > i:
                box.setCurrentIndex(idx_list[i] + 1)
                node = node.get(str(idx_list[i]), {}).get("category", {}) if node else None
            else:
                box.setCurrentIndex(0)
                node = None
            box.blockSignals(False)

    def load_materials(self):
        # material_data.json에서 불러오기
        try:
            raw = load_data(DATA_FILE)
        except:
            raw = {}
        self.materials = raw
        self.material_select.blockSignals(True)
        self.material_select.clear()
        self.material_select.addItem("새로 입력")
        for name in self.materials:
            self.material_select.addItem(name)
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
            meta = self.materials.get(mat_name, {})
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
            self.market_price.setValue(mat.get("market_price", 0))
            t = mat.get("market_price_time", None)
            self.market_price_time.setText(str(t) if t else "-")

    def save_material(self):
        materials = load_data(DATA_FILE)
        n = self.name.text()
        b = self.buy_price.value()
        f = self.fee.value()
        c = self.count.value()
        m = self.market_price.value()
        enchant = str(self.enchant.currentData())
        category_idx = self.get_selected_category_index()
        now = datetime.datetime.now().isoformat(sep=" ", timespec="seconds") if m else materials.get(n, {}).get("enchant", {}).get(enchant, {}).get("market_price_time")
        if not n:
            QMessageBox.warning(self, "경고", "재료명을 입력하세요")
            return
        # 중복 체크
        if self.material_select.currentIndex() == 0 and n in materials:
            QMessageBox.warning(self, "경고", "이미 존재하는 아이템입니다. 수정하려면 리스트에서 선택하세요.")
            return
        # 구조 맞추기
        if n not in materials or not isinstance(materials[n], dict):
            materials[n] = {"category": category_idx, "enchant": {}}
        else:
            materials[n]["category"] = category_idx
        if "enchant" not in materials[n]:
            materials[n]["enchant"] = {}
        materials[n]["enchant"][enchant] = {
            "buy_price": b,
            "fee": f,
            "count": c,
            "market_price": m,
            "market_price_time": now
        }
        save_data(DATA_FILE, materials)
        QMessageBox.information(self, "알림", "저장됨")
        self.load_materials()
        self.material_select.setCurrentText(n)
