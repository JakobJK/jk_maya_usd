
from PySide6 import QtCore, QtWidgets, QtGui
from shiboken6 import wrapInstance
from functools import partial

import maya.OpenMayaUI as omui
import maya.api.OpenMaya as om
import os
from maya import cmds

from jk_maya_usd.constants import DESTINATION
from jk_maya_usd.exporter import CustomUSDExporter
from jk_maya_usd.importer import CustomUSDImporter
from jk_maya_usd.maya_utilities import create_scope, create_variant, create_variant_set, add_type_attribute

def get_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    main_window = wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    return main_window

class ComponentsUI(QtWidgets.QMainWindow):
    instance = None

    @classmethod
    def show_UI(cls):
        if not cls.instance:
            cls.instance = ComponentsUI()
        if cls.instance.isHidden():
            cls.instance.show()
        else:
            cls.instance.raise_()
            cls.instance.activateWindow()


    def __init__(self, parent=get_main_window()):
        super().__init__(parent)

        self.exporter = CustomUSDExporter()
        self.importer = CustomUSDImporter()

        self.export_path = DESTINATION

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Window | QtCore.Qt.WindowStaysOnTopHint)
        self.raise_()
        self.activateWindow()
        self.setWindowTitle("Components UI")
        self.setMinimumSize(300, 100)
        self.central_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.central_widget)
        layout.addWidget(self.build_ui())
        layout.addWidget(self.export_ui())
        layout.addWidget(self.import_ui())
        layout.addWidget(self.testing_ui())
        layout.addStretch()
        self.setCentralWidget(self.central_widget)

    def build_ui(self):
        group_box = QtWidgets.QGroupBox("Create / Set USD Nodes")
        layout = QtWidgets.QVBoxLayout(group_box)
        for usd_type in {"Scope", "VariantSet", "Variant"}:
            usd_type_button = QtWidgets.QPushButton(f"Create {usd_type}")
            usd_type_button.clicked.connect(partial(self._create_usd_node, usd_type))
            layout.addWidget(usd_type_button)
        return group_box

    def export_ui(self):
        group_box = QtWidgets.QGroupBox("Export to USD")
        layout = QtWidgets.QVBoxLayout(group_box)

        
        path_layout = QtWidgets.QHBoxLayout()
        self.export_path_label = QtWidgets.QLabel(self.export_path)
        browse_button = QtWidgets.QPushButton("Select Folder")
        browse_button.clicked.connect(self._select_export_folder)

        path_layout.addWidget(self.export_path_label)
        path_layout.addWidget(browse_button)
        layout.addLayout(path_layout)

        export_button = QtWidgets.QPushButton("Export Selected Nodes")
        export_button.clicked.connect(self._export_selected)

        layout.addWidget(export_button)

        return group_box

    def import_ui(self):
        group_box = QtWidgets.QGroupBox("Import from USD")
        layout = QtWidgets.QVBoxLayout(group_box)

        self.import_list = QtWidgets.QListWidget()
        self._populate_import_list()

        import_button = QtWidgets.QPushButton("Import Selected USD")
        import_button.clicked.connect(self._import_selected)

        layout.addWidget(self.import_list)
        layout.addWidget(import_button)

        return group_box

    def testing_ui(self):
        group_box = QtWidgets.QGroupBox("TD Area")
        layout = QtWidgets.QVBoxLayout(group_box)
        return group_box


    def _create_usd_node(self, usd_type):
        if selection:= cmds.ls(selection=True):
            for node in selection:
                add_type_attribute(node, usd_type)
        else:
            if usd_type == "Scope":
                create_scope(usd_type.lower())
            if usd_type == "VariantSet":
                create_variant_set(usd_type.lower())
            if usd_type == "Variant":
                create_variant(usd_type.lower())

    def _select_export_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Export Folder", self.export_path)
        if folder:
            self.export_path = folder
            self.export_path_label.setText(folder)
        self._populate_import_list()


    def _export_selected(self):
        print("Exporting...")
        for node in cmds.ls(selection=True):
            self.exporter.export_to_usd(f"{self.export_path}/{node}.usda")


    def _import_selected(self):
        selected_items = self.import_list.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            file_path = os.path.join(self.export_path, item.text())
            self.importer.import_from_usd(file_path)


    def _populate_import_list(self):
        self.import_list.clear()
        if os.path.exists(self.export_path):
            for file in os.listdir(self.export_path):
                if file.endswith(".usda") or file.endswith(".usd"):
                    self.import_list.addItem(file)


