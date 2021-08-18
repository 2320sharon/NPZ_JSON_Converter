import os as os                   
import numpy as np
from numpy.lib.npyio import load
import json
import pathlib
from exceptions import *
import logging
from datetime import datetime
from pathlib import Path     #necessary for reading the npz files and writing the final json file
import os

#                                               LOG CREATION FUNCTIONS
#-----------------------------------------------------------------------------------------------------------------------
def make_log_file_path():
      timestampStr = datetime.now().strftime("%d-%b-%Y_%H_%M_%S")
      file_name="log_"+timestampStr+".log"
      dir_path = Path.cwd().joinpath('log_files')
      print(f"\nLog files location: {dir_path}")
      if not os.path.exists(dir_path):
          print(f"\nLocation does not exist: {dir_path}.\n Creating it now. \n")
          os.mkdir(dir_path)
      log_path=dir_path.joinpath(file_name)
      print(f"\nLog: {log_path} has been created. \n")
      return log_path

def create_filehandler_logger(file_log_name): 
      file_handler = logging.FileHandler(file_log_name)
      file_handler.setFormatter(formatter)
      logger.addHandler(file_handler)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
#-----------------------------------------------------------------------------------------------------------------------

class JSON_npz:
    """A class to hold all data associated with an npz file and contains methods to convert from npz to json.
    """
    def __init__(self,file_path,file_name,user_ID="",mongo_data=""):
        self.file_path=file_path
        self.file_name=file_name
        self.user_ID = user_ID
        self.mongo_data = mongo_data
        logger.info(f"A new JSON_npz object was created for file: {self.file_path}")

    def check_file(self):
     """check_file(self): checks if the file given is an .npz file or not. 
        
        Returns nothing

        Args:
            self: instance variable

        Raises IncorrectFileTypeException
        Raises exception when the file is not of type NPZ
     """
     filename,file_extension= os.path.splitext(self.file_name)
     if file_extension != ".npz":                                                            #if npz file does not exist throw an exception
        logger.error(f"ERROR \n Invalid file type {file_extension} is not allowed only .npz files! \n File: {self.file_path} is not a valid .npz file. \n End of ERROR")
        raise IncorrectFileTypeException(filename=self.file_name)
    
    def get_user_ID(self):
     """Returns the user_ID by using the file name.

        Returns the user_ID by using the file name from the self method.

        Args:
            self: instance variable

        Returns:
          string: The user id
     """
     # userID - this would work as long as the user ID doesnt contain an underscore
     self.user_ID = self.file_name.split('.npz')[0].split('_')[-1]

     ## Treat users without an ID as anonymous
     if self.user_ID.startswith('Enter'):
        self.user_ID = 'anon'
     logger.info(f"\n USER ID: {self.user_ID} for file: {self.file_name}")
     return self.user_ID
    
    def read_npz(self):
     """read_npz: Reads the contents of the npz file and transforms it into a dictionary.

        Args:
            self: instance variable

        Returns:
           If successful: returns a dictionary containing data from the npz file.

     Raises:
            NPZCorruptException: An error occurred while reading the npz file.

            IOError: An error occured while trying to load the npz file as a pickle
     """
     self.get_user_ID()    #call the get_user_ID() to calculate the userID
     data = dict()
     # load file
     try:
        with load(self.file_path, allow_pickle=True) as dat:
            #create a dictionary of variables
            #automatically converted the keys in the npz file, dat to keys in the dictionary, data, then assigns the arrays to data
            for k in dat.keys():
                try:
                    data[k] = dat[k]
                except KeyError as key_error:
                    raise NPZCorruptException()   #triggers an error message stating this npz file was corrupted is formated incorrectly
            del dat
     except IOError as err:
         logger.error(err)
         raise  NPZCorruptException(msg=err.__str__)

     #keys of the new dictionary    

     #array of class names
     try:
      classes_array = data['classes']
      classes_array=classes_array.tolist()
      num_classes = len(classes_array)
 
      # classes as integers
      classes_integer = np.arange(1,num_classes)
      classes_integer=classes_integer.tolist()
 
      #classes acyually present in the scene
      #unique finds all the unique items in an array and returns an array containing those items and flattens it into 1d [1,2],[3,4] becomes [1,2,3,4]
      classes_present_integer = np.unique(data['label'].flatten())
      classes_present_integer=classes_present_integer.tolist()
 
 
      #classes present as string
      #uses the indexes from the classes_present_integer to generate a string for all the classes present in the image
      classes_present_array = [data['classes'][k] for k in classes_present_integer]
 
      #pen width
      pen_width =  data['settings'][0]
 
      #CRF_theta
      CRF_theta =  data['settings'][1]
 
      #CRF_mu
      CRF_mu =  data['settings'][2]
 
      #CRF_downsample_factor
      CRF_downsample_factor =  data['settings'][3]
  
      #Classifier_downsample_factor
      Classifier_downsample_factor =  data['settings'][4]
  
      #prob_of_unary_potential
      prob_of_unary_potential =  data['settings'][5]
      doodle_spatial_density = np.sum(data['doodles'].flatten()>0) / np.prod(np.shape(data['doodles']))
  
      ##number of input image bands
      num_image_bands = np.ndim(data['image'])
     except KeyError as keyerr:
         logger.error(keyerr)
         raise NPZCorruptException(msg="The contents of the NPZ file are invalid.")

     ## make lists to construct a dictionary (there's probably a better way)
     variables = [self.user_ID, classes_array, num_classes, classes_integer,
                 classes_present_integer, classes_present_array, 
                 pen_width, CRF_theta, CRF_mu, CRF_downsample_factor,
                 Classifier_downsample_factor, prob_of_unary_potential,
                 doodle_spatial_density, num_image_bands]
                 
     variable_names = ['user_ID', 'classes_array', 'num_classes', 'classes_integer',
                 'classes_present_integer', 'classes_present_array', 
                 'pen_width', 'CRF_theta', 'CRF_mu', 'CRF_downsample_factor',
                 'Classifier_downsample_factor', 'prob_of_unary_potential',
                 'doodle_spatial_density']
                 
     info_for_mongo = dict()
     for n,v in zip(variable_names,variables):
         info_for_mongo[n] = v
 
     logger.info(f"\nMongo Dict: {info_for_mongo}\nFile:{self.file_name}\n")
     return info_for_mongo
 
    def create_json(self,mong_dict):
        try:
            mongo_json=json.dumps(mong_dict)
        except TypeError as err:
            logger.error(f"\nUnable to serialize the object\n {err}")
            raise UltimateException(err)
        return mongo_json