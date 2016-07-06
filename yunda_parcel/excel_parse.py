import xlrd
from django.db import transaction

class CnCustomsTaxExcelParse(object):
    @transaction.commit_on_success
    def read_excel(self,excel_name):
        wb=xlrd.open_workbook(file_contents=excel_name)