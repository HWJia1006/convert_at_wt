import sys
import os
import pandas as pd
from collections import OrderedDict

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QRadioButton, QButtonGroup, QTabWidget, QFormLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QFileDialog, QLabel,
    QMessageBox, QTextEdit, QScrollArea, QCheckBox
)
from PyQt6.QtCore import Qt

# --- 1. CORE LOGIC (Copied from the original script) ---
# This part remains unchanged. It's the "engine" of our application.

# Element Configuration Area
ATOMIC_MASSES = OrderedDict([
    ('Al', 26.9815385),
    ('Li', 6.94),
    ('Cu', 63.546),
    ('Mg', 24.305),
    ('Zr', 91.224),
    ('Mn', 54.938044),
    # You can easily add more elements here
    # ('Si', 28.0855),
])

def wt_to_at(wt_percents: dict) -> dict:
    """Converts weight percent (wt%) to atomic percent (at%)."""
    # ... (The exact same function from the previous script)
    moles = {el: wt / ATOMIC_MASSES[el] for el, wt in wt_percents.items() if el in ATOMIC_MASSES and wt > 0}
    total_moles = sum(moles.values())
    if total_moles == 0:
        return {el: 0 for el in wt_percents.keys()}
    return {el: (mol / total_moles) * 100 for el, mol in moles.items()}

def at_to_wt(at_percents: dict) -> dict:
    """Converts atomic percent (at%) to weight percent (wt%)."""
    # ... (The exact same function from the previous script)
    mass_contributions = {el: at * ATOMIC_MASSES[el] for el, at in at_percents.items() if el in ATOMIC_MASSES and at > 0}
    total_mass = sum(mass_contributions.values())
    if total_mass == 0:
        return {el: 0 for el in at_percents.keys()}
    return {el: (mass / total_mass) * 100 for el, mass in mass_contributions.items()}


# --- 2. GUI APPLICATION CLASS ---

class ConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weight% <-> Atomic% Converter")
        self.setGeometry(100, 100, 700, 550) # x, y, width, height

        # --- Central Widget and Layout ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self._create_widgets()
        self._create_layout()
        self._connect_signals()

    def _create_widgets(self):
        """Initialize all UI widgets."""
        # Conversion direction
        self.rb_wt_to_at = QRadioButton("Weight% (wt) → Atomic% (at)")
        self.rb_at_to_wt = QRadioButton("Atomic% (at) → Weight% (wt)")
        self.rb_wt_to_at.setChecked(True)
        self.conversion_group = QButtonGroup()
        self.conversion_group.addButton(self.rb_wt_to_at)
        self.conversion_group.addButton(self.rb_at_to_wt)

        # Tabs for different modes
        self.tabs = QTabWidget()
        self.single_point_tab = QWidget()
        self.batch_tab = QWidget()
        self.tabs.addTab(self.single_point_tab, "Single Point Calculation")
        self.tabs.addTab(self.batch_tab, "Batch Calculation (CSV)")

        # --- Single Point Tab Widgets ---
        self.element_inputs = {}
        self.form_layout = QFormLayout()
        for element in ATOMIC_MASSES.keys():
            line_edit = QLineEdit("0")
            self.element_inputs[element] = line_edit
            self.form_layout.addRow(f"{element} (%):", line_edit)
        
        self.btn_calculate_single = QPushButton("Calculate")
        self.results_table = QTableWidget()
        self.results_table.setRowCount(1)
        self.results_table.setVerticalHeaderLabels(["Value"])


        # --- Batch Tab Widgets ---
        self.file_path_le = QLineEdit()
        self.file_path_le.setPlaceholderText("Click 'Browse' to select a CSV file")
        self.btn_browse = QPushButton("Browse...")
        
        self.columns_label = QLabel("Please select the columns containing elemental compositions:")
        self.scroll_area = QScrollArea() # To handle many columns
        self.scroll_area.setWidgetResizable(True)
        self.columns_widget = QWidget()
        self.columns_layout = QVBoxLayout(self.columns_widget)
        self.scroll_area.setWidget(self.columns_widget)
        self.column_checkboxes = []

        self.btn_process_batch = QPushButton("Process File")
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        
    def _create_layout(self):
        """Assemble widgets into layouts."""
        # Top layout for conversion type
        conversion_layout = QHBoxLayout()
        conversion_layout.addWidget(self.rb_wt_to_at)
        conversion_layout.addWidget(self.rb_at_to_wt)
        
        # --- Single Point Tab Layout ---
        single_tab_layout = QVBoxLayout(self.single_point_tab)
        single_tab_layout.addLayout(self.form_layout)
        single_tab_layout.addWidget(self.btn_calculate_single, alignment=Qt.AlignmentFlag.AlignRight)
        single_tab_layout.addSpacing(20)
        single_tab_layout.addWidget(QLabel("Results:"))
        single_tab_layout.addWidget(self.results_table)

        # --- Batch Tab Layout ---
        batch_tab_layout = QVBoxLayout(self.batch_tab)
        file_select_layout = QHBoxLayout()
        file_select_layout.addWidget(QLabel("CSV File:"))
        file_select_layout.addWidget(self.file_path_le)
        file_select_layout.addWidget(self.btn_browse)
        
        batch_tab_layout.addLayout(file_select_layout)
        batch_tab_layout.addWidget(self.columns_label)
        batch_tab_layout.addWidget(self.scroll_area)
        batch_tab_layout.addWidget(self.btn_process_batch)
        batch_tab_layout.addWidget(QLabel("Log:"))
        batch_tab_layout.addWidget(self.log_area)

        # --- Main Layout ---
        self.main_layout.addLayout(conversion_layout)
        self.main_layout.addWidget(self.tabs)

    def _connect_signals(self):
        """Connect widget signals to handler methods (slots)."""
        self.btn_calculate_single.clicked.connect(self._perform_single_calculation)
        self.btn_browse.clicked.connect(self._browse_file)
        self.btn_process_batch.clicked.connect(self._perform_batch_calculation)

    # --- Handler Methods (Slots) ---
    
    def _perform_single_calculation(self):
        """Handles the 'Calculate' button click for single point mode."""
        input_percents = {}
        try:
            for element, line_edit in self.element_inputs.items():
                value = float(line_edit.text())
                if value < 0:
                    raise ValueError("Percentage cannot be negative.")
                input_percents[element] = value
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", f"Invalid input: {e}\nPlease enter valid numbers.")
            return

        # Determine conversion function
        if self.rb_wt_to_at.isChecked():
            from_unit, to_unit = "wt", "at"
            result = wt_to_at(input_percents)
        else:
            from_unit, to_unit = "at", "wt"
            result = at_to_wt(input_percents)
            
        self._display_single_results(result, to_unit)

    def _display_single_results(self, results, unit):
        """Populates the results table with calculation output."""
        # Use ATOMIC_MASSES keys to maintain order
        headers = [f"{el} ({unit}%)" for el in ATOMIC_MASSES.keys()]
        self.results_table.setColumnCount(len(headers))
        self.results_table.setHorizontalHeaderLabels(headers)
        
        for i, element in enumerate(ATOMIC_MASSES.keys()):
            value = results.get(element, 0) # Get value or 0 if not in result
            item = QTableWidgetItem(f"{value:.4f}")
            self.results_table.setItem(0, i, item)
        self.results_table.resizeColumnsToContents()


    def _browse_file(self):
        """Opens a file dialog to select a CSV file."""
        file_name, _ = QFileDialog.getOpenFileName(self, "Open CSV File", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            self.file_path_le.setText(file_name)
            self._load_csv_columns(file_name)

    def _load_csv_columns(self, file_path):
        """Reads CSV headers and creates checkboxes for column selection."""
        # Clear previous checkboxes
        for checkbox in self.column_checkboxes:
            checkbox.deleteLater()
        self.column_checkboxes.clear()

        try:
            df = pd.read_csv(file_path, nrows=0) # Read only headers for speed
            # Filter out unnamed columns
            columns = [col for col in df.columns if not col.startswith('Unnamed:')]
            for col in columns:
                checkbox = QCheckBox(col)
                # Heuristically check if the column is one of our elements
                if col in ATOMIC_MASSES:
                    checkbox.setChecked(True)
                self.columns_layout.addWidget(checkbox)
                self.column_checkboxes.append(checkbox)
        except Exception as e:
            QMessageBox.critical(self, "File Error", f"Could not read columns from file: {e}")

    def _perform_batch_calculation(self):
        """Handles the 'Process File' button click for batch mode."""
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
        self.log_area.append(f"Selected component columns: {', '.join(selected_cols)}")
        
        # Check for unknown elements
        unknown_elements = [col for col in selected_cols if col not in ATOMIC_MASSES]
        if unknown_elements:
            msg = f"WARNING: The following selected columns are not in the known elements list and will be ignored: {', '.join(unknown_elements)}"
            self.log_area.append(msg)
        
        element_cols = [col for col in selected_cols if col in ATOMIC_MASSES]
        if not element_cols:
            self.log_area.append("Error: None of the selected columns are known elements. Aborting.")
            return
            
        # Determine conversion function
        if self.rb_wt_to_at.isChecked():
            conversion_func, from_unit, to_unit = wt_to_at, "wt", "at"
        else:
            conversion_func, from_unit, to_unit = at_to_wt, "at", "wt"
        
        try:
            df = pd.read_csv(csv_path)
            # Ensure selected columns exist in dataframe
            for col in element_cols:
                if col not in df.columns:
                    raise KeyError(f"Column '{col}' not found in the CSV file.")
            
            # Define row-wise calculation function
            def calculate_row(row):
                input_percents = row[element_cols].astype(float).to_dict()
                result_percents = conversion_func(input_percents)
                return pd.Series(result_percents)

            result_df = df.apply(calculate_row, axis=1)
            result_df = result_df.rename(columns={el: f"{el}({to_unit}%)" for el in result_df.columns})
            final_df = pd.concat([df, result_df], axis=1)

            # Save to new file
            base_name, ext = os.path.splitext(csv_path)
            output_path = f"{base_name}-{to_unit}.csv"
            final_df.to_csv(output_path, index=False)
            
            self.log_area.append("\n--- CALCULATION COMPLETE ---")
            self.log_area.append(f"Success! Results saved to: {output_path}")
            QMessageBox.information(self, "Success", f"Processing complete. Results saved to:\n{output_path}")

        except Exception as e:
            self.log_area.append(f"\n--- AN ERROR OCCURRED ---")
            self.log_area.append(str(e))
            QMessageBox.critical(self, "Processing Error", f"An error occurred during batch processing:\n{e}")


# --- 3. APPLICATION ENTRY POINT ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConverterApp()
    window.show()
    sys.exit(app.exec())
