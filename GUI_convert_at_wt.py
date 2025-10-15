import sys
import os
import pandas as pd
from collections import OrderedDict

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QButtonGroup,
    QTabWidget,
    QGridLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QLabel,
    QMessageBox,
    QTextEdit,
    QScrollArea,
    QCheckBox,
    QGroupBox,
    QDoubleSpinBox,
    QLineEdit,  # <--- 修正：添加了 QLineEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

# --- 1. CORE LOGIC (Unchanged) ---
# Element Configuration Area - ADD/REMOVE elements here
ATOMIC_MASSES = OrderedDict(
    [
        ("Al", 26.9815385),
        ("Li", 6.94),
        ("Cu", 63.546),
        ("Mg", 24.305),
        ("Zr", 91.224),
        ("Mn", 54.938044),
        # For a richer periodic table, you can add more, e.g.:
        ("H", 1.008),
        ("He", 4.0026),
        ("Be", 9.0122),
        ("B", 10.81),
        ("C", 12.011),
        ("N", 14.007),
        ("O", 15.999),
        ("F", 18.998),
        ("Ne", 20.180),
        ("Na", 22.990),
        ("Si", 28.085),
        ("P", 32.06),
        ("S", 32.06),
        ("Cl", 35.45),
        ("Ar", 39.948),
        ("K", 39.098),
        ("Ca", 40.078),
        ("Sc", 44.956),
        ("Ti", 47.867),
        ("V", 50.942),
        ("Cr", 51.996),
        ("Fe", 55.845),
        ("Co", 58.933),
        ("Ni", 58.693),
        ("Zn", 65.38),
    ]
)

# Data for periodic table layout: {Symbol: (row, column)}
PERIODIC_TABLE_LAYOUT = {
    "H": (0, 0),
    "He": (0, 17),
    "Li": (1, 0),
    "Be": (1, 1),
    "B": (1, 12),
    "C": (1, 13),
    "N": (1, 14),
    "O": (1, 15),
    "F": (1, 16),
    "Ne": (1, 17),
    "Na": (2, 0),
    "Mg": (2, 1),
    "Al": (2, 12),
    "Si": (2, 13),
    "P": (2, 14),
    "S": (2, 15),
    "Cl": (2, 16),
    "Ar": (2, 17),
    "K": (3, 0),
    "Ca": (3, 1),
    "Sc": (3, 2),
    "Ti": (3, 3),
    "V": (3, 4),
    "Cr": (3, 5),
    "Mn": (3, 6),
    "Fe": (3, 7),
    "Co": (3, 8),
    "Ni": (3, 9),
    "Cu": (3, 10),
    "Zn": (3, 11),
    "Ga": (3, 12),
    "Ge": (3, 13),
    "As": (3, 14),
    "Se": (3, 15),
    "Br": (3, 16),
    "Kr": (3, 17),
    "Rb": (4, 0),
    "Sr": (4, 1),
    "Y": (4, 2),
    "Zr": (4, 3),
    "Nb": (4, 4),
    "Mo": (4, 5),
    "Tc": (4, 6),
    "Ru": (4, 7),
    "Rh": (4, 8),
    "Pd": (4, 9),
    "Ag": (4, 10),
    "Cd": (4, 11),
    "In": (4, 12),
    "Sn": (4, 13),
    "Sb": (4, 14),
    "Te": (4, 15),
    "I": (4, 16),
    "Xe": (4, 17),
    "Cs": (5, 0),
    "Ba": (5, 1),
    "La": (5, 2),
    "Hf": (5, 3),
    "Ta": (5, 4),
    "W": (5, 5),
    "Re": (5, 6),
    "Os": (5, 7),
    "Ir": (5, 8),
    "Pt": (5, 9),
    "Au": (5, 10),
    "Hg": (5, 11),
    "Tl": (5, 12),
    "Pb": (5, 13),
    "Bi": (5, 14),
    "Po": (5, 15),
    "At": (5, 16),
    "Rn": (5, 17),
    "Fr": (6, 0),
    "Ra": (6, 1),
    "Ac": (6, 2),
    "Rf": (6, 3),
    "Db": (6, 4),
    "Sg": (6, 5),
    "Bh": (6, 6),
    "Hs": (6, 7),
    "Mt": (6, 8),
    "Ds": (6, 9),
    "Rg": (6, 10),
    "Cn": (6, 11),
    "Nh": (6, 12),
    "Fl": (6, 13),
    "Mc": (6, 14),
    "Lv": (6, 15),
    "Ts": (6, 16),
    "Og": (6, 17),
}


def wt_to_at(wt_percents: dict) -> dict:
    moles = {
        el: wt / ATOMIC_MASSES[el]
        for el, wt in wt_percents.items()
        if el in ATOMIC_MASSES and wt > 0
    }
    total_moles = sum(moles.values())
    if total_moles == 0:
        return {el: 0 for el in wt_percents.keys()}
    return {el: (mol / total_moles) * 100 for el, mol in moles.items()}


def at_to_wt(at_percents: dict) -> dict:
    mass_contributions = {
        el: at * ATOMIC_MASSES[el]
        for el, at in at_percents.items()
        if el in ATOMIC_MASSES and at > 0
    }
    total_mass = sum(mass_contributions.values())
    if total_mass == 0:
        return {el: 0 for el in at_percents.keys()}
    return {el: (mass / total_mass) * 100 for el, mass in mass_contributions.items()}


# --- 2. GUI APPLICATION CLASS ---


class ConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weight% <-> Atomic% Converter")
        self.setGeometry(100, 100, 800, 750)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self._create_widgets()
        self._create_layout()
        self._connect_signals()

    def _create_widgets(self):
        # Conversion direction
        self.rb_wt_to_at = QRadioButton("Weight% (wt) → Atomic% (at)")
        self.rb_at_to_wt = QRadioButton("Atomic% (at) → Weight% (wt)")
        self.rb_wt_to_at.setChecked(True)

        # Tabs
        self.tabs = QTabWidget()
        self.single_point_tab = QWidget()
        self.batch_tab = QWidget()
        self.tabs.addTab(self.single_point_tab, "Single Point Calculation")
        self.tabs.addTab(self.batch_tab, "Batch Calculation (CSV)")

        # --- New Single Point Tab Widgets ---
        self._create_single_point_tab_widgets()

        # --- Batch Tab Widgets (Unchanged) ---
        self.file_path_le = QLineEdit()
        self.btn_browse = QPushButton("Browse...")
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.columns_widget = QWidget()
        self.columns_layout = QVBoxLayout(self.columns_widget)
        self.scroll_area.setWidget(self.columns_widget)
        self.column_checkboxes = []
        self.btn_process_batch = QPushButton("Process File")
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)

    def _create_single_point_tab_widgets(self):
        """Create all widgets for the redesigned single point tab."""
        self.pt_buttons = {}
        self.pt_layout = QGridLayout()
        self.pt_layout.setSpacing(2)

        for symbol, (row, col) in PERIODIC_TABLE_LAYOUT.items():
            btn = QPushButton(symbol)
            btn.setCheckable(True)
            btn.setFixedSize(35, 35)
            if symbol in ATOMIC_MASSES:
                # Style for enabled elements
                btn.setStyleSheet(
                    "QPushButton:checked { background-color: #6495ED; color: white; }"
                )
                btn.toggled.connect(self._update_input_fields)
            else:
                # Style for disabled elements
                btn.setEnabled(False)
                btn.setStyleSheet(
                    "QPushButton { background-color: #E0E0E0; color: #A0A0A0; }"
                )

            self.pt_buttons[symbol] = btn
            self.pt_layout.addWidget(btn, row, col)

        self.active_element_inputs = {}  # Will store QDoubleSpinBox widgets
        self.dynamic_inputs_layout = QGridLayout()

        self.sum_label = QLabel("Sum: 0.00 %")
        font = self.sum_label.font()
        font.setBold(True)
        self.sum_label.setFont(font)

        self.btn_calculate_single = QPushButton("Calculate")
        self.results_table = QTableWidget()
        self.results_table.setRowCount(1)
        self.results_table.setVerticalHeaderLabels(["Value"])

    def _create_layout(self):
        # Top layout for conversion type
        conversion_layout = QHBoxLayout()
        conversion_layout.addWidget(self.rb_wt_to_at)
        conversion_layout.addWidget(self.rb_at_to_wt)

        # --- Single Point Tab Layout ---
        self._layout_single_point_tab()

        # --- Batch Tab Layout (Unchanged) ---
        self._layout_batch_tab()

        # --- Main Layout ---
        self.main_layout.addLayout(conversion_layout)
        self.main_layout.addWidget(self.tabs)

    def _layout_single_point_tab(self):
        """Assemble the redesigned single point tab layout."""
        layout = QVBoxLayout(self.single_point_tab)

        pt_group = QGroupBox("1. Select Elements from Periodic Table")
        pt_group.setLayout(self.pt_layout)

        inputs_group = QGroupBox("2. Enter Composition")
        inputs_layout = QVBoxLayout(inputs_group)
        inputs_layout.addLayout(self.dynamic_inputs_layout)
        inputs_layout.addWidget(self.sum_label, alignment=Qt.AlignmentFlag.AlignRight)

        results_group = QGroupBox("3. Results")
        results_layout = QVBoxLayout(results_group)
        results_layout.addWidget(self.results_table)

        layout.addWidget(pt_group)
        layout.addWidget(inputs_group)
        layout.addWidget(self.btn_calculate_single)
        layout.addWidget(results_group)

    def _layout_batch_tab(self):
        """Assemble the batch calculation tab layout."""
        batch_tab_layout = QVBoxLayout(self.batch_tab)
        file_select_layout = QHBoxLayout()
        file_select_layout.addWidget(QLabel("CSV File:"))
        file_select_layout.addWidget(self.file_path_le)
        file_select_layout.addWidget(self.btn_browse)

        columns_label = QLabel(
            "Please select the columns containing elemental compositions:"
        )
        batch_tab_layout.addLayout(file_select_layout)
        batch_tab_layout.addWidget(columns_label)
        batch_tab_layout.addWidget(self.scroll_area)
        batch_tab_layout.addWidget(self.btn_process_batch)
        batch_tab_layout.addWidget(QLabel("Log:"))
        batch_tab_layout.addWidget(self.log_area)

    def _connect_signals(self):
        self.btn_calculate_single.clicked.connect(self._perform_single_calculation)
        self.btn_browse.clicked.connect(self._browse_file)
        self.btn_process_batch.clicked.connect(self._perform_batch_calculation)

    # --- Helper & Slot Methods ---

    def _clear_layout(self, layout):
        """Removes all widgets from a layout."""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _update_input_fields(self):
        """Dynamically create input fields based on selected elements."""
        self._clear_layout(self.dynamic_inputs_layout)
        self.active_element_inputs.clear()

        selected_elements = sorted(
            [symbol for symbol, btn in self.pt_buttons.items() if btn.isChecked()]
        )

        for i, symbol in enumerate(selected_elements):
            label = QLabel(f"{symbol} (%):")
            spin_box = QDoubleSpinBox()
            spin_box.setRange(0.0, 100.0)
            spin_box.setDecimals(3)
            spin_box.setSingleStep(0.1)
            spin_box.valueChanged.connect(self._update_sum_label)

            self.active_element_inputs[symbol] = spin_box

            # Add to grid layout (2 columns)
            row, col = divmod(i, 2)
            self.dynamic_inputs_layout.addWidget(label, row, col * 2)
            self.dynamic_inputs_layout.addWidget(spin_box, row, col * 2 + 1)

        self._update_sum_label()

    def _update_sum_label(self):
        """Calculate and display the sum of current inputs."""
        total = sum(
            spin_box.value() for spin_box in self.active_element_inputs.values()
        )
        self.sum_label.setText(f"Sum: {total:.3f} %")

        if 99.9 <= total <= 100.1:
            self.sum_label.setStyleSheet("color: green;")
        else:
            self.sum_label.setStyleSheet("color: red;")

    def _perform_single_calculation(self):
        """Handles the 'Calculate' button click for single point mode."""
        if not self.active_element_inputs:
            QMessageBox.warning(
                self, "Input Error", "Please select at least one element."
            )
            return

        input_percents = {
            el: sb.value() for el, sb in self.active_element_inputs.items()
        }

        if self.rb_wt_to_at.isChecked():
            result = wt_to_at(input_percents)
            to_unit = "at"
        else:
            result = at_to_wt(input_percents)
            to_unit = "wt"

        self._display_single_results(result, to_unit)

    def _display_single_results(self, results, unit):
        """Populates the results table with calculation output."""
        sorted_elements = sorted(results.keys())
        headers = [f"{el} ({unit}%)" for el in sorted_elements]
        self.results_table.setColumnCount(len(headers))
        self.results_table.setHorizontalHeaderLabels(headers)

        for i, element in enumerate(sorted_elements):
            value = results.get(element, 0)
            item = QTableWidgetItem(f"{value:.4f}")
            self.results_table.setItem(0, i, item)
        self.results_table.resizeColumnsToContents()

    # --- Batch Calculation Methods (Unchanged) ---
    def _browse_file(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open CSV File", "", "CSV Files (*.csv)"
        )
        if file_name:
            self.file_path_le.setText(file_name)
            self._load_csv_columns(file_name)

    def _load_csv_columns(self, file_path):
        for checkbox in self.column_checkboxes:
            checkbox.deleteLater()
        self.column_checkboxes.clear()
        try:
            df = pd.read_csv(file_path, nrows=0)
            columns = [col for col in df.columns if not col.startswith("Unnamed:")]
            for col in columns:
                checkbox = QCheckBox(col)
                if col in ATOMIC_MASSES:
                    checkbox.setChecked(True)
                self.columns_layout.addWidget(checkbox)
                self.column_checkboxes.append(checkbox)
        except Exception as e:
            QMessageBox.critical(
                self, "File Error", f"Could not read columns from file: {e}"
            )

    def _perform_batch_calculation(self):
        self.log_area.clear()
        csv_path = self.file_path_le.text()
        if not csv_path:
            self.log_area.append("Error: No CSV file selected.")
            return
        selected_cols = [cb.text() for cb in self.column_checkboxes if cb.isChecked()]
        if not selected_cols:
            self.log_area.append("Error: No component columns selected.")
            return

        self.log_area.append(f"Starting batch processing for: {csv_path}")
        element_cols = [col for col in selected_cols if col in ATOMIC_MASSES]
        if self.rb_wt_to_at.isChecked():
            conv_func, to_unit = wt_to_at, "at"
        else:
            conv_func, to_unit = at_to_wt, "wt"
        try:
            df = pd.read_csv(csv_path)

            def calculate_row(row):
                return pd.Series(conv_func(row[element_cols].astype(float).to_dict()))

            result_df = df.apply(calculate_row, axis=1).rename(
                columns=lambda el: f"{el}({to_unit}%)"
            )
            final_df = pd.concat([df, result_df], axis=1)
            output_path = f"{os.path.splitext(csv_path)[0]}-{to_unit}.csv"
            final_df.to_csv(output_path, index=False)
            self.log_area.append(f"\nSuccess! Results saved to: {output_path}")
            QMessageBox.information(
                self,
                "Success",
                f"Processing complete. Results saved to:\n{output_path}",
            )
        except Exception as e:
            self.log_area.append(f"\n--- AN ERROR OCCURRED ---\n{e}")
            QMessageBox.critical(self, "Processing Error", f"An error occurred:\n{e}")


# --- 3. APPLICATION ENTRY POINT ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConverterApp()
    window.show()
    sys.exit(app.exec())
