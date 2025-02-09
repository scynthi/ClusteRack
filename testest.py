import tkinter as tk
from modules.ui import UI, AppWindow
from modules.renderer.main import SoftwareRender
from PIL import Image, ImageTk

# Tkinter UI
class App(AppWindow):
    def __init__(self):
        super().__init__()

        self.frame1 = tk.Frame(self.content, width=300, height=200, bg="black")
        self.frame1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.frame2 = tk.Frame(self.content, width=300, height=200, bg="black")
        self.frame2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.image = ImageTk.PhotoImage(Image.open("./Assets/Images/rack.png").resize((80, 200), Image.NEAREST))
        self.button = tk.Button(self.content, text="", image=self.image)
        self.button.grid(row=1, column=0)

        self.renderer1 = UI.EmbedRenderer(self.frame1, "rack_8", 12, self).get_renderer()
        self.renderer2 = UI.EmbedRenderer(self.frame2, "computer", 10, self).get_renderer()


if __name__ == "__main__":
    app = App()
    app.mainloop()
