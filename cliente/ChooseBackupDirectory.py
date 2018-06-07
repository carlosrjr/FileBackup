# coding: utf-8

from Tkinter import *
import tkFileDialog, os

class zipFileGui(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)

		fonte1=('Verdana','10','bold')
		self.lbl = Label(self,text='Path: ', font=fonte1,width=8)
		self.lbl.pack(side=LEFT)

		self.pathdir=Entry(self,width=45, font=fonte1)
		self.pathdir.focus_force() # Para o foco começar neste campo
		self.pathdir.pack(side=LEFT)

		self.selecionar = Button (self, text="abrir", command=self.selectFileGui)
		self.selecionar.pack()

		self.ok = Button (self, text="ok", command=self.setPathDir)
		self.ok.pack()

		self.grid_rowconfigure(1, weight=1)
		self.grid_columnconfigure(0, weight=1)

		self.lbl.grid(row=0, column=0)
		self.pathdir.grid(row=0, column=1)
		self.selecionar.grid(row=0, column=2)
		self.ok.grid(row=1, column=1)

		self.pack()

	def selectFileGui(self):
		path = tkFileDialog.askdirectory().encode("utf-8")
		self.pathdir.delete(0, "end")
		self.pathdir.insert(20, path)

	def setPathDir(self):
		print("{0}".format(self.pathdir.get().encode("utf-8")))
		if(os.path.isdir("{0}".format(self.pathdir.get().encode("utf-8")))):
			file = open("PathFileBackup.fbk", "wb")
			file.write("{0}".format(self.pathdir.get().encode("utf-8")))
			file.close()
			self.quit()

if __name__ == "__main__":
	app = zipFileGui()
	app.master.title("Escolher diretório de Backup")
	app.master.geometry("580x80+100+100")
	app.master.resizable(False, False)
	mainloop()