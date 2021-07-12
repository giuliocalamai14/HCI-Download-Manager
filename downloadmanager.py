from tkinter import *
from tkinter import ttk, filedialog, messagebox
from tkinter.ttk import Progressbar
from tkmacosx import Button
from PIL import Image, ImageTk
from sys import platform
import tkmacosx
import tkinter
import requests
import re
import os
import threading

# Main declaration: folder and background color app
folder_path = ""

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


# Takes the URL from entry widget and start a thread for download
def pass_url_data():
    url = entry_url.get()
    if url is None or url == "":
        messagebox.showwarning(title="Error",
                               message="Download link incorrect. Choose a correct one.")
    else:
        event_thread = threading.Event()
        event_thread.set()
        download_thread = threading.Thread(target=lambda: add_download_item(url, event_thread))
        download_thread.start()


# Convert the size downloaded
def get_standard_size(size):
    standards = ['bytes', 'KB', 'MB', 'GB', 'TB']
    for x in standards:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0
    return size


# Updates the folder where the files will be saved
def browse_button():
    global folder_path
    filename = filedialog.askdirectory()
    entry_directory.delete(0, "end")
    folder_path = filename
    entry_directory.insert(END, folder_path)


# Pause/Resume thread downloading
def paused(event_thread):
    if event_thread.isSet() is False:
        event_thread.set()
    else:
        event_thread.clear()


# Delete the selected download
def delete(frame_item):
    res = messagebox.askquestion("Delete", "Cancel the current download?")
    if res == 'yes':
        frame_item.destroy()


# Main thread function: create frame, send request, start download
def add_download_item(url, event_thread):
    # Send URL request
    req = requests.get(url, allow_redirects=True, stream=True)
    # Check the size of download
    if "content-length" in req.headers:
        total_size = req.headers['content-length']
    else:
        total_size = None

    filename = ""

    # Check and define the name of the file
    if "content-disposition" in req.headers.keys():
        f_name = re.findall("filename=(.+)", req.headers["content-disposition"])[0]
    else:
        f_name = url.split("/")[-1]

    f_name.replace(" ", "")

    # Check if path selected exist
    if os.path.exists(folder_path):
        path = folder_path + "/" + f_name
        # Create a frame_item representing the element in download
        frame_item = Frame(download_frame, bg=bg_item, padx=5, pady=5, highlightbackground=bg_item_border,
                           highlightcolor=bg_item_border, highlightthickness=1)

        img = Image.open("./icons/download_icon_win.png")
        if platform == 'darwin':
            img = Image.open("./icons/download_icon_mac.png").convert("RGB")
        render = ImageTk.PhotoImage(img.resize((54, 54), Image.ANTIALIAS))
        label = Label(frame_item, bg=bg_item, image=render)
        label.image = render
        label.grid(row=0, column=0, rowspan=2)

        # Title of the element in download
        title = Label(frame_item, bg=bg_item, fg="white", text=f_name, padx=5, pady=5, anchor="w")
        title.config(font=("Arial", "15"))
        title.grid(row=0, column=1, sticky="nsew")

        # Setting a theme for the progress bar (on OSX)
        s = ttk.Style()
        s.theme_use('default')
        s.configure("bar.Horizontal.TProgressbar", troughcolor='#BFBDC1', bordercolor='#BFBDC1',
                    background='#5fa769', lightcolor='#5fa769', darkcolor='#5fa769', borderless=True)

        # Define a progress bar
        progress = Progressbar(frame_item, orient=HORIZONTAL, mode="determinate",
                               style="bar.Horizontal.TProgressbar")
        progress['value'] = 0
        progress.grid(row=1, column=1, sticky="nsew")

        # Labels for percentage and size
        percent = StringVar()
        percent.set("0 %")
        label_percentage = Label(frame_item, textvariable=percent, padx=5, anchor="w", bg=bg_item, fg="white")
        label_percentage.grid(row=0, column=2)
        size = StringVar()
        size.set("0 KB")
        label_size = Label(frame_item, textvariable=size, padx=5, anchor="w", bg=bg_item, fg="white")
        label_size.grid(row=1, column=2)

        # Buttons for pause/resume and delete downloads
        btn_text = StringVar()
        btn_text.set("Pause")
        button_pause_resume = Button(frame_item, textvariable=btn_text, bg=bg_button_resume, fg="white",
                                     activebackground=bg_button_resume_onclick, borderless=True, focusthickness=0,
                                     command=lambda: paused(event_thread), padx=5, pady=5)
        button_pause_resume.grid(row=0, column=3)
        button_delete = Button(frame_item, text="Delete", bg=bg_delete, fg="white",
                               activebackground=bg_delete_onclick, borderless=True, focusthickness=0,
                               command=lambda: delete(frame_item), padx=5, pady=5)
        button_delete.grid(row=1, column=3)

        frame_item.pack(fill="x", expand=True)
        frame_item.columnconfigure(1, weight=1)

        loop = True
        bytes_read = 0
        # Main loop of thread
        while loop:
            try:
                # Define the mode of writing: "wb" -> writing binary ; "ab" -> append binary
                # "wb" is used the first time the file is created
                # "ab" is used on every resume to continue the download
                if bytes_read == 0:
                    write_mode = "wb"
                else:
                    write_mode = "ab"
                    resume_header = {'Range': 'bytes=%d-' % bytes_read}
                    req = requests.get(url, headers=resume_header, stream=True, allow_redirects=True)
                # Create the file in the selected path
                with open(path, write_mode) as file_obj:
                    # Start the download and write the file with a
                    for chunk in req.iter_content(chunk_size=1024):
                        if chunk:
                            if event_thread.isSet() is False:
                                pause_resume = "Resume"
                                btn_text.set(pause_resume)
                                # Suspend the thread and wait for a signal
                                # then exit the for loop and resume the download
                                event_thread.wait()
                                break
                            else:
                                pause_resume = "Pause"
                                btn_text.set(pause_resume)
                            file_obj.write(chunk)
                            bytes_read += len(chunk)
                            current_size = os.path.getsize(path)
                            # Update the current downloaded size
                            size.set(str(get_standard_size(current_size)))
                            if total_size is not None:
                                # Update the progress bar value
                                percent_value = round((int(current_size) / int(total_size)) * 100)
                                percent.set(str(percent_value) + " %")
                                progress['value'] = percent_value
                            else:
                                percent.set("Unknown")
                                progress.config(mode="indeterminate")
                                progress.start()
                    print("Exiting for loop")
                    if total_size is not None:
                        current_size = os.path.getsize(path)
                        size.set(str(get_standard_size(current_size)))
                        percent_value = round((int(current_size) / int(total_size)) * 100)
                        percent.set(str(percent_value) + " %")
                        progress['value'] = percent_value
                    else:
                        current_size = os.path.getsize(path)
                        size.set(str(get_standard_size(current_size)))
                        percent.set("100 %")
                        progress['value'] = 100
                if progress['value'] == 100:
                    loop = False
            except tkinter.TclError:
                print("Terminating Thread")

    else:
        messagebox.showwarning(title="Error",
                               message="The selected path doesn't exist. Please select a correct one")
    print("Thread Finished!!")


