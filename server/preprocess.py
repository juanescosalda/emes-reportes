
import os
import csv
import pickle
import calendar
import logging
import server.utils as utils
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame
from pandas.core.series import Series
from datetime import date


class Preprocessing:

    COLS = \
        [
            "Grupo",
            "Subgrupo",
            "Código",
            "Descripción",
            "Bodega",
            "Id Cliente",
            "Cliente",
            "Tipo",
            "Número",
            "Fecha",
            "Cantidad",
            "Precio Neto",
            "Costo Total",
            "Valor descuento",
            "% Descuento",
            "Vendedor",
            "NIT",
            "Sigla",
        ]

    NUM_COLS = \
        [
            "Cantidad",
            "Precio Neto",
            "Costo Total",
            "Valor descuento",
            "% Descuento"
        ]

    def __init__(self,
                 path_csv: str,
                 path_groups: str):
        """
        Constructor

        Args:
            path_grid (str): path to 260 report
            path_groups (str): path to "proveedores" file
        """
        self.base, self.discounts = \
            self.__request_df_groups(path_groups)

        # convert csv file into pkl file
        path_pkl = self.__csv_to_pkl(path_csv)

        # read main pickle file (260 report)
        self.data = self.__read_file(path_pkl)

    def __csv_to_pkl(self, path_csv: str) -> str:
        """
        Converts .csv file into .pkl file

        Args:
            path_csv (str): Path to csv file

        Returns:
            str: Path to pickle file
        """
        try:
            path_pkl = path_csv.replace('csv', 'pkl')

            if not os.path.exists(path_pkl):
                with open(path_csv, 'r') as f:
                    reader = csv.reader(f, delimiter=";")
                    pickle.dump(list(reader), open(path_pkl, 'wb'))

            return path_pkl

        except Exception as e:
            logging.error(
                f'Excepción {e} al crear el archivo .pkl',
                exc_info=True
            )

    def __request_df_groups(
            self,
            path_groups: str) -> tuple[DataFrame, DataFrame]:
        """
        Read Excel file and prepare dataframe

        Args:
            path_groups (str): Path to groups file

        Returns:
            tuple[DataFrame, DataFrame]: Price base and discounts dataframes
        """
        try:
            wb = pd.read_excel(
                path_groups,
                index_col=0,
                sheet_name=None
            )

            df_base = wb['Base']
            df_desc = wb['Descuentos']

            return (
                df_base,
                df_desc.astype({'Codigo': 'string'})
            )

        except Exception as e:
            logging.error(
                f'No se pudo inicializar el dataframe de grupos. Exception: {e}',
                exc_info=True
            )

            return (pd.DataFrame() for _ in range(2))

    def __read_file(self, path_grid: str) -> DataFrame:
        """
        Read main report file

        Args:
            path_grid (str): Path to pickle file

        Returns:
            DataFrame: Report 260
        """
        data = pd.read_pickle(
            path_grid
        )

        df = pd.DataFrame(data)

        df.columns = df.iloc[0]
        df = df[1:]
        df = df.set_index('Grupo', drop=True)

        return df

    def __drop_unneeded_rows(self, df: DataFrame) -> DataFrame:
        """
        Args:
            df (DataFrame): main dataframe

        Returns:
            DataFrame: With removed rows
        """
        dropped_suppliers = list(
            set(df.index) - set(self.base.index)
        )

        return df.drop(index=dropped_suppliers)

    def __drop_unneeded_cols(self, df: DataFrame) -> DataFrame:
        """
        Args:
            df (DataFrame): main dataframe

        Returns:
            DataFrame: dataframe with columns dropped
        """
        return df.drop(
            [
                "Id",
                "porcentaje_iva",
                "porcentaje_iva3",
                "Precio+Iva",
                "Valor Utilidad",
                "Costo Unidad",
                "%Uti",
                "notas",
                "vendedor_operacion",
                "direccion",
                "Ciudad",
                "Subgrupo3",
                "Subgrupo4",
                "Subgrupo5",
                "linea",
                "Alterna"
            ],
            axis='columns'
        )

    def __reset_index(self, df: DataFrame, drop: bool) -> DataFrame:
        """
        Reset dataframe index
        """
        return df.reset_index(
            drop=drop
        )

    def __set_column_names(self, df: DataFrame) -> DataFrame:
        """
        Raises:
            Exception: if columns does not match df columns
        """
        if len(df.columns) == len(Preprocessing.COLS):
            df.columns = Preprocessing.COLS
            return df
        else:
            raise Exception("Columns of the dataframe must be the same"
                            " as those in the list ")

    def __fill_nan_numeric_cols(self, df: DataFrame) -> DataFrame:
        """
        Args:
            df (DataFrame): Main dataframe

        Returns:
            DataFrame: dataframe with filled nan values
        """
        df.loc[:, Preprocessing.NUM_COLS] = \
            df.loc[:, Preprocessing.NUM_COLS].replace('', 0)

        return df

    def __set_dtypes(self, df: DataFrame) -> DataFrame:
        """
        Args:
            df (DataFrame): Main dataframe

        Returns:
            DataFrame: set data types
        """
        try:
            df[Preprocessing.NUM_COLS] = (
                df[Preprocessing.NUM_COLS]
                .replace(
                    {
                        r'^\((.*?)\)$': r'-\1',
                        r'[\,]': r'',
                        r'[\$]': r''
                    },
                    regex=True)
                .astype(float)
            )

            df = (
                df
                .astype(
                    {
                        'NIT': 'int64',
                        'Código': 'string'
                    }
                )
                .convert_dtypes()
            )

            df['Fecha'] = (
                df['Fecha']
                .apply(utils.format_datetime)
                .dt.strftime('%d/%m/%Y')
            )

        except Exception as e:
            logging.error(
                f"Error {e} cambiando los tipos de datos de las columnas numéricas y de tiempo",
                exc_info=True
            )

        return df

    def __include_net_prices(self, df: DataFrame) -> DataFrame:
        """
        Args:
            df (DataFrame): Main dataframe

        Returns:
            DataFrame: stores net prices with discount.
        """
        try:
            df['% Descuento'] = np.ceil(df['% Descuento']) / 100.0
            df['Precio Neto'] = df['Precio Neto'] / (1 - df['% Descuento'])

        except KeyError:
            logging.error(
                'No existen las columnas de precio neto o % descuento',
                exc_info=True
            )

        return df

    def _create_date_ranges(self, row: Series) -> list:
        """
        Args:
            row (Series): dataframe row as Series object

        Returns:
            list: contains all date ranges
        """
        dates = self.__get_discount_periods(
            dates=row['Fecha']
        )

        # create pd date_range for each row
        date_range = self.__create_date_range(
            year=self.__year,
            month=self.__month,
            discounts=dates
        )

        return date_range

    def __check_discount_day(
            self,
            year: str,
            month: str,
            dates: list) -> bool:
        """
        Check if discount range is valid

        Args:
            year (str): period year
            month (str): period month
            dates (list): contains prev and last day of each period

        Returns:
            bool: true is discount is valid
        """
        prev, last = map(int, dates)

        assert prev <= last, f"Invalid date range: {prev} - {last}"

        assert date(year, month, prev) <= date(
            year, month, last), f"Invalid date range: {prev} - {last}"

        last_day = calendar.monthrange(year, month)[1]
        assert last <= last_day, f"Invalid date range: {prev} - {last}"

        return True

    def __get_discount_periods(self, dates: str) -> list:
        """
        Split each row dates

        Args:
            dates (str): row dates

        Returns:
            list: contains splitted discount dates
        """
        days = \
            [
                day.split("_")
                for day in dates.split(";")
            ]

        return days

    def __is_discount_valid(
            self,
            year: str,
            month: str,
            discounts: list) -> bool:
        """
        Args:
            year (str): Period year
            month (str): Period month
            discounts (list): [prev, last] Day of each discount period

        Returns:
            bool: True is discount is valid
        """
        assert self.__check_discount_day(
            year, month, discounts), "Invalid discount date(s)"

        return True

    def __create_date_range(
            self,
            year: str,
            month: str,
            discounts: list) -> list:
        """
        Create pandas date_range object

        Args:
            year (str): Period year
            month (str): Period month
            discounts (list): [prev, last] Day of each discount period

        Returns:
            list: contains date_range objects
        """
        date_range = \
            [
                self.__get_date_range(start, end, month, year)
                for start, end in discounts if self.__is_discount_valid(year, month, [start, end])
            ]

        return sorted(set(sum(date_range, [])))

    def __get_date_range(
            self,
            prev: int,
            last: int,
            month: int,
            year: int) -> list:
        """
        Args:
            prev (int): First day of discount
            last (int): Last day of discount
            month (int): Month of report
            year (int): Year of report

        Returns:
            list: Date range of discounts
        """
        return (pd.date_range(
            start=f'{year}-{month}-{prev}',
            end=f'{year}-{month}-{last}'
        )
            .strftime('%d/%m/%Y')
            .tolist())

    def get_suppliers(self) -> dict:
        """
        Returns:
            dict: Format {"name": have_discount}
        """
        suppliers_with_discount = sorted(
            set(self.discounts.index.to_list()))

        return {
            name: name in suppliers_with_discount
            for name in self.base.index
        }

    def run(self) -> None:
        """
        Main method
        """
        # get month and year
        d = utils.format_datetime(
            self.data['fecha_factura'].values[0]
        )

        self.__month = d.month
        self.__year = d.year

        # preprocess main data report
        self.data = (
            self.data
            .pipe(self.__drop_unneeded_rows)
            .pipe(self.__drop_unneeded_cols)
            .pipe(self.__reset_index, False)
            .pipe(self.__set_column_names)
            .pipe(self.__fill_nan_numeric_cols)
            .pipe(self.__set_dtypes)
            .pipe(self.__include_net_prices)
        )

        # preprocess discounts df
        self.discounts.dropna(
            subset=['Fecha', '% Desc real'],
            inplace=True
        )

        self.discounts['Rango'] = \
            self.discounts.apply(
                self._create_date_ranges,
                axis=1
        )

        self.discounts.drop(
            columns=['Fecha', 'Descripción'],
            inplace=True
        )
