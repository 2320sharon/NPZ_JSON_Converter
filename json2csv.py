
import pandas as pd
import json
from tkinter import Tk
from tkinter.filedialog import askopenfilename


Tk().withdraw()
json_file = askopenfilename(title='Select a json file', filetypes=[("Pick json file","*.json")])

df = pd.read_json (json_file)
df.to_csv (json_file.replace('.json','.csv'), index = None)
