from tkinter import *
from tkinter import Button, Label, filedialog, messagebox, ttk
import numpy as np
import os
from numpy.lib.npyio import load
import json
from classes import *

#if you want to pass variable to functions from buttons use button=(root,text="sample",command=Lambda: funcion(var))

#                                                   Setting up the Log Files
# -----------------------------------------------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
log_file=make_log_file_path()

create_filehandler_logger(log_file)

file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
#                                                  End of setting up the Log Files
# -----------------------------------------------------------------------------------------------------------------------

#Defining my colors
# ---------------------------------
background_color ='#290628'
button_purple="#6200B3"
#----------------------------------

#                                                  Setting up Tkinter
# -----------------------------------------------------------------------------------------------------------------------
root = Tk(className='Npz to JSON converter')
window_width = 910
window_height = 480
# get the screen dimension
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
# find the center point
center_x = int(screen_width/2 - window_width / 2)
center_y = int(screen_height/2 - window_height / 2)
# set the position of the window to the center of the screen
root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
root.minsize(window_width,window_height)
root['background']=background_color
root.attributes('-alpha',0.95)          #makes the GUI transparent
#-------------------------------------------------------------------------------------

progress_bar=ttk.Progressbar(root,orient=HORIZONTAL,length='300', mode='determinate')
# progress_bar.grid(row=10,column=3, pady=10)

#                                                  End of Setting up Tkinter
# -----------------------------------------------------------------------------------------------------------------------
def stop():
    progress_bar.stop()

def step(increament):
    progress_bar['value']+=increament

def empty_progress():
    """Set the progress bar to empty """
    progress_bar['value']=0

#                                                   DIALOG BOXES
#-----------------------------------------------------------------------------------------------------------------------
def Error_box(msg):
    messagebox.showerror(title='ERROR', message=f"{msg}\nThere has been an unrecoverable error.\nExiting now")
    root.quit()

def EmptySource_box():
    MsgBox = messagebox.askquestion ('Empty Source Folder',"You don\'t have any npz files in your source_files. \n Would you like to add some npz files?",icon = 'warning')
    if MsgBox == 'yes':
        if os.name != 'posix':
            os.startfile( Path.cwd().joinpath('source_files'), 'open')
        else:
            os.system('xdg-open '+os.getcwd()+os.sep+'source_files')
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
        num_files=len([name for name in os.listdir(file_path) if  os.path.isfile(file_path.joinpath(name))])
        if num_files <= 0:
            return 0
        else:
            return num_files

def verify_source_dest_exist():
    dest_exist=0
    for entry in os.scandir(Path.cwd()):                                         #check for the source or destination folders
            if entry.is_dir() and entry.name == r"destination_files":
                dest_exist=1
    # If either the destination_files do not exist create it
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

def read_files(destination_path,increament):
    successful_write=0
    try:
        with open(destination_path,'a') as outfile:
            for entry in os.scandir(Path.cwd()):
                    if entry.is_dir() and entry.name == r"source_files":
                            for subentry in os.scandir(entry.path):
                                filename,file_extension= os.path.splitext(subentry.name)
                                obj=JSON_npz(subentry.path, subentry.name);
                                try:
                                    step(increament)
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
    step(increament)
    if successful_write:
        logger.debug("\nSuccessful JSON CREATION\n")
        Success_box(destination_path)
    else:
        logger.debug("\nUnsuccessful JSON CREATION\n")

def startup():
    # verify_source_dest_exist()                                  #On startup verify the source and destination files exist
    empty_progress()
    source_path=pathlib.Path.cwd().joinpath("source_files")     #Path to source_files (where the npz files are read from)
    num_files=count_files(source_path)                          #count the number of files in source_files to be used for the progress bar
    increament=progress_bar_increament(num_files)               #determines how much progress bar should fill with each npz file read
    return increament

def delete_item_list():
    npz_listbox.delete('anchor')

def deleteAll_listbox():
    npz_listbox.delete(0,'end')

def create_file_list(path_npz):
    #Function to convert all the items in the path to a list
    #and checks for .npz files
    #OS MAY HAVE ISSUES WITH LINUX AND MAC
    if os.path.exists(path_npz):                #ensure the path exists before attempting to access the directory
        files_list=os.listdir(path_npz)
        if files_list != []:                    #Ensure it is not an empty directory
            npz_list = [file for file in files_list if file.lower().endswith('.npz') and os.path.isfile(os.path.join(path_npz, file))]
            print(npz_list)
            return npz_list 
        else:
            print("empty list")
            #throw empty list exception
            return []
    else:
        print("path does not exist")
        #throw invalid npz path  exception
        return []

def open_file_dialog():
    path_npz=filedialog.askdirectory(mustexist=True,initialdir= '/',title='Please select a directory')
    print(path_npz)
    text.set(f"{path_npz}")

    #Update the list box
    files_list=create_file_list(path_npz)
    if files_list == []:
        print("No valid npz files")
        return
        #throw exception for no valid npz files
    #catch exception here and trigger message box

    #delete everything from listbox first to ensure clean insert
    deleteAll_listbox()
    #insert into listbox
    for item in files_list:
        npz_listbox.insert('end',item)

def read_npz_listbox():
    list_size=npz_listbox.size()
    npztuple =npz_listbox.get(0,list_size-1)
    npzlist=list(npztuple)
    return npzlist


#                                                   END OF HELPER FUNCTIONS
#-----------------------------------------------------------------------------------------------------------------------

#Instruction frame to hold the title and the instructions
#-----------------------------------------------------------------
instruction_frame=Frame(root,background=background_color)
label_title = Label(instruction_frame, text="\nNPZ to JSON converter\n")
label_title.config( foreground= "white",background=background_color)
label_title.grid(row=0,column=2,pady=5)

label_instructions = Label(instruction_frame, text="Instructions:\n1. Select the folder where the .npz files are located by using the \"Select npz Folder\" button.\n2. Click the \"Convert\" button to convert the .npx files to .json.\n3. Click \"Open Result\" to see your resulting json file. ")
label_instructions.config( foreground= "white",background=background_color)
label_instructions.grid(row=0,column=2,pady=5)

instruction_frame.pack(side='top')
#-------------------------------------------------------------

#Frame to hold the "Choose a Folder" button and the corresponding labels
#-----------------------------------------------------------------
folder_frame=Frame(root,height = 75,width = 180,pady=10,padx=10,background="white")
folder_frame.pack(side='left',padx=10,pady=10)

#Making a label to hold the path where the .npz files are 
#global StringVar method of changing a label
text = StringVar()
text.set('')                        #this allows  the text within the label to change
label=Label(folder_frame, textvariable=text)
label.config( foreground= "white",background=background_color)
label.grid(row=1,column=0)

#Label instrctions for path to .npz
label_folder_instr=Label(folder_frame,text="Directory containing .npz files:")
label_folder_instr.config( foreground= "white",background=background_color)
label_folder_instr.grid(row=0,column=0)

#Button to open a folder
Open_Folder_button = Button(folder_frame, text="Choose Dir", command= open_file_dialog,background=button_purple,fg="white")
Open_Folder_button.grid(row=2,column=0,pady=10,padx=5)
#-------------------------------------------------------------------

#Create frame to hold scrolling list and buttons to change list
list_holder=Frame(root,width=190,height = 210,background="white",padx=7,pady=7)
list_holder.pack(side='right',pady=10,padx=5)


#Create a frame to hold the list
list_frame=Frame(list_holder,height = 600,width = 300,pady=10)
xlist_scroll_bar=Scrollbar(list_frame, orient='horizontal')
ylist_scroll_bar=Scrollbar(list_frame, orient='vertical')


#Create the listbox to hold the files in the directory to read .npz files from
npz_listbox=Listbox(list_frame,width=50,yscrollcommand=ylist_scroll_bar.set,xscrollcommand=xlist_scroll_bar.set,bg=background_color,fg="white",selectbackground="#EA7AF4",highlightbackground="#EA7AF4",highlightcolor="#EA7AF4")

#Configure the scrollbar to scroll within the list vertically and horizontally
ylist_scroll_bar.config(command=npz_listbox.yview)
xlist_scroll_bar.config(command=npz_listbox.xview)
#1. Pack the scrollbar within the listframe
xlist_scroll_bar.pack(side='bottom',fill='x')
#2. Pack the frame 
list_frame.pack(side='right',padx=10)
#3.Place the list within the frame
npz_listbox.pack(side='left')
#4.Place the vertical scrollbar after the horizontal one
ylist_scroll_bar.pack(side='right',fill='y')

delete_all_button=Button(list_holder,text="Clear All",command=deleteAll_listbox,background=button_purple,fg="white")
delete_all_button.pack(side='bottom',pady=50)

delete_button=Button(list_holder,text="Delete File",command=delete_item_list,background=button_purple,fg="white")
delete_button.pack(side='bottom',pady=30)

#---------------------------------------------------------------------------

def open_result():
    empty_progress()
    verify_source_dest_exist()
    if os.name != 'posix':
        os.startfile(Path.cwd().joinpath('destination_files'), 'open')
    else:
        os.system('xdg-open '+os.getcwd()+os.sep+'destination_files')

button_result = Button(root, text="Open JSON", command=open_result,background=button_purple,fg="white")
button_result.pack(side='bottom',pady=10)

def progress_bar_increament(num_files):
    try:
        if num_files==0:
            return 100                          #There are no files to count so the increament is 100
        return 100/num_files
    except ZeroDivisionError as err:
        logger.error(err)
        Error_box("There was an error loading the logging files due to no files in source_files being provided. Please add files to the source_files directory.")


def open_source():
    empty_progress()
    verify_source_dest_exist()
    if os.name != 'posix':
        os.startfile( Path.cwd().joinpath('source_files'), 'open')
    else:
        os.system('xdg-open '+os.getcwd()+os.sep+'source_files')

def run_code():
    increament=startup()
    destination_path=create_destination_file()
    read_files(destination_path,increament)
    delete_empty_json_result(destination_path)

button_run = Button(root, text="Run", command=run_code,background=button_purple,fg="white")
button_run.pack(side=BOTTOM)



root.wait_visibility()                                #waits until the window is visible
startup()                                             #Calculate progressbar increament, checks if source_files and destination_files exist
root.mainloop()
