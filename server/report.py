import copy
import random
import logging
import pandas as pd
from server.excel import XlsxWriterEditor
from pandas.core.frame import DataFrame
from server.preprocess import Preprocessing


class EmesReport:

    PRICES = \
        [
            'Precio Neto',
            'Costo Total',
            'Nota'
        ]

    LEFT_ALIGN = \
        [
            'Descripción',
            'Cliente',
            'Vendedor',
            'NIT',
            'Sigla'
        ]

    JOINED_SUPPLIERS = \
        [
            '248-TECNOQUIMICAS',
            '115-BAXTER',
            '206-MK',
            '254-WASSER CH'
        ]

    SUMMARY_COLS = \
        [
            'Descuento sistema',
            'Descuento feria',
            'Diferencia feria $',
            'Descuento real',
            'Diferencia real $',
            'Diferencia real %',
        ]

    def __init__(self):
        """
        Default constructor
        """
        self.__df_use = None

    @property
    def data(self) -> DataFrame:
        return self.__data

    @property
    def base(self) -> DataFrame:
        return self.__df_base

    @property
    def discounts(self) -> DataFrame:
        return self.__df_discounts

    @property
    def summary(self) -> DataFrame:
        return self.__df_summ

    @property
    def use(self) -> DataFrame:
        return self.__df_use

    @property
    def suppliers(self) -> dict:
        return self.__suppliers

    @property
    def active_suppliers(self) -> dict:
        return self.__active_suppliers

    def get_suppliers(self) -> list:
        return self.__df_base.index.to_list()

    def __get_use_value_by_type(
            self,
            base: float,
            value: float) -> tuple[float, float]:
        """
        Args:
            base (float): Discount by period (money)
            value (float): Percentage of monetary value

        Returns:
            tuple[float, float]: [total diff, use value]
        """
        if value < 0:
            logging.error(
                "El valor de aprovechamiento debe ser mayor o igual a 0"
            )

            return 0

        use = value if value > 1 else base * value
        val = base + use

        return val, use

    def __select_all_products(self, name: str) -> bool:
        """
        Args:
            name (str): Supplier name

        Returns:
            bool: True if same discount apply for all products
        """
        return self.__df_discounts.loc[name, 'Codigo'][0] == '0'

    def __remove_bonus_rows(self, df: DataFrame) -> DataFrame:
        """
        Remove rows with 'Bonificados'

        Args:
            df (DataFrame): Main dataframe

        Returns:
            DataFrame: Dataframe with deleted rows
        """
        df = df.loc[df['Subgrupo'] != 'Bonificados']
        df = df.loc[~df['Código'].str.endswith('BOF')]

        return df

    def __select_by_date_range(
            self,
            df: DataFrame,
            name: str) -> tuple[DataFrame, DataFrame]:
        """
        Args:
            df (DataFrame): Dataframe with 'Fecha' column
            name (str): Supplier name

        Returns:
            tuple: (df) [In-period, Out-of-period]
        """
        if self.__suppliers[name]:
            df_ss = self.__df_discounts.query('Proveedor == @name')

            if self.__select_all_products(name):
                mask = df['Fecha'].isin(df_ss['Rango'].values[0])
            else:
                code_range = df_ss.set_index('Codigo').to_dict()['Rango']

                mask = df.apply(
                    lambda x: any(y == x['Fecha']
                                  for y in code_range.get(x['Código'], [])),
                    axis=1
                )

            # Delete all the product with bonus
            df_in = df[mask]
            df_in = self.__remove_bonus_rows(df_in)

            df_out = df[~mask].sort_values(by=['Nota'], ascending=False)
            df_out = self.__remove_bonus_rows(df_out)

            return df_in, df_out
        else:
            return df, None

    def __reallocate_discounts(
            self,
            df_in: DataFrame,
            df_out: DataFrame,
            discount_diff: float,
            base_price: str,
            use_value: float) -> DataFrame:
        """
        Args:
            df_in (DataFrame): Discount period
            df_out (DataFrame): Non-discount period
            discount_diff (float): Max diff allowed
            base_price (str): Base discount price column
            use_value (float): 'Aprovechamiento'

        Returns:
            DataFrame: Contains data with the addition of discount
        """
        if df_out is not None and not df_out.empty:
            total_diff, _ = self.__get_use_value_by_type(
                discount_diff,
                use_value
            )

            # Calculate the discount value
            discount_value = df_out[base_price] * df_out['% Descuento']

            # Add '% Descuento', 'Nota' and 'Fecha' columns
            df_out['Nota'] = discount_value

            # Prepare data
            df_out = (
                df_out
                .sort_values(by=['Nota'], ascending=False)
                .reset_index(drop=True)
            )

            # Cumulative discounts column
            df_out['cumsum'] = df_out['Nota'].cumsum()

            # Select next value to condition if exists
            match_list = df_out.index[df_out['cumsum'] <= total_diff].tolist()

            if match_list:
                if match_list[-1] + 2 > df_out.shape[0]:
                    df_out = df_out.query('cumsum <= @total_diff')
                else:
                    df_out = df_out.iloc[:match_list[-1] + 2]

                # Includes the next value where condition is reached
                df_out = df_out.query('`% Descuento` >= 0')

                # Append the new rows to df_in
                df_in = pd.concat(
                    [
                        df_in,
                        df_out
                    ],
                    ignore_index=True
                )

        return df_in

    def _set_sheet1(self, df: DataFrame) -> DataFrame:
        """
        Set 'Rotacion' sheet features
        """
        df_out = copy.deepcopy(df)

        return df_out.drop(
            [
                "% Descuento",
                "Nota"
            ],
            axis='columns'
        )

    def __get_note_discounts(
            self,
            df: DataFrame,
            name: str,
            base_price: str) -> DataFrame:
        """
        Calculates Nota (real discount)

        Args:
            df (DataFrame): Supplier dafaframe
            name (str): Supplier name
            base_price (str): Base price column

        Returns:
            DataFrame: Contains added 'Nota' column
        """
        if name in self.__active_suppliers:
            df_ss = self.__df_discounts[self.__df_discounts.index == name]

            if self.__select_all_products(name):
                df['% Descuento'] = float(df_ss['% Desc real'].values[0])
                df['Rango'] = [
                    df_ss['Rango'].values[0] for _ in range(df.shape[0])
                ]
            else:
                df = df.merge(
                    df_ss,
                    left_on='Código',
                    right_on='Codigo',
                    how='left'
                )

                df['% Descuento'] = df['% Desc real'].fillna(
                    value=0  # df['% Descuento']  # REVISAR SI LLENAR CON CERO
                )

                values = random.choice(
                    df['Rango'].dropna().tolist()
                )

                df['Rango'] = [
                    values if not isinstance(x, list) else x
                    for x in df['Rango']
                ]

                df = df.drop(columns=['Codigo', '% Desc real'])

        df["Nota"] = df[base_price] * df["% Descuento"]

        return df

    def __remove_columns_by_mode(
            self,
            df: DataFrame,
            mode: int) -> DataFrame:
        """
        Remove columns based on mode
        """
        dropped_cols = ["Costo Unidad"]

        if mode == 1:
            dropped_cols += ["Costo Total"]

        # Check if columns to be dropped exist in the dataframe
        cols_to_drop = set(dropped_cols) & set(df.columns)

        return \
            df.drop(cols_to_drop, axis='columns') if cols_to_drop else df

    def __sort_by_date(self, df: DataFrame) -> DataFrame:
        """
        Args:
            df (DataFrame): Dataframe to sort

        Returns:
            DataFrame: Sorted dataframe
        """
        return df.sort_values(
            by=['Fecha']
        )

    def __sort_by_description(self, df: DataFrame) -> DataFrame:
        """
        Args:
            df (DataFrame): Dataframe to sort

        Returns:
            DataFrame: Sorted dataframe by description
        """
        return df.sort_values(
            by=['Descripción']
        )

    def __get_discount_diff(
            self,
            df_all: DataFrame,
            df_in: DataFrame) -> tuple:
        """
        Compare real discount vs 260 discount report
        """
        try:
            assert 'Valor descuento' in df_all.columns, \
                'Column "Valor descuento" not found in df_all'
            assert 'Cantidad' in df_all.columns, \
                'Column "Cantidad" not found in df_all'
            assert 'Nota' in df_in.columns, \
                'Column "Nota" not found in df_in'

            # Check for missing or null values
            assert df_all[['Valor descuento', 'Cantidad']].notnull().all().all(), \
                'df_all contains missing or null values'
            assert df_in['Nota'].notnull().all().all(), \
                'df_in contains missing or null values'

            sum_discount = df_all['Valor descuento'] @ df_all['Cantidad']
            sum_notes = df_in['Nota'].sum()

            discount_diff = sum_discount - sum_notes

            return (discount_diff, sum_discount, sum_notes)

        except AssertionError as e:
            logging.error(str(e))
            return (0, 0, 0)

        except Exception as e:
            logging.error(
                f"Error calculating discount difference: {e}",
                exc_info=True
            )

            return (0, 0, 0)

    def __drop_unneeded_cols(self, df: DataFrame) -> DataFrame:
        """
        Drop original discount column (260 report)
        """
        col_idx = df.columns.get_loc('Sigla')

        cols_to_drop = df.columns[col_idx + 1:].to_list()

        # Add common columns
        cols_to_drop.append('Valor descuento')
        cols_to_drop.append('Fecha')

        return df.drop(
            cols_to_drop,
            axis='columns'
        )

    def __reorder_cols(self, df: DataFrame) -> DataFrame:
        """
        Args:
            df (DataFrame): Unsorted df with discount column next to price

        Returns
            DataFrame: Sorted dataframe.
        """
        loc = df.columns.get_loc('% Descuento') + 1

        df.insert(
            loc=loc,
            column='Nota',
            value=df.pop('Nota')
        )

        return df

    def __reset_index(self, df: DataFrame, drop: bool) -> DataFrame:
        """
        Reset dataframe index
        """
        return df.reset_index(
            drop=drop
        )

    def _set_sheet2(
            self,
            df: DataFrame,
            mode: int,
            name: str,
            use_mode: bool) -> tuple[DataFrame, DataFrame]:
        """
        Args:
            df (DataFrame): Supplier df
            mode (int): Base price discount
            name (str): Supplier name
            use_mode (bool): True if 'Aprovechamiento' is incorporated

        Returns:
            tuple: (df 'Rotación', df 'Teleferias')
        """
        base_price = 'Precio Neto' if mode == 1 else 'Costo Total'

        df_all = copy.deepcopy(df)

        df_all = (
            df_all
            .pipe(self.__get_note_discounts, name, base_price)
            .pipe(self.__remove_columns_by_mode, mode)
            .pipe(self.__sort_by_date)
            .pipe(self.__reorder_cols)
        )

        df_in, df_out = self.__select_by_date_range(
            df_all,
            name
        )

        # Compare real discount vs 260 discount report
        discount_diff, sum_discount, sum_notes = self.__get_discount_diff(
            df_all,
            df_in
        )

        if discount_diff > 0:
            if self.__df_use is None:
                use_value = 0
            else:
                if name in self.__df_use.index:
                    use_value = self.__df_use.loc[name, 'Aprovechamiento']
                else:
                    use_value = 0

            df_in = self.__reallocate_discounts(
                df_in,
                df_out,
                discount_diff,
                base_price,
                use_value
            )

        # Delete rows with discount less than zero and negative prices
        df_in = df_in[(df_in[base_price] > 0) & (df_in['% Descuento'] > 0)]

        # In case of zero-discount use all the dataframe
        if df_in.empty:
            df_in = df_all

        sum_real_discount = df_in['Nota'].sum()

        # Fill summary
        self.__fill_summary(
            name,
            sum_discount,
            sum_notes,
            sum_real_discount,
            use_mode
        )

        return (
            df_all.pipe(self.__drop_unneeded_cols)
                  .pipe(self.__reset_index, True)
                  .pipe(self.__sort_by_description),
            df_in.pipe(self.__drop_unneeded_cols)
                 .pipe(self.__reset_index, True)
                 .pipe(self.__sort_by_description)
        )

    def __fill_summary(
            self,
            name: str,
            sum_discount: float,
            sum_notes: float,
            sum_real_discount: float,
            use_mode: bool) -> None:
        """
        Fill report summary
        """
        if not use_mode:
            self.__df_summ.loc[name, 'Descuento sistema'] = sum_discount
            self.__df_summ.loc[name, 'Descuento feria'] = sum_notes

            diff_note = sum_notes - sum_discount
            self.__df_summ.loc[name, 'Diferencia feria $'] = diff_note
        else:
            self.__df_summ.loc[name, 'Descuento real'] = sum_real_discount

            diff_real = sum_real_discount - sum_discount
            self.__df_summ.loc[name, 'Diferencia real $'] = diff_real

            temp = diff_real / sum_discount if sum_discount != 0.0 else 0.0
            self.__df_summ.loc[name, 'Diferencia real %'] = temp

    def __join_to_data(
            self,
            df_to_add: DataFrame,
            sheet: int) -> None:
        """
        Args:
            df_to_add (DataFrame): df to join at the end
            sheet (int): sheet id (1: Rotacion, 2: Teleferias)
        """
        if sheet == 1:
            self.__df1_joined = pd.concat([
                self.__df1_joined,
                df_to_add]
            )

        elif sheet == 2:
            self.__df2_joined = pd.concat([
                self.__df2_joined,
                df_to_add]
            )

    def _process_data(
            self,
            df: DataFrame,
            use_mode: bool,
            include_reports: bool) -> None:
        """
        Args:
            df (DataFrame): dataframe subset
        """
        name = df.iloc[0, 0]

        mode = self.__df_base.loc[name, 'Base descuento']

        # Get Teleferias sheet
        df2, df_sheet2 = self._set_sheet2(
            df=df,
            mode=mode,
            name=name,
            use_mode=use_mode
        )

        # Get Rotacion sheet
        df_sheet1 = self._set_sheet1(df2)

        # Join dataframe for joined suppliers case
        if name in EmesReport.JOINED_SUPPLIERS:
            self.__join_to_data(df_sheet1, 1)
            self.__join_to_data(df_sheet2, 2)

            if name in EmesReport.JOINED_SUPPLIERS[:3]:
                return

            # If last supplier of list
            df_sheet1 = self.__df1_joined.\
                sort_values(by='Descripción').\
                copy()
            df_sheet2 = self.__df2_joined.\
                sort_values(by='Descripción').\
                copy()

            name = '248-TECNOQUIMICAS'

        # Save dataframes into Excel
        self.__to_excel(
            name,
            df_sheet1,
            df_sheet2,
            use_mode,
            include_reports
        )

    def __summary_to_excel(self) -> None:
        """
        Save summary into Excel
        """
        path = self.__path_to + f'\\Resumen.xlsx'

        with pd.ExcelWriter(path, engine='xlsxwriter') as writer:
            xlsx = XlsxWriterEditor(writer.book)

            mask = self.__df_summ['Proveedor'].isin(
                self.__active_suppliers)

            df_ss = self.__df_summ[mask]

            df_ss.to_excel(
                writer,
                sheet_name='Resumen',
                engine='xlsxwriter',
                index=False
            )

            xlsx.format_worksheet(
                df=df_ss,
                worksheet=writer.sheets['Resumen'],
                prices_cols=EmesReport.SUMMARY_COLS[:5],
                left_align_cols=['Proveedor'],
                perc_cols=['Diferencia real %'],
                include_sum=True
            )

    def __to_excel(
            self,
            name: str,
            df1: DataFrame,
            df2: DataFrame,
            use_mode: bool,
            include_reports: bool) -> None:
        """
        Function to save dataframes into Excel file

        Args:
            name (str): supplier name
            df1 (DataFrame): sheet 1 dataframe
            df2 (DataFrame): sheet 2 dataframe
            use_mode (bool): true if is Teleferia file
            include_reports (bool): true if save previous reports into Excel file
        """
        if not use_mode and not include_reports:
            return

        file_suffix = '' if use_mode else '_prev'
        file_path = self.__path_to + f'\\{name}{file_suffix}.xlsx'

        with pd.ExcelWriter(file_path,
                            engine='xlsxwriter') as writer:
            xlsx = XlsxWriterEditor(writer.book)

            df1.to_excel(
                writer,
                sheet_name='Rotación',
                engine='xlsxwriter',
                index=False
            )

            # Edit worksheet
            xlsx.format_worksheet(
                df=df1,
                worksheet=writer.sheets['Rotación'],
                prices_cols=EmesReport.PRICES,
                left_align_cols=EmesReport.LEFT_ALIGN
            )

            if name in self.__active_suppliers:
                if name != '134-COASPHARMA':
                    df2.to_excel(
                        writer,
                        sheet_name='Teleferia',
                        engine='xlsxwriter',
                        index=False
                    )

                    # Edit worksheet
                    xlsx.format_worksheet(
                        df=df2,
                        worksheet=writer.sheets['Teleferia'],
                        prices_cols=EmesReport.PRICES,
                        left_align_cols=EmesReport.LEFT_ALIGN,
                        perc_cols=['% Descuento'],
                        include_sum=True
                    )

    def initialize(
            self,
            path_to: str,
            path_grid: str,
            path_groups: str) -> None:
        """
        Creates main dataframes

        Args:
            path_to (str): Path to save reports
            path_grid (str): Path where 260 report is located
            path_groups (str): Path where proveedores.xlsx is located
        """
        self.__path_to = path_to

        # Create Preprocessing object
        p = Preprocessing(
            path_grid,
            path_groups
        )

        p.run()

        self.__df_base = p.base
        self.__df_discounts = p.discounts

        self.__data = p.data
        self.__suppliers = p.get_suppliers()
        self.__active_suppliers = \
            [k for k, v in self.__suppliers.items() if v]

        # Create summary report dataframe
        self.__df_summ = pd.DataFrame(
            columns=EmesReport.SUMMARY_COLS
        )

        self.__df_summ.index.names = ['Proveedor']

        # Create joined dataframes from special case (Tecnoquímicas)
        self.__df1_joined, self.__df2_joined = (
            pd.DataFrame() for _ in range(2)
        )

    def include_use(
            self,
            suppliers: list,
            use_dict: dict) -> None:
        """
        Function to include Use
        """
        df = pd.DataFrame(
            data=use_dict.values(),
            columns=['Aprovechamiento'],
            index=use_dict.keys()
        )

        self.__df_use = df.convert_dtypes()

        # Update files including use
        self.run(
            suppliers,
            use_mode=True,
            include_reports=True
        )

    def run(
            self,
            suppliers: list = [],
            use_mode: bool = True,
            include_reports: bool = False) -> None:
        """
        Main class to process data and save into Excel file
        """
        if not suppliers:
            suppliers = self.get_suppliers()

        for supplier in suppliers:
            try:
                mask = self.__data.Grupo == supplier
                df_ss = self.__data[mask]
                self._process_data(
                    df_ss,
                    use_mode,
                    include_reports
                )
            except Exception as e:
                logging.error(
                    f'Exception {e} occurred in supplier {supplier}',
                    exc_info=True
                )

        if use_mode:
            self.__df_summ.reset_index(
                drop=False,
                inplace=True
            )

            self.__summary_to_excel()
