import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import Calendar
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db as firebase_db
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import threading
import subprocess
import pyperclip

# Đường dẫn đến tệp firebase-adminsdk.json
FIREBASE_ADMIN_SDK_PATH = "D:/Downloads/khkttoanguoc/khkttoanquoc-firebase-adminsdk-n1m40-4fc83d627b.json"

# Khởi tạo Firebase Realtime Database
cred = credentials.Certificate(FIREBASE_ADMIN_SDK_PATH)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://khkttoanquoc-default-rtdb.asia-southeast1.firebasedatabase.app/'
})
db = firebase_db.reference()

# Thông tin SMTP 
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USERNAME = 'khktthptlocphat@gmail.com'
SMTP_PASSWORD = 'irag deoa hzlf ldse'

# Khai báo biến toàn cục
verification_code = ""
register_window = None 
success_window = None  

def send_verification_email(email, verification_code):
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        
        message = MIMEMultipart()
        message['From'] = SMTP_USERNAME
        message['To'] = email
        message['Subject'] = 'Xác thực tài khoản'
        body = f'Mã xác thực của bạn là: {verification_code}'
        message.attach(MIMEText(body, 'plain'))
        
        server.sendmail(SMTP_USERNAME, email, message.as_string())
        server.quit()

        return True
    except Exception as e:
        print("Error sending verification email:", e)
        return False

def generate_verification_code():
    return str(random.randint(1000, 9999))

def register():
    global verification_code  
    email = email_entry.get()

    # Kiểm tra xem email đã được đăng ký trước đó chưa
    if db.child("users").order_by_child("email").equal_to(email).get():
        messagebox.showwarning("Cảnh báo", "Email đã được đăng ký.")
        return

    # Gửi mã xác thực đến email người dùng
    verification_code = generate_verification_code()  # Gán giá trị cho biến toàn cục
    if send_verification_email(email, verification_code):
        # Hiển thị cửa sổ xác thực
        show_verification_window()
    else:
        messagebox.showerror("Lỗi", "Đã xảy ra lỗi trong quá trình gửi mã xác thực.")

def show_verification_window():
    global register_window
    global verification_entry
    global verification_code

    register_window = tk.Toplevel(root)  
    register_window.title("Xác thực")
    
    # Verification Code Label and Entry
    verification_label = tk.Label(register_window, text="Mã xác thực:")
    verification_label.grid(row=0, column=0, padx=5, pady=5)
    verification_entry = tk.Entry(register_window)
    verification_entry.grid(row=0, column=1, padx=5, pady=5)

    # Verify Button
    verify_button = tk.Button(register_window, text="Xác thực", command=verify_user)
    verify_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    # Resend Button
    resend_button = tk.Button(register_window, text="Gửi lại mã", command=resend_verification)
    resend_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

def resend_verification():
    email = email_entry.get()

    # Kiểm tra xem email đã được đăng ký trước đó chưa
    user_data = db.child("users").order_by_child("email").equal_to(email).get()
    if user_data:
        # Gửi lại mã xác thực đến email người dùng
        global verification_code
        verification_code = generate_verification_code()  # Tạo mã xác thực mới
        if send_verification_email(email, verification_code):
            messagebox.showinfo("Thông báo", "Mã xác thực mới đã được gửi đến email của bạn.")
        else:
            messagebox.showerror("Lỗi", "Đã xảy ra lỗi trong quá trình gửi mã xác thực.")
    else:
        messagebox.showerror("Lỗi", "Email chưa được đăng ký.")

def verify_user():
    global verification_code

    entered_code = verification_entry.get()  # Lấy mã xác thực được nhập vào
    if entered_code == verification_code:
        # Xác thực thành công, tạo tài khoản người dùng
        user_data = {
            'name': name_entry.get(),
            'password': password_entry.get(),
            'email': email_entry.get(),
            'gender': gender_combobox.get(),
            'birth_date': cal.get_date(),
            'verified': True
        }
        db.child("users").push(user_data)
        messagebox.showinfo("Thông báo", "Tài khoản đã được tạo thành công.")
        register_window.destroy()  # Đóng cửa sổ đăng ký
        show_login_success() # Hiển thị cửa sổ thông báo đăng nhập thành công
    else:
        messagebox.showerror("Lỗi", "Mã xác thực không đúng.")

