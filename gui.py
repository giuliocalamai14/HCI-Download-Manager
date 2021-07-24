from tkinter import *
from tkinter import ttk
from tkinter.ttk import Progressbar
from tkmacosx import Button
from PIL import Image, ImageTk
from sys import platform
import tkmacosx

# Main declaration: folder and background color app

bg_main = "#BFBDC1"
bg_bar = "#37323E"
bg_item = "#6D6A75"
bg_item_border = "#BFBDC1"
bg_button = "#DE9E36"
bg_button_onclick = "#e4ae58"
bg_button_resume = "#5fa769"
bg_button_resume_onclick = "#78b581"
bg_delete = "#f34958"
bg_delete_onclick = "#f56e7a"


class Gui:
    def __init__(self, root, downloader):
        self.folder_path = ""
        self.downloader = downloader

        # Create a frame element to put inside the root window
        self.frame = Frame(root, bg=bg_main)
        self.frame.pack(fill="both", expand=True)

        # Create a input_frame that will contain the buttons
        self.input_frame = Frame(self.frame, bg=bg_bar, padx=5, pady=5)
        self.input_frame.grid_columnconfigure(0, weight=1)

        # Define and place the 2 buttons inside the input_frame element
        self.label_url = Label(self.input_frame, text="Insert URL", bg=bg_bar, fg="white", padx=5, pady=5, anchor="w")
        self.label_url.grid(row=0, column=0, sticky="nsew")

        if platform == 'darwin':
            self.entry_url = Entry(self.input_frame, bg="white", fg="black", width=50)
        else:
            self.entry_url = Entry(self.input_frame, bg="white", fg="black", width=80)

        self.entry_url.grid(row=0, column=1)
        self.button_download = Button(self.input_frame, text="Download", bg=bg_button, fg="black",
                                      activebackground=bg_button_onclick,
                                      activeforeground="black", borderless=True, focusthickness=0,
                                      command=lambda: self.downloader.pass_url_data(self),
                                      padx=10, pady=10)
        self.button_download.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
        self.label_directory = Label(self.input_frame, text="SAVE directory", bg=bg_bar, fg="white", padx=5, pady=5,
                                     anchor="w")
        self.label_directory.grid(row=1, column=0, sticky="nsew")

        if platform == 'darwin':
            self.entry_directory = Entry(self.input_frame, bg="white", fg="black", width=50)
        else:
            self.entry_directory = Entry(self.input_frame, bg="white", fg="black", width=80)

        self.entry_directory.insert(END, self.folder_path)
        self.entry_directory.grid(row=1, column=1)
        self.button_browse = Button(self.input_frame, text="Browse", bg=bg_button, fg="black",
                                    activebackground=bg_button_onclick,
                                    activeforeground="black", borderless=True, focusthickness=0,
                                    command=lambda: self.downloader.browse_button(self),
                                    padx=10, pady=10)
        self.button_browse.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)

        self.input_frame.pack(fill="x")

        self.download_frame = tkmacosx.SFrame(self.frame, bg=bg_main, autohidescrollbar=True, mousewheel=True,
                                              scrollbarwidth=14)
        self.download_frame.pack(fill="both", expand=True)


class GuiItem:

    def __init__(self, gui, f_name, event_thread):
        # Create a frame_item representing the element in download
        self.frame_item = Frame(gui.download_frame, bg=bg_item, padx=5, pady=5, highlightbackground=bg_item_border,
                                highlightcolor=bg_item_border, highlightthickness=1)

        self.img = Image.open("./icons/download_icon_win.png")
        if platform == 'darwin':
            self.img = Image.open("./icons/download_icon_mac.png").convert("RGB")
        self.render = ImageTk.PhotoImage(self.img.resize((54, 54), Image.ANTIALIAS))
        self.label = Label(self.frame_item, bg=bg_item, image=self.render)
        self.label.image = self.render
        self.label.grid(row=0, column=0, rowspan=2)

        # Title of the element in download
        self.title = Label(self.frame_item, bg=bg_item, fg="white", text=f_name, padx=5, pady=5, anchor="w")
        self.title.config(font=("Arial", "15"))
        self.title.grid(row=0, column=1, sticky="nsew")

        # Setting a theme for the progress bar (on OSX)
        self.s = ttk.Style()
        self.s.theme_use('default')
        self.s.configure("bar.Horizontal.TProgressbar", troughcolor='#BFBDC1', bordercolor='#BFBDC1',
                         background='#5fa769', lightcolor='#5fa769', darkcolor='#5fa769', borderless=True)

        # Define a progress bar
        self.progress = Progressbar(self.frame_item, orient=HORIZONTAL, mode="determinate",
                                    style="bar.Horizontal.TProgressbar")
        self.progress['value'] = 0
        self.progress.grid(row=1, column=1, sticky="nsew")

        # Labels for percentage and size
        self.percent = StringVar()
        self.percent.set("0 %")
        self.label_percentage = Label(self.frame_item, textvariable=self.percent, padx=5, anchor="w", bg=bg_item,
                                      fg="white")
        self.label_percentage.config(font=("Arial", "13"))
        self.label_percentage.grid(row=0, column=2)
        self.size = StringVar()
        self.size.set("0 KB")
        self.label_size = Label(self.frame_item, textvariable=self.size, padx=5, anchor="w", bg=bg_item, fg="white")
        self.label_size.config(font=("Arial", "11"))
        self.label_size.grid(row=1, column=2)

        # Buttons for pause/resume and delete downloads
        self.btn_text = StringVar()
        self.btn_text.set("Pause")
        self.button_pause_resume = Button(self.frame_item, textvariable=self.btn_text, bg=bg_button_resume, fg="white",
                                          activebackground=bg_button_resume_onclick, borderless=True, focusthickness=0,
                                          command=lambda: gui.downloader.paused(event_thread), padx=5, pady=5)
        self.button_pause_resume.grid(row=0, column=3)
        self.button_delete = Button(self.frame_item, text="Delete", bg=bg_delete, fg="white",
                                    activebackground=bg_delete_onclick, borderless=True, focusthickness=0,
                                    command=lambda: gui.downloader.delete(self.frame_item), padx=5, pady=5)
        self.button_delete.grid(row=1, column=3)

        self.frame_item.pack(fill="x", expand=True)
        self.frame_item.columnconfigure(1, weight=1)
