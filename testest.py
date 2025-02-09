import tkinter as tk
from modules.ui import UI, AppWindow
from modules.renderer.main import SoftwareRender

# Tkinter UI
class App(AppWindow):
    def __init__(self):
        super().__init__()

        self.frame1 = tk.Frame(self.content, width=300, height=200, bg="black")
        self.frame1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.frame2 = tk.Frame(self.content, width=300, height=200, bg="black")
        self.frame2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.renderer1 = UI.EmbedRenderer(self.frame1, "rack_1", self).get_renderer()
        self.renderer2 = UI.EmbedRenderer(self.frame2, "rack_2", self).get_renderer()


if __name__ == "__main__":
    app = App()
    app.mainloop()
