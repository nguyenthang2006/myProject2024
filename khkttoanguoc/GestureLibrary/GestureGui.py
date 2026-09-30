import tkinter as tk
from PIL import Image, ImageTk
from tkinter import messagebox
import sys

sys.path.append("D:/Downloads/khktqg/GestureLibrary/hand_lib")
sys.path.append("D:/Downloads/khktqg/GestureLibrary/shoulder_lib")
sys.path.append("D:/Downloads/khktqg/GestureLibrary/neck_lib")
sys.path.append("D:/Downloads/khktqg/GestureLibrary/spinal_lib")

try:
    from shoulder_lib.ShoulderRecognition import ShoulderGestureRecognition
    from hand_lib.HandRecognition import HandGestureRecognition
    from neck_lib.NeckRecognition import NeckGestureController
    from spinal_lib.SpinalRecognition import SpinalGestureRecognition
except ImportError as e:
    messagebox.showerror("Lỗi", "Không thể import một số module từ GestureLibrary.")
    exit()

class KHKTAPP:
    def __init__(self, master):
        self.master = master
        self.master.title("Chọn bài tập ")

        # Định nghĩa đường dẫn đến hình ảnh cho các nút
        image_path1 = "D:/Downloads/khktqg/GuiImage/neck_but_img.jpg"
        image_path2 = "D:/Downloads/khktqg/GuiImage/hand_but_img.jpg"
        image_path3 = "D:/Downloads/khktqg/GuiImage/shoulder_but_img.jpg"
        image_path4 = "D:/Downloads/khktqg/GuiImage/spinal_but_img.jpg"

        # Mở và chuyển đổi hình ảnh sang định dạng mà tkinter có thể nhận diện được
        image1 = Image.open(image_path1)
        photo1 = ImageTk.PhotoImage(image1)

        image2 = Image.open(image_path2)
        photo2 = ImageTk.PhotoImage(image2)

        image3 = Image.open(image_path3)
        photo3 = ImageTk.PhotoImage(image3)

        image4 = Image.open(image_path4)
        photo4 = ImageTk.PhotoImage(image4)

        # Tạo và đặt nút 1 với hình ảnh
        self.button1 = tk.Button(master, image=photo1, command=self.ShoulderExcercise)
        self.button1.image = photo1  # Giữ tham chiếu để hình ảnh không bị hủy
        self.button1.pack(pady=10)

        # Tạo và đặt nút 2 với hình ảnh
        self.button2 = tk.Button(master, image=photo2, command=self.HandExcercise)
        self.button2.image = photo2  # Giữ tham chiếu để hình ảnh không bị hủy
        self.button2.pack(pady=10)

        # Tạo và đặt nút 3 với hình ảnh
        self.button3 = tk.Button(master, image=photo3, command=self.NeckExcercise)
        self.button3.image = photo3  # Giữ tham chiếu để hình ảnh không bị hủy
        self.button3.pack(pady=10)

        # Tạo và đặt nút 4 với hình ảnh
        self.button4 = tk.Button(master, image=photo4, command=self.SpinalExcercise)
        self.button4.image = photo4  # Giữ tham chiếu để hình ảnh không bị hủy
        self.button4.pack(pady=10)

    def set_logo(self, image_path):
        try:
            image = Image.open(image_path)
            logo = ImageTk.PhotoImage(image)
            self.master.iconphoto(True, logo)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể đặt logo: {e}")

    def ShoulderExcercise(self):
        try:
            shoulder_controller = ShoulderGestureRecognition()
            shoulder_controller.shoulder_start_webcam()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi thực hiện Excercise vai: {e}")

    def HandExcercise(self):
        try:
            hand_controller = HandGestureRecognition()
            hand_controller.hand_start_webcam()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi thực hiện Excercise tay: {e}")

    def NeckExcercise(self):
        try:
            neck_controller = NeckGestureController()
            neck_controller.neck_start_webcam()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi thực hiện Excercise cổ: {e}")

    def SpinalExcercise(self):
        try:
            spinal_controller = SpinalGestureRecognition()
            spinal_controller.spinal_start_webcam()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi khi thực hiện Excercise cột sống: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = KHKTAPP(root)

    # Đường dẫn đến ảnh logo của bạn
    logo_path = "D:/Downloads/khktqg/GuiImage/logo.ico"
    app.set_logo(logo_path)

    root.mainloop()
