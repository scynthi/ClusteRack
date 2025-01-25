from customtkinter import *
import os
from modules.ui import UI

app : CTk = CTk()
app.title("ClusteRack")
app.geometry("800x400")
app.iconbitmap(os.path.join("images", "logo.ico"))
app.resizable(True, True)
# app.grid_rowconfigure([0,1], weight=1)
# app.grid_columnconfigure(0, weight=1)


UI.Button(app, text="Yooo", command=lambda: print("yooo")).grid(column=0, row=0)
UI.Label(app, text="Teststts").grid(column=0, row=1)


app.mainloop()