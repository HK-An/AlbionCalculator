import sys
import datetime
import json
import os
from profit_manager import ProfitManager
from sale_register import SaleRegister
from inventory_manager import InventoryManager
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QComboBox, QMessageBox, QSpinBox
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
        if self._recipe_window is None:
            self._recipe_window = RecipeManager()
        self._recipe_window.show()

    def open_calc(self):
        self._calc_window = RecipeCalc()
        self._calc_window.show()

    def open_sale(self):
        self._sale_window = SaleRegister()
        self._sale_window.show()


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
        self.materials = QTextEdit()
        self.materials.setPlaceholderText("재료명:수량 (줄바꿈 구분)")

        layout.addWidget(QLabel("레시피명"))
        layout.addWidget(self.recipe_name)
        layout.addWidget(QLabel("제작산출갯수"))
        layout.addWidget(self.output_count)
        layout.addWidget(QLabel("재료:수량"))
        layout.addWidget(self.materials)

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

    def load_recipes(self):
        self.recipes = load_data(RECIPE_FILE)
        self.name_select.blockSignals(True)
        self.name_select.clear()
        self.name_select.addItem("새로 입력")
        for name in self.recipes:
            self.name_select.addItem(name)
        self.name_select.blockSignals(False)

    def set_editable(self, enable):
        self.recipe_name.setEnabled(enable)
        self.output_count.setEnabled(enable)
        self.materials.setEnabled(enable)

    def select_changed(self):
        idx = self.name_select.currentIndex()
        if idx == 0:
            self.set_editable(True)
            self.recipe_name.setText("")
            self.output_count.setValue(1)
            self.materials.setPlainText("")
            self.btn_edit.setEnabled(False)
        else:
            key = self.name_select.currentText()
            rec = self.recipes.get(key, {})
            self.recipe_name.setText(rec.get("name", key))
            self.output_count.setValue(rec.get("output_count", 1))
            mats = rec.get("materials", {})
            self.materials.setPlainText(
                "\n".join(f"{k}:{v}" for k, v in mats.items())
            )
            self.set_editable(False)
            self.btn_edit.setEnabled(True)

    def enable_edit(self):
        self.set_editable(True)
        self.editing = True

    def load_selected_recipe(self):
        idx = self.recipe_select.currentIndex()
        if idx == 0:  # 새로 입력
            self.name.setText("")
            self.output.setValue(1)
            self.materials.setPlainText("")
        else:
            rname = self.recipe_select.currentText()
            recipe = self.recipes.get(rname, {})
            self.name.setText(rname)
            self.output.setValue(recipe.get("output", 1))
            mats = recipe.get("materials", {})
            lines = [f"{k}:{v}" for k, v in mats.items()]
            self.materials.setPlainText("\n".join(lines))

    def save_recipe(self):
        n = self.recipe_name.text()
        out_cnt = self.output_count.value()
        mats = {}
        for l in self.materials.toPlainText().splitlines():
            try:
                k, v = l.split(":")
                mats[k.strip()] = int(v)
            except:
                QMessageBox.warning(self, "경고", f"형식오류: {l}")
                return
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


class RecipeCalc(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("제작비용 계산")
        layout = QVBoxLayout()
        self.recipe_select = QComboBox()
        self.refresh_recipes()
        btn_calc = QPushButton("계산")
        btn_calc.clicked.connect(self.calc_cost)
        btn_make = QPushButton("제작")
        btn_make.clicked.connect(self.make_recipe)
        self.market = QSpinBox()
        self.market.setMaximum(99999999)
        self.result = QLabel("-")

        layout.addWidget(QLabel("레시피 선택"))
        layout.addWidget(self.recipe_select)
        layout.addWidget(QLabel("시장가 입력 (1회 생산 기준)"))
        layout.addWidget(self.market)
        layout.addWidget(btn_calc)
        layout.addWidget(btn_make)
        layout.addWidget(QLabel("손익/제작 결과"))
        layout.addWidget(self.result)
        self.setLayout(layout)

    def refresh_recipes(self):
        self.recipe_select.clear()
        recipes = load_data(RECIPE_FILE)
        self.recipes = recipes
        for r in recipes:
            self.recipe_select.addItem(r)

    def calc_cost(self):
        recipe_name = self.recipe_select.currentText()
        recipes = self.recipes
        materials = load_data(DATA_FILE)
        if recipe_name not in recipes:
            self.result.setText("레시피 없음")
            return
        recipe = recipes[recipe_name]
        mats = recipe["materials"]
        output_cnt = recipe.get("output", 1)
        total = 0
        fee_total = 0
        for mat, cnt in mats.items():
            if mat in materials:
                buy = materials[mat]["buy_price"]
                fee = materials[mat]["fee"]
                total += buy * cnt
                fee_total += fee
            else:
                self.result.setText(f"{mat} 정보 없음")
                return
        craft_cost = total + fee_total
        # 단가
        if output_cnt > 0:
            unit_cost = craft_cost / output_cnt
        else:
            unit_cost = 0
        market_price = self.market.value()
        profit = market_price - unit_cost
        msg = f"총 제작비용(1회 제작): {craft_cost}\n" \
              f"산출 갯수: {output_cnt}\n" \
              f"개당 제작단가: {unit_cost:.2f}\n" \
              f"시장가-단가 손익: {profit:.2f} ({'이익' if profit > 0 else '손해'})"
        self.result.setText(msg)

    def make_recipe(self):
        recipe_name = self.recipe_select.currentText()
        recipes = self.recipes
        materials = load_data(DATA_FILE)
        if recipe_name not in recipes:
            self.result.setText("레시피 없음")
            return
        recipe = recipes[recipe_name]
        mats = recipe["materials"]
        output_cnt = recipe.get("output", 1)

        # 재고 충분성 확인 (산출 갯수만큼)
        for mat, cnt in mats.items():
            if mat not in materials:
                self.result.setText(f"{mat} 정보 없음")
                return
            if materials[mat].get("count", 0) < cnt * output_cnt:
                self.result.setText(f"{mat} 재고 부족 (필요: {cnt * output_cnt}, 보유: {materials[mat].get('count', 0)})")
                return

        # 차감 및 저장
        for mat, cnt in mats.items():
            materials[mat]["count"] -= cnt * output_cnt
        save_data(DATA_FILE, materials)
        self.result.setText(f"제작 성공, 재고 {output_cnt}개분 차감 완료")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
