import os
from src.common import utils
from src.modules.interfaces import Module
from src.modules import *

tzid = "America/New_York" # change this to reflect what time zone your gradescope uses
TIMEZONE_OFFSET = 0 # this is the difference between your timezone and the gradescope submission page timezone (i believe gradescope shows what the institution chooses but im not too sure)

# Compile assignments into a list
assignments = {}
modules = [
    Gradescope()
]
for module in modules:
    module.run(assignments)

# Save the list to a json file to import later
utils.save_data('assignments', assignments)

# cleans out anything older that 180 days to prevent huge files
utils.old_cleaner()

# converts the json to an ical file and saves it
utils.json_to_ics(tzid, time_offset=TIMEZONE_OFFSET)

