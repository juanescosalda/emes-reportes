import locale
import logging
from pandas.core.frame import DataFrame
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class ChecklistDialog(QDialog):

    def __init__(
            self,
            name,
            suppliers=None,
            checked=False,
            icon=None,
            parent=None):
        """
        Constructor
        """
        super().__init__(parent)

        self.name = name
        self.model = QStandardItemModel()
        self.listView = QListView()

        for supplier in suppliers:
            item = QStandardItem(supplier)
            item.setCheckable(True)
            check = \
                (Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked)
            item.setCheckState(check)
            self.model.appendRow(item)

        self.listView.setModel(self.model)
        self.listView.setSizeAdjustPolicy(
            QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )

        # Create buttons
        self.okButton = QPushButton("OK")
        self.cancelButton = QPushButton("Cancel")
        self.selectButton = QPushButton("Select All")
        self.unselectButton = QPushButton("Unselect All")

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)
        hbox.addWidget(self.selectButton)
        hbox.addWidget(self.unselectButton)

        vbox = QVBoxLayout()
        vbox.addWidget(self.listView)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setWindowTitle(self.name)

        if icon:
            self.setWindowIcon(icon)

        self.okButton.clicked.connect(self.onAccept)
        self.cancelButton.clicked.connect(self.reject)
        self.selectButton.clicked.connect(self.select)
        self.unselectButton.clicked.connect(self.unselect)

    def reject(self):
        QDialog.reject(self)

    def onAccept(self):
        self.choices = \
            [
                self.model.item(i).text()
                for i in range(self.model.rowCount())
                if self.model.item(i).checkState() == Qt.CheckState.Checked
            ]

        self.accept()

    def select(self):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            item.setCheckState(Qt.CheckState.Checked)

    def unselect(self):
        for i in range(self.model.rowCount()):
            item = self.model.item(i)
            item.setCheckState(Qt.CheckState.Unchecked)


class TableView(QDialog):

    def __init__(self, df: DataFrame):
        super().__init__()
        rows = df.shape[0]

        # Controls
        self.model = QStandardItemModel(rows, 4)
        self.tableView = QTableView()

        self.model.setHorizontalHeaderLabels([
            'Nombre del proveedor',
            'Descuento sistema',
            'Descuento feria',
            'Diferencia feria $',
            'Aprovechamiento'
        ])

        # Features
        self.tableView.setModel(self.model)
        self.tableView.setSizeAdjustPolicy(
            QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )
        self.tableView.resizeColumnsToContents()
        self.tableView.setShowGrid(False)

        try:
            for idx, row in df.iterrows():
                # Supplier column
                item = QStandardItem(row['Proveedor'])
                item.setTextAlignment(Qt.AlignmentFlag.AlignLeft)
                self.model.setItem(idx, 0, item)

                # 260 discount column
                temp = locale.currency(
                    row['Descuento sistema'],
                    grouping=True,
                    symbol=True
                )
                item = QStandardItem(temp)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.model.setItem(idx, 1, item)

                # Note discount column
                temp = locale.currency(
                    row['Descuento feria'],
                    grouping=True,
                    symbol=True
                )
                item = QStandardItem(temp)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.model.setItem(idx, 2, item)

                # Difference between discounts column
                temp = locale.currency(
                    row['Diferencia feria $'],
                    grouping=True,
                    symbol=True
                )
                item = QStandardItem(temp)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.model.setItem(idx, 3, item)

                # 'Aprovechamiento' column
                item = QStandardItem("0")
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.model.setItem(idx, 4, item)

        except KeyError:
            logging.error(
                "No existe la columna en el dataframe",
                exc_info=True
            )

        # Create buttons
        self.okButton = QPushButton("OK")
        self.cancelButton = QPushButton("Cancel")

        # Add widgets to layout
        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)

        vbox = QVBoxLayout()
        vbox.addWidget(self.tableView)
        vbox.addStretch(1)
        vbox.addLayout(hbox)

        self.setLayout(vbox)

        self.okButton.clicked.connect(self.onAccept)
        self.cancelButton.clicked.connect(self.reject)

    def onAccept(self):
        """
        OK button click action
        """
        self.choices = \
            {
                self.model.item(i, 0).text():
                self.__str2float(self.model.item(i, 4).text())
                for i in range(self.model.rowCount())
            }

        self.accept()

    def __str2float(self, text: str) -> float:
        """
        Args:
            text (str): value in string format

        Returns:
            float: value converted to float
        """
        try:
            if text.find('%') == -1:
                out_value = float(text)
            else:
                out_value = float(text[:-1]) / 100.0

        except ValueError:
            logging.error(
                'El texto no se puede convertir a número',
                exc_info=True
            )

            out_value = 0.0

        return out_value
