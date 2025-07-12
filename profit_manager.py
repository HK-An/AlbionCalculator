import os
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox,
    QCheckBox, QLineEdit, QHBoxLayout
)

class ProfitManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("수익 정산")
        layout = QVBoxLayout()
        self.sale_list = QComboBox()
        self.detail = QLabel("-")

        # 판매가 수정부
        self.edit_enable = QCheckBox("총/개당 판매가 수정")
        self.unit_sale_edit = QLineEdit()
        self.total_sale_edit = QLineEdit()
        self.unit_sale_edit.setEnabled(False)
        self.total_sale_edit.setEnabled(False)

        self.edit_enable.stateChanged.connect(self.toggle_edit_enable)

        h1 = QHBoxLayout()
        h1.addWidget(QLabel("개당판매가"))
        h1.addWidget(self.unit_sale_edit)
        h2 = QHBoxLayout()
        h2.addWidget(QLabel("총판매가"))
        h2.addWidget(self.total_sale_edit)

        btn_recalc = QPushButton("재계산")
        btn_recalc.clicked.connect(self.recalculate)
        self.btn_done = QPushButton("거래완료")
        self.btn_done.clicked.connect(self.complete_sale)

        layout.addWidget(QLabel("판매 내역(미완료)"))
        layout.addWidget(self.sale_list)
        layout.addWidget(QLabel("상세"))
        layout.addWidget(self.detail)
        layout.addWidget(self.edit_enable)
        layout.addLayout(h1)
        layout.addLayout(h2)
        layout.addWidget(btn_recalc)
        layout.addWidget(self.btn_done)
        self.setLayout(layout)
        self.sale_list.currentIndexChanged.connect(self.show_detail)
        self.refresh_sales()

    def toggle_edit_enable(self):
        enabled = self.edit_enable.isChecked()
        self.unit_sale_edit.setEnabled(enabled)
        self.total_sale_edit.setEnabled(enabled)
        self.btn_done.setEnabled(not enabled)

    def refresh_sales(self):
        filename = "sale_data.json"
        self.sales = []
        self.sale_list.clear()
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
            for i, sale in enumerate(data):
                if sale.get("status") != "판매완료":
                    self.sales.append((i, sale))
                    # 인첸트 표시 추가
                    self.sale_list.addItem(
                        f"{sale.get('item','')} (인첸트{sale.get('enchant',0)}, "
                        f"개당판매가:{sale.get('unit_sale_price', sale.get('sale_price', '-'))}, "
                        f"총판매가:{sale.get('total_sale_price', sale.get('sale_price', '-'))}, "
                        f"이익:{sale.get('profit','-')})"
                    )
        self.show_detail()

    def show_detail(self):
        idx = self.sale_list.currentIndex()
        if idx < 0 or idx >= len(self.sales):
            self.detail.setText("-")
            # ... (생략)
            return
        i, sale = self.sales[idx]
        unit_sale = str(sale.get('unit_sale_price', sale.get('sale_price', '')))
        total_sale = str(sale.get('total_sale_price', sale.get('sale_price', '')))
        # 인첸트 표시
        self.detail.setText(
            f"아이템: {sale.get('item','')}\n"
            f"인첸트: {sale.get('enchant', 0)}\n"
            f"판매수량: {sale.get('count', '-')}\n"    # <- 추가
            f"구매가(1개): {sale.get('unit_buy_price', sale.get('buy_price', '-'))}\n"
            f"수수료(1개): {sale.get('unit_fee', sale.get('fee', '-'))}\n"
            f"총원가: {sale.get('total_cost', '-')}\n"
            f"개당판매가: {unit_sale}\n"
            f"총판매가: {total_sale}\n"
            f"이익: {sale.get('profit','-')}\n"
            f"상태: {sale.get('status','')}"
        )
        self.unit_sale_edit.setText(unit_sale)
        self.total_sale_edit.setText(total_sale)
        self.edit_enable.setChecked(False)
        self.toggle_edit_enable()

    def recalculate(self):
        idx = self.sale_list.currentIndex()
        if idx < 0 or idx >= len(self.sales):
            return
        rec_idx, sale = self.sales[idx]
        try:
            new_unit = float(self.unit_sale_edit.text())
            new_total = float(self.total_sale_edit.text())
        except Exception:
            QMessageBox.warning(self, "오류", "판매가 입력 오류")
            return
        count = sale.get("count", 1)
        calc_total = round(new_unit * count, 2)
        if abs(calc_total - new_total) > 0.01:
            ret = QMessageBox.question(
                self,
                "일치하지 않음",
                f"개당×수량={calc_total} 이지만, 총판매가={new_total} 입니다.\n"
                "어떤 값을 기준으로 저장할까요? (Yes:개당 판매가 기준 || NO:총 판매가 기준)",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            if ret == QMessageBox.Yes:
                # 개당판매가 기준으로 총판매가 덮어쓰기
                new_total = calc_total
                self.total_sale_edit.setText(str(new_total))
            else:
                # 총판매가 기준으로 개당판매가 덮어쓰기
                if count > 0:
                    new_unit = round(new_total / count, 2)
                self.unit_sale_edit.setText(str(new_unit))
        # 저장
        filename = "sale_data.json"
        with open(filename, "r") as f:
            data = json.load(f)
        data[rec_idx]["unit_sale_price"] = new_unit
        data[rec_idx]["total_sale_price"] = new_total
        # profit도 갱신
        a = data[rec_idx].get("unit_buy_price", 0) + data[rec_idx].get("unit_fee", 0)
        profit = (new_unit - a) * count
        data[rec_idx]["profit"] = profit
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        QMessageBox.information(self, "알림", "재계산 및 저장 완료")
        self.refresh_sales()

    def complete_sale(self):
        idx = self.sale_list.currentIndex()
        if idx < 0 or idx >= len(self.sales):
            return
        rec_idx, sale = self.sales[idx]
        filename = "sale_data.json"
        with open(filename, "r") as f:
            data = json.load(f)
        data[rec_idx]["status"] = "판매완료"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        QMessageBox.information(self, "알림", "거래완료 처리됨")
        self.refresh_sales()