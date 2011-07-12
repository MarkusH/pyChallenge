#!/usr/bin/env python


import sys
from PyQt4 import QtCore
from PyQt4 import QtGui
from subprocess import PIPE, Popen


class PyChallengeGUI(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)

        self.qtext = QtGui.QTextEdit(self)
        self.qtext.setReadOnly(True)

        self.qpb1 = QtGui.QPushButton("Get Rating", self)
        self.qpb1.setMinimumSize(self.qpb1.sizeHint())

        self.qpb2 = QtGui.QPushButton("Compare", self)
        self.qpb2.setMinimumSize(self.qpb2.sizeHint())

        self.qpb3 = QtGui.QPushButton("Worst", self)
        self.qpb3.setMinimumSize(self.qpb3.sizeHint())

        self.qpb4 = QtGui.QPushButton("Best", self)
        self.qpb4.setMinimumSize(self.qpb4.sizeHint())

        self.qpb5 = QtGui.QPushButton("Update", self)
        self.qpb5.setMinimumSize(self.qpb5.sizeHint())

        self.qedit1 = QtGui.QLineEdit("1",self)
        self.qedit2 = QtGui.QLineEdit("2",self)
        self.qedit3 = QtGui.QLineEdit("10",self)

        self.qcb = QtGui.QComboBox(self)
        self.qcb.addItem("chess")

        self.qcb2 = QtGui.QComboBox(self)
        self.qcb2.addItem("elo")
        #self.qcb2.addItem("glicko")
        #self.qcb2.addItem("glicko2")

        qlab1 = QtGui.QLabel(self)
        qlab1.setText("Player 1:")
        qlab2 = QtGui.QLabel(self)
        qlab2.setText("Player 2:")
        qlab3 = QtGui.QLabel(self)
        qlab3.setText("Best/Worst:")

        self.frame1 = QtGui.QFrame(self)

        self.frame2 = QtGui.QFrame(self)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.frame1)
        layout.addWidget(self.frame2)

        layout2 = QtGui.QHBoxLayout(self.frame1)
        layout2.addWidget(self.qpb1)
        layout2.addWidget(self.qpb2)
        layout2.addWidget(self.qpb4)
        layout2.addWidget(self.qpb3)
        layout2.addWidget(self.qpb5)

        layout3 = QtGui.QHBoxLayout(self.frame2)
        layout3.addWidget(self.qcb)
        layout3.addWidget(self.qcb2)
        layout3.addWidget(qlab1)
        layout3.addWidget(self.qedit1)
        layout3.addWidget(qlab2)
        layout3.addWidget(self.qedit2)
        layout3.addWidget(qlab3)
        layout3.addWidget(self.qedit3)

        layout.addWidget(self.qtext)
        layout.activate()

        QtCore.QObject.connect(self.qpb1, QtCore.SIGNAL('clicked()'),
            self.rating)
        QtCore.QObject.connect(self.qpb2, QtCore.SIGNAL('clicked()'),
            self.compare)
        QtCore.QObject.connect(self.qpb3, QtCore.SIGNAL('clicked()'),
            self.worst)
        QtCore.QObject.connect(self.qpb4, QtCore.SIGNAL('clicked()'),
            self.best)
        QtCore.QObject.connect(self.qpb5, QtCore.SIGNAL('clicked()'),
            self.update)

        self.setGeometry(300, 300, 700, 450)
        self.setWindowTitle('pyChallenge - Graphical User Interface')

    def compare(self):
        self.qtext.setText(Popen(["./pychallenge.py", "-g",
            self.qcb.currentText(), "-a", self.qcb2.currentText(),
            "compare", self.qedit1.text(), self.qedit2.text()], stdout=PIPE)
            .communicate()[0])

    def rating(self):
        self.qtext.setText(Popen(["./pychallenge.py", "-g",
            self.qcb.currentText(), "-a", self.qcb2.currentText(),  "rating",
            self.qedit1.text()], stdout=PIPE).communicate()[0])

    def worst(self):
        self.qtext.setText(Popen(["./pychallenge.py", "-g",
            self.qcb.currentText(), "-a", self.qcb2.currentText(),  "worst",
            self.qedit3.text()], stdout=PIPE).communicate()[0])

    def best(self):
        self.qtext.setText(Popen(["./pychallenge.py", "-g",
            self.qcb.currentText(), "-a", self.qcb2.currentText(),  "best",
            self.qedit3.text()], stdout=PIPE).communicate()[0])

    def update(self):
        self.qtext.setText(Popen(["./pychallenge.py", "-g",
            self.qcb.currentText(), "-a", self.qcb2.currentText(), "update"],
            stdout=PIPE).communicate()[0])


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    pcg = PyChallengeGUI()
    pcg.show()
    sys.exit(app.exec_())
