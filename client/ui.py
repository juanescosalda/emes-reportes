# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 17:31:01 2022

@author: juane
"""

# %% PyQT UI test
import sys
import logging
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.uic import loadUi
from server.report import EmesReport
import os
import traceback
from pandas.core.frame import DataFrame
import locale
import client.logo_emes as logo_emes

logging.basicConfig(filename='gui.log',
                    format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')

locale.setlocale(locale.LC_ALL, '')


class WorkerSignals(QObject):
    """
    Defines the signals available from a running worker thread.

    finished: No data
    error: tuple (exctype, value, traceback.format_exc() )
    result: object data returned from processing, anything

    """
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    type callback: function
    """

    def __init__(self, fn, *args):
        super().__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        try:
            result = self.fn(*self.args)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class ChecklistDialog(QDialog):

    def __init__(
            self,
            name,
            suppliers=None,
            checked=False,
            icon=None,
            parent=None):

        super().__init__(parent)

        self.name = name
        self.icon = icon
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

        # create buttons
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
        if self.icon is not None:
            self.setWindowIcon(self.icon)

        self.okButton.clicked.connect(self.onAccept)
        self.cancelButton.clicked.connect(self.reject)
        self.selectButton.clicked.connect(self.select)
        self.unselectButton.clicked.connect(self.unselect)

    def reject(self):
        QDialog.reject(self)

    def onAccept(self):
        self.choices = [
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

        # controls
        self.model = QStandardItemModel(rows, 4)
        self.tableView = QTableView()

        self.model.setHorizontalHeaderLabels([
            'Nombre del proveedor',
            'Descuento sistema',
            'Descuento feria',
            'Diferencia feria $',
            'Aprovechamiento'
        ])

        # features
        self.tableView.setModel(self.model)
        self.tableView.setSizeAdjustPolicy(
            QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents
        )
        self.tableView.resizeColumnsToContents()
        self.tableView.setShowGrid(False)

        try:
            for idx, row in df.iterrows():
                # supplier column
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

                # note discount column
                temp = locale.currency(
                    row['Descuento feria'],
                    grouping=True,
                    symbol=True
                )
                item = QStandardItem(temp)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
                self.model.setItem(idx, 2, item)

                # difference between discounts column
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

        # create buttons
        self.okButton = QPushButton("OK")
        self.cancelButton = QPushButton("Cancel")

        # add widgets to layout
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
        self.choices = {
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
        out_value = 0.0

        try:
            if text.find('%') == -1:
                out_value = float(text)
            else:
                out_value = float(text[0:-1]) / 100.0

        except ValueError:
            logging.error(
                'El texto no se puede convertir a número',
                exc_info=True
            )

        return out_value


class TableViewWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self):
        super().__init__()
        self.resize(850, 450)

    def add_data(self, df: DataFrame) -> None:
        """
        Args:
            suppliers (list): company suppliers
        """
        self.form = TableView(df)

        # execute check list
        if self.form.exec():
            self.values = self.form.choices
        else:
            self.values = list()


class SuppliersWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self):
        super().__init__()
        self.resize(850, 450)

    def add_suppliers(self, suppliers: list):
        """
        Args:
            suppliers (list): company suppliers
        """
        self.form = ChecklistDialog(
            "Proveedores",
            suppliers,
            checked=True
        )

        # execute check list
        if self.form.exec():
            self.values = [str(value) for value in self.form.choices]
        else:
            self.values = list()


class MainWindow(QDialog):

    def __init__(self):
        super().__init__()
        loadUi("gui.ui", self)

        # init threadpool
        self.threadpool = QThreadPool()

        # create suppliers subwindow
        self.subwindow_suppliers = SuppliersWindow()

        # create tableview subwindow
        self.subwindow_table = TableViewWindow()

        # all suppliers list
        self.all_suppliers = list()
        self.suppliers = list()

        # upload buttons
        self.advancePath.clicked.connect(self.browse_advance_file)
        self.suppliersPath.clicked.connect(self.browse_suppliers_file)
        self.toPath.clicked.connect(self.set_directory_to_save_files)

        # main buttons
        self.uploadButton.pressed.connect(self.click_upload_button)
        self.chooseSuppliersButton.clicked.connect(self.click_show_suppliers)
        self.runButton.clicked.connect(self.click_create_summary)
        self.useButton.clicked.connect(self.click_include_use)

        # default value
        self._path_groups = os.path.expanduser(
            r'~\Documentos\Emes\suppliers report\data'
        )

        if not os.path.exists(self._path_groups):
            self._path_groups = os.path.expanduser(
                r'~\OneDrive\Documentos\Emes\suppliers report\data'
            )

        self.suppliersFile.setText(
            self._path_groups + '\\proveedores.xlsx'
        )

    def __alert(self) -> int:
        """
        Create and show QMessageBox
        """
        msg = QMessageBox(
            parent=self,
            text="Se han terminado de crear todos los reportes"
        )

        msg.setWindowTitle("Completado")
        msg.setIcon(QMessageBox.Icon.Information)
        ret = msg.exec()

        return ret

    def __show_subwindow_listview(self):
        """
        Show subwindow of selected suppliers
        """
        self.subwindow_suppliers.add_suppliers(self.all_suppliers)
        self.subwindow_suppliers.setParent(self)
        self.subwindow_suppliers.show()

    def __show_subwindow_table(self):
        """
        Show subwindow of table summary and use input
        """
        df = self.emes.summary.copy().reset_index(drop=False)
        cols = self.emes.active_suppliers

        df_ss = df[df['Proveedor'].isin(cols)].reset_index(drop=True)

        self.subwindow_table.add_data(df_ss)
        self.subwindow_table.setParent(self)
        self.subwindow_table.show()

    def progress_fn(self, n):
        print("%d%% done" % n)

    def print_output(self, s):
        print(s)

    def thread_complete(self):
        print("Thread complete!")

    def click_show_suppliers(self):
        """
        Button click method to show suppliers in subwindow
        """
        self.__show_subwindow_listview()

    def click_upload_button(self):
        """
        Button click method to create EmesReport object
        """
        self.__thread_upload_files()

    def click_create_summary(self):
        """
        Button click method to create summary
        """
        self.__thread_create_summary()

    def click_include_use(self):
        """
        Button click method to include use
        """
        self.__thread_include_use()

    def __thread_upload_files(self):
        """
        Add thread to create EmesReport object and upload files
        """
        worker = Worker(self.__upload_files, None)
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.__show_subwindow_listview)
        worker.signals.progress.connect(self.progress_fn)

        # start thread
        self.threadpool.start(worker)

    def __thread_create_summary(self):
        """
        Add thread to create report Emes
        """
        worker = Worker(self.__create_summary, None)
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.__show_subwindow_table)
        worker.signals.progress.connect(self.progress_fn)

        # start thread
        self.threadpool.start(worker)

    def __thread_include_use(self):
        """
        Add thread to create report Emes
        """
        # worker
        worker = Worker(self.__include_use, None)
        worker.signals.result.connect(self.print_output)
        worker.signals.finished.connect(self.__alert)
        worker.signals.progress.connect(self.progress_fn)

        # start thread
        self.threadpool.start(worker)

    def __upload_files(self, *args) -> None:
        """
        Instantiate EmesReport class and pass args
        """
        path_grid = self.advanceFile.text()
        path_groups = self.suppliersFile.text()
        path_to = self.toFile.text()

        try:
            self.emes = EmesReport(
                path_grid,
                path_to,
                path_groups
            )

            if self.emes is not None:
                self.all_suppliers = self.emes.get_suppliers()

        except (PermissionError, FileNotFoundError):
            self.__error_msg_box(
                'No se pudieron cargar los archivos'
            )

    def __create_summary(self, *args):
        """
        Generate summary without use (aprovechamiento)
        """
        self.suppliers = self.subwindow_suppliers.values

        try:
            self.emes.run(
                self.suppliers,
                use_mode=False,
                include_reports=False
            )
        except AttributeError:
            self.__error_msg_box(
                'Aún no se han cargado los archivos'
            )

    def __include_use(self, *args):
        """
        Include use (aprovechamiento)
        """
        self.suppliers = self.subwindow_suppliers.values

        try:
            self.emes.include_use(
                self.suppliers,
                self.subwindow_table.values
            )
        except AttributeError:
            self.__error_msg_box(
                'Aún no se han cargado los archivos'
            )

    def __error_msg_box(self, msg_str) -> bool:
        """
        Message box if error
        """
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)

        # setting message for Message Box
        msg.setText(msg_str)

        # setting Message box window title
        msg.setWindowTitle("Error")
        res = msg.exec()

        # save in the log
        logging.error(
            msg_str,
            exc_info=True
        )

        return res

    def browse_advance_file(self):
        """
        Browse Advance 260 report
        """
        fname = QFileDialog.getOpenFileName(
            self,
            caption='Open file',
            directory='C:\smd_files\grid_export'
        )

        self.advanceFile.setText(
            os.path.normpath(fname[0])
        )

    def browse_suppliers_file(self):
        """
        Browse suppliers file
        """
        fname = QFileDialog.getOpenFileName(
            self,
            caption='Open file',
            directory=self._path_groups
        )

        self.suppliersFile.setText(
            os.path.normpath(fname[0])
        )

    def set_directory_to_save_files(self):
        """
        Set directory to store data
        """
        path = os.path.expanduser(
            r'~\Documentos\Emes\suppliers report\reports'
        )

        if not os.path.exists(path):
            path = os.path.expanduser(
                r'~\OneDrive\Documentos\Emes\suppliers report\reports'
            )

        fname = QFileDialog.getExistingDirectory(
            self,
            caption='Open a folder',
            directory=path,
            options=QFileDialog.Option.ShowDirsOnly
        )

        self.toFile.setText(
            os.path.normpath(fname)
        )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainwindow = MainWindow()
    widget = QStackedWidget()
    widget.addWidget(mainwindow)
    widget.setFixedWidth(945)
    widget.setFixedHeight(630)
    widget.show()
    sys.exit(app.exec())