def forgot_password():
    global forgot_password_window
    global email_entry_forgot

    # Tạo cửa sổ nhập email để gửi lại mã xác thực
    forgot_password_window = tk.Toplevel(root)
    forgot_password_window.title("Quên mật khẩu")

    # Email Label and Entry
    email_label_forgot = tk.Label(forgot_password_window, text="Email:")
    email_label_forgot.grid(row=0, column=0, padx=5, pady=5)
    email_entry_forgot = tk.Entry(forgot_password_window)
    email_entry_forgot.grid(row=0, column=1, padx=5, pady=5)

    # Send Verification Code Button
    send_code_button = tk.Button(forgot_password_window, text="Gửi mã xác thực", command=send_verification_code_forgot)
    send_code_button.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

def send_verification_code_forgot():
    email = email_entry_forgot.get()

    # Kiểm tra xem email đã được đăng ký trước đó hay chưa
    user_data = db.child("users").order_by_child("email").equal_to(email).get()
    if user_data:
        # Gửi lại mã xác thực đến email người dùng
        global verification_code_forgot
        verification_code_forgot = generate_verification_code()  # Tạo mã xác thực mới
        if send_verification_email(email, verification_code_forgot):
            messagebox.showinfo("Thông báo", "Mã xác thực mới đã được gửi đến email của bạn.")
            show_verification_password_window()  # Hiển thị cửa sổ nhập mã xác thực và mật khẩu mới
        else:
            messagebox.showerror("Lỗi", "Đã xảy ra lỗi trong quá trình gửi mã xác thực.")
    else:
        messagebox.showerror("Lỗi", "Email chưa được đăng ký.")

def show_verification_password_window():
    global verification_password_window
    global verification_entry_forgot
    global new_password_entry

    verification_password_window = tk.Toplevel(forgot_password_window)
    verification_password_window.title("Nhập mã xác thực và mật khẩu mới")

    # Verification Code Label and Entry
    verification_label = tk.Label(verification_password_window, text="Mã xác thực:")
    verification_label.grid(row=0, column=0, padx=5, pady=5)
    verification_entry_forgot = tk.Entry(verification_password_window)
    verification_entry_forgot.grid(row=0, column=1, padx=5, pady=5)

    # New Password Label and Entry
    new_password_label = tk.Label(verification_password_window, text="Mật khẩu mới:")
    new_password_label.grid(row=1, column=0, padx=5, pady=5)
    new_password_entry = tk.Entry(verification_password_window, show="*")
    new_password_entry.grid(row=1, column=1, padx=5, pady=5)

    # Confirm Button
    confirm_button = tk.Button(verification_password_window, text="Xác nhận", command=confirm_forgot_password)
    confirm_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

def confirm_forgot_password():
    entered_code = verification_entry_forgot.get()
    new_password = new_password_entry.get()

    # Kiểm tra xem mã xác thực có đúng không
    if entered_code == verification_code_forgot:
        email = email_entry_forgot.get()

        # Cập nhật mật khẩu mới vào cơ sở dữ liệu
        user_data = db.child("users").order_by_child("email").equal_to(email).get()
        for user_id, data in user_data.items():
            db.child("users").child(user_id).update({"password": new_password})
        messagebox.showinfo("Thông báo", "Mật khẩu đã được cập nhật thành công.")
        verification_password_window.destroy()
        forgot_password_window.destroy()
    else:
        messagebox.showerror("Lỗi", "Mã xác thực không đúng.")

def show_login_screen():
    # Xóa dữ liệu đã nhập trong các trường
    name_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)
    email_entry.delete(0, tk.END)
    gender_combobox.set('')
    cal.set_date((2022, 1, 1))  # Đặt lại ngày sinh mặc định

    # Hiển thị lại cửa sổ giao diện đăng nhập
    root.deiconify()  # Hiển thị cửa sổ gốc nếu đã bị ẩn

def logout():
    # Đóng cửa sổ hiện tại (cửa sổ thành công)
    success_window.destroy()
    # Hiển thị lại giao diện đăng nhập
    show_login_screen()

