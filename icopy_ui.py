
from Tkinter import *
import ttk
import tkFileDialog
import icopy
from os import path


class ImageCopyUi():


    def __init__(self, parent):

        self.parent = parent
        self.initUI()

    def initUI(self):


        self.dir_opt = options = {}
        options['initialdir'] = path.dirname(path.abspath(__file__))
        options['mustexist'] = False
        options['parent'] = self.parent
        self.source = StringVar()
        self.target = StringVar()
        self.tmp_str = StringVar()

        mainframe = ttk.Frame(self.parent, padding=(3,3,12,12))
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        sbtn = ttk.Button(mainframe, text="Source", command=self.ask_source_directory)
        sbtn.grid(row=0, column=0, sticky=W)

        stext = ttk.Entry(mainframe, width=30, textvariable=self.source)
        stext.grid(row=1, column=0, columnspan=2, sticky=W+E)

        tbtn = ttk.Button(mainframe, text="Target", command=self.ask_target_directory)
        tbtn.grid(row=0, column=2, sticky=W)

        ttext = ttk.Entry(mainframe, width=30, textvariable=self.target)
        ttext.grid(row=1, column=2, columnspan=2, sticky=W+E)

        cbtn = ttk.Button(mainframe, text="Copy", command=self.copy_files)
        cbtn.grid(row=5, column=0, sticky=W)

        qbtn = ttk.Button(mainframe, text="Quit", command=self.parent.destroy)
        qbtn.grid(row=5, column=3, sticky=E)

        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        mainframe.columnconfigure(0, weight=3)
        mainframe.columnconfigure(1, weight=3)
        mainframe.columnconfigure(2, weight=3)
        mainframe.columnconfigure(3, weight=3)

        mainframe.rowconfigure(0, weight=1)
        mainframe.rowconfigure(1, weight=1)
        mainframe.rowconfigure(2, weight=1)
        mainframe.rowconfigure(5, weight=1)

        for child in mainframe.winfo_children(): child.grid_configure(padx=3, pady=3)
        logtext = Text(mainframe, width=30, height=15, state='disabled')
        logtext.grid(row=2, column=0, columnspan=4, rowspan=3, padx=5, pady=3, sticky=(W+E))

        assert isinstance(self.parent.bind, object)
        self.parent.bind('<Return>', self.copy_files)

    def ask_source_directory(self):
        """Returns a selected directoryname."""
        self.tmp_str.set(tkFileDialog.askdirectory(**self.dir_opt))

        if self.tmp_str.get() is not "":
            self.source.set(self.tmp_str.get())

        self.tmp_str.set("")

    def ask_target_directory(self):
        """Returns a selected directoryname."""
        self.tmp_str.set(tkFileDialog.askdirectory(**self.dir_opt))

        if self.tmp_str.get() is not "":
            self.target.set(self.tmp_str.get())

        self.tmp_str.set("")

    def copy_files(self):
        # Create instance of iCopy and copy files
        self.ic = icopy.ImageCopy(str(self.source), str(self.target), True)
        self.ic.copy_files()

def main():

    root = Tk()
    root.title('ImageCopy')
    ImageCopyUi(root)
    root.mainloop()


if __name__ == '__main__':
    main()