# APPLICATION GUI WITH TKINTER
# Create the main windows with title and dimension
root = Tk()
root.title("HCI-Download Manager")
# root.resizable(False, False)
root.geometry("800x500")

# Create a frame element to put inside the root window
frame = Frame(root, bg=bg_main)
frame.pack(fill="both", expand=True)

# Create a input_frame that will contain the buttons
input_frame = Frame(frame, bg=bg_bar, padx=5, pady=5)

# Define and place the 2 buttons inside the input_frame element
label_url = Label(input_frame, text="Insert URL", bg=bg_bar, fg="white", padx=5, pady=5, anchor="w")
label_url.grid(row=0, column=0, sticky="nsew")
entry_url = Entry(input_frame, bg="white", fg="black", width=50)
entry_url.grid(row=0, column=1)
button_download = Button(input_frame, text="Download", bg=bg_button, fg="black", activebackground=bg_button_onclick,
                         activeforeground="black", borderless=True, focusthickness=0, command=pass_url_data, padx=10,
                         pady=10)
button_download.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
input_frame.grid_columnconfigure(0, weight=1)
label_directory = Label(input_frame, text="SAVE directory", bg=bg_bar, fg="white", padx=5, pady=5, anchor="w")
label_directory.grid(row=1, column=0, sticky="nsew")
entry_directory = Entry(input_frame, bg="white", fg="black", width=50)
entry_directory.insert(END, folder_path)
entry_directory.grid(row=1, column=1)
button_browse = Button(input_frame, text="Browse", bg=bg_button, fg="black", activebackground=bg_button_onclick,
                       activeforeground="black", borderless=True, focusthickness=0, command=browse_button, padx=10,
                       pady=10)
button_browse.grid(row=1, column=2, sticky="nsew", padx=10, pady=10)

input_frame.pack(fill="x")

download_frame = tkmacosx.SFrame(frame, bg=bg_main, autohidescrollbar=True, mousewheel=True, scrollbarwidth=14)
download_frame.pack(fill="both", expand=True)

# Fundamental for running the program in a loop mode
root.mainloop()
