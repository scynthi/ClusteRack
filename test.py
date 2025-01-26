from customtkinter import *
import os
from modules.ui import UI
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.figure
import numpy as np

set_appearance_mode("light")

app : CTk = CTk()
app.title("ClusteRack")
app.geometry("800x600")
app.iconbitmap(os.path.join("images", "logo.ico"))
app.resizable(True, True)
# app.grid_rowconfigure([0,1], weight=1)
# app.grid_columnconfigure(0, weight=1)

x_list = []
y_list = []

fig : matplotlib.figure.Figure = matplotlib.figure.Figure(figsize=(3, 3))
ax = fig.add_subplot()
ax.set_ylim(0, 10)
ax.set_title("CPU Usage")
canvas = FigureCanvasTkAgg(fig, app)
canvas.get_tk_widget().grid(column=1, row=2)

UI.Button(app, text="Yooo", command=lambda: add_point()).grid(column=0, row=0)
UI.Label(app, text="Teststts").grid(column=0, row=1)

def add_point() -> None:
    ax.clear()
    ax.set_ylim(0, 10)
    ax.set_title("CPU Usage")

    if len(x_list) == 0:
        x_list.append(1)
    else:
        x_list.append(x_list[-1]+1)
    
    y_list.append(np.random.randint(1, 10))

    if len(y_list) == 100:
        last_y_item = y_list[-1]
        last_x_item = x_list[-1]

        y_list.clear()
        x_list.clear()

        x_list.append(last_x_item)
        y_list.append(last_y_item)

    ax.plot(x_list, y_list, color="#00a4bd")
    canvas.draw()

app.mainloop()