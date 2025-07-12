import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QSpinBox, QPushButton, QMessageBox
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

class SaleRegister(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("판매등록")
        self.materials = {}
        layout = QVBoxLayout()
        self.item_select = QComboBox()
        self.enchant_select = QComboBox()
        for i in range(0, 5):
            self.enchant_select.addItem(f"{i} 인첸트", i)
        self.buy_price_label = QLabel("-")
        self.fee_label = QLabel("-")
        self.sum_label = QLabel("-")
        self.count_spin = QSpinBox()
        self.count_spin.setMaximum(99999999)
        self.sale_price = QSpinBox()
        self.sale_price.setMaximum(99999999)
        btn_calc = QPushButton("계산")
        btn_calc.clicked.connect(self.calc_profit)
        btn_register = QPushButton("등록")
        btn_register.clicked.connect(self.register_sale)
        self.result = QLabel("-")

        layout.addWidget(QLabel("판매할 아이템 선택"))
        layout.addWidget(self.item_select)
        layout.addWidget(QLabel("인첸트 선택"))
        layout.addWidget(self.enchant_select)
        layout.addWidget(QLabel("구매가(1개)"))
        layout.addWidget(self.buy_price_label)
        layout.addWidget(QLabel("수수료(1개)"))
        layout.addWidget(self.fee_label)
        layout.addWidget(QLabel("구매가+수수료(1개)"))
        layout.addWidget(self.sum_label)
        layout.addWidget(QLabel("판매수량"))
        layout.addWidget(self.count_spin)
        layout.addWidget(QLabel("판매가(1개 기준 시장가)"))
        layout.addWidget(self.sale_price)
        layout.addWidget(btn_calc)
        layout.addWidget(QLabel("손익 결과"))
        layout.addWidget(self.result)
        layout.addWidget(btn_register)
        self.setLayout(layout)

        self.item_select.currentIndexChanged.connect(self.update_item_info)
        self.enchant_select.currentIndexChanged.connect(self.update_item_info)
        self.refresh_items()

    def refresh_items(self):
        self.item_select.clear()
        self.enchant_select.clear()
        materials = load_data(DATA_FILE)
        self.materials = materials
        # 아이템명별로 "갯수 1개 이상인 인첸트"만 콤보에 추가
        filtered_items = []
        for item_name, enchants in materials.items():
            for enchant_str, mat in enchants.items():
                if mat.get("count", 0) > 0:
                    filtered_items.append((item_name, enchant_str))
                    break  # 이 아이템은 보여주기(최소 1개라도 인첸트가 있으면)
        for item_name, _ in filtered_items:
            self.item_select.addItem(item_name)
        # 인첸트 콤보도 해당 아이템에서 count>0인 인첸트만
        self.item_select.currentIndexChanged.connect(self.refresh_enchants)
        self.refresh_enchants()

    def refresh_enchants(self):
        self.enchant_select.blockSignals(True)
        self.enchant_select.clear()
        item = self.item_select.currentText()
        enchants = self.materials.get(item, {})
        for enchant_str, mat in enchants.items():
            if mat.get("count", 0) > 0:
                self.enchant_select.addItem(f"{enchant_str} 인첸트", int(enchant_str))
        self.enchant_select.blockSignals(False)
        self.update_item_info()

    def update_item_info(self):
        item = self.item_select.currentText()
        enchant = str(self.enchant_select.currentData())
        mat = self.materials.get(item, {}).get(enchant, {})
        self.buy_price_label.setText(str(mat.get("buy_price", "-")))
        self.fee_label.setText(str(mat.get("fee", "-")))
        try:
            self.sum_label.setText(str(mat["buy_price"] + mat["fee"]))
        except:
            self.sum_label.setText("-")
        self.result.setText("-")
        market_price = mat.get("market_price", None)
        if market_price is not None:
            self.sale_price.setValue(market_price)

    def calc_profit(self):
        item = self.item_select.currentText()
        enchant = str(self.enchant_select.currentData())
        mat = self.materials.get(item, {}).get(enchant, {})
        if not mat:
            self.result.setText("아이템/인첸트 정보 없음")
            return
        cnt = self.count_spin.value()
        a = (mat.get("buy_price", 0) + mat.get("fee", 0)) * cnt
        b = self.sale_price.value() * cnt
        unit_profit = self.sale_price.value() - (mat.get("buy_price", 0) + mat.get("fee", 0))
        total_profit = b - a
        self.result.setText(
            f"개당 이익: {unit_profit} ({'이익' if unit_profit > 0 else '손해'})\n"
            f"총 이익: {total_profit} ({'이익' if total_profit > 0 else '손해'})"
        )

    def register_sale(self):
        item = self.item_select.currentText()
        enchant = str(self.enchant_select.currentData())
        mat = self.materials.get(item, {}).get(enchant, {})
        if not mat:
            QMessageBox.warning(self, "경고", "아이템/인첸트 정보 없음")
            return
        cnt = self.count_spin.value()
        stock = mat.get("count", 0)
        if cnt <= 0:
            QMessageBox.warning(self, "경고", "판매수량을 입력하세요")
            return
        if stock < cnt:
            QMessageBox.warning(self, "경고", f"재고 부족 (보유:{stock}, 요청:{cnt})")
            return

        a = (mat.get("buy_price", 0) + mat.get("fee", 0)) * cnt
        b = self.sale_price.value() * cnt
        unit_profit = self.sale_price.value() - (mat.get("buy_price", 0) + mat.get("fee", 0))
        profit = b - a

        # 인벤토리에서 차감
        materials = load_data(DATA_FILE)
        if item not in materials or enchant not in materials[item]:
            QMessageBox.warning(self, "경고", "인벤토리 정보 오류")
            return
        materials[item][enchant]["count"] = stock - cnt
        save_data(DATA_FILE, materials)

        # sale_data.json에 append
        filename = "sale_data.json"
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
        else:
            data = []
        data.append({
            "item": item,
            "enchant": int(enchant),
            "unit_buy_price": mat.get("buy_price", 0),
            "unit_fee": mat.get("fee", 0),
            "unit_cost": mat.get("buy_price", 0) + mat.get("fee", 0),
            "count": cnt,
            "total_cost": a,
            "unit_sale_price": self.sale_price.value(),
            "total_sale_price": self.sale_price.value() * cnt,
            "profit": profit
        })
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        QMessageBox.information(self, "알림", "판매등록 완료")
        self.refresh_items()