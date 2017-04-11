import tkinter as tk
import tkinter.scrolledtext as ScrolledText
from tkinter import filedialog

from tkinter.ttk import *
import logging
import icopy
# import stdout_redirect as stdtotextw
from os import path

class TextHandler(logging.Handler):
    # This class allows you to log to a Tkinter Text or ScrolledText widget
    # Adapted from Moshe Kaplan: https://gist.github.com/moshekaplan/c425f861de7bbf28ef06

    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text.configure(state='normal')
            self.text.insert(tk.END, msg + '\n')
            self.text.configure(state='disabled')
            # Autoscroll to the bottom
            self.text.yview(tk.END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)


class ImageCopyUi(tk.Frame):

    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.source = tk.StringVar()
        self.target = tk.StringVar()
        self.tmp_str = tk.StringVar()
        self.noCopy = tk.BooleanVar()
        self.initgui()

    def initgui(self):

        self.dir_opt = options = {}
        options['initialdir'] = path.dirname(path.abspath(__file__))
        options['mustexist'] = False
        options['parent'] = self.parent

        # define mainframe which contains rest of the widgets
        mainframe = Frame(self.parent, width=400, padding=(3,3,12,12))
        mainframe.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        # define widgets
        btn_source = Button(mainframe, text="Source", command=self.ask_source_directory)
        btn_source.grid(row=0, column=0, sticky=tk.W)

        entry_source = Entry(mainframe, width=40, textvariable=self.source)
        entry_source.grid(row=1, column=0, columnspan=3, sticky=tk.W+tk.E)

        btn_target = Button(mainframe, text="Target", command=self.ask_target_directory)
        btn_target.grid(row=0, column=3, sticky=tk.W)

        entry_target = Entry(mainframe, width=40, textvariable=self.target)
        entry_target.grid(row=1, column=3, columnspan=3, sticky=tk.W+tk.E)

        self.btn_copy = Button(mainframe, text="Copy", command=self.copy_files, state='disabled')
        self.btn_copy.grid(row=5, column=0, sticky=tk.W)

        checkNoCopy = Checkbutton(mainframe, text='No Copying', variable=self.noCopy, onvalue=True, offvalue=False)
        checkNoCopy.grid(row=5, column=2, sticky=tk.W)

        btn_quit = Button(mainframe, text="Quit", command=self.parent.destroy)
        btn_quit.grid(row=5, column=4, sticky=tk.E)

        # Configure widgets
        for child in mainframe.winfo_children(): child.grid_configure(padx=3, pady=3)

        # Add text widget to display logging info
        st = ScrolledText.ScrolledText(mainframe, width=80, height=25, state='disabled')
        # st.configure(font='TkFixedFont')
        st.grid(row=2, column=0, columnspan=5, rowspan=3, padx=5, pady=3, sticky=('nswe'))

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

        # Create textLogger
        text_handler = TextHandler(st)

        # Logging configuration
        logging.basicConfig(filename='icopy.log',
                            filemode='w',
                            level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')

        # Add the handler to logger
        logger = logging.getLogger()
        logger.addHandler(text_handler)

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
        self.ic_thread = icopy.ImageCopy(self.source.get(), self.target.get(), self.noCopy.get())
        self.ic_thread.start()
        # disable Copy button
        if self.ic_thread.is_alive():
            self.btn_copy.config(state='disabled')
            self._check_thread()

        self.btn_copy.config(state='enabled')

    def _check_thread(self):
        # Still alive? Check again in half a second
        if self.ic_thread.is_alive():
            self.parent.after(100, self._check_thread)


def main():
    root = tk.Tk()
    root.title('ImageCopy')
    root.option_add('*tearOff', 0)
    ImageCopyUi(root)
    root.mainloop()

if __name__ == '__main__':
    main()
