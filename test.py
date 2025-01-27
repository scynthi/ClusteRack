from customtkinter import *
import os
import matplotlib.axes
from modules.ui import UI, AppWindow
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.figure
import numpy as np
from computer import Computer


app : CTk = AppWindow("400x500")
app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(0, weight=1)

frame : CTkFrame = CTkFrame(app)
frame.grid(column=0, row=0)

UI.Button(frame, text="Start", command=lambda: add_point()).grid(column=0, row=0)


fig : matplotlib.figure.Figure = matplotlib.figure.Figure(figsize=(3, 3))
canvas : FigureCanvasTkAgg = FigureCanvasTkAgg(fig, frame)
canvas.get_tk_widget().grid(column=0, row=1)

ax : matplotlib.axes._axes.Axes = fig.add_subplot()
ax.set_ylim(0, 10)
ax.set_title("CPU Usage")


pc : Computer = Computer(os.path.normpath(r"C:\GitHub\ClusteRack\Test folder\cluster0\szamitogep2"))


time_count : list = [0]
usage_list : list = [0]


def add_point() -> None:
    ax.clear()
    ax.set_ylim(0, 10)
    ax.set_title("CPU Usage")

    if len(time_count) == 30:
        last_usage : float = usage_list[-1]
        last_time : int = time_count[-1]

        usage_list.clear()
        time_count.clear()

        usage_list.append(last_usage)
        time_count.append(last_time)

    usage : float = pc.calculate_resource_usage()["cpu_usage_percent"]
    usage_list.append(usage)
    time_count.append(time_count[-1]+1)

    ax.plot(time_count, usage_list, color="#00a4bd")
    canvas.draw()
    
    app.after(400, add_point)



app.mainloop()