#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys
import multiprocessing

from PyQt5.QtWidgets import QApplication

from ui.ui_imagedialog import MyWin
from src.eventor import Eventor

# Инцилизация окна приложения
if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    ui = MyWin()
    eventor = Eventor(ui)
    eventor.load_data()
    ui.show()

    # Привязка событий к кнопкам
    ui.AddCards.clicked.connect(eventor.thread_add_cards)
    ui.PriceReloadedCards.clicked.connect(eventor.thread_update_price_all_cards)
    ui.Recalculation.clicked.connect(eventor.event_price_recalculation)
    ui.RemoveAllData.clicked.connect(eventor.event_remove_all_cards)
    ui.RemoveCard.clicked.connect(eventor.event_remove_card)
    ui.LoadDataCards.clicked.connect(eventor.event_load_data_to_excel)
    ui.SaveToExcel.clicked.connect(eventor.event_save_to_excel)
    ui.StopParse.clicked.connect(eventor.event_stop_parse)

    ui.SearchByName.textChanged.connect(eventor.event_find_name_card)

    sys.exit(app.exec_())
