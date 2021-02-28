import sys
from PySide2.QtCore import  QSize, QSizeF, QDate,Signal
from PySide2.QtGui import QTextDocument, QTextCursor, QFont
from PySide2.QtPrintSupport import QPrinter, QPrintPreviewDialog
from PySide2.QtWidgets import QWidget, QFormLayout, QLineEdit, QPlainTextEdit, QSpinBox, QDateEdit, QTableWidget, QHeaderView, QPushButton, QHBoxLayout, QTextEdit, QApplication, QMainWindow




font = QFont('Arial',16)



class InvoiceForm(QWidget):
    submitted = Signal(dict)
    
    def __init__(self, parent=None):                                        # + parent=None
        super().__init__(parent)                                            # + parent
        self.setLayout(QFormLayout())
        self.inputs = dict()
        self.inputs['Customer Name'] = QLineEdit()
        self.inputs['Customer Address'] = QPlainTextEdit()
        self.inputs['Invoice Date'] = QDateEdit(date=QDate.currentDate(), calendarPopup=True)
        self.inputs['Days until Due'] = QSpinBox()
        for label, widget in self.inputs.items():
            self.layout().addRow(label, widget)

        self.line_items = QTableWidget(rowCount=10, columnCount=3)
        self.line_items.setHorizontalHeaderLabels(['Job', 'Rate', 'Hours'])
        self.line_items.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout().addRow(self.line_items)
        for row in range(self.line_items.rowCount()):
            for col in range(self.line_items.columnCount()):
                if col > 0:
                    w = QSpinBox()
                    self.line_items.setCellWidget(row, col, w)

        submit = QPushButton('Create Invoice', clicked=self.on_submit)
        
# +     vvvvvv                                        vvvvvvvvvvvvv 
        _print = QPushButton('Print Invoice', clicked=self.window().printpreviewDialog)  # + _print, + self.window()
        self.layout().addRow(submit, _print)                                             # + _print

    def on_submit(self):
        data = {'c_name': self.inputs['Customer Name'].text(),
                'c_addr': self.inputs['Customer Address'].toPlainText(),
                'i_date': self.inputs['Invoice Date'].date().toString(),
                'i_due': self.inputs['Invoice Date'].date().addDays(self.inputs['Days until Due'].value()).toString(),
                'i_terms': '{} days'.format(self.inputs['Days until Due'].value()),
                'line_items': list()}

        for row in range(self.line_items.rowCount()):
            if not self.line_items.item(row, 0):
                continue
            job = self.line_items.item(row, 0).text()
            rate = self.line_items.cellWidget(row, 1).value()
            hours = self.line_items.cellWidget(row, 2).value()
            total = rate * hours
            row_data = [job, rate, hours, total]
            if any(row_data):
                data['line_items'].append(row_data)

        data['total_due'] = sum(x[3] for x in data['line_items'])
        self.submitted.emit(data)
        # remove everything else in this function below this point
# +
        return data                                                            # +++
        

class InvoiceView(QTextEdit):
    dpi = 72
    doc_width = 8.5 * dpi
    doc_height = 6 * dpi

    def __init__(self):
        super().__init__(readOnly=True)
        self.setFixedSize(QSize(self.doc_width, self.doc_height))

    def build_invoice(self, data):
        document = QTextDocument()
        self.setDocument(document)
        document.setPageSize(QSizeF(self.doc_width, self.doc_height))
        document.setDefaultFont(font)
        cursor = QTextCursor(document)
        cursor.insertText(f"Customer Name: {data['c_name']}\n")
        cursor.insertText(f"Customer Address: {data['c_addr']}\n")
        cursor.insertText(f"Date: {data['i_date']}\n")
        cursor.insertText(f"Total Due: {data['total_due']}\n")
# +        
        return document                                                         # +++
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
# +                                    vvvv
        self.invoiceForm = InvoiceForm(self)                                    # + self
        
        layout.addWidget(self.invoiceForm)
        self.invoiceView = InvoiceView()
        layout.addWidget(self.invoiceView)
        # hide the widget right now...
        self.invoiceView.setVisible(False)
        self.invoiceForm.submitted.connect(self.showPreview)

    def showPreview(self, data):
        self.invoiceView.setVisible(True)
        self.invoiceView.build_invoice(data)

# +++ vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
    def printpreviewDialog(self):
        previewDialog = QPrintPreviewDialog()
        previewDialog.paintRequested.connect(self.printPreview)  
        previewDialog.exec_()

    def printPreview(self, printer):
#        self.invoiceView.build_invoice.print_(printer)        
        data = self.invoiceForm.on_submit()
        document = self.invoiceView.build_invoice(data)
        document.print_(printer)
# +++ ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()