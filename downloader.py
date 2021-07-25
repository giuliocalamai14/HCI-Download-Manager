import os
import threading
from tkinter import *
import requests
import tkinter
from tkinter import filedialog, messagebox
from gui import GuiItem


# Updates the folder where the files will be saved
def browse_button(gui):
    filename = filedialog.askdirectory()
    gui.folder_path = filename
    gui.entry_directory.delete(0, "end")
    gui.entry_directory.insert(END, gui.folder_path)


# Takes the URL from entry widget and start a thread for download
def pass_url_data(gui):
    url = gui.entry_url.get()
    if url is None or url == "":
        messagebox.showwarning(title="Error",
                               message="Download link incorrect. Choose a correct one.")
    else:
        event_thread = threading.Event()
        event_thread.set()
        download_thread = threading.Thread(target=lambda: add_download_item(url, event_thread, gui))
        download_thread.start()


# Convert the size downloaded
def get_standard_size(size):
    standards = ['bytes', 'KB', 'MB', 'GB', 'TB']
    for x in standards:
        if size < 1024.0:
            return "%3.1f %s" % (size, x)
        size /= 1024.0
    return size


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


def add_download_item(url, event_thread, gui):
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
    if os.path.exists(gui.folder_path):
        path = gui.folder_path + "/" + f_name
        if os.path.exists(path) is False:
            downloading_item = GuiItem(gui, f_name, event_thread)
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
                                    downloading_item.btn_text.set(pause_resume)
                                    # Suspend the thread and wait for a signal
                                    # then exit the for loop and resume the download
                                    event_thread.wait()
                                    break
                                else:
                                    pause_resume = "Pause"
                                    downloading_item.btn_text.set(pause_resume)
                                file_obj.write(chunk)
                                bytes_read += len(chunk)
                                current_size = os.path.getsize(path)
                                # Update the current downloaded size
                                downloading_item.size.set(str(get_standard_size(current_size)))
                                if total_size is not None:
                                    # Update the progress bar value
                                    percent_value = round((int(current_size) / int(total_size)) * 100)
                                    downloading_item.percent.set(str(percent_value) + " %")
                                    downloading_item.progress['value'] = percent_value
                                else:
                                    downloading_item.percent.set("Unknown")
                                    downloading_item.progress.config(mode="indeterminate")
                                    downloading_item.progress.start()
                        print("Exiting for loop")
                        if total_size is not None:
                            current_size = os.path.getsize(path)
                            downloading_item.size.set(str(get_standard_size(current_size)))
                            downloading_item.percent_value = round((int(current_size) / int(total_size)) * 100)
                            downloading_item.percent.set(str(percent_value) + " %")
                            downloading_item.progress['value'] = percent_value
                        else:
                            current_size = os.path.getsize(path)
                            downloading_item.size.set(str(get_standard_size(current_size)))
                            downloading_item.percent.set("100 %")
                            downloading_item.progress['value'] = 100
                    if downloading_item.progress['value'] >= 100:
                        downloading_item.percent.set("100 %")
                        loop = False
                except tkinter.TclError:
                    print("Terminating Thread")
        else:
            messagebox.showwarning(title="Error",
                                   message="File already exist in the selected path or is downloading")
    else:
        messagebox.showwarning(title="Error",
                               message="The selected path doesn't exist. Please select a correct one")
    print("Thread Finished!!")
