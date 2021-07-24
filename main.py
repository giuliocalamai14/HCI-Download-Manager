from tkinter import *
import downloader
from gui import Gui

if __name__ == '__main__':
    # APPLICATION GUI WITH TKINTER
    # Create the main windows with title and dimension
    root = Tk()
    gui = Gui(root, downloader)
    root.title("HCI-Download Manager")
    root.geometry("800x500")
    root.mainloop()
