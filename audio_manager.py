from customtkinter import *
from modules.ui import UI, AppWindow
from pygame import mixer
import random


mixer.init()
mixer.set_num_channels(3)

startup_channel: mixer.Channel = mixer.Channel(0)
click_channel: mixer.Channel = mixer.Channel(1)
misc_channel: mixer.Channel = mixer.Channel(2)

small_click_list: list[str] = [
    r"Sounds\small_click1.wav",
    r"Sounds\small_click2.wav",
    r"Sounds\small_click3.wav",
]

startup_sound: mixer.Sound = mixer.Sound(r"Sounds\start_up.wav")
click_sounds: list[mixer.Sound] = [mixer.Sound(sound) for sound in small_click_list]
big_click_sound: mixer.Sound = mixer.Sound(r"Sounds\big_click.wav")

close_computer_sound: mixer.Sound = mixer.Sound(r"Sounds\close_computer.wav")
close_program_sound: mixer.Sound = mixer.Sound(r"Sounds\close_program.wav")
error_sound: mixer.Sound = mixer.Sound(r"Sounds\error.wav")
notification_sound: mixer.Sound = mixer.Sound(r"Sounds\notification.wav")

last_click_sound: mixer.Sound | None = None

class AudioManager:
    def play_startup() -> None: startup_channel.play(startup_sound)
    
    def play_close_computer() -> None: misc_channel.play(close_computer_sound)
    
    def play_close_program() -> None: misc_channel.play(close_program_sound)
    
    def play_error() -> None: misc_channel.play(error_sound)
    
    def play_notification() -> None: misc_channel.play(notification_sound)
    
    def play_big_click() -> None: misc_channel.play(big_click_sound)

    def play_rnd_click() -> None:
        global last_click_sound
        sound: mixer.Sound = random.choice(click_sounds)
        while sound == last_click_sound:
            sound = random.choice(click_sounds)
        last_click_sound = sound
        click_channel.play(sound)
    
    def stop() -> None: mixer.stop()


# Test ui -------
app: AppWindow = AppWindow("800x400")
app.grid_columnconfigure(0, weight=1)
app.grid_rowconfigure([0], weight=1)

center_frame: CTkFrame = CTkFrame(app)
center_frame.grid(column=0, row=0)

UI.Button(center_frame, text="Start", command=AudioManager.play_startup).grid(column=0, row=2)
UI.Button(center_frame, text="Click", command=AudioManager.play_rnd_click).grid(column=1, row=2)
UI.Button(center_frame, text="Stop", command=AudioManager.stop).grid(column=0, row=3)
UI.Button(center_frame, text="Close Computer", command=AudioManager.play_close_computer).grid(column=2, row=2)
UI.Button(center_frame, text="Close Program", command=AudioManager.play_close_program).grid(column=3, row=2)
UI.Button(center_frame, text="Error", command=AudioManager.play_error).grid(column=4, row=2)
UI.Button(center_frame, text="Notification", command=AudioManager.play_notification).grid(column=5, row=2)

app.mainloop()