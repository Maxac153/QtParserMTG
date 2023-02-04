# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'untitled.ui'
#
# Created by: PyQt5 UI code generator 5.15.8
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(800, 600)
        Form.setMinimumSize(QtCore.QSize(800, 600))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../logo/logo.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Form.setWindowIcon(icon)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout_6.setContentsMargins(3, 3, 3, 3)
        self.verticalLayout_6.setSpacing(3)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.DollarExchangeRate = QtWidgets.QSpinBox(Form)
        self.DollarExchangeRate.setMinimum(1)
        self.DollarExchangeRate.setMaximum(999)
        self.DollarExchangeRate.setObjectName("DollarExchangeRate")
        self.gridLayout.addWidget(self.DollarExchangeRate, 1, 7, 1, 1)
        self.frame_2 = QtWidgets.QFrame(Form)
        self.frame_2.setMinimumSize(QtCore.QSize(420, 0))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Tables = QtWidgets.QTabWidget(self.frame_2)
        self.Tables.setObjectName("Tables")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tab_4)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.TableStarCityGames = QtWidgets.QTableWidget(self.tab_4)
        self.TableStarCityGames.setObjectName("TableStarCityGames")
        self.TableStarCityGames.setColumnCount(6)
        self.TableStarCityGames.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.TableStarCityGames.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.TableStarCityGames.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.TableStarCityGames.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.TableStarCityGames.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.TableStarCityGames.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.TableStarCityGames.setHorizontalHeaderItem(5, item)
        self.verticalLayout_4.addWidget(self.TableStarCityGames)
        self.Tables.addTab(self.tab_4, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.tab_3)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.TableGoldFish = QtWidgets.QTableWidget(self.tab_3)
        self.TableGoldFish.setObjectName("TableGoldFish")
        self.TableGoldFish.setColumnCount(6)
        self.TableGoldFish.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.TableGoldFish.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.TableGoldFish.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.TableGoldFish.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.TableGoldFish.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.TableGoldFish.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.TableGoldFish.setHorizontalHeaderItem(5, item)
        self.verticalLayout_3.addWidget(self.TableGoldFish)
        self.Tables.addTab(self.tab_3, "")
        self.verticalLayout_2.addWidget(self.Tables)
        self.gridLayout.addWidget(self.frame_2, 2, 1, 1, 9)
        self.SiteList = QtWidgets.QComboBox(Form)
        self.SiteList.setMinimumSize(QtCore.QSize(100, 0))
        self.SiteList.setObjectName("SiteList")
        self.SiteList.addItem("")
        self.SiteList.addItem("")
        self.gridLayout.addWidget(self.SiteList, 1, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 1, 1, 1)
        self.frame_4 = QtWidgets.QFrame(Form)
        self.frame_4.setMinimumSize(QtCore.QSize(0, 0))
        self.frame_4.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.frame_4)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.gridLayout.addWidget(self.frame_4, 0, 0, 1, 3)
        self.frame_3 = QtWidgets.QFrame(Form)
        self.frame_3.setMinimumSize(QtCore.QSize(0, 0))
        self.frame_3.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.frame_3)
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4.setSpacing(10)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label = QtWidgets.QLabel(self.frame_3)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_4.addWidget(self.label)
        spacerItem = QtWidgets.QSpacerItem(533, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem)
        self.RemoveAllData = QtWidgets.QPushButton(self.frame_3)
        self.RemoveAllData.setMaximumSize(QtCore.QSize(30, 30))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.RemoveAllData.setFont(font)
        self.RemoveAllData.setObjectName("RemoveAllData")
        self.horizontalLayout_4.addWidget(self.RemoveAllData, 0, QtCore.Qt.AlignRight)
        self.gridLayout.addWidget(self.frame_3, 3, 0, 1, 9)
        self.NumberDownloadedLinks = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.NumberDownloadedLinks.setFont(font)
        self.NumberDownloadedLinks.setObjectName("NumberDownloadedLinks")
        self.gridLayout.addWidget(self.NumberDownloadedLinks, 3, 9, 1, 1, QtCore.Qt.AlignRight)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 1, 3, 1, 3)
        self.Recalculation = QtWidgets.QPushButton(Form)
        self.Recalculation.setMaximumSize(QtCore.QSize(26, 26))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.Recalculation.setFont(font)
        self.Recalculation.setObjectName("Recalculation")
        self.gridLayout.addWidget(self.Recalculation, 1, 8, 1, 1, QtCore.Qt.AlignRight)
        self.PriceReloadedCards = QtWidgets.QPushButton(Form)
        self.PriceReloadedCards.setMaximumSize(QtCore.QSize(26, 26))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.PriceReloadedCards.setFont(font)
        self.PriceReloadedCards.setObjectName("PriceReloadedCards")
        self.gridLayout.addWidget(self.PriceReloadedCards, 1, 9, 1, 1, QtCore.Qt.AlignRight)
        self.label_3 = QtWidgets.QLabel(Form)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 6, 1, 1, QtCore.Qt.AlignRight)
        self.frame = QtWidgets.QFrame(Form)
        self.frame.setMinimumSize(QtCore.QSize(260, 0))
        self.frame.setMaximumSize(QtCore.QSize(300, 16777215))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.toolBox = QtWidgets.QToolBox(self.frame)
        self.toolBox.setMinimumSize(QtCore.QSize(0, 0))
        self.toolBox.setMaximumSize(QtCore.QSize(16777215, 235))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.toolBox.setFont(font)
        self.toolBox.setObjectName("toolBox")
        self.page = QtWidgets.QWidget()
        self.page.setGeometry(QtCore.QRect(0, 0, 283, 175))
        self.page.setObjectName("page")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.page)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.NumberCards = QtWidgets.QTextEdit(self.page)
        self.NumberCards.setMaximumSize(QtCore.QSize(155, 16777215))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.NumberCards.setFont(font)
        self.NumberCards.setObjectName("NumberCards")
        self.gridLayout_2.addWidget(self.NumberCards, 1, 0, 1, 1)
        self.LinkCards = QtWidgets.QTextEdit(self.page)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.LinkCards.setFont(font)
        self.LinkCards.setObjectName("LinkCards")
        self.gridLayout_2.addWidget(self.LinkCards, 1, 1, 1, 1)
        self.AddCards = QtWidgets.QPushButton(self.page)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.AddCards.setFont(font)
        self.AddCards.setObjectName("AddCards")
        self.gridLayout_2.addWidget(self.AddCards, 2, 0, 1, 2)
        self.label_4 = QtWidgets.QLabel(self.page)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 0, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.page)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 0, 1, 1, 1)
        self.LoadDataCards = QtWidgets.QPushButton(self.page)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.LoadDataCards.setFont(font)
        self.LoadDataCards.setObjectName("LoadDataCards")
        self.gridLayout_2.addWidget(self.LoadDataCards, 3, 0, 1, 2)
        self.horizontalLayout_3.addLayout(self.gridLayout_2)
        self.toolBox.addItem(self.page, "")
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setGeometry(QtCore.QRect(0, 0, 283, 69))
        self.page_2.setObjectName("page_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.page_2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.frame_5 = QtWidgets.QFrame(self.page_2)
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frame_5)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout_3 = QtWidgets.QGridLayout()
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.SaveToExcel = QtWidgets.QPushButton(self.frame_5)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.SaveToExcel.setFont(font)
        self.SaveToExcel.setObjectName("SaveToExcel")
        self.gridLayout_3.addWidget(self.SaveToExcel, 0, 0, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout_3)
        self.verticalLayout_5.addWidget(self.frame_5, 0, QtCore.Qt.AlignTop)
        self.toolBox.addItem(self.page_2, "")
        self.verticalLayout.addWidget(self.toolBox, 0, QtCore.Qt.AlignTop)
        self.label_6 = QtWidgets.QLabel(self.frame)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.verticalLayout.addWidget(self.label_6)
        self.BrokenLinks = QtWidgets.QTextEdit(self.frame)
        self.BrokenLinks.setMaximumSize(QtCore.QSize(16777215, 50))
        self.BrokenLinks.setObjectName("BrokenLinks")
        self.verticalLayout.addWidget(self.BrokenLinks)
        self.PriceReloadedCard = QtWidgets.QPushButton(self.frame)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.PriceReloadedCard.setFont(font)
        self.PriceReloadedCard.setObjectName("PriceReloadedCard")
        self.verticalLayout.addWidget(self.PriceReloadedCard)
        self.RemoveCard = QtWidgets.QPushButton(self.frame)
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.RemoveCard.setFont(font)
        self.RemoveCard.setObjectName("RemoveCard")
        self.verticalLayout.addWidget(self.RemoveCard)
        self.gridLayout.addWidget(self.frame, 1, 0, 2, 1, QtCore.Qt.AlignTop)
        self.verticalLayout_6.addLayout(self.gridLayout)

        self.retranslateUi(Form)
        self.Tables.setCurrentIndex(0)
        self.toolBox.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Parser Cards MTG"))
        item = self.TableStarCityGames.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Количество"))
        item = self.TableStarCityGames.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Название карты"))
        item = self.TableStarCityGames.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Название сета"))
        item = self.TableStarCityGames.horizontalHeaderItem(3)
        item.setText(_translate("Form", "Цена в долларах"))
        item = self.TableStarCityGames.horizontalHeaderItem(4)
        item.setText(_translate("Form", "Цена в рублях"))
        item = self.TableStarCityGames.horizontalHeaderItem(5)
        item.setText(_translate("Form", "Ссылка"))
        self.Tables.setTabText(self.Tables.indexOf(self.tab_4), _translate("Form", "Star City Games"))
        item = self.TableGoldFish.horizontalHeaderItem(0)
        item.setText(_translate("Form", "Количество"))
        item = self.TableGoldFish.horizontalHeaderItem(1)
        item.setText(_translate("Form", "Название карты"))
        item = self.TableGoldFish.horizontalHeaderItem(2)
        item.setText(_translate("Form", "Название сета"))
        item = self.TableGoldFish.horizontalHeaderItem(3)
        item.setText(_translate("Form", "Цена в долларах"))
        item = self.TableGoldFish.horizontalHeaderItem(4)
        item.setText(_translate("Form", "Цена в рублях"))
        item = self.TableGoldFish.horizontalHeaderItem(5)
        item.setText(_translate("Form", "Ссылка"))
        self.Tables.setTabText(self.Tables.indexOf(self.tab_3), _translate("Form", "Gold Fish"))
        self.SiteList.setItemText(0, _translate("Form", "Star City Games"))
        self.SiteList.setItemText(1, _translate("Form", "Gold Fish"))
        self.label_2.setText(_translate("Form", "Выбор откуда парсим:"))
        self.label.setText(_translate("Form", "Количество обработанных ссылок:"))
        self.RemoveAllData.setText(_translate("Form", "🗑"))
        self.NumberDownloadedLinks.setText(_translate("Form", "0/0"))
        self.Recalculation.setText(_translate("Form", "$"))
        self.PriceReloadedCards.setText(_translate("Form", "🗘"))
        self.label_3.setText(_translate("Form", "Курс доллара:"))
        self.AddCards.setText(_translate("Form", "Добавить"))
        self.label_4.setText(_translate("Form", "Количество:"))
        self.label_5.setText(_translate("Form", "Ссылки для парсинга:"))
        self.LoadDataCards.setText(_translate("Form", "Загрузить данные из Excel таблицы"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page), _translate("Form", "Добавление карт"))
        self.SaveToExcel.setText(_translate("Form", "Excel"))
        self.toolBox.setItemText(self.toolBox.indexOf(self.page_2), _translate("Form", "Экспорт"))
        self.label_6.setText(_translate("Form", "Ошибки:"))
        self.PriceReloadedCard.setText(_translate("Form", "Обновить цену карты"))
        self.RemoveCard.setText(_translate("Form", "Удалить карту из таблицы"))

class MyWin(QtWidgets.QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def closeEvent(self, event):
        rate = self.DollarExchangeRate.text()
        list_index = self.SiteList.currentIndex()
        tables_index = self.Tables.currentIndex()

        with open("src/initiation/data.config", "w") as file:
            file.write(f'DollarExchangeRate: {rate}\n')
            file.write(f'Tables: {tables_index}\n')
            file.write(f'SiteList: {list_index}')
