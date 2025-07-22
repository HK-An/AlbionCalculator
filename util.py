import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECIPE_FILE = os.path.join(BASE_DIR, 'receipe', 'recipes.json')
MATERIAL_FILE = os.path.join(BASE_DIR, 'inventory', 'material_data.json')
LANG_FILE = os.path.join(BASE_DIR, '', 'lang.json')

def load_data(filename):
    with open(filename, encoding="utf-8") as f:
        return json.load(f)

def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

class Util():
    def __init__(self):
        self.load_materials()
        self.load_lang()

    def get_item_from_inventory(self, item_name):
        return self.materials.get(item_name, {})

    def add_inventory(self, item_name, item_count, fee):
        mat = self.materials.get(item_name, {})
        if mat != {}:
            # 1. count 증가
            new_mat = self.increase_enchant_count(mat, "0", item_count)
            # 2. fee 계산 (fee × output_count)
            new_mat = self.increase_enchant_fee(new_mat, "0", fee)
            # 3. 전체 materials에서 해당 항목 갱신
            self.update_material(item_name, new_mat)
            # 4. 파일 저장
            self.save_materials()
            return new_mat
        else:
            print("item not found")
            return None

    def increase_enchant_count(self, mat_json, enchant_str, add_count):
        """mat_json["enchant"][enchant_str]["count"]에 add_count만큼 더해서 반영"""
        if "enchant" not in mat_json:
            mat_json["enchant"] = {}
        if enchant_str not in mat_json["enchant"]:
            mat_json["enchant"][enchant_str] = {}
        cur = mat_json["enchant"][enchant_str].get("count", 0)
        mat_json["enchant"][enchant_str]["count"] = cur + add_count
        return mat_json
    
    def increase_enchant_fee(self, mat_json, enchant_str, fee):
        """기존 fee 값 × output_count로 갱신"""
        if "enchant" not in mat_json:
            mat_json["enchant"] = {}
        if enchant_str not in mat_json["enchant"]:
            mat_json["enchant"][enchant_str] = {}
        feeOrigin = mat_json["enchant"][enchant_str].get("fee", 0)
        mat_json["enchant"][enchant_str]["fee"] = feeOrigin + fee
        return mat_json
    
    def update_material(self, item_name, new_mat_json):
        """self.materials에서 item_name에 해당하는 값을 new_mat_json으로 갱신"""
        self.materials[item_name] = new_mat_json

    def save_materials(self):
        """self.materials 전체를 파일로 저장"""
        save_data(MATERIAL_FILE, self.materials)

    def load_materials(self):
        # material_data.json에서 불러오기
        try:
            material_raw = load_data(MATERIAL_FILE)
        except:
            material_raw = {}

        self.materials = material_raw
    
    def load_lang(self):
        try:
            lang_raw = load_data(LANG_FILE)
        except:
            lang_raw = {}
        self.lang = lang_raw

    def consume_ingredients_and_transfer_fee(self, materials_dict, output_count):
        """
        materials_dict: {'item_name': 사용수량, ...}
        output_count: 산출 갯수
        """
        for item, remaining_count in materials_dict.items():
            mat = self.materials.get(item, {})
            if not mat or "enchant" not in mat or "0" not in mat["enchant"]:
                continue
            # 재고(수량) 감소
            old_count = mat["enchant"]["0"].get("count", 0)
            used_count = old_count - remaining_count
            mat["enchant"]["0"]["count"] = max(0, old_count - used_count)
            # fee 전가 계산
            old_fee = mat["enchant"]["0"].get("fee", 0)
            # 평균 단가 * 소모량
            avg_unit_fee = int(old_fee / old_count) if old_count else 0
            transfer_fee = avg_unit_fee * used_count
            # fee 차감
            mat["enchant"]["0"]["fee"] = max(0, old_fee - transfer_fee)
            # 저장
            self.materials[item] = mat
            # 리턴값: 이 fee를 산출물에 더해줘야 함
            yield item, transfer_fee
        self.save_materials()

    def get_text_from_lang(self, lang, text):
        return self.lang.get(lang).get(text, {})
