from PyQt6.QtWidgets import *
from client.dialogs import ChecklistDialog, TableView
from pandas.core.frame import DataFrame


class SuppliersWindow(QWidget):

    def __init__(self, parent: QWidget = None):
        """
        Constructor

        Args:
            parent (QWidget o QDialog, optional): Parent widget or dialog. Defaults to None.
        """
        super().__init__(parent)
        self.resize(850, 450)
        self.form = None

    def add_suppliers(self, suppliers: list):
        """
        Displays a checklist dialog for selecting suppliers.

        Args:
            suppliers (list): A list of company suppliers.

        Returns:
            A list of selected supplier names.
        """
        self.form = ChecklistDialog(
            name="Proveedores",
            suppliers=suppliers,
            checked=True
        )

        # Execute check list
        if self.form.exec():
            self.values = [str(value) for value in self.form.choices]
        else:
            self.values = []


class TableViewWindow(QWidget):

    def __init__(self, parent: QWidget = None):
        """
        Constructor

        Args:
            parent (QObject, optional): Parent widget or dialog. Defaults to None.
        """
        super().__init__(parent)
        self.resize(850, 450)
        self.form = None

    def add_data(self, df: DataFrame) -> None:
        """
        Args:
            suppliers (list): company suppliers
        """
        self.form = TableView(df)

        self.values = self.form.choices if self.form.exec() else []
