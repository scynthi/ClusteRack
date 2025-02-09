from modules.ui import AppWindow, UI
from tkinter import Frame
from modules.ui import *

app: AppWindow = AppWindow("800x500")
content : UI.Frame = app.content

render = UI.EmbedRenderer(content, "rack_1", app)

app.mainloop()