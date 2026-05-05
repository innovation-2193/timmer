import tkinter as tk
from tkinter import messagebox
import time
import threading
import platform
import os

class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("โปรแกรมจับเวลา")
        self.root.geometry("300x250")
        self.root.resizable(False, False)
        
        self.running = False
        self.is_alarming = False # ตัวแปรเช็คว่าเสียงกำลังเตือนอยู่หรือไม่
        
        tk.Label(root, text="⏳ ตั้งเวลา", font=("Helvetica", 16, "bold")).pack(pady=10)
        
        frame = tk.Frame(root)
        frame.pack()
        
        self.m_var = tk.StringVar(value="0")
        tk.Entry(frame, textvariable=self.m_var, width=3, font=("Helvetica", 20), justify='center').pack(side=tk.LEFT, padx=5)
        tk.Label(frame, text="นาที", font=("Helvetica", 12)).pack(side=tk.LEFT)
        
        self.s_var = tk.StringVar(value="10")
        tk.Entry(frame, textvariable=self.s_var, width=3, font=("Helvetica", 20), justify='center').pack(side=tk.LEFT, padx=5)
        tk.Label(frame, text="วินาที", font=("Helvetica", 12)).pack(side=tk.LEFT)
        
        self.time_label = tk.Label(root, text="00:10", font=("Helvetica", 40, "bold"), fg="blue")
        self.time_label.pack(pady=15)
        
        btn_frame = tk.Frame(root)
        btn_frame.pack()
        tk.Button(btn_frame, text="เริ่ม", command=self.start_timer, width=8, bg="#28a745", fg="white", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="หยุด/รีเซ็ต", command=self.reset_timer, width=8, bg="#dc3545", fg="white", font=("Helvetica", 10, "bold")).pack(side=tk.LEFT, padx=5)

    def update_display(self):
        try:
            m = int(self.m_var.get() or 0)
            s = int(self.s_var.get() or 0)
            self.time_label.config(text=f"{m:02d}:{s:02d}")
        except ValueError:
            pass

    def start_timer(self):
        if not self.running:
            try:
                m = int(self.m_var.get() or 0)
                s = int(self.s_var.get() or 0)
                total_seconds = m * 60 + s
                
                if total_seconds > 0:
                    self.running = True
                    threading.Thread(target=self.countdown, args=(total_seconds,), daemon=True).start()
            except ValueError:
                messagebox.showerror("ข้อผิดพลาด", "กรุณาใส่เป็นตัวเลขเท่านั้น")

    def countdown(self, total_seconds):
        while total_seconds > 0 and self.running:
            m, s = divmod(total_seconds, 60)
            self.time_label.config(text=f"{m:02d}:{s:02d}")
            time.sleep(1)
            total_seconds -= 1
        
        if self.running:
            self.time_label.config(text="00:00")
            self.running = False
            
            # เมื่อเวลาเหลือ 0 ให้เริ่มวนลูปเสียงเตือนใน Thread ใหม่
            self.is_alarming = True
            threading.Thread(target=self.play_sound_loop, daemon=True).start()
            
            # โชว์หน้าต่างเด้งให้กดหยุด (โปรแกรมจะหยุดรอให้คนกด OK ตรงนี้)
            messagebox.showwarning("หมดเวลา", "⏰ หมดเวลาแล้ว!\n\nกดปุ่ม OK เพื่อปิดเสียงเตือน")
            
            # เมื่อผู้ใช้กด OK จะรันคำสั่งด้านล่างนี้เพื่อปิดเสียง
            self.is_alarming = False
            self.update_display()

    def reset_timer(self):
        self.running = False
        self.is_alarming = False # หยุดเสียงด้วยถ้ากดรีเซ็ตตอนดังอยู่
        self.update_display()

    def play_sound_loop(self):
        # ฟังก์ชันนี้จะเล่นเสียงวนลูปไปเรื่อยๆ จนกว่า self.is_alarming จะเป็น False (กด OK)
        sys_name = platform.system()
        while self.is_alarming:
            try:
                if sys_name == "Windows":
                    import winsound
                    winsound.Beep(1000, 500) # ร้องนาน 0.5 วิ
                    time.sleep(0.1) # เว้นช่วง 0.1 วิ
                elif sys_name == "Darwin":  # สำหรับ macOS
                    os.system("afplay /System/Library/Sounds/Glass.aiff")
                    time.sleep(0.5)
                else:
                    print('\a')
                    time.sleep(1)
            except Exception:
                time.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    app = TimerApp(root)
    app.m_var.trace_add("write", lambda *args: app.update_display())
    app.s_var.trace_add("write", lambda *args: app.update_display())
    root.mainloop()