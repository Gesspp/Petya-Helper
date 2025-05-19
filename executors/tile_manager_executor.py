import time
import win32gui
import win32api
import psutil
import pygetwindow as gw
from screeninfo import get_monitors
import win32process
from pywinauto import Desktop
import keyboard
import time
import win32con


class TileManager:  
    def window_resize(self, x, y, program, width, height):
        prg_finder = win32gui.FindWindow(None, program)
        win32gui.MoveWindow(prg_finder, x, y, width, height, True)

    def get_monitor_size(self):
        monitor = get_monitors()[0]
        width, height = monitor.width, monitor.height
        return width, height
    
    def tile_windows(self, prg1, prg2, ratio):
        width, height = self.get_monitor_size()
        try:
            width1 = int(width * ratio[0] / 100)
            width2 = width - width1
            win1 = self._get_windows_by_program_name(prg1)
            win1.resizeTo(width1, height)
            win1.moveTo(0, 0)
            win2 = self._get_windows_by_program_name(prg2)
            win2.resizeTo(width2, height)
            win2.moveTo(width1, 0)
            print(width1, width2)
        except IndexError:
            print("IndexError")
            return
        except Exception as e:
            print(e)
                
    def _get_hwnd_by_process_name(self, process_name):
        hwnds = []
        def callback(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    if psutil.Process(pid).name().lower() == process_name.lower():
                        hwnds.append(hwnd)
                except:
                    pass
        win32gui.EnumWindows(callback, None)
        return hwnds

    def _get_windows_by_program_name(self, program_name: str):
        hwnds = self._get_hwnd_by_process_name(f"{program_name}.exe")
        for w in gw.getAllWindows(): 
            if (w._hWnd in hwnds or w.title.strip().lower() == program_name) and w.title.strip() != "": 
                return w
        raise Exception(f"Программа {program_name} не открыта")
    

    def get_monitor_sizes(self):
        monitors = []
        for monitor in win32api.EnumDisplayMonitors():
            monitors.append(win32api.GetMonitorInfo(monitor[0])) #type: ignore
        return monitors

    def emulate_win_arrow(self, title, direction):
        hwnd = self._get_windows_by_program_name(title)
        win32gui.ShowWindow(hwnd._hWnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd._hWnd)
        time.sleep(0.1)
        keyboard.press_and_release(f"win+{direction}")
        time.sleep(0.1)
        keyboard.press_and_release("enter")

if __name__ == "__main__":
    tile_manager = TileManager()
    tile_manager.emulate_win_arrow("chrome", "right")