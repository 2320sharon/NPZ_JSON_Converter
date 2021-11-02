
import pandas as pd
import json
from tkinter import Tk
from tkinter.filedialog import askopenfilename


Tk().withdraw()
json_file = askopenfilename(title='Select a json file', filetypes=[("Pick json file","*.json")])


with open(json_file) as f:
    json_txt = f.readlines()

npzdatadict = {}

fields = ['image_filename',
'label_image_filename',
'annotation_image_filename',
'user_ID',
'classes_array',
'num_classes',
'classes_integer',
'classes_present_integer',
'classes_present_array',
'pen_width',
'CRF_theta',
'CRF_mu',
'CRF_downsample_factor',
'Classifier_downsample_factor',
'prob_of_unary_potential',
'doodle_spatial_density',
'num_of_scales']

# make fields
for f in fields:
    npzdatadict[f]=[]

# update all fields
for entry in json_txt:
    wjdata = json.loads(entry)
    for f in fields:
        npzdatadict[f].append(wjdata[f])

#convert to pandas dataframe, then to csv
meta=pd.DataFrame.from_dict(npzdatadict)
meta_fles = meta.image_filename.values
meta.to_csv(json_file.replace('.json','.csv'))
