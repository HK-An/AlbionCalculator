import os
import json
from receipe.recipe_form import RecipeForm
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QComboBox, QLineEdit, QSpinBox)


# RECIPE_FILE = os.path.join(BASE_DIR, '..', 'recipes.json')


class CraftingManager(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.recipe_form = RecipeForm("Crafting Manager")
        layout.addWidget(self.recipe_form)
        # self.recipe_form.show()
        # self.setLayout(layout)