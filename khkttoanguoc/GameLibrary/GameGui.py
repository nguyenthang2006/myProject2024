import tkinter as tk
from PIL import Image, ImageTk
import pyperclip
import swimmingfish.FishGame as fishgame
import carrace.CarGame as cargame
import runningman.RunningMan as rungame

class GameInterface:
    def __init__(self, master):
        self.master = master
        master.title("Chọn Game nào ")

        self.logoPath = 'D:/Downloads/khktqg/GuiImage/logo.ico'
        master.iconbitmap(self.logoPath)

        # Lấy email từ clipboard
        self.email = pyperclip.paste()

        fish_button_image = "D:/Downloads/khktqg/GuiImage/fish_game_but.jpg"
        car_button_image = "D:/Downloads/khktqg/GuiImage/car_race_but.jpg"
        running_button_image = "D:/Downloads/khktqg/GuiImage/running_man_but.jpg"
        
        # Mở và chuyển đổi hình ảnh sang định dạng mà tkinter có thể nhận diện được
        fish_image = Image.open(fish_button_image)
        photo1 = ImageTk.PhotoImage(fish_image)

        car_image = Image.open(car_button_image)
        photo2 = ImageTk.PhotoImage(car_image)

        running_image = Image.open(running_button_image)
        photo3 = ImageTk.PhotoImage(running_image)

        self.label = tk.Label(master, text="Email của bạn:")
        self.label.pack()

        self.email_label = tk.Label(master, text=self.email)
        self.email_label.pack()

        self.fish_start_button = tk.Button(master, image=photo1, command=self.fish_start_game)
        self.fish_start_button.image = photo1
        self.fish_start_button.pack()

        self.car_start_button = tk.Button(master, image=photo2, command=self.car_start_game)
        self.car_start_button.image = photo2
        self.car_start_button.pack()

        self.running_man_button = tk.Button(master, image=photo3 , command=self.running_man_game)
        self.running_man_button.image = photo3
        self.running_man_button.pack()

    def fish_start_game(self):
        fishgame.run_fish_game(self.email)

    def car_start_game(self):
        cargame.run_car_game(self.email)

    def running_man_game(self):
        rungame.run_runningman_game(self.email)

root = tk.Tk()
my_gui = GameInterface(root)
root.mainloop()
