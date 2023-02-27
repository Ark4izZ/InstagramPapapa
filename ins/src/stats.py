from PySide2.QtWidgets import QApplication, QMessageBox, QPushButton, QFileDialog
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
import analyse


class Stats:

    def __init__(self):
        qfile_stats = QFile('./uiFile/InsScrap.ui')
        qfile_stats.open(QFile.ReadOnly)

        self.ui = QUiLoader().load(qfile_stats)
        qfile_stats.close()

        # self.ui=QUiLoader().load('./uiFile/InsScrap.ui')
        # self.ui.button.clicked.connect(self.handleCalc)
        # self.ui.QPushButton('start').clicked.connect(self.handleCalc)
        self.ui.start.clicked.connect(self.start)
        self.ui.analysis.clicked.connect(self.analyse)
        self.ui.user_list.clicked.connect(self)
        # self.ui.

    def start(self):
        pass
        # self.ui.textBrowser.append()

    def show_posts(self):
        pass

    def show_users(self):
        pass

    def user_list(self):
        file = QFileDialog.getOpenFileName(self.ui, "选择文件")
        print(type(file))
        print(file)
        with open(file[0], 'r') as f:
            U = f.readlines()
            f.close()
            for u in U:
                self.ui.textBrowser.append(u)

    def csv2sql(self):
        pass

    def analyse(self):
        # analyse.user()
        analyse.wc_of_posts()



app = QApplication([])
stats = Stats()
stats.ui.show()
app.exec_()