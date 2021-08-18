from tkinter import *
from tkinter import messagebox,Button,Label,ttk
import numpy as np
import os
from numpy.lib.npyio import load
import json
from classes import *

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
log_file=make_log_file_path()

create_filehandler_logger(log_file)

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


root = Tk(className='Npz to JSON converter')
root.geometry("667x400") # set window size
root.minsize(680,350)
root['background']='#A2E08E'
root.tk.call('wm', 'iconphoto', root._w, PhotoImage(file=r'C:\Users\Sharon\USGS_workspace\assets\success.png'))

progress_bar=ttk.Progressbar(root,orient=HORIZONTAL,length='300', mode='determinate')

progress_bar.grid(row=10,column=3, pady=10)

def stop():
    progress_bar.stop()

def step():
    progress_bar['value']+=increament

def empty_progress():
    progress_bar['value']=0


#                                                   DIALOG BOXES
#-----------------------------------------------------------------------------------------------------------------------
def Error_box(msg):
    messagebox.showerror(title='ERROR', message=f"{msg}\nThere has been an unrecoverable error.\nExiting now")
    root.quit()

def EmptySource_box():
    MsgBox = messagebox.askquestion ('Empty Source Folder',"You don\'t have any npz files in your source_files. \n Would you like to add some npz files?",icon = 'warning')
    if MsgBox == 'yes':
       os.startfile( Path.cwd().joinpath('source_files'), 'open')
    else:
        messagebox.showerror(title='Exit', message='There are no npz files in source_files directory.\nExiting now')
        root.quit()

def Invalid_npz_box(filename):
        messagebox.showerror(title='Exit', message=f"{filename} was not a valid npz file and was skipped.")

def Success_box(filename_json):
        messagebox.showinfo(title='Success', message=f"{filename_json} was generated",icon='info')        

#                                                   End of DIALOG BOXES
#-----------------------------------------------------------------------------------------------------------------------    


#   
#                                                HELPER FUNCTIONS FOR READING NPZ FILES
#-----------------------------------------------------------------------------------------------------------------------

def count_files(file_path):
    if os.path.isdir(file_path):
        return len([name for name in os.listdir(file_path) if  os.path.isfile(file_path.joinpath(name))])

def verify_source_dest_exist():
    source_exist=0
    dest_exist=0
    for entry in os.scandir(Path.cwd()):                                         #check for the source or destination folders 
            if entry.is_dir():                                                      
                if entry.name == r"source_files": 
                    source_exist= 1                                              #Set source_exist because source_files exists otherwise it stays 0
                    #check if there are any files in source_files
                    if not os.listdir(entry.path):
                        logger.debug("The source_files folder is empty")
                        EmptySource_box()
                elif entry.name == r"destination_files": 
                    dest_exist=1
    # If either the source_files or destination_files do not exist create it
    if not source_exist :
                logger.debug("\n The directory source_files is missing and will be created.")
                os.mkdir("source_files")
    if not dest_exist :
                logger.debug("\n The directory destination_files is missing and will be created.")
                os.mkdir("destination_files")

def create_destination_file():
    timestampStr = datetime.now().strftime("%d-%b-%Y_%H_%M_%S")
    dest_file="npz_data_"+timestampStr+".json"
    result_path = Path.cwd().joinpath('destination_files')
    destination_path=result_path.joinpath(dest_file)
    return destination_path

def delete_empty_json_result(file_path):
    """delete_empty_json_result: Checks if json file generated is empty and if it is then it is deleted"""
    if os.path.exists(file_path) and os.stat(file_path).st_size == 0:
        logger.debug("Empty file found. Deleting now.")
        os.remove(file_path)

def read_files(destination_path):
    successful_write=0
    try:
        with open(destination_path,'a') as outfile:
            for entry in os.scandir(Path.cwd()):              
                    if entry.is_dir() and entry.name == r"source_files":                                                      
                            for subentry in os.scandir(entry.path):                  
                                filename,file_extension= os.path.splitext(subentry.name)
                                obj=JSON_npz(subentry.path, subentry.name);
                                try:
                                    step()
                                    obj.check_file()                         #if its a valid npz file then read the file  
                                    obj.get_user_ID()
                                    try:
                                        mongo_dict=obj.read_npz()
                                        try:
                                            json_data=obj.create_json(mongo_dict)
                                            outfile.write(json_data)                #write the json data to the json file
                                            outfile.write("\n")                     #put a new line character after each json write
                                            successful_write=1
                                        except UltimateException as strong_error:
                                            logger.exception(strong_error)
                                            Error_box("ERROR: Cannot write to the file.")
                                    except NPZCorruptException as err:
                                        logger.exception(err)
                                        Invalid_npz_box(filename)
                                except IncorrectFileTypeException as npz_file_error:
                                    logger.exception(npz_file_error)
                                    Invalid_npz_box(filename)
    except IOError as file_read_err:
        logger.error(file_read_err)
        Error_box("ERROR cannot read from source_files.")
    step()
    if successful_write:
        logger.debug("\nSuccessful JSON CREATION\n")
        Success_box(destination_path)
    else:
        logger.debug("\nUnsuccessful JSON CREATION\n")

def startup():
    verify_source_dest_exist()

#                                                   END OF HELPER FUNCTIONS
#-----------------------------------------------------------------------------------------------------------------------

label_title = Label(root, text="\nNPZ to JSON converter\n")
label_title.grid(row=1,column=3,pady=10)

label_instructions = Label(root, text="Instructions:\n1. Place valid npz files into the folder called \"source_files\" by using the \"Open Source Files\" button.\n2. Click the \"Run\" button.\n3. Click \"Open Results\" to see your resulting json file. ")
label_instructions.grid(row=2,column=3,pady=10)

def open_result():
    empty_progress()
    verify_source_dest_exist()
    os.startfile(Path.cwd().joinpath('destination_files'), 'open')
button_result = Button(root, text="Open Result", command=open_result)
button_result.grid(row=5,column=3,pady=10)

def progress_bar_increament(num_files):
    return 100/num_files

def open_source():
    empty_progress()
    verify_source_dest_exist()
    os.startfile( Path.cwd().joinpath('source_files'), 'open')
button_source = Button(root, text="Open Source Files", command=open_source)
button_source.grid(row=5,column=2,pady=10,padx=5)

def run_code():
    empty_progress()
    verify_source_dest_exist()
    destination_path=create_destination_file()
    read_files(destination_path)
    delete_empty_json_result(destination_path)
button_run = Button(root, text="Run", command=run_code)
button_run.grid(row=5,column=4 ,pady=10,padx=5)   



root.wait_visibility()                                #waits until the window is visible
verify_source_dest_exist()                            #On startup verify the source and destination files exist
source_path=pathlib.Path.cwd().joinpath("source_files")
num_files=count_files(source_path)
increament=progress_bar_increament(num_files)
root.mainloop()