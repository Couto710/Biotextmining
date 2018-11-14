import re
import string
import os
import json
import subprocess
from collections import Counter

for filename in os.listdir("./c04-group/"):

	print filename.split('.')[0]