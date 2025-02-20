import sys
import shutil
from colorama import init
import colorama

colorama.init()

def update_prompt(prompt, user_input, cursor_pos):
    # Get dynamic terminal width
    cols = shutil.get_terminal_size().columns
    
    # Combine prompt and input
    full_text = f"{prompt}>{user_input}"
    
    # Calculate how many lines the text occupies
    lines_needed = (len(full_text) // cols) + 1
    
    # Move up and clear all lines used previously
    sys.stdout.write("\r")
    for _ in range(lines_needed):
        sys.stdout.write("\033[K")  # Clear the current line
        sys.stdout.write("\033[F")  # Move up a line
    
    # Move back down to the original line position
    for _ in range(lines_needed):
        sys.stdout.write("\033[E")  # Move down a line
    
    # Move to the start of the line
    sys.stdout.write("\r")
    
    # Redraw the prompt and input
    sys.stdout.write(full_text)
    
    # Clear to the end of the line (in case of leftovers)
    sys.stdout.write("\033[K")
    
    # Calculate the cursor's position in the combined text
    cursor_absolute_pos = len(prompt) + 1 + cursor_pos
    
    # Calculate how many lines the cursor should be down from the start
    cursor_line = cursor_absolute_pos // cols
    cursor_col = cursor_absolute_pos % cols
    
    # Move up to the correct line
    for _ in range(lines_needed - cursor_line - 1):
        sys.stdout.write("\033[F")  # Move up a line
    
    # Move to the correct column
    sys.stdout.write(f"\r\033[{cursor_col}C")
    
    sys.stdout.flush()

# Example usage:
prompt = "Command"
user_input = "This is a very long input that will definitely wrap to the next line in the terminal. This is a very long input that will definitely wrap to the next line in the terminal."
cursor_pos = len(user_input)  # Cursor at the end

update_prompt(prompt, user_input, cursor_pos)