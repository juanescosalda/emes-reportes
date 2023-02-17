# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 17:31:01 2022

@author: juane
"""

# %% PyQT UI test
import os
import sys
import logging
import locale
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.uic import loadUi
from client.widgets import SuppliersWindow, TableViewWindow
from client.worker import Worker
import client.logo_emes as logo_emes


locale.setlocale(locale.LC_ALL, '')


class MainWindow(QDialog):

    def __init__(self, emes=None):
        """
        Constructor

        Args:
            emes (EmesReport): EmesReport object
        """
        super().__init__()
        loadUi("gui/gui.ui", self)

        # Copy EmesReport object
        self._emes = emes

        # Initialize thread pool
        self.threadpool = QThreadPool()

        # Create suppliers subwindow
        self.subwindow_suppliers = SuppliersWindow()

        # Create tableview subwindow
        self.subwindow_table = TableViewWindow()

        # all suppliers list
        self.all_suppliers = []
        self.suppliers = []

        # Upload buttons
        self.advancePath.clicked.connect(self.browse_advance_file)
        self.suppliersPath.clicked.connect(self.browse_suppliers_file)
        self.toPath.clicked.connect(self.set_directory_to_save_files)

        # Main buttons
        self.uploadButton.pressed.connect(self.click_upload_button)
        self.chooseSuppliersButton.clicked.connect(self.click_show_suppliers)
        self.runButton.clicked.connect(self.click_create_summary)
        self.useButton.clicked.connect(self.click_include_use)

        # Set default values
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
        df = self._emes.summary.copy().reset_index(drop=False)
        cols = self._emes.active_suppliers

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
        worker = Worker(self.__upload_files)
        worker.signals.result.connect(self.print_output)
        worker.signals.progress.connect(self.progress_fn)
        worker.signals.finished.connect(self.__show_subwindow_listview)

        # Start thread
        self.threadpool.start(worker)

    def __thread_create_summary(self):
        """
        Add thread to create report Emes
        """
        worker = Worker(self.__create_summary)
        worker.signals.result.connect(self.print_output)
        worker.signals.progress.connect(self.progress_fn)
        worker.signals.finished.connect(self.__show_subwindow_table)

        # Start thread
        self.threadpool.start(worker)

    def __thread_include_use(self):
        """
        Add thread to create report Emes
        """
        # worker
        worker = Worker(self.__include_use)
        worker.signals.result.connect(self.print_output)
        worker.signals.progress.connect(self.progress_fn)
        worker.signals.finished.connect(self.__alert)

        # Start thread
        self.threadpool.start(worker)

    def __upload_files(self) -> None:
        """
        Instantiate EmesReport class and pass args
        """
        path_grid = self.advanceFile.text()
        path_groups = self.suppliersFile.text()
        path_to = self.toFile.text()

        try:
            self._emes.initialize(
                path_to,
                path_grid,
                path_groups
            )

            if self._emes:
                self.all_suppliers = self._emes.get_suppliers()

        except (PermissionError, FileNotFoundError):
            self.__error_msg_box(
                'No se pudieron cargar los archivos'
            )

    def __create_summary(self):
        """
        Generate summary without use (aprovechamiento)
        """
        self.suppliers = self.subwindow_suppliers.values

        try:
            self._emes.run(
                self.suppliers,
                use_mode=False,
                include_reports=False
            )

        except AttributeError:
            self.__error_msg_box(
                'Aún no se han cargado los archivos'
            )

    def __include_use(self):
        """
        Include use (aprovechamiento)
        """
        self.suppliers = self.subwindow_suppliers.values

        try:
            self._emes.include_use(
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


def run_ui(emes):
    app = QApplication(sys.argv)
    mainwindow = MainWindow(emes)
    widget = QStackedWidget()
    widget.addWidget(mainwindow)
    widget.setFixedWidth(945)
    widget.setFixedHeight(630)
    widget.show()
    sys.exit(app.exec())
