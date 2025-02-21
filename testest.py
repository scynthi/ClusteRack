import os
import time

# Set a unique title
title = "Custom Command Interpreter"

# Start the new cmd window with the unique title
os.system(f'start cmd /c "title {title} && py interp_test.py"')