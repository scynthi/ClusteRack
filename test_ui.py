from modules.ui import AppWindow, UI
from tkinter import Frame
from modules.ui_obj_renderer import EmbedRendererWindow

app: AppWindow = AppWindow("800x500")
content : UI.Frame = app.content

test_frame : Frame = Frame(content)
test_frame.grid(row=0, column=0)

software_render: EmbedRendererWindow = EmbedRendererWindow(test_frame, "rack_2").pygame_frame.grid(row=0, column=0)


app.mainloop()