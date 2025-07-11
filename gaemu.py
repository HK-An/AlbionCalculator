import sys
import datetime
import json
import os
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

        btn_inv.clicked.connect(self.open_inventory)
        btn_recipe.clicked.connect(self.open_recipe)
        btn_calc.clicked.connect(self.open_calc)
        btn_sale.clicked.connect(self.open_sale)

        layout.addWidget(btn_inv)
        layout.addWidget(btn_recipe)
        layout.addWidget(btn_calc)
        layout.addWidget(btn_sale)
        self.setLayout(layout)

        self._inventory_window = None
        self._recipe_window = None
        self._calc_window = None
        self._sale_window = None

    def open_inventory(self):
        if self._inventory_window is None:
            self._inventory_window = InventoryManager()
        self._inventory_window.show()

    def open_recipe(self):
        if self._recipe_window is None:
            self._recipe_window = RecipeManager()
        self._recipe_window.show()

    def open_calc(self):
        if self._calc_window is None:
            self._calc_window = RecipeCalc()
        self._calc_window.show()

    def open_sale(self):
        if self._sale_window is None:
            self._sale_window = SaleRegister()
        self._sale_window.show()



# class MaterialInput(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("재료 입력")
#         layout = QVBoxLayout()
#         self.name = QLineEdit()
#         self.buy_price = QSpinBox()
#         self.buy_price.setMaximum(9999999)
#         self.fee = QSpinBox()
#         self.fee.setMaximum(9999999)
#         btn = QPushButton("저장")
#         btn.clicked.connect(self.save_material)

#         layout.addWidget(QLabel("재료명"))
#         layout.addWidget(self.name)
#         layout.addWidget(QLabel("구매가격"))
#         layout.addWidget(self.buy_price)
#         layout.addWidget(QLabel("제작시 수수료"))
#         layout.addWidget(self.fee)
#         layout.addWidget(btn)
#         self.setLayout(layout)

#     def save_material(self):
#         materials = load_data(DATA_FILE)
#         n = self.name.text()
#         b = self.buy_price.value()
#         f = self.fee.value()
#         if not n:
#             QMessageBox.warning(self, "경고", "재료명을 입력하세요")
#             return
#         materials[n] = {"buy_price": b, "fee": f}
#         save_data(DATA_FILE, materials)
#         QMessageBox.information(self, "알림", "저장됨")
class InventoryManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("인벤토리")
        layout = QVBoxLayout()
        self.material_select = QComboBox()
        self.material_select.addItem("새로 입력")
        self.load_materials()
        self.material_select.currentIndexChanged.connect(self.load_selected_material)

        self.name = QLineEdit()
        self.buy_price = QSpinBox()
        self.buy_price.setMaximum(9999999)
        self.fee = QSpinBox()
        self.fee.setMaximum(9999999)
        self.count = QSpinBox()
        self.count.setMaximum(9999999)
        self.market_price = QSpinBox()
        self.market_price.setMaximum(99999999)
        self.market_price_time = QLabel("-")
        btn_save = QPushButton("저장")
        btn_save.clicked.connect(self.save_material)

        layout.addWidget(QLabel("재료(검색/선택)"))
        layout.addWidget(self.material_select)
        layout.addWidget(QLabel("재료명"))
        layout.addWidget(self.name)
        layout.addWidget(QLabel("구매가격"))
        layout.addWidget(self.buy_price)
        layout.addWidget(QLabel("제작시 수수료"))
        layout.addWidget(self.fee)
        layout.addWidget(QLabel("재고수량"))
        layout.addWidget(self.count)
        layout.addWidget(QLabel("시장가 입력"))
        layout.addWidget(self.market_price)
        layout.addWidget(QLabel("시장가 입력일시"))
        layout.addWidget(self.market_price_time)
        layout.addWidget(btn_save)
        self.setLayout(layout)

    def load_materials(self):
        self.materials = load_data(DATA_FILE)
        for name in self.materials:
            self.material_select.addItem(name)

    def load_selected_material(self):
        idx = self.material_select.currentIndex()
        if idx == 0:  # 새로 입력
            self.name.setText("")
            self.buy_price.setValue(0)
            self.fee.setValue(0)
            self.count.setValue(0)
            self.market_price.setValue(0)
            self.market_price_time.setText("-")
        else:
            mat_name = self.material_select.currentText()
            mat = self.materials.get(mat_name, {})
            self.name.setText(mat_name)
            self.buy_price.setValue(mat.get("buy_price", 0))
            self.fee.setValue(mat.get("fee", 0))
            self.count.setValue(mat.get("count", 0))
            self.market_price.setValue(mat.get("market_price", 0))
            t = mat.get("market_price_time", None)
            if t:
                self.market_price_time.setText(str(t))
            else:
                self.market_price_time.setText("-")

    def save_material(self):
        materials = load_data(DATA_FILE)
        n = self.name.text()
        b = self.buy_price.value()
        f = self.fee.value()
        c = self.count.value()
        m = self.market_price.value()
        now = datetime.datetime.now().isoformat(sep=" ", timespec="seconds") if m else materials.get(n, {}).get("market_price_time")
        if not n:
            QMessageBox.warning(self, "경고", "재료명을 입력하세요")
            return
        materials[n] = {
            "buy_price": b,
            "fee": f,
            "count": c,
            "market_price": m,
            "market_price_time": now
        }
        save_data(DATA_FILE, materials)
        QMessageBox.information(self, "알림", "저장됨")
        self.material_select.clear()
        self.material_select.addItem("새로 입력")
        self.load_materials()
        self.material_select.setCurrentText(n)

class RecipeManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("레시피")
        layout = QVBoxLayout()
        self.recipe_select = QComboBox()
        self.recipe_select.addItem("새로 입력")
        self.load_recipes()
        self.recipe_select.currentIndexChanged.connect(self.load_selected_recipe)

        self.name = QLineEdit()
        self.output = QSpinBox()
        self.output.setMinimum(1)
        self.output.setMaximum(99999)
        self.materials = QTextEdit()
        btn_save = QPushButton("저장")
        btn_save.clicked.connect(self.save_recipe)

        layout.addWidget(QLabel("레시피 선택"))
        layout.addWidget(self.recipe_select)
        layout.addWidget(QLabel("레시피명"))
        layout.addWidget(self.name)
        layout.addWidget(QLabel("제작 산출 갯수"))
        layout.addWidget(self.output)
        layout.addWidget(QLabel("재료명:수량 (줄바꿈 구분)"))
        layout.addWidget(self.materials)
        layout.addWidget(btn_save)
        self.setLayout(layout)

    def load_recipes(self):
        self.recipes = load_data(RECIPE_FILE)
        for rname in self.recipes:
            self.recipe_select.addItem(rname)

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
        recipes = load_data(RECIPE_FILE)
        n = self.name.text()
        output_cnt = self.output.value()
        lines = self.materials.toPlainText().splitlines()
        mats = {}
        for l in lines:
            try:
                mat, cnt = l.split(":")
                mats[mat.strip()] = int(cnt)
            except:
                QMessageBox.warning(self, "경고", f"형식오류: {l}")
                return
        recipes[n] = {
            "materials": mats,
            "output": output_cnt
        }
        save_data(RECIPE_FILE, recipes)
        QMessageBox.information(self, "알림", "저장됨")
        # 목록 최신화
        self.recipe_select.clear()
        self.recipe_select.addItem("새로 입력")
        self.load_recipes()
        self.recipe_select.setCurrentText(n)


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


class SaleRegister(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("판매등록")
        layout = QVBoxLayout()
        self.item_select = QComboBox()
        self.buy_price_label = QLabel("-")
        self.fee_label = QLabel("-")
        self.sum_label = QLabel("-")
        self.sale_price = QSpinBox()
        self.sale_price.setMaximum(99999999)
        btn_calc = QPushButton("계산")
        btn_calc.clicked.connect(self.calc_profit)
        btn_register = QPushButton("등록")
        btn_register.clicked.connect(self.register_sale)
        self.result = QLabel("-")

        layout.addWidget(QLabel("판매할 아이템 선택"))
        layout.addWidget(self.item_select)
        layout.addWidget(QLabel("구매가"))
        layout.addWidget(self.buy_price_label)
        layout.addWidget(QLabel("수수료"))
        layout.addWidget(self.fee_label)
        layout.addWidget(QLabel("구매가+수수료"))
        layout.addWidget(self.sum_label)
        layout.addWidget(QLabel("판매가 입력"))
        layout.addWidget(self.sale_price)
        layout.addWidget(btn_calc)
        layout.addWidget(QLabel("손익 결과"))
        layout.addWidget(self.result)
        layout.addWidget(btn_register)
        self.setLayout(layout)

        self.item_select.currentIndexChanged.connect(self.update_item_info)
        self.refresh_items()  # <= 모든 위젯 정의 이후에 호출

    def refresh_items(self):
        self.item_select.clear()
        materials = load_data(DATA_FILE)
        self.materials = materials
        for k in materials.keys():
            self.item_select.addItem(k)
        self.update_item_info()

    def update_item_info(self):
        item = self.item_select.currentText()
        mat = self.materials.get(item, {})
        self.buy_price_label.setText(str(mat.get("buy_price", "-")))
        self.fee_label.setText(str(mat.get("fee", "-")))
        try:
            self.sum_label.setText(str(mat["buy_price"] + mat["fee"]))
        except:
            self.sum_label.setText("-")
        self.result.setText("-")

    def calc_profit(self):
        item = self.item_select.currentText()
        mat = self.materials.get(item, {})
        if not mat:
            self.result.setText("아이템 정보 없음")
            return
        a = mat.get("buy_price", 0) + mat.get("fee", 0)
        b = self.sale_price.value()
        profit = b - a
        self.result.setText(f"손익: {profit} ({'이익' if profit > 0 else '손해'})")

    def register_sale(self):
        item = self.item_select.currentText()
        mat = self.materials.get(item, {})
        if not mat:
            QMessageBox.warning(self, "경고", "아이템 정보 없음")
            return
        a = mat.get("buy_price", 0) + mat.get("fee", 0)
        b = self.sale_price.value()
        profit = b - a

        # sale_data.json에 append
        filename = "sale_data.json"
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = json.load(f)
        else:
            data = []
        data.append({
            "item": item,
            "buy_price": mat.get("buy_price", 0),
            "fee": mat.get("fee", 0),
            "total_cost": a,
            "sale_price": b,
            "profit": profit
        })
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        QMessageBox.information(self, "알림", "판매등록 완료")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
