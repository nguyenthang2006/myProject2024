import tkinter as tk
from tkinter import ttk
import firebase_admin
from firebase_admin import credentials, db as firebase_db
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pyperclip

# Khởi tạo Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("D:/Downloads/khktqg/khktqg-b3fa7-firebase-adminsdk-tml3u-0aeb1d5f8a.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://khktqg-b3fa7-default-rtdb.asia-southeast1.firebasedatabase.app/'
    })

# Hàm lấy dữ liệu từ Firebase cho mỗi loại trò chơi
def get_scores(game_type, email):
    db = firebase_db.reference()
    user_data = db.child("users").order_by_child("email").equal_to(email).get()
    scores_with_time = []
    for user_id, data in user_data.items():
        user_scores = db.child(f"users/{user_id}/{game_type}").get()
        if user_scores:
            for score_key, score_data in user_scores.items():
                scores_with_time.append((score_data["timestamp"], score_data["score"]))
    return scores_with_time

# Hàm vẽ biểu đồ cho từng loại trò chơi
def plot_game_scores(game_type, email, ax, color, time_unit):
    scores_with_time = get_scores(game_type, email)
    if scores_with_time:
        scores_with_time.sort(key=lambda x: x[0])
        timestamps, scores = zip(*scores_with_time)
        timestamps = [datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M") for ts in timestamps]

        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        ax.plot(timestamps, scores, color=color)
        ax.set_title(f"{game_type.capitalize()} Scores Over Time")
        ax.set_xlabel("Time")
        ax.set_ylabel("Score")

# Hàm vẽ cả ba biểu đồ
def plot_all_scores(email):
    fig, axs = plt.subplots(3, 1, figsize=(8, 6), sharex=False)

    colors = ['blue', 'green', 'red']  # Màu của từng đường

    for i, (game_type, color) in enumerate(zip(["swimming_fish", "running_man", "car_game"], colors)):
        plot_game_scores(game_type, email, axs[i], color, "auto")  # Sửa đổi ở đây

    plt.tight_layout()
    plt.show()

# Tạo cửa sổ giao diện
root = tk.Tk()
root.title("Plot All Game Scores")

# Ẩn cửa sổ giao diện chính
root.withdraw()

# Lấy email từ clipboard và mở dashboard tự động
email = pyperclip.paste()
plot_all_scores(email)

root.mainloop()
