from Tkinter import *
import ttk
import tkFileDialog
import icopy
import stdout_redirect as stdtotextw
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

        # define mainframe which contains rest of the widgets
        mainframe = ttk.Frame(self.parent, padding=(3,3,12,12))
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        # define widgets
        sbtn = ttk.Button(mainframe, text="Source", command=self.ask_source_directory)
        sbtn.grid(row=0, column=0, sticky=W)

        stext = ttk.Entry(mainframe, width=30, textvariable=self.source)
        stext.grid(row=1, column=0, columnspan=3, sticky=W+E)

        tbtn = ttk.Button(mainframe, text="Target", command=self.ask_target_directory)
        tbtn.grid(row=0, column=3, sticky=W)

        ttext = ttk.Entry(mainframe, width=30, textvariable=self.target)
        ttext.grid(row=1, column=3, columnspan=3, sticky=W+E)

        self.cbtn = ttk.Button(mainframe, text="Copy", command=self.copy_files, state='disabled')
        self.cbtn.grid(row=5, column=0, sticky=W)

        qbtn = ttk.Button(mainframe, text="Quit", command=self.parent.destroy)
        qbtn.grid(row=5, column=4, sticky=E)

        # configure rows and columns
        self.parent.columnconfigure(0, weight=1)
        self.parent.rowconfigure(0, weight=1)
        mainframe.columnconfigure(0, weight=3)
        mainframe.columnconfigure(1, weight=3)
        mainframe.columnconfigure(2, weight=3)
        mainframe.columnconfigure(3, weight=3)
        mainframe.columnconfigure(4, weight=3)


        mainframe.rowconfigure(0, weight=1)
        mainframe.rowconfigure(1, weight=1)
        mainframe.rowconfigure(2, weight=1)
        mainframe.rowconfigure(5, weight=1)

        # Configure widgets
        for child in mainframe.winfo_children(): child.grid_configure(padx=3, pady=3)

        # create text widget; stdout will be directed here when copying files
        self.logtext = Text(mainframe, width=0, height=25, state = 'disabled')
        self.logtext.grid(row=2, column=0, columnspan=5, rowspan=3, padx=5, pady=3, sticky=(W+E))

        # create stdout redirector
        self.redir = stdtotextw.Std_redirector(self.logtext)

        # create a Scrollbar and associate it with txt
        scrollb = Scrollbar(mainframe, command=self.logtext.yview)
        scrollb.grid(row=2, column=4, padx=5, pady=3, sticky='nse')
        self.logtext['yscrollcommand'] = scrollb.set

        # bind pressing Return key to copy_files() function
        #assert isinstance(self.parent.bind, object)
        #self.parent.bind('<Return>', self.copy_files)

        # create menu
        # win = Toplevel(self.parent)
        # menubar = Menu(win)
        # appmenu = Menu(menubar, name='apple')
        # menubar.add_cascade(menu='apple')
        # appmenu.add_command(label='About My Application')
        # appmenu.add_separator()
        # menu_file = Menu(menubar)
        # menu_help = Menu(menubar)
        # menubar.add_cascade(menu=menu_file, label='File')
        # menubar.add_cascade(menu=menu_help, label='Help')
        # menu_file.add_command(label='Save log', command=self.savelog)
        # win['menu'] = menubar

        print("ImageCopy UI initialized.")


    def savelog(self):
        pass

    def ask_source_directory(self):
        """Returns a selected directoryname."""
        self.tmp_str.set(tkFileDialog.askdirectory(**self.dir_opt))

        if self.tmp_str.get() is not "":
            self.source.set(self.tmp_str.get())

        self.tmp_str.set("")

        if self.source.get() is not "" and self.target.get() is not "":
            self.cbtn.config(state = 'normal')


    def ask_target_directory(self):
        """Returns a selected directoryname."""
        self.tmp_str.set(tkFileDialog.askdirectory(**self.dir_opt))

        if self.tmp_str.get() is not "":
            self.target.set(self.tmp_str.get())

        self.tmp_str.set("")

        if self.source.get() is not "" and self.target.get() is not "":
            self.cbtn.config(state = 'normal')

    def copy_files(self):
        # Create instance of iCopy and copy files
        self.logtext.config(state = 'normal')
        self.redir.flush()
        self.redir.start()
        self.ic = icopy.ImageCopy(self.source.get(), self.target.get(), False)
        self.ic.copy_files()
        self.redir.flush()
        self.redir.stop()
        self.logtext.config(state = 'disabled')

def main():

    root = Tk()
    root.title('ImageCopy')
    root.option_add('*tearOff', 0)
    ImageCopyUi(root)
    root.mainloop()



if __name__ == '__main__':
    main()
