import tkinter as tk
from NPZClass import *
import FileManipulators
from tkinter import filedialog, messagebox, ttk

class InstructionFrame(tk.Frame):
    def __init__(self,parent):
        super().__init__(parent,background=parent.frame_color)
        self.__create_widgets(parent)
    
    def __create_widgets(self,parent):
        label_title =  tk.Label(self, text="\nNPZ to JSON converter\n")
        label_title.config( foreground= "white",background=parent.frame_color)
        label_title.grid(row=0,column=2,pady=5)

        label_instructions = tk.Label(self, text="Instructions:\n1. Select the folder where the .npz files are located by using the \"Select npz Folder\" button.\n2. Click the \"Run\" button to convert the .npz files to .json.\n3. Click \"Open JSON\" to see your resulting json file. ")
        label_instructions.config( foreground= "white",background=parent.frame_color)
        label_instructions.grid(row=0,column=2,pady=5)
        
class MainApp(tk.Tk):

     #Defining App colors
    # ---------------------------------
    background_color ='#121212'
    frame_color='#292929'
    text_color='#6C6C6C'
    button_purple="#6200B3"
    #----------------------------------

    #                                                   DIALOG BOXES
    #-----------------------------------------------------------------------------------------------------------------------
    def CriticalErrorBox(self,msg):
        """" A system error dialog box that informs the user an recoverable error has occured and the program will quit. 
        Args:
            self: An instance of the MainApp class
            msg: A custom msg provided by the program that typically specifies what kind of error occured.

        Returns:
            None
        Raises:
            None
        """
        messagebox.showerror(title='ERROR', message=f"{msg}\nThere has been an unrecoverable error.\nExiting now")
        self.quit()

    def ErrorBox(self,msg):
        """" A system error dialog box that informs the user an recoverable error has occured and the program will quit. 
        Args:
            self: An instance of the MainApp class
            msg: A custom msg provided by the program that typically specifies what kind of error occured.

        Returns:
            None
        Raises:
            None
        """
        messagebox.showerror(title='ERROR', message=f"{msg}")

    def EmptySource_box(self,npz_path):
        """" A system error dialog box that asks the user to choose a directory to open .npz files with or quits the program
        
            If the user selects yes and chooses to select a directory to read .npz files from the open_file_dialog()
            will be executed. If the user selects option no then the program exits.

        Args:
            self: An instance of the MainApp class
            npz_path: a pathlib.path to the current directory where .npz files would be read from

        Returns:
            Exits the program if the user choose not to select a directory with .npz files
        Raises:
            None
        """
        MsgBox = messagebox.askquestion (title=f"Would you like to add some .npz files?",message=f"You don\'t have any npz files at the location:\n {npz_path}.\n Would you like to add some .npz files?",icon = 'warning')
        if MsgBox == 'yes':
            self.open_file_dialog()
        else:
            messagebox.showerror(title='Exit', message=f"There are no npz files in {npz_path} directory.\nExiting now")
            self.quit()

    def Invalid_npz_box(self,filename):
        """" A system error dialog box that informs the user an error occured while attempting to read the filename
        
        Args:
            self: An instance of the MainApp class.
            filename: A string specifying the file name that could not be processed.

        Returns:
            None
        Raises:
            None
        """
        messagebox.showerror(title='Exit', message=f"{filename} was not a valid npz file and was skipped.")

    def Success_box(self,filename):
        """" A system info dialog box that informs the user a json file was successfully created.
        
        Args:
            self: An instance of the MainApp class.
            filename: A string specifying the file name that was generated.

        Returns:
            None
        Raises:
            None
        """
        messagebox.showinfo(title='Success', message=f"{filename} was generated",icon='info')
    #                                                   End of DIALOG BOXES
    #-----------------------------------------------------------------------------------------------------------------------

    def __init__(self, logger):
        tk.Tk.__init__(self,className=" NPZ to JSON converter")
        self.logger=logger
        self.logger.info("\nSuccessfully created base app\n")
        #make sure the destination folder exists to store the resulting JSON file
        self.wait_visibility()
        FileManipulators.verify_destination_exists(self.logger)
        #create the main app's gui
        self.build_main_app()
        #make the subframes within the main app
        self.__create_frames()


        #Frame to hold the "Choose a Folder" button and the corresponding labels
        #-----------------------------------------------------------------
        self.folder_frame=tk.Frame(self,height = 75,width = 180,pady=10,padx=10,background=MainApp.frame_color)
        self.folder_frame.pack(side='left',padx=10,pady=10)

        self.path_label=tk.Label(self.folder_frame, text="")
        self.path_label.config( foreground= "white",background=MainApp.frame_color)
        self.path_label.grid(row=1,column=0)

        #path_label instrctions for path to .npz
        self.label_folder_instr=tk.Label(self.folder_frame,text="Directory containing .npz files:")
        self.label_folder_instr.config( foreground= "white",background=MainApp.frame_color)
        self.label_folder_instr.grid(row=0,column=0)

        #Button to open a folder
        self.Open_Folder_button = tk.Button(self.folder_frame, text="Choose Dir", command= self.open_file_dialog,background=MainApp.button_purple,fg="white")
        self.Open_Folder_button.grid(row=2,column=0,pady=10,padx=5)
        #-------------------------------------------------------------------

        #Create frame to hold scrolling list and buttons to change list
        self.list_holder=tk.Frame(self,width=190,height = 210,background=MainApp.frame_color,padx=7,pady=7)
        self.list_holder.pack(side='right',pady=10,padx=5)


        #Create a frame to hold the list
        self.list_frame=tk.Frame(self.list_holder,height = 600,width = 300,pady=10)
        self.xlist_scroll_bar=tk.Scrollbar(self.list_frame, orient='horizontal')
        self.ylist_scroll_bar=tk.Scrollbar(self.list_frame, orient='vertical')

        #Create the buttons within the same frame holding the listbox
        delete_button=tk.Button(self.list_holder,text="Delete File",command=self.delete_item_list,background=MainApp.button_purple,fg="white")
        delete_button.grid(column=0,row = 0,pady=5,padx=10)

        delete_all_button=tk.Button(self.list_holder,text="Clear All",command=self.deleteAll_listbox,background=MainApp.button_purple,fg="white")
        delete_all_button.grid(column=0,row = 2,pady=5,padx=10)

        #Create the listbox to hold the files in the directory to read .npz files from
        self.npz_listbox=tk.Listbox(self.list_frame,width=50,yscrollcommand=self.ylist_scroll_bar.set,xscrollcommand=self.xlist_scroll_bar.set,bg=MainApp.background_color,fg="white",highlightbackground="#EA7AF4",selectbackground="#EA7AF4",activestyle='none')

        #Configure the scrollbar to scroll within the list vertically and horizontally
        self.ylist_scroll_bar.config(command=self.npz_listbox.yview)
        self.xlist_scroll_bar.config(command=self.npz_listbox.xview)
        #1. Pack the scrollbar within the listframe
        self.xlist_scroll_bar.pack(side='bottom',fill='x')
        #2. Pack the frame 
        self.list_frame.grid(column=2,row=1,padx=5,pady=5)
        #3.Place the list within the frame
        self.npz_listbox.pack(side='left')
        #4.Place the vertical scrollbar after the horizontal one
        self.ylist_scroll_bar.pack(side='right',fill='y')

        self.button_result = tk.Button( text="Open JSON",command=lambda:FileManipulators.open_result(self.logger), background=MainApp.button_purple,fg="white")
        self.button_result.pack(side='bottom',pady=10)

        self.button_run = tk.Button(text="Run", command=self.run_code,background=MainApp.button_purple,fg="white")
        self.button_run.pack(side='bottom')

    def build_main_app(self):
        """"Builds the main frame of the app.

        Builds the main frame of the app by specifiying the dimensions of the app, the background colors, the transparency, and
        where on the user's screen it will display.

        Note: This may cause errors on user's who have multiple displays.

        Args:
             self: An instance of the MainApp class.
        Returns:
           None.
        Raises:
            None.
        """
        window_width = 910
        window_height = 480
        # get the screen dimension
        screen_width =  self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # find the center point
        center_x = int(screen_width/2 - window_width / 2)
        center_y = int(screen_height/2 - window_height / 2)
        # set the position of the window to the center of the screen
        self.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.minsize(window_width,window_height)
        self['background']=MainApp.background_color
        self.attributes('-alpha',0.97)          #makes the GUI transparent

    def __create_frames(self):
        """"Creates independent sub frames to be nested within the main frame.

        Creates the instrcution frame and packs it into the main frame.

        Args:
             self: An instance of the MainApp class.
        Returns:
           None.
        Raises:
            None.
        """
        self.instructionframe=InstructionFrame(self)
        self.instructionframe.pack(side='top')

    def read_files(self,source_path,npz_list,destination_path):
        """"Reads all the files in npz_list that are in the directory specified by source_path to the directory in destination_path

       Reads the files in the npz_list and appends each filename in npz_list with the source_path to create an absolute path to the .npz file.
       It then extracts all the relevant data from the .npz files and writes it the location specifed by destination_path.

        Args:
             self: An instance of the MainApp class.
             source_path: pathlib.path location of the directory containing .npz files to be processed
             npz_list: A list of .npz files that will be processed
             destination_path: pathlib.path location of the file that was written to. 
        Returns:
           None.
        Raises:
            UltimateException: The JSON file could not be created due to an error.
            NPZCorruptException: The .npz file could not be converted to JSON.
            IncorrectFileTypeException: A non .npz file was read causing an error
            IOError: An error occured while accessing the .npz file or json file.
        """
        successful_JSON_generated=False
        if npz_list == []:
            self.logger.exception("Empty listbox provided")
            self.EmptySource_box(source_path)
        # Create a list to hold the JSON data that will be written to the file
        JSONArray=[]
        classesArrayGiven=[]
        badFilesList=[]
        for entry in npz_list:
            npz_file_path=source_path.joinpath(entry)
            filename,file_extension= os.path.splitext(npz_file_path.name)
            # Initalize the NPZtoJSON class  with the path to the NPZ file and the name of the NPZ file
            obj=NPZtoJSON(npz_file_path, npz_file_path.name);
            try:
                obj.check_file()                #Verify valid .npz file & if not correct file type trigger IncorrectFileTypeException
                obj.get_user_ID()               #Get the User_ID from the .npz file
                try:                            #If npz file is corrupt trigger NPZCorruptException
                    # Create a dictionary based on the data in the npz file
                    # readClassesNPZ
                    # Passes classes to npz
                    classesArrayGiven,mongo_dict=obj.read_npz(classesArrayGiven)
                    try:
                        # Convert the dictionary to JSON
                        json_data=obj.create_json(mongo_dict)
                        JSONArray.append(json_data)
                    except UltimateException as strong_error:
                        self.logger.exception(strong_error)
                        self.CriticalErrorBox("ERROR: Cannot create a JSON file exiting now.")
                except NPZCorruptException as err:
                    # Add to list of bad files
                    self.logger.exception(err)
                    badFilesList.append(npz_file_path.name)
                    self.Invalid_npz_box(npz_file_path.name)
            except IncorrectFileTypeException as npz_file_error:
                # Add to list of bad files
                self.logger.exception(npz_file_error)
                badFilesList.append(npz_file_path.name)
                self.Invalid_npz_box(npz_file_path.name)
        try:
            with open(destination_path,'a') as outfile:
                if JSONArray != []:
                    #Last spot in JSONArray
                    JSONArrayLastSpot=len(JSONArray)-1
                    print("\n JSONArray",JSONArray)
                    outfile.write("[")
                    for item in JSONArray:
                        outfile.write(item)
                        # If the index of the current item is the last spot in the JSON array do NOT write the comma
                        if JSONArray.index(item) != JSONArrayLastSpot:
                            outfile.write(",")
                    outfile.write("]")
                    successful_JSON_generated=True
        except IOError as file_read_err:
            self.logger.error(file_read_err)
            self.CriticalErrorBox("ERROR cannot read any files from {source_path}}.")

        #At the end check if at least one .npz file was converted to JSON successfully.
        if successful_JSON_generated:
            self.Success_box(destination_path)

        # Only print the bad files to a text file if there are any to print
        if badFilesList != []:
            badFilePath=FileManipulators.create_badFile_file()
            with open(badFilePath, 'a') as writer:
                for file in badFilesList:
                    writer.write(file+"\n")
            self.ErrorBox(f"A list of invalid files have been written to: ${badFilePath}")
             
    def update_path_label(self,new_path):
        self.path_label.config( text=f"{new_path}")

    def delete_item_list(self):
        """"Deletes the selected item from the listbox"""
        self.npz_listbox.delete('anchor')

    def deleteAll_listbox(self):
        """"Deletes all items from the listbox"""
        self.npz_listbox.delete(0,'end')

    def read_npz_listbox(self):
        """"Reads all items in the listbox.

       Gets the size of the listbox then reads all the items from the listbox and returns them as a list.

        Args:
             self: An instance of the MainApp class.
        Returns:
           A list containing all the files in the listbox.
        Raises:
           None.
        """       
        list_size=self.npz_listbox.size()
        npztuple =self.npz_listbox.get(0,list_size-1)
        npzlist=list(npztuple)
        return npzlist

    def create_file_list(self,path_npz):
        #Function to convert all the items in the path to a list containing only .npz files
        #OS MAY HAVE ISSUES WITH LINUX AND MAC
        if os.path.exists(path_npz):                #ensure the path exists before attempting to access the directory
            files_list=os.listdir(path_npz)
            if files_list != []:                    #Ensure it is not an empty directory
                npz_list = [file for file in files_list if file.lower().endswith('.npz') and os.path.isfile(os.path.join(path_npz, file))]
                print(npz_list)
                return npz_list 
            else:
                print("empty list")
                self.EmptySource_box(path_npz)
                return []
        else:
            print("path does not exist")
            self.CriticalErrorBox(msg=f"ERROR\nThe folder {path_npz} does not exist.\n")
            return []

    def open_file_dialog(self):
        """"Prompts the user to specify a directory where the .npz files are located. Then saves the absolute path to a label and inserts all
        the .npz files into the listbox.

       Prompts the user to specify a directory where the .npz files are located using a system file box. Then saves the absolute path to a label.
       It then clears the listbox to ensure a clean insert and inserts all the .npz files into the listbox.

        Args:
             self: An instance of the MainApp class.
        Returns:
          None.
        Raises:
           None.
        """    
        path_npz=filedialog.askdirectory(mustexist=True,initialdir= '/',title='Please select a directory')
        self.update_path_label(path_npz)

        #Update the list box
        files_list=self.create_file_list(path_npz)
        files_list.sort()
        # Reverse because insert the array from bottom to top in listbox
        files_list.reverse()

        #delete everything from listbox first to ensure clean insert
        self.deleteAll_listbox()
        #insert all the files into the listbox
        for item in files_list:
            self.npz_listbox.insert('end',item)

    def run_code(self):
        """"Creates a json file from the .npz files in the listbox.
       
       Runs all the necessary functions to create a json file. It starts by verifiying the destination files directory exists in the cwd.
       It then gets the absolute path to the directory containing the .npz files. It gets the list of the .npz file name from the listbox.
       It then reads all the .npz files and creates a json file. It then checks if the JSON file generated is empty and if it is then it deletes
       it.

        Args:
             self: An instance of the MainApp class.
        Returns:
          None.
        Raises:
           None.
        """  
        # Check that the destination folder exists and if it does not then create one
        FileManipulators.verify_destination_exists(self.logger)
        destination_path=FileManipulators.create_destination_file()
        path_npz_str = self.path_label.cget("text")                      #receieves the path where the files are located.
        path_npz=pathlib.Path(str(path_npz_str))
        npz_list=self.read_npz_listbox()                                 #gets the list of npz files from the listbox.
        self.read_files(path_npz,npz_list,destination_path)
        FileManipulators.delete_empty_file(destination_path,self.logger)

if __name__ == "__main__":
    #Creates a logger and the corresponding logfile.
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
    log_file=make_log_file_path()

    create_filehandler_logger(log_file)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    #Runs App
    app=MainApp(logger)
    app.mainloop()
