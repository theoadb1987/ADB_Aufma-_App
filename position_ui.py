# ui/position_ui.py - PyQt5 zu PyQt6 migriert
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import (QWidget, QFormLayout, QLineEdit, QComboBox, 
                            QTextEdit, QDoubleSpinBox, QPushButton, QDialog,
                            QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
                            QTableWidgetItem, QHeaderView, QGridLayout, QFrame)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QIcon
from models.product import ProductType

class PositionListUI(QWidget):
    """UI component for displaying and interacting with a list of positions."""
    
    # Signals
    position_selected = pyqtSignal(int)
    
    def __init__(self, parent=None):
        """Initialize the position list UI component."""
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Positions table
        self.positions_table = QTableWidget()
        self.positions_table.setColumnCount(5)
        self.positions_table.setHorizontalHeaderLabels(["Nr.", "Titel", "Produkttyp", "Menge", "Preis"])
        self.positions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.positions_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.positions_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.positions_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.positions_table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.positions_table)
        
    def set_positions(self, positions):
        """Set the positions to display in the table."""
        self.positions_table.setRowCount(0)
        
        for position in positions:
            row = self.positions_table.rowCount()
            self.positions_table.insertRow(row)
            
            # Position number
            number_item = QTableWidgetItem(position.get('number', ''))
            self.positions_table.setItem(row, 0, number_item)
            
            # Title
            title_item = QTableWidgetItem(position.get('title', ''))
            self.positions_table.setItem(row, 1, title_item)
            
            # Product Type
            product_type = position.get('product_type', '')
            product_type_item = QTableWidgetItem(product_type)
            self.positions_table.setItem(row, 2, product_type_item)
            
            # Quantity
            quantity = position.get('quantity', 0.0)
            quantity_item = QTableWidgetItem(f"{quantity:.2f}")
            quantity_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.positions_table.setItem(row, 3, quantity_item)
            
            # Price
            price = position.get('price', 0.0)
            price_item = QTableWidgetItem(f"{price:.2f} €")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.positions_table.setItem(row, 4, price_item)
            
            # Store position ID as item data (hidden)
            number_item.setData(Qt.ItemDataRole.UserRole, position.get('id'))
            
    def select_position(self, position_id):
        """Select a position in the table by its ID."""
        for row in range(self.positions_table.rowCount()):
            item = self.positions_table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == position_id:
                self.positions_table.selectRow(row)
                break
                
    def _on_selection_changed(self, selected, deselected):
        """Handle table selection change."""
        indexes = selected.indexes()
        if indexes:
            # Get the position ID from the first cell of the selected row
            position_id = indexes[0].data(Qt.ItemDataRole.UserRole)
            if position_id:
                self.position_selected.emit(position_id)


