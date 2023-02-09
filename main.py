from server.report import EmesReport
import pandas as pd


def main():
    path_main = r'C:\Users\juane\OneDrive\Documentos\Emes\suppliers report'
    path_groups = path_main + '\\data'
    path_to = path_main + '\\reports\\Diciembre'

    file_name = r'C:\SMD_FILES\grid_export\Grd_20230201083735.pkl'

    emes = EmesReport(file_name,
                      path_to,
                      path_groups + "\\proveedores.xlsx")

    emes.run(['146-EXPOFARMA'])

    # emes.run(['189-LAPROFF'],
    #          False, False)  # sin aprovechamiento
    # emes.include_use(
    #     ['189-LAPROFF'],
    #     {'189-LAPROFF': 300000}
    # )  # con aprovechamiento


if __name__ == '__main__':
    main()
