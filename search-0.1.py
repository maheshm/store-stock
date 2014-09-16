import sys
from PyQt4 import QtCore, QtGui
from searchui import Ui_MainWindow
from passwd import Ui_Dialog
import sqlite3
import string

con=sqlite3.connect('main.sqlite')
db=con.cursor()

DEBUG = 0

if DEBUG==1:
	try:
		db.executescript("""create table stock(name , 'cost price', price, stock, PRIMARY KEY (name) ON CONFLICT IGNORE );""")
		print "Done"

	except:
		print "Table already there"

no_of_results=0


class MyTableModel(QtCore.QAbstractTableModel): 
    def __init__(self, datain, headerdata, parent=None, *args): 
        """ datain: a list of lists
            headerdata: a list of strings
        """
        QtCore.QAbstractTableModel.__init__(self, parent, *args) 
        self.arraydata = datain
        self.headerdata = headerdata
 
    def rowCount(self, parent): 
        return len(self.arraydata) 
 
    def columnCount(self, parent): 
	if self.arraydata:
	        return len(self.arraydata[0])
	else:
		return 0 
    
    def data(self, index, role): 
        if not index.isValid(): 
            return QtCore.QVariant() 
        elif role != QtCore.Qt.DisplayRole: 
            return QtCore.QVariant() 
        return QtCore.QVariant(self.arraydata[index.row()][index.column()]) 

    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
		return QtCore.QVariant(self.headerdata[col])
        return QtCore.QVariant()

    def layoutchanged(self):
        self.emit(QtCore.SIGNAL("layoutChanged()"))

class passwdwin(QtGui.QDialog):
	def __init__(self, parent=None):
		self.parent = parent
		QtGui.QWidget.__init__(self, parent)
		self.ui = Ui_Dialog()
		self.ui.setupUi(self)

	def accept(self):
		db.execute("select * from login")
		for row in db:
			if str(self.ui.lineEdit.text())==row[0] and str(self.ui.lineEdit_2.text())==row[1]:
				self.parent.password = 1
				self.parent.show()
				self.parent.ui.pushButton_2.show()
				self.parent.ui.pushButton_3.show()	        
				self.hide()
			else:
				self.ui.label_3.setText("Username or Password or both are incorrect")
				self.ui.lineEdit_2.setText("")
		

	def reject(self):
		self.parent.show()
		self.hide()

	def clicked(self):
		pass

	def closeEvent (self, e):
		self.parent.show()

class StartQT4(QtGui.QMainWindow):
	global no_of_results, db, con
	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		self.ui = Ui_MainWindow()
		self.ui.setupUi(self)
		self.tabledata=[]
		self.header=[]
		self.settabledata()
		self.tm = MyTableModel(self.tabledata, self.header, self)
		self.ui.tableView.setModel(self.tm)
#		self.refreshtable()
		#self.ui.tableView.resizeColumnsToContents()		
		self.ui.tableView.setColumnWidth(0,400);
		#hh = self.ui.tableView.horizontalHeader()
		#hh.setStretchLastSection(True)
		self.password = 0
		self.ui.pushButton_2.hide()
		self.ui.pushButton_3.hide()	        

	def refreshtable(self):
		self.ui.tableView.setColumnWidth(0,400);


	def settabledata(self):
		self.tabledata = []
		db.execute("select * from stock order by name")
		for row in db:
			#print row[0],row[1],row[2],row[3], no_of_results
			self.tabledata.append(row)
		for row in db.description:
			self.header.append(row[0])

	def deleteButtonPressed(self):
		reply = QtGui.QMessageBox.question(self, 'Message',"Are you sure to delete?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
		if reply == QtGui.QMessageBox.Yes:
			db.execute("delete from stock where name = ? ", (str(self.ui.lineEdit_2.text()),))
			con.commit()
			self.settabledata()
			self.helper()
			self.refreshtable()

	def on_actionLogin_triggered(self, checked=None):
		if checked is None: return
		print "actionLogin pressed"
		if self.password == 0:
			mypass = passwdwin(self)
			mypass.show()
			self.hide()
			self.ui.actionLogin.setText("Logout")
		else:
			self.password = 0
			self.ui.pushButton_2.hide()
			self.ui.pushButton_3.hide()	
			self.ui.actionLogin.setText("Login")        

	def lineedittTextChanged(self, text):
		self.search = str(text)
		self.helper()
		self.refreshtable()
		#print text

	def helper(self):
		self.tm.emit(QtCore.SIGNAL("layoutAboutToBeChanged()"))
		self.tm.arraydata = []
		for col in self.tabledata:
			if string.lower(self.search) in string.lower(col[0]):
				#print col[0],col[1],col[2],col[3]
				self.tm.arraydata.append(col)
		self.tm.layoutchanged()

	def searchButtonPressed(self):
		#global no_of_results
#		print "Button pressed"
		self.searchstock()
		self.refreshtable()		

	def searchstock(self):
		global no_of_results
		db.execute("select * from stock where name=?",(self.search,))
		no_of_results=0
		for row in db:
			no_of_results=no_of_results+1
#			print row[0],row[1],row[2],row[3], no_of_results

	def tableRowClicked(self, index):
#		print "index.row", index.row()
		self.ui.lineEdit_2.setText(self.tm.arraydata[index.row()][0])
		self.ui.lineEdit_3.setText(str(self.tm.arraydata[index.row()][1]))
		self.ui.lineEdit_4.setText(str(self.tm.arraydata[index.row()][2]))
		self.ui.lineEdit_5.setText(str(self.tm.arraydata[index.row()][3]))

	def addButtonPressed(self):
		global no_of_results
		#reply = QtGui.QMessageBox.question(self, 'Message',"Are you sure to add/edit?", QtGui.QMessageBox.Yes | QtGui.QMessageBox.No, QtGui.QMessageBox.No)
		#if reply == QtGui.QMessageBox.Yes:
		self.searchstock()
		if (str(self.ui.lineEdit_3.text())==''):
			self.ui.lineEdit_3.setText("0.0")
		if (str(self.ui.lineEdit_4.text())==''):
			self.ui.lineEdit_4.setText("0.0")
		if (str(self.ui.lineEdit_5.text())==''):
			self.ui.lineEdit_5.setText("0.0")
		if self.search != '':
			if no_of_results>0:
				entry = (str(self.ui.lineEdit_2.text()), float(self.ui.lineEdit_3.text()), float(self.ui.lineEdit_4.text()), float(self.ui.lineEdit_5.text()),self.search)
				print "there is already an entry", entry
				db.execute("update stock set name = ?, 'cost price' = ?, price = ?, stock = ? where name = ?", entry)
				con.commit()
			else:
				entry = (str(self.ui.lineEdit_2.text()), float(self.ui.lineEdit_3.text()), float(self.ui.lineEdit_4.text()), float(self.ui.lineEdit_5.text()))
				print "add it", entry
				db.execute("insert into stock (name, 'cost price', price, stock) values (?, ?, ?, ?)", entry)
				con.commit()
			self.settabledata()
			self.helper()
			self.refreshtable()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = StartQT4()
    myapp.show()
    sys.exit(app.exec_())

