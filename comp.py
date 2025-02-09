from customtkinter import *
import os
import matplotlib.axes
from modules.ui import UI, AppWindow
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.figure as figure
from modules.computer import Computer


app: CTk = AppWindow("800x500")
#app.grid_rowconfigure(0, weight=1)
app.grid_columnconfigure(1, weight=1)

frame: CTkFrame = CTkFrame(app)
frame.grid(column=1, row=0)

# pygame_frame: CTkFrame = CTkFrame(app, width=300, height=200)
# pygame_frame.grid(column=0, row=0)

fig: figure.Figure = figure.Figure(figsize=(3, 3))
canvas: FigureCanvasTkAgg = FigureCanvasTkAgg(fig, frame)
ax: matplotlib.axes._axes.Axes = fig.add_subplot()
ax.set_ylim(0, 100)
ax.set_title("CPU Usage")

button: UI.Button = UI.Button(frame, text="Start Monitoring", command=lambda: add_point())
button.grid(column=0, row=0)

canvas.get_tk_widget().grid(column=0, row=1)

pc: Computer = Computer(os.path.normpath(r"./Test folder\cluster0\szamitogep3"))


time_count: list = [0]
usage_list: list = [0]


def add_point() -> None:
    button.configure(command=None)
    ax.clear()
    ax.set_ylim(0, 100)
    ax.set_title("CPU Usage")

    if len(time_count) == 30:
        last_usage: float = usage_list[-1]
        last_time: int = time_count[-1]

        usage_list.clear()
        time_count.clear()

        usage_list.append(last_usage)
        time_count.append(last_time)

    usage: float = pc.calculate_resource_usage()["core_usage_percent"]
    usage_list.append(usage)
    time_count.append(int(time_count[-1]+1))

    ax.plot(time_count, usage_list, color="#00a4bd")
    canvas.draw()
    
    app.after(400, add_point)

app.protocol("WM_DELETE_WINDOW", lambda: os._exit(0))
app.mainloop()