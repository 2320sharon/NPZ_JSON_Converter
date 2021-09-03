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

        label_instructions = tk.Label(self, text="Instructions:\n1. Select the folder where the .npz files are located by using the \"Select npz Folder\" button.\n2. Click the \"Convert\" button to convert the .npx files to .json.\n3. Click \"Open Result\" to see your resulting json file. ")
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
    def Error_box(self,msg):
        """" A system error dialog box that informs the user an recoverable error has occured and the prorgram will quit. 
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
        tk.Tk.__init__(self,className="Npz to JSON converter")
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


        #Create the listbox to hold the files in the directory to read .npz files from
        self.npz_listbox=tk.Listbox(self.list_frame,width=50,yscrollcommand=self.ylist_scroll_bar.set,xscrollcommand=self.xlist_scroll_bar.set,bg=MainApp.background_color,fg="white",highlightbackground="#EA7AF4",selectbackground="#EA7AF4",activestyle=None)

        #Configure the scrollbar to scroll within the list vertically and horizontally
        self.ylist_scroll_bar.config(command=self.npz_listbox.yview)
        self.xlist_scroll_bar.config(command=self.npz_listbox.xview)
        #1. Pack the scrollbar within the listframe
        self.xlist_scroll_bar.pack(side='bottom',fill='x')
        #2. Pack the frame 
        self.list_frame.pack(side='right',padx=10)
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

    def alert_JSON_write(self,write_status,destination_path):
        """"Writes a message to the log file depending on whether a successful write to the json file occured or not.

       If write status is true it writes success message to the log file if at least one .npz file was written to the JSON file
       specified by the destination_path.
       If write status is false it means the .npz file was not written to the JSON file specified by the destination_path.

        Args:
             self: An instance of the MainApp class.
             write_status: Boolean. True=Successful Write   False=Failed Write
             destination_path: pathlib.path location of the file that was written to. 
        Returns:
           None.
        Raises:
            None.
        """
        if write_status:
            self.logger.debug(f"\nSuccessful JSON CREATION\n The file was written to {destination_path}.\n")
        else:
            self.logger.debug(f"\nUnsuccessful JSON CREATION\nThe file was written to {destination_path}.\n")

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
        successful_write=False
        if npz_list == []:
            self.logger.exception("Empty listbox provided")
            self.EmptySource_box(source_path)
        try:
            with open(destination_path,'a') as outfile:
                for entry in npz_list:
                    npz_file_path=source_path.joinpath(entry)
                    print(npz_file_path)
                    filename,file_extension= os.path.splitext(npz_file_path.name)
                    print(filename,file_extension)
                    obj=JSON_npz(npz_file_path, npz_file_path.name);
                    try:
                        obj.check_file()                         #if its a valid npz file then read the file
                        obj.get_user_ID()
                        try:
                            mongo_dict=obj.read_npz()
                            try:
                                json_data=obj.create_json(mongo_dict)
                                outfile.write(json_data)                #write the json data to the json file
                                outfile.write("\n")                     #put a new line character after each json write
                                successful_write=True
                                self.alert_JSON_write(True,destination_path)
                            except UltimateException as strong_error:
                                self.logger.exception(strong_error)
                                self.Error_box("ERROR: Cannot create a JSON file exiting now.")
                        except NPZCorruptException as err:
                            self.logger.exception(err)
                            self.Invalid_npz_box(filename)
                    except IncorrectFileTypeException as npz_file_error:
                        self.logger.exception(npz_file_error)
                        self.Invalid_npz_box(filename)
        except IOError as file_read_err:
            self.logger.error(file_read_err)
            self.Error_box("ERROR cannot read any files from {source_path}}.")

        #At the end check if at least one .npz file was converted to JSON successfully.
        if successful_write:
            self.Success_box(destination_path)
        if not successful_write:
            self.alert_JSON_write(False,destination_path)

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
            self.Error_box(msg=f"ERROR\nThe folder {path_npz} does not exist.\n")
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