class PositionDetailUI(QWidget):
    """UI component for displaying and editing position details."""
    
    # Signals
    product_selected = pyqtSignal(object)  # List of product IDs
    product_type_selected = pyqtSignal(object)  # ProductType signal
    
    def __init__(self, parent=None):
        """Initialize the position detail UI component."""
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        """Set up the UI components."""
        # Main layout
        layout = QFormLayout(self)
        
        # Position template selection
        template_layout = QHBoxLayout()
        self.template_combo = QComboBox()
        self.template_combo.currentTextChanged.connect(self._on_template_selected)
        template_layout.addWidget(self.template_combo)
        
        self.no_template_checkbox = QPushButton("Ohne Vorlage")
        self.no_template_checkbox.setCheckable(True)
        self.no_template_checkbox.clicked.connect(self._on_no_template_clicked)
        template_layout.addWidget(self.no_template_checkbox)
        
        layout.addRow("Vorlage:", template_layout)
        
        # Position number
        self.position_number_edit = QLineEdit()
        layout.addRow("Position Nr.:", self.position_number_edit)
        
        # Title
        self.title_edit = QLineEdit()
        layout.addRow("Titel:", self.title_edit)
        
        # Product selection with button
        product_layout = QHBoxLayout()
        self.product_edit = QLineEdit()
        self.product_edit.setReadOnly(True)
        product_layout.addWidget(self.product_edit)
        
        self.select_product_button = QPushButton("Auswählen...")
        self.select_product_button.clicked.connect(self._open_product_selection_dialog)
        product_layout.addWidget(self.select_product_button)
        
        layout.addRow("Produkt:", product_layout)
        
        # Description
        self.description_edit = QTextEdit()
        layout.addRow("Beschreibung:", self.description_edit)
        
        # Quantity
        self.quantity_spin = QDoubleSpinBox()
        self.quantity_spin.setRange(0, 9999.99)
        self.quantity_spin.setDecimals(2)
        layout.addRow("Menge:", self.quantity_spin)
        
        # Unit
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["Stück", "m", "m²", "m³", "Pauschal"])
        layout.addRow("Einheit:", self.unit_combo)
        
        # Price
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 999999.99)
        self.price_spin.setDecimals(2)
        self.price_spin.setSuffix(" €")
        layout.addRow("Preis:", self.price_spin)
        
        # Store template data
        self._templates = []
        self._selected_template = None
        
    def set_data(self, position_data):
        """Set the UI fields from position data."""
        if not position_data:
            self.clear()
            return
        
        # Set template if available
        template_code = position_data.get('template_code', '')
        if template_code:
            template_index = self.template_combo.findData(template_code)
            if template_index >= 0:
                self.template_combo.setCurrentIndex(template_index)
            
        self.position_number_edit.setText(position_data.get('number', ''))
        self.title_edit.setText(position_data.get('title', ''))
        
        # Handle multiple products
        product_ids = position_data.get('product_ids', [])
        if product_ids:
            # For now, show count of selected products
            self.product_edit.setText(f"{len(product_ids)} Produkte ausgewählt")
        else:
            # Fallback to legacy single product display
            self.product_edit.setText(position_data.get('product_name', ''))
        self.description_edit.setText(position_data.get('description', ''))
        self.quantity_spin.setValue(position_data.get('quantity', 0.0))
        
        unit = position_data.get('unit', 'Stück')
        unit_index = self.unit_combo.findText(unit)
        if unit_index >= 0:
            self.unit_combo.setCurrentIndex(unit_index)
            
        self.price_spin.setValue(position_data.get('price', 0.0))
        
        # Store the product ID and type (not displayed in UI)
        self._current_product_id = position_data.get('product_id', None)
        self._selected_product_ids = position_data.get('product_ids', [])
        
        # Set product type if available
        product_type_str = position_data.get('product_type', '')
        if product_type_str:
            # Try to find matching ProductType
            from models.product import ProductType
            for pt in ProductType:
                if pt.display_name == product_type_str:
                    self.selected_product_type = pt
                    break
            else:
                # If no exact match, store as string
                self.selected_product_type = product_type_str
        
    def get_data(self):
        """Get the data from UI fields."""
        template_code = ""
        if not self.no_template_checkbox.isChecked() and self.template_combo.currentData():
            template_code = self.template_combo.currentData()
            
        return {
            'template_code': template_code,
            'number': self.position_number_edit.text(),
            'title': self.title_edit.text(),
            'product_id': getattr(self, '_current_product_id', None),  # Legacy support
            'product_ids': getattr(self, '_selected_product_ids', []),  # New multi-select
            'product_name': self.product_edit.text(),
            'product_type': getattr(self, 'selected_product_type', None),
            'description': self.description_edit.toPlainText(),
            'quantity': self.quantity_spin.value(),
            'unit': self.unit_combo.currentText(),
            'price': self.price_spin.value()
        }
        
    def clear(self):
        """Clear all form fields."""
        self.template_combo.setCurrentIndex(0)
        self.no_template_checkbox.setChecked(False)
        self.position_number_edit.clear()
        self.title_edit.clear()
        self.product_edit.clear()
        self.description_edit.clear()
        self.quantity_spin.setValue(0.0)
        self.unit_combo.setCurrentIndex(0)
        self.price_spin.setValue(0.0)
        self._current_product_id = None
        self._selected_product_ids = []
        self._selected_template = None
        
    def _load_default_products(self):
        """Load default products if no products service is available."""
        # Default products for demonstration
        self._products = [
            {'id': 1, 'name': 'Kunststofffenster Standard', 'price': 249.99},
            {'id': 2, 'name': 'Aluminium-Fenster Premium', 'price': 499.99},
            {'id': 3, 'name': 'Holzfenster Natur', 'price': 399.99},
            {'id': 4, 'name': 'Rolllade Standard', 'price': 149.99},
            {'id': 5, 'name': 'Rolllade Elektrisch', 'price': 299.99},
            {'id': 6, 'name': 'Insektenschutz', 'price': 89.99},
            {'id': 7, 'name': 'Fensterbrett innen', 'price': 59.99},
            {'id': 8, 'name': 'Fensterbrett außen', 'price': 79.99},
            {'id': 9, 'name': 'Plissee Standard', 'price': 129.99},
            {'id': 10, 'name': 'Markise Gelenkarm', 'price': 599.99}
        ]
        
    def _open_product_selection_dialog(self):
        """Open the dialog for product selection."""
        # Load products data if not already loaded
        if not hasattr(self, '_products') or not self._products:
            self._load_default_products()
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Produkt auswählen")
        dialog.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Product type selection with icons
        type_frame = QFrame()
        type_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        type_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 5px;
                padding: 10px;
            }
        """)
        type_layout = QVBoxLayout(type_frame)
        
        type_label = QLabel("<b>Produktkategorie wählen:</b>")
        type_layout.addWidget(type_label)
        
        # Icon grid for product types
        icon_grid = QGridLayout()
        self.selected_product_type = None
        self.type_buttons = {}
        
        for i, product_type in enumerate(ProductType):
            btn = QPushButton()
            btn.setFixedSize(120, 80)
            btn.setStyleSheet("""
                QPushButton {
                    border: 2px solid #dee2e6;
                    border-radius: 8px;
                    background-color: white;
                    text-align: center;
                    padding: 5px;
                }
                QPushButton:hover {
                    border-color: #0070f5;
                    background-color: #f0f8ff;
                }
                QPushButton:checked {
                    border-color: #0070f5;
                    background-color: #e3f2fd;
                    font-weight: bold;
                }
            """)
            btn.setCheckable(True)
            
            # Try to load icon
            if product_type.icon_exists():
                icon = QIcon(product_type.icon_path)
                btn.setIcon(icon)
                btn.setIconSize(btn.size() * 0.6)
            
            btn.setText(product_type.display_name)
            btn.clicked.connect(lambda checked, pt=product_type: self._on_product_type_selected(pt))
            
            self.type_buttons[product_type] = btn
            row, col = divmod(i, 3)  # 3 columns
            icon_grid.addWidget(btn, row, col)
        
        type_layout.addLayout(icon_grid)
        layout.addWidget(type_frame)
        
        # Search field
        search_layout = QHBoxLayout()
        search_label = QLabel("Suche:")
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self._filter_products)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Products table with multi-selection
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["Auswahl", "ID", "Name", "Preis"])
        self.products_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.products_table.setSelectionMode(QTableWidget.SelectionMode.MultiSelection)
        self.products_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.products_table)
        
        # Track selected product IDs
        self._dialog_selected_product_ids = getattr(self, '_selected_product_ids', []).copy()
        
        # Buttons
        button_layout = QHBoxLayout()
        select_button = QPushButton("Auswählen")
        select_button.clicked.connect(self._accept_multi_product_selection)
        cancel_button = QPushButton("Abbrechen")
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(select_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # Store dialog as instance variable for later reference
        self._product_dialog = dialog
        
        # Populate products table with loaded data
        self._populate_products_table(self._products)
        
        # Show dialog
        dialog.exec()
    
    def _on_product_type_selected(self, product_type: ProductType):
        """Handle product type selection."""
        # Uncheck all other buttons
        for btn in self.type_buttons.values():
            btn.setChecked(False)
        
        # Check selected button
        self.type_buttons[product_type].setChecked(True)
        self.selected_product_type = product_type
        
    def get_selected_product_type(self) -> ProductType:
        """Get the currently selected product type."""
        return self.selected_product_type
        
    def set_products(self, products):
        """Set the products to display in the selection dialog."""
        self._products = products
        # Populate table only if it exists (dialog has been opened)
        if hasattr(self, 'products_table'):
            self._populate_products_table(products)
        
    def _populate_products_table(self, products):
        """Populate the products table with the given products."""
        from PyQt6.QtWidgets import QCheckBox
        from PyQt6.QtCore import Qt
        
        self.products_table.setRowCount(0)
        
        for product in products:
            row = self.products_table.rowCount()
            self.products_table.insertRow(row)
            
            # Checkbox for selection
            checkbox = QCheckBox()
            product_id = product.get('id', 0)
            if product_id in getattr(self, '_dialog_selected_product_ids', []):
                checkbox.setChecked(True)
            checkbox.stateChanged.connect(lambda state, pid=product_id: self._on_product_checkbox_changed(state, pid))
            self.products_table.setCellWidget(row, 0, checkbox)
            
            # ID
            id_item = QTableWidgetItem(str(product_id))
            self.products_table.setItem(row, 1, id_item)
            
            # Name
            name_item = QTableWidgetItem(product.get('name', ''))
            self.products_table.setItem(row, 2, name_item)
            
            # Price
            price = product.get('price', 0.0)
            price_item = QTableWidgetItem(f"{price:.2f} €")
            price_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self.products_table.setItem(row, 3, price_item)
            
    def _filter_products(self, text):
        """Filter the products table based on search text."""
        if not hasattr(self, '_products'):
            return
            
        filtered_products = []
        
        for product in self._products:
            if (text.lower() in str(product.get('id', '')).lower() or
                    text.lower() in product.get('name', '').lower()):
                filtered_products.append(product)
                
        self._populate_products_table(filtered_products)
        
    def _accept_product_selection(self):
        """Handle product selection from the dialog."""
        selected_rows = self.products_table.selectedIndexes()
        
        if not selected_rows:
            return
            
        # Get the row of the first selected cell
        row = selected_rows[0].row()
        
        # Get product ID and name
        product_id = int(self.products_table.item(row, 0).text())
        product_name = self.products_table.item(row, 1).text()
        
        # Update the product field
        self.product_edit.setText(product_name)
        self._current_product_id = product_id
        
        # Emit signal
        self.product_selected.emit(product_id)
        
        # Close dialog
        self._product_dialog.accept()
    
    def _on_product_checkbox_changed(self, state, product_id):
        """Handle product checkbox state change."""
        if not hasattr(self, '_dialog_selected_product_ids'):
            self._dialog_selected_product_ids = []
            
        if state == 2:  # Checked
            if product_id not in self._dialog_selected_product_ids:
                self._dialog_selected_product_ids.append(product_id)
        else:  # Unchecked
            if product_id in self._dialog_selected_product_ids:
                self._dialog_selected_product_ids.remove(product_id)
    
    def _accept_product_type_selection(self):
        """Handle product type selection acceptance."""
        if hasattr(self, 'selected_product_type') and self.selected_product_type:
            # Update the product field with the selected type
            self.product_edit.setText(self.selected_product_type.display_name)
            
            # Emit the product type selected signal
            self.product_type_selected.emit(self.selected_product_type)
            
            # Close dialog
            self._product_dialog.accept()
        else:
            # Show warning if no product type selected
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self._product_dialog, "Auswahl erforderlich", 
                              "Bitte wählen Sie einen Produkttyp aus.")
    
    def _accept_multi_product_selection(self):
        """Handle multi-product selection acceptance."""
        if not hasattr(self, '_dialog_selected_product_ids'):
            self._dialog_selected_product_ids = []
            
        if self._dialog_selected_product_ids:
            # Store selected product IDs
            self._selected_product_ids = self._dialog_selected_product_ids.copy()
            
            # Update UI display
            count = len(self._selected_product_ids)
            self.product_edit.setText(f"{count} Produkt{'e' if count != 1 else ''} ausgewählt")
            
            # Emit signal with selected product IDs
            self.product_selected.emit(self._selected_product_ids)
            
            # Close dialog
            self._product_dialog.accept()
        else:
            # Show warning if no products selected
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self._product_dialog, "Auswahl erforderlich", 
                              "Bitte wählen Sie mindestens ein Produkt aus.")
    
    def set_templates(self, templates):
        """Set available position templates."""
        self._templates = templates
        self.template_combo.clear()
        self.template_combo.addItem("-- Vorlage wählen --", "")
        
        for template in templates:
            self.template_combo.addItem(template.display_name, template.code)
    
    def _on_template_selected(self, text):
        """Handle template selection."""
        if self.template_combo.currentData():
            template_code = self.template_combo.currentData()
            # Find the selected template
            self._selected_template = None
            for template in self._templates:
                if template.code == template_code:
                    self._selected_template = template
                    break
            
            if self._selected_template:
                # Pre-fill form fields from template
                if self._selected_template.name and not self.title_edit.text():
                    self.title_edit.setText(self._selected_template.name)
                
                # Set product if default product type is specified
                if self._selected_template.default_product_type:
                    # Here we could pre-select the product type in the product dialog
                    pass
                
                # Uncheck "Ohne Vorlage"
                self.no_template_checkbox.setChecked(False)
    
    def _on_no_template_clicked(self, checked):
        """Handle 'Ohne Vorlage' checkbox."""
        if checked:
            self.template_combo.setCurrentIndex(0)  # Reset to "-- Vorlage wählen --"
            self._selected_template = None
    
    def get_selected_template(self):
        """Get the currently selected template."""
        return self._selected_template
    
    def set_product_type(self, product_type: ProductType):
        """Set the selected product type."""
        self.selected_product_type = product_type
        if product_type:
            self.product_edit.setText(product_type.display_name)