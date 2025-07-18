import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QSpinBox, QPushButton
)
from PyQt5.QtWidgets import QMessageBox

RECIPE_FILE = "recipes.json"
DATA_FILE = "material_data.json"

def load_data(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

class RecipeCalc(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("제작 계산")
        layout = QVBoxLayout()
        self.recipe_select = QComboBox()
        self.refresh_recipes()
        self.fee_spin = QSpinBox()
        self.fee_spin.setMaximum(9999999)
        btn_calc = QPushButton("계산")
        btn_calc.clicked.connect(self.calc_cost)
        btn_make = QPushButton("제작")
        btn_make.clicked.connect(self.make_recipe)
        self.market = QSpinBox()
        self.market.setMaximum(99999999)
        self.result = QLabel("-")
        self.fee_spin = QSpinBox()
        self.fee_spin.setMaximum(9999999)
        self.make_count = QSpinBox()
        self.make_count.setMaximum(999999)

        layout.addWidget(QLabel("레시피 선택"))
        layout.addWidget(self.recipe_select)
        layout.addWidget(QLabel("개당 제작 수수료"))
        layout.addWidget(self.fee_spin)
        layout.addWidget(QLabel("개당 제작 수수료"))
        layout.addWidget(self.fee_spin)
        layout.addWidget(QLabel("제작 갯수"))
        layout.addWidget(self.make_count)
        layout.addWidget(QLabel("시장가 입력 (1회 생산 기준)"))
        layout.addWidget(self.market)
        layout.addWidget(btn_calc)
        layout.addWidget(btn_make)
        layout.addWidget(QLabel("손익/제작 결과"))
        layout.addWidget(self.result)
        self.setLayout(layout)

    def refresh_recipes(self):
        self.recipe_select.clear()
        self.recipe_select.addItem("선택없음")
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
        output_cnt = recipe.get("output_count", 1)
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
        idx = self.recipe_select.currentIndex()
        if idx == 0:
            self.result.setText("레시피를 선택하세요")
            return
        recipe_name = self.recipe_select.currentText()
        recipes = self.recipes
        materials = load_data(DATA_FILE)
        if recipe_name not in recipes:
            self.result.setText("레시피 없음")
            return
        recipe = recipes[recipe_name]
        mats = recipe["materials"]
        output_cnt = recipe.get("output_count", 1)
        make_cnt = self.make_count.value()

        # 1회 제작에 필요한 재료 수량 * 제작 횟수
        for mat, cnt in mats.items():
            if mat not in materials:
                self.result.setText(f"{mat} 정보 없음")
                return
            need = cnt * make_cnt
            inv = materials[mat].get("enchant", {}).get("0", {}).get("count", 0)
            if inv < need:
                self.result.setText(f"{mat} 재고 부족 (필요: {need}, 보유: {inv})")
                return

        # 차감
        for mat, cnt in mats.items():
            materials[mat]["enchant"]["0"]["count"] -= cnt * make_cnt

        # 산출물 인벤토리 증가
        if recipe_name not in materials:
            # 없으면 새로 등록
            materials[recipe_name] = {"count": 0}
        if "count" not in materials[recipe_name]:
            materials[recipe_name]["count"] = 0
        materials[recipe_name]["count"] += make_cnt * output_cnt

        # 제작시 수수료 입력 반영
        fee_val = self.fee_spin.value()
        materials[recipe_name]["fee"] = fee_val

        save_data(DATA_FILE, materials)
        self.result.setText(f"제작 성공: {recipe_name} {make_cnt * output_cnt}개, 인벤토리 반영 완료")
        self.update_detail()


    def update_detail(self):
        idx = self.recipe_select.currentIndex()
        if idx == 0:
            self.detail_label.setText("-")
            return
        recipe_name = self.recipe_select.currentText()
        recipes = self.recipes
        materials = load_data(DATA_FILE)
        if recipe_name not in recipes:
            self.detail_label.setText("레시피 정보 없음")
            return
        recipe = recipes[recipe_name]
        mats = recipe["materials"]
        msg = ""
        for mat, cnt in mats.items():
            inv_cnt = materials.get(mat, {}).get("count", 0)
            msg += f"{mat}: 필요 {cnt}, 보유 {inv_cnt}\n"
        # self.detail_label.setText(msg.strip())
        # detail_label 업데이트 뒤
        # 만약 여러 재료 중 fee를 대표로 한 가지만 쓸 거면:
        if mats:
            mat0 = list(mats.keys())[0]
            fee0 = materials.get(mat0, {}).get("fee", 0)
            self.fee_spin.setValue(fee0)
        else:
            self.fee_spin.setValue(0)
