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
    """"Creates the absoltute path where the log file will be generated

        Uses the current date and time to generate a unique log file.

    Args:
        None.
    Returns:
        A pathlib.Path containing the absolute path to the directory called log_files
        For example:
            For a windows machine:
                C:\programs\npz_to_json_converter\log_files\log_03-Sep-2021_07_47_40.log
    Raises:
        None.
        """
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
    """"Creates the file handler for the logger using the filename

    Args:
        None.
    Returns:
        None.
    Raises:
        None.
        """
    file_handler = logging.FileHandler(file_log_name)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

#Creating the logger here
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')
#-----------------------------------------------------------------------------------------------------------------------

class NPZtoJSON:
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

        Raises:
             IncorrectFileTypeException: Raises exception when the file is not of type NPZ
     """
     filename,file_extension= os.path.splitext(self.file_name)
     if file_extension != ".npz":                                                            #if npz file does not exist throw an exception
        logger.error(f"ERROR \n Invalid file type {file_extension} is not allowed only .npz files! \n File: {self.file_path} is not a valid .npz file. \n End of ERROR")
        raise IncorrectFileTypeException(filename=self.file_name)

    def get_user_ID(self):
     """Returns the user_ID by using the file name.

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

    def getClasses(self, classesArrayGiven):
        """getClasses : gets a list of classses from the user provided npz file and if the npz file does not provide the classes. It either
        prompts the user for a text file containing the names of the classes or uses the classesGivenArray to get the classes from when the user
        previously entered the classes.

        Args:
            classesArrayGiven ([string]): classes given by the user given txt file with the names of the classes

        Raises:
            NPZCorruptException: raised if the keys in the npz file are invalid
            NPZCorruptException: raised if there is an IOError reading the file

        Returns:
            isMissingClasses : returns true is classes were missing from the npz file
            PrevMissingClasses : returns true if classes were missing from a previously read npz file
            classes_array : returns the classes read from the npz or the user provided class.txt
        """
        # PrevMissingClasses: true: previous files had missing classes so use classesArrayGiven
        # PrevMissingClasses: false: no previous files had missing classes you many need to populate classesArrayGiven
        PrevMissingClasses=False
        data = dict()
        try:
           with load(self.file_path, allow_pickle=True) as dat:
               for k in dat.keys():
                   try:
                       data[k] = dat[k]
                   except KeyError as key_error:
                       raise NPZCorruptException()   
               del dat
        except IOError as err:
            logger.error(err)
            raise  NPZCorruptException(msg=err.__str__)

         # isMissingClasses default true, but if classes are missing set to true
        isMissingClasses=False 
        try:
              classes_array = data['classes']
              classes_array=classes_array.tolist()
        except KeyError as keyerr:
              logger.error(keyerr)
    
         # If classesArrayGiven = [] : means no missing classes have been detected before so prompt the user for classes
        if 'classes_array' not in locals() and classesArrayGiven == []:
              from tkinter import Tk
              from tkinter.filedialog import askopenfilename
              Tk().withdraw()
              classfile = askopenfilename(title='Classes are missing. Select a file containing class (label) names', filetypes=[("Pick classes.txt file","*.txt")])
              with open(classfile) as f:
                  classes = f.readlines()
                  classesArrayGiven = [c.strip() for c in classes]
              isMissingClasses=True
              return isMissingClasses,PrevMissingClasses,classesArrayGiven
        elif 'classes_array' not in locals() and classesArrayGiven != []:
              isMissingClasses=True            
              PrevMissingClasses=True
              return isMissingClasses,PrevMissingClasses,classesArrayGiven
    
         #If files were present in the npz file this line will run
        return isMissingClasses,PrevMissingClasses,classes_array

    def read_npz(self,classesArrayGiven):
     """read_npz: Reads the contents of the npz file and transforms it into a dictionary.

        Args:
            self: instance variable

        Returns:
           If successful: returns a dictionary containing data from the npz file and classesGivenArray containing classes provided by the user for any
           npx files that were missing classes.

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

     #classes acyually present in the scene
     #unique finds all the unique items in an array and returns an array containing those items and flattens it into 1d [1,2],[3,4] becomes [1,2,3,4]
     try:
        classes_present_integer = np.unique(data['label'].flatten())
        classes_present_integer=classes_present_integer.tolist()
     except KeyError as key_error:
        raise NPZCorruptException()   #triggers an error message stating this npz file was corrupted is formated incorrectly

     isMissingClasses,PrevMissingClasses,classes_array=self.getClasses(classesArrayGiven)

     #  if classes were missing and no previous files had missing classes update classes given array so any other files with missing classes use
     # classesArrayGiven instead of prompting the user for another classes.txt file
     if (isMissingClasses == True and PrevMissingClasses ==False):
         classesArrayGiven=classes_array

     num_classes = len(classes_array)

     # classes as integers
     classes_integer = np.arange(1,num_classes)
     classes_integer=classes_integer.tolist()


     #classes present as string
     #uses the indexes from the classes_present_integer to generate a string for all the classes present in the image
     classes_present_array = [classes_array[k] for k in classes_present_integer]

     doodle_spatial_density = np.sum(data['doodles'].flatten()>0) / np.prod(np.shape(data['doodles']))

     ##number of input image bands
     num_image_bands = np.ndim(data['image'])

     #does 'settings exist'?
     try:
         settings = data['settings']
     except KeyError as keyerr:
         logger.error(keyerr)
         settings = ['null']

     ##new doodler: pen_width, crf_downsample_value, rf_downsample_value, crf_theta_slider_value, crf_mu_slider_value, gt_prob, n_sigmas
     if len(settings)==6: #pre-scales
          #pen width
          pen_width =  data['settings'][0]

          #CRF_theta
          CRF_theta =  data['settings'][3]

          #CRF_mu
          CRF_mu =  data['settings'][4]

          #CRF_downsample_factor
          CRF_downsample_factor =  data['settings'][1]

          #Classifier_downsample_factor
          Classifier_downsample_factor =  data['settings'][2]

          #prob_of_unary_potential
          prob_of_unary_potential =  data['settings'][5]

     elif len(settings)==7:#post-scales
          #pen width
          pen_width =  data['settings'][0]

          #CRF_theta
          CRF_theta =  data['settings'][3]

          #CRF_mu
          CRF_mu =  data['settings'][4]

          #CRF_downsample_factor
          CRF_downsample_factor =  data['settings'][1]

          #Classifier_downsample_factor
          Classifier_downsample_factor =  data['settings'][2]

          #prob_of_unary_potential
          prob_of_unary_potential =  data['settings'][5]

          #number of scales
          num_of_scales =  data['settings'][6]

     if 'num_of_scales' not in locals():
         num_of_scales='null'

     if 'pen_width' not in locals():
         pen_width='null'
         CRF_theta ='null'
         CRF_mu ='null'
         CRF_downsample_factor ='null'
         prob_of_unary_potential ='null'
         num_of_scales = 'null'
         Classifier_downsample_factor = 'null'

     #name of image and label image that will be generated from the npz files
     if self.user_ID == 'anon':
      image_filename = str(self.file_path).split(os.sep)[-1]+'_image.jpg'.replace(self.file_name.split('.npz')[0].split('_')[-1], 'anon')
      label_image_filename = str(self.file_path).split(os.sep)[-1]+'_label.png'.replace(self.file_name.split('.npz')[0].split('_')[-1], 'anon')
      annotation_image_filename = str(self.file_path).split(os.sep)[-1]+'_annotation.png'.replace(self.file_name.split('.npz')[0].split('_')[-1], 'anon')
     else:
      image_filename = str(self.file_path).split(os.sep)[-1]+'_image.jpg'
      label_image_filename =  str(self.file_path).split(os.sep)[-1]+'_label.png'
      annotation_image_filename =  str(self.file_path).split(os.sep)[-1]+'_annotation.png'

     # except KeyError as keyerr:
     #     logger.error(keyerr)
     #     raise NPZCorruptException(msg="The contents of the NPZ file are invalid.")

     # ####+==================================================================================================
     # ##DB's version of this code that also writes out the images, labels and annotation labesl to files
     # write_images = True
     # if write_images:
     #    from skimage import io
     #    try:
     #        os.mkdir('destination_images')
     #    except:
     #        pass
     #    try:
     #        os.mkdir('destination_images'+os.sep+'image_files')
     #        os.mkdir('destination_images'+os.sep+'label_files')
     #        os.mkdir('destination_images'+os.sep+'annotation_files')
     #    except:
     #        pass
     #
     #    print('destination_images'+os.sep+'image_files'+os.sep+image_filename)
     #    io.imsave('destination_images'+os.sep+'image_files'+os.sep+image_filename,
     #            data['image'].astype('uint8').squeeze(), quality=100, chroma_subsampling=False)
     #    io.imsave('destination_images'+os.sep+'label_files'+os.sep+label_image_filename,
     #            np.argmax(data['label'].astype('uint8'),-1).squeeze(),  compression=0)
     #    io.imsave('destination_images'+os.sep+'annotation_files'+os.sep+annotation_image_filename,
     #            data['doodles'].astype('uint8').squeeze(), compression=0)
     # ####+==================================================================================================
     # ####+==================================================================================================
     # ####+==================================================================================================

     ## make lists to construct a dictionary (there's probably a better way)
     variables = [image_filename, label_image_filename, annotation_image_filename,
                 self.user_ID, classes_array, num_classes, classes_integer,
                 classes_present_integer, classes_present_array,
                 pen_width, CRF_theta, CRF_mu, CRF_downsample_factor,
                 Classifier_downsample_factor, prob_of_unary_potential,
                 doodle_spatial_density, num_image_bands, num_of_scales] # added num_of_scales

     variable_names = ['image_filename', 'label_image_filename', 'annotation_image_filename',
                 'user_ID', 'classes_array', 'num_classes', 'classes_integer',
                 'classes_present_integer', 'classes_present_array',
                 'pen_width', 'CRF_theta', 'CRF_mu', 'CRF_downsample_factor',
                 'Classifier_downsample_factor', 'prob_of_unary_potential',
                 'doodle_spatial_density', 'num_of_scales'] # added num_of_scales

     info_for_mongo = dict()
     for n,v in zip(variable_names,variables):
         info_for_mongo[n] = v

     logger.info(f"\nMongo Dict: {info_for_mongo}\nFile:{self.file_name}\n")
     return classesArrayGiven,info_for_mongo

    def create_json(self,mong_dict):
        """"Creates a json file using the mongo dictionary provided by mongo_dict.

        Args:
           self: instance variable
           mongo_dict: A dictionary created from the npz file.
        Returns:

        Raises:
            TypeError: Cannot serialize the dictionary into JSON
            """
        try:
            mongo_json=json.dumps(mong_dict)
        except TypeError as err:
            logger.error(f"\nUnable to serialize the object\n {err}")
            raise UltimateException(err)
        return mongo_json
