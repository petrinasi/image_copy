import Tkinter as Tk
import sys

class Std_redirector():
    def __init__(self,text_widget):
        self.widget = text_widget
        self.defstdout = sys.stdout

    def write(self,string):
        self.widget.see(Tk.END)
        self.widget.insert("end",string)

    def start(self):
        sys.stdout = self

    def stop(self):
        sys.stdout = self.defstdout

    def flush(self):
        self.defstdout.flush()
