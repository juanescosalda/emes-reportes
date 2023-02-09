from xlsxwriter import Workbook
from xlsxwriter.worksheet import Worksheet
from pandas.core.frame import DataFrame


class XlsxWriterEditor:

    ROW_HEIGHT = 18

    def __init__(self, wb: Workbook) -> None:
        self.__workbook = wb
        self.__set_formats()

    def __set_formats(self) -> None:
        """
        Set all used formats
        """
        common_format = {
            'font_name': 'Arial',
            'font_size': 10,
            'valign': 'vcenter',
            'align': 'center',
            'bold': True
        }

        # set header format
        self.head_format = self.__workbook.add_format(
            common_format
        )

        # set entered cols format
        common_format['bold'] = False

        self.center_format = self.__workbook.add_format(
            common_format
        )

        # set body format
        common_format['align'] = 'left'

        self.body_format = self.__workbook.add_format(
            common_format
        )

        # set prices format
        common_format['align'] = 'right'
        common_format['num_format'] = '[$$-409] #,##0.00'

        self.price_format = self.__workbook.add_format(
            common_format
        )

        # set percentage format
        common_format['num_format'] = '0.00%'
        common_format['align'] = 'center'

        self.perc_format = self.__workbook.add_format(
            common_format
        )

    @staticmethod
    def get_column_width(df: DataFrame, col: int) -> int:
        return max(df[col].astype(str).map(len).max(), len(col)) + 5

    def format_worksheet(self,
                         df: DataFrame,
                         worksheet: Worksheet,
                         prices_cols: list,
                         left_align_cols: list,
                         perc_cols: list = [],
                         include_sum: bool = False) -> None:
        """
        Args:
            df (DataFrame): dataframe to edit
            worksheet (Worksheet): worsheet object
            prices_cols (list): price format cols
            left_align_cols (list): left align format cols
            perc_cols (list): percentage format cols
            include_sum (bool, optional): sum subtotals. Defaults to False.
        """
        # get dimensions
        max_row, max_col = df.shape

        extra_rows = 2 if include_sum else 1

        # remove grid lines
        worksheet.hide_gridlines(2)

        # format each row
        for row in range(max_row + extra_rows):
            if row == 0:
                worksheet.set_row(
                    row,
                    XlsxWriterEditor.ROW_HEIGHT,
                    self.head_format
                )
            else:
                worksheet.set_row(
                    row,
                    XlsxWriterEditor.ROW_HEIGHT
                )

        # format each col
        for col_idx, col in enumerate(df):
            column_width = XlsxWriterEditor.get_column_width(df, col)

            if col in prices_cols:
                new_format = self.price_format
            else:
                if col in left_align_cols:
                    new_format = self.body_format
                elif col in perc_cols:
                    new_format = self.perc_format
                else:
                    new_format = self.center_format

            worksheet.set_column(
                col_idx,
                col_idx,
                column_width,
                new_format
            )

            # ignore most common error
            worksheet.ignore_errors({
                'number_stored_as_text': f'C1:I{max_row + 1}'
            })

        total_cols = prices_cols + ['Cantidad']

        # set column settings
        if include_sum:
            column_settings = [
                {
                    'header': column,
                    'total_function': 'sum'
                }
                if column in total_cols
                else
                {
                    'header': column
                }
                for column in df.columns
            ]
        else:
            column_settings = [
                {
                    'header': column
                }
                for column in df.columns
            ]

        # create table
        if include_sum:
            worksheet.add_table(
                0,
                0,
                max_row + 1,
                max_col - 1,
                {
                    'columns': column_settings,
                    'total_row': 1
                }
            )
        else:
            worksheet.add_table(
                0,
                0,
                max_row,
                max_col - 1,
                {
                    'columns': column_settings,
                }
            )
