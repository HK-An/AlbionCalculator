import json
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RECIPE_FILE = os.path.join(BASE_DIR, 'receipe', 'recipes.json')
MATERIAL_FILE = os.path.join(BASE_DIR, 'inventory', 'material_data.json')

def load_data(filename):
    with open(filename, encoding="utf-8") as f:
        return json.load(f)

class Util():
    def __init__(self):
        self.load_materials()

    def getIndexByNameFromMaterialJson(self, name):
        self.materials.get(name, {})
        print()

    def add_inventory(self, item_name, item_count):
        self.getIndexByNameFromMaterialJson(item_name)
        print("count->",item_count)
        # print("fee->", self.fee.value())

        for ingredient_row in self.ingredient_rows:
            self.getIndexByNameFromMaterialJson(ingredient_row.combo.currentText())


    
    def load_materials(self):
        # material_data.json에서 불러오기
        try:
            material_raw = load_data(MATERIAL_FILE)
        except:
            material_raw = {}

        self.materials = material_raw
