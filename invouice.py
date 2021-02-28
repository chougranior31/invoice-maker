from fbs_runtime.application_context.PySide2 import ApplicationContext
import os
import sys
import sqlite3
import datetime

from PySide2.QtWidgets import QAction, QDateEdit, QDateTimeEdit, QTableView, QApplication
from PySide2.QtCore import QDate, QDateTime, QTimer
from PySide2.QtPrintSupport import QPrinter ,QPrintPreviewDialog, QPrintDialog
from PySide2.QtGui import QTextBlockFormat, QTextDocument, QTextCursor
from PySide2 import QtSql, QtWidgets, QtCore, QtGui




class Table(QtWidgets.QDialog):
    def __init__(self):
        super(Table, self).__init__()
        with sqlite3.connect('teste.db') as db:
            cursor=db.cursor()
            cursor.execute('select * from articles ORDER BY Code_Article')
            title = [cn[0] for cn in cursor.description]
            rows = [cn[0] for cn in cursor.description]
            cur=cursor.fetchall()
            layout = QtWidgets.QGridLayout() 
            self.table = QtWidgets.QTableWidget()
            self.setGeometry(500,500,500,400)
            qr = self.frameGeometry()
            cp = QtWidgets.QDesktopWidget().availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())
            self.label2=QtWidgets.QLabel(self)
            self.label2.setPixmap(QtGui.QPixmap('image.png'))
            self.label2.setGeometry(0,0,500,400)
            self.table.setColumnCount(8)
            self.table.setHorizontalHeaderLabels(title)
            for i,row in enumerate(cur):
                self.table.insertRow(self.table.rowCount())
                for j,val in enumerate(row):
                    self.table.setItem(i, j, QtWidgets.QTableWidgetItem(str(val)))
            layout.addWidget(self.table, 0, 0)
            self.setLayout(layout)
            self.setWindowTitle('Receipt Table')

            layout.addWidget(self.table, 0, 0, 1, 2)
            self.buttonPrint = QtWidgets.QPushButton('Print', self)
            self.buttonPrint.clicked.connect(self.handlePrint)
            self.buttonPreview = QtWidgets.QPushButton('Preview', self)
            self.buttonPreview.clicked.connect(self.handlePreview)
            layout.addWidget(self.buttonPrint, 1, 0)
            layout.addWidget(self.buttonPreview, 1, 1)
            self.setLayout(layout)


    def handlePrint(self):
        dialog = QPrintDialog()
        if dialog.exec_() == QtGui.QDialog.Accepted:
            self.handlePaintRequest(dialog.printer())

    def handlePreview(self):
        dialog = QPrintPreviewDialog()
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()



    def handlePaintRequest(self, printer):
        document = self.makeTableDocument()
        document.print_(printer)

    def makeTableDocument(self):
        document = QtGui.QTextDocument()
        cursor = QtGui.QTextCursor(document)
        rows = self.table.rowCount()
        columns = self.table.columnCount()
        table = cursor.insertTable(rows + 1, columns)
        format = table.format()
        format.setHeaderRowCount(1)
        table.setFormat(format)
        format = cursor.blockCharFormat()
        format.setFontWeight(QtGui.QFont.Bold)
        for column in range(columns):
            cursor.setCharFormat(format)
            cursor.insertText(
                self.table.horizontalHeaderItem(column).text())
            cursor.movePosition(QtGui.QTextCursor.NextCell)
        for row in range(rows):
            for column in range(columns):
                cursor.insertText(
                    self.table.item(row, column).text())
                cursor.movePosition(QtGui.QTextCursor.NextCell)
        return document





def main():
    app = QApplication(sys.argv)
    window = Table()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()