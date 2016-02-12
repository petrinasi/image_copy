from tkinter import *
from tkinter import filedialog
from tkinter.ttk import *
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
        self.noCopy = BooleanVar()

        # define mainframe which contains rest of the widgets
        mainframe = Frame(self.parent, padding=(3,3,12,12))
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))

        # define widgets
        btn_source = Button(mainframe, text="Source", command=self.ask_source_directory)
        btn_source.grid(row=0, column=0, sticky=W)

        entry_source = Entry(mainframe, width=40, textvariable=self.source)
        entry_source.grid(row=1, column=0, columnspan=3, sticky=W+E)

        btn_target = Button(mainframe, text="Target", command=self.ask_target_directory)
        btn_target.grid(row=0, column=3, sticky=W)

        entry_target = Entry(mainframe, width=40, textvariable=self.target)
        entry_target.grid(row=1, column=3, columnspan=3, sticky=W+E)

        self.btn_copy = Button(mainframe, text="Copy", command=self.copy_files, state='disabled')
        self.btn_copy.grid(row=5, column=0, sticky=W)

        checkNoCopy = Checkbutton(mainframe, text='No Copying', variable=self.noCopy, onvalue=True, offvalue=False)
        checkNoCopy.grid(row=5, column=2, sticky=W)

        btn_quit = Button(mainframe, text="Quit", command=self.parent.destroy)
        btn_quit.grid(row=5, column=4, sticky=E)

        # Configure widgets
        for child in mainframe.winfo_children(): child.grid_configure(padx=3, pady=3)

        # create text widget; stdout will be directed here when copying files
        self.logtext = Text(mainframe, width=0, height=25, state = 'disabled')
        self.logtext.grid(row=2, column=0, columnspan=5, rowspan=3, padx=5, pady=3, sticky=('nswe'))

        # create stdout redirector
        self.redir = stdtotextw.Std_redirector(self.logtext)

        # create a Scrollbar and associate it with txt
        scrollb = Scrollbar(mainframe, command=self.logtext.yview)
        scrollb.grid(row=2, column=4, padx=5, pady=3, rowspan=3, sticky='nse')
        self.logtext['yscrollcommand'] = scrollb.set

        # bind pressing Return key to copy_files() function
        #assert isinstance(self.parent.bind, object)
        #self.parent.bind('<Return>', self.copy_files)

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
        mainframe.rowconfigure(3, weight=1)
        mainframe.rowconfigure(4, weight=1)
        mainframe.rowconfigure(5, weight=1)

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
        self.tmp_str.set(filedialog.askdirectory(**self.dir_opt))

        if self.tmp_str.get() is not "":
            self.source.set(self.tmp_str.get())

        self.tmp_str.set("")

        if self.source.get() is not "" and self.target.get() is not "":
            self.btn_copy.config(state = 'normal')


    def ask_target_directory(self):
        """Returns a selected directoryname."""
        self.tmp_str.set(filedialog.askdirectory(**self.dir_opt))

        if self.tmp_str.get() is not "":
            self.target.set(self.tmp_str.get())

        self.tmp_str.set("")

        if self.source.get() is not "" and self.target.get() is not "":
            self.btn_copy.config(state = 'normal')

    def copy_files(self):
        # Create instance of iCopy and copy files
        self.logtext.config(state = 'normal')
        self.redir.flush()
        self.redir.start()
        self.ic = icopy.ImageCopy(self.source.get(), self.target.get(), self.noCopy.get())
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
