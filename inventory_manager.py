import os
import json
import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QSpinBox, QPushButton, QMessageBox, QHBoxLayout
)

DATA_FILE = "material_data.json"

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}

def save_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

class InventoryManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("인벤토리")
        layout = QVBoxLayout()

        # 1. 검색/카테고리 위젯
        filter_layout = QHBoxLayout()
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("아이템명 검색")
        self.search_box.textChanged.connect(self.filter_materials)
        filter_layout.addWidget(QLabel("이름검색"))
        filter_layout.addWidget(self.search_box)
        self.category_select = QComboBox()
        self.category_select.addItem("전체")
        self.category_select.currentIndexChanged.connect(self.filter_materials)
        filter_layout.addWidget(QLabel("카테고리"))
        filter_layout.addWidget(self.category_select)
        layout.addLayout(filter_layout)

        # 2. 아이템선택 콤보
        self.material_select = QComboBox()
        self.material_select.addItem("새로 입력")
        self.material_select.currentIndexChanged.connect(self.load_selected_material)
        layout.addWidget(QLabel("재료(검색/선택)"))
        layout.addWidget(self.material_select)

        # 3. 아이템명/카테고리/인첸트 등 입력
        self.name = QLineEdit()
        layout.addWidget(QLabel("재료명"))
        layout.addWidget(self.name)
        self.category_input = QComboBox()
        # 카테고리 종류는 실제 데이터 로딩 이후 세팅
        layout.addWidget(QLabel("카테고리"))
        layout.addWidget(self.category_input)
        self.enchant = QComboBox()
        for i in range(0, 5):
            self.enchant.addItem(f"{i} 인첸트", i)
        layout.addWidget(QLabel("인첸트"))
        layout.addWidget(self.enchant)
        self.buy_price = QSpinBox()
        self.buy_price.setMaximum(9999999)
        layout.addWidget(QLabel("구매가격"))
        layout.addWidget(self.buy_price)
        self.fee = QSpinBox()
        self.fee.setMaximum(9999999)
        layout.addWidget(QLabel("제작시 수수료"))
        layout.addWidget(self.fee)
        self.count = QSpinBox()
        self.count.setMaximum(9999999)
        layout.addWidget(QLabel("재고수량"))
        layout.addWidget(self.count)
        self.market_price = QSpinBox()
        self.market_price.setMaximum(99999999)
        layout.addWidget(QLabel("시장가 입력"))
        layout.addWidget(self.market_price)
        self.market_price_time = QLabel("-")
        layout.addWidget(QLabel("시장가 입력일시"))
        layout.addWidget(self.market_price_time)
        btn_save = QPushButton("저장")
        btn_save.clicked.connect(self.save_material)
        layout.addWidget(btn_save)
        self.setLayout(layout)

        self.materials = {}
        self.load_materials()

    def load_materials(self):
        # 데이터 로딩 및 구조 보정
        raw = load_data(DATA_FILE)
        self.materials = {}
        category_set = set()
        for name, val in raw.items():
            # category/enchant 구조로 변환
            if isinstance(val, dict) and "enchant" in val:
                self.materials[name] = val
                if "category" in val:
                    category_set.add(val["category"])
            else:
                # 구버전 호환
                self.materials[name] = {
                    "category": "",
                    "enchant": val if isinstance(val, dict) else {"0": val}
                }
        # 카테고리 콤보 업데이트
        self.category_select.blockSignals(True)
        self.category_select.clear()
        self.category_select.addItem("전체")
        for c in sorted(category_set):
            if c: self.category_select.addItem(c)
        self.category_select.blockSignals(False)
        # 입력폼의 카테고리 선택도 동기화
        self.category_input.clear()
        self.category_input.addItem("")  # 공백(없음)
        for c in sorted(category_set):
            if c: self.category_input.addItem(c)
        self.filter_materials()

    def filter_materials(self, *args):
        name_filter = self.search_box.text().strip()
        category_filter = self.category_select.currentText()
        self.material_select.blockSignals(True)
        self.material_select.clear()
        self.material_select.addItem("새로 입력")
        for name, meta in self.materials.items():
            if category_filter != "전체" and meta.get("category","") != category_filter:
                continue
            if name_filter and name_filter not in name:
                continue
            self.material_select.addItem(name)
        self.material_select.blockSignals(False)

    def load_selected_material(self):
        idx = self.material_select.currentIndex()
        if idx == 0:  # 새로 입력
            self.name.setText("")
            self.category_input.setCurrentIndex(0)
            self.enchant.setCurrentIndex(0)
            self.buy_price.setValue(0)
            self.fee.setValue(0)
            self.count.setValue(0)
            self.market_price.setValue(0)
            self.market_price_time.setText("-")
        else:
            mat_name = self.material_select.currentText()
            meta = self.materials.get(mat_name, {})
            # 카테고리 표시
            category_val = meta.get("category","")
            cat_idx = self.category_input.findText(category_val)
            self.category_input.setCurrentIndex(cat_idx if cat_idx>=0 else 0)
            self.name.setText(mat_name)
            # 인첸트별 정보 로딩(기본 0인첸트)
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
        category = self.category_input.currentText()
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
            materials[n] = {"category": category, "enchant": {}}
        else:
            materials[n]["category"] = category
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