def login():
    email = email_entry.get()
    password = password_entry.get()

    # Kiểm tra xem email đã được đăng ký trước đó hay chưa
    user_data = db.child("users").order_by_child("email").equal_to(email).get()
    if user_data:
        # Kiểm tra mật khẩu và các thông tin khác
        for user_id, data in user_data.items():
            if data.get('password') == password and \
               data.get('name') == name_entry.get() and \
               data.get('gender') == gender_combobox.get() and \
               data.get('birth_date') == cal.get_date():
                messagebox.showinfo("Thông báo", "Đăng nhập thành công.")
                show_login_success()  # Truyền user_id vào hàm show_login_success
                return
    messagebox.showerror("Lỗi", "Thông tin đăng nhập không chính xác.")

def show_login_success():
    global success_window
    
    # Tải logo mới
    
    email_to_copy = email_entry.get()
    pyperclip.copy(email_to_copy)
    
    def run_exercise():
        threading.Thread(target=launch_exercise).start()

    def run_game():
        threading.Thread(target=launch_game).start()

    def dash_board():
        threading.Thread(target=launch_dash_board).start()

    def launch_exercise():
        subprocess.run(["python", "D:/Downloads/khktqg/GestureLibrary/GestureGui.py"])

    def launch_game():
        subprocess.run(["python", "D:/Downloads/khktqg/GameLibrary/GameGui.py"])  

    def launch_dash_board():
        subprocess.run(["python", "D:/Downloads/khktqg/DashBoard/UserDashBoard.py"])

    success_window = tk.Toplevel(root)
    success_window.title("Đăng nhập thành công")
    

    welcome_label = tk.Label(success_window, text="Chào mừng! Đăng nhập thành công.")
    welcome_label.pack(pady=5)

    excercise_button = tk.Button(success_window, text="Chọn bài tập", command=run_exercise)
    excercise_button.pack(pady=5)

    Game_button = tk.Button(success_window, text="Chơi trò chơi", command=run_game)
    Game_button.pack(pady=5)

    dash_board_button = tk.Button(success_window, text="Xem điểm số của bạn", command=dash_board)
    dash_board_button.pack(pady=5)

    logout_button = tk.Button(success_window, text="Đăng xuất", command=logout)
    logout_button.pack(pady=5)


root = tk.Tk()
root.title("User Information")

# Name Label and Entry
name_label = tk.Label(root, text="Tên:")
name_label.grid(row=0, column=0, padx=5, pady=5)
name_entry = tk.Entry(root)
name_entry.grid(row=0, column=1, padx=5, pady=5)

# Password Label and Entry
password_label = tk.Label(root, text="Mật khẩu:")
password_label.grid(row=1, column=0, padx=5, pady=5)
password_entry = tk.Entry(root, show="*")
password_entry.grid(row=1, column=1, padx=5, pady=5)

# Email Label and Entry
email_label = tk.Label(root, text="Email:")
email_label.grid(row=2, column=0, padx=5, pady=5)
email_entry = tk.Entry(root)
email_entry.grid(row=2, column=1, padx=5, pady=5)

# Gender Label and Combobox
gender_label = tk.Label(root, text="Giới tính :")
gender_label.grid(row=3, column=0, padx=5, pady=5)
gender_combobox = ttk.Combobox(root, values=["Nam", "Nữ", "Khác"])
gender_combobox.grid(row=3, column=1, padx=5, pady=5)

# Birth Date Label and Calendar
birth_date_label = tk.Label(root, text="Ngày sinh:")
birth_date_label.grid(row=4, column=0, padx=5, pady=5)
cal = Calendar(root)
cal.grid(row=4, column=1, padx=5, pady=5)

# Register Button
register_button = tk.Button(root, text="Đăng ký", command=register)
register_button.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

# Login Button
login_button = tk.Button(root, text="Đăng nhập", command=login)
login_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

# Forgot Password Button
forgot_password_button = tk.Button(root, text="Quên mật khẩu", command=forgot_password)
forgot_password_button.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

logoPath = 'D:/Downloads/khktqg/GuiImage/logo.ico'
root.iconbitmap(logoPath)

root.mainloop()
