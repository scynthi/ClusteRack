from pygame import mixer
import random
from colorama import Fore, Style, Back, init
init(autoreset=True)


small_click_list: list[str] = [
    r"Assets\Sounds\small_click1.wav",
    r"Assets\Sounds\small_click2.wav",
    r"Assets\Sounds\small_click3.wav",
]


class AudioManager:
    def __init__(self) -> None:

        self.initialized : bool = True

        try:
            mixer.set_num_channels(3)
        except:
            try:
                mixer.init()
                mixer.set_num_channels(3)
            except:
                print(f"{Fore.BLACK + Back.RED}Error while initializing AudioManager. Audio will be disabled for stabilazition purposes.")
                self.initialized = False
                return

        self.startup_channel: mixer.Channel = mixer.Channel(0)
        self.click_channel: mixer.Channel = mixer.Channel(1)
        self.misc_channel: mixer.Channel = mixer.Channel(2)

        self.startup_sound: mixer.Sound = mixer.Sound(r"Assets\Sounds\start_up.wav")
        self.click_sounds: list[mixer.Sound] = [mixer.Sound(sound) for sound in small_click_list]
        self.big_click_sound: mixer.Sound = mixer.Sound(r"Assets\Sounds\big_click.wav")

        self.close_computer_sound: mixer.Sound = mixer.Sound(r"Assets\Sounds\close_computer.wav")
        self.close_program_sound: mixer.Sound = mixer.Sound(r"Assets\Sounds\close_program.wav")
        self.error_sound: mixer.Sound = mixer.Sound(r"Assets\Sounds\error.wav")
        self.notification_sound: mixer.Sound = mixer.Sound(r"Assets\Sounds\notification.wav")
        self.accept_sound: mixer.Sound = mixer.Sound(r"Assets\Sounds\accept.wav")

        self.last_click_sound: mixer.Sound | None = None

    def play_startup(self) -> None:
        if not self.initialized: return

        self.startup_channel.play(self.startup_sound)

    def play_accept(self) -> None:
        if not self.initialized: return

        self.misc_channel.play(self.accept_sound)
    
    def play_close_computer(self) -> None:
        if not self.initialized: return

        self.misc_channel.play(self.close_computer_sound)
    
    def play_close_program(self) -> None:
        if not self.initialized: return

        self.misc_channel.play(self.close_program_sound)
    
    def play_error(self) -> None:
        if not self.initialized: return

        self.misc_channel.play(self.error_sound)
    
    def play_notification(self) -> None: 
        if not self.initialized: return

        self.misc_channel.play(self.notification_sound)
    
    def play_big_click(self) -> None:
        if not self.initialized: return

        self.misc_channel.play(self.big_click_sound)

    def play_rnd_click(self) -> None:
        if not self.initialized: return

        sound: mixer.Sound = random.choice(self.click_sounds)
        while sound == self.last_click_sound:
            sound = random.choice(self.click_sounds)

        self.last_click_sound = sound
        self.click_channel.play(sound)
    
    def stop(self) -> None:
        if not self.initialized: return
        
        mixer.stop()