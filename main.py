import sys

from PyQt5.QtWidgets import QApplication

from ui_dev.first_gui import CreateWindow


# def load_securities(info):
#     res = GetSecurityHistory(
#         info=info,
#         _from=now() - timedelta(days=300),
#         to=now(),
#         interval=CandleInterval.CANDLE_INTERVAL_DAY,
#         token=user.get_token(),
#         on_finish=lambda n, y: print(
#             len(y),
#             sep='\n'
#         )
#     )
#
#     res.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wndw = CreateWindow(app)
    wndw.create_main()
    sys.exit(app.exec_())

