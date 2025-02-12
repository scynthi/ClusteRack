from modules.ui import AppWindow, UI
from modules.ui import *

app = AppWindow()
app.after(1000, UI.SubWindow)
app.mainloop()