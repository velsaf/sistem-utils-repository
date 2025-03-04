import os
import time
import psutil
import subprocess
import curses
from art import *

def get_uptime():
    uptime_seconds = int(time.time() - psutil.boot_time())
    uptime_hours = uptime_seconds // 3600
    uptime_minutes = (uptime_seconds % 3600) // 60
    return f"{uptime_hours}ч {uptime_minutes}мин"

def get_battery_status():
    battery = psutil.sensors_battery()
    if battery:
        return f"{battery.percent}% ({'Заряжается' if battery.power_plugged else 'Разряжается'})"
    return "Нет данных о батарее"


def get_cpu_info():
    cpu_info = {
        "model": subprocess.getoutput("lscpu | grep 'Model name' | cut -d':' -f2").strip(),
        "usage": f"{psutil.cpu_percent(interval=0.1)}%",
        "temp": subprocess.getoutput("sensors | grep 'Core 0' | awk '{print $3}'").strip()
    }
    return cpu_info

def get_gpu_info():
    gpu_info = {
        "model": subprocess.getoutput("lspci | grep -i vga | cut -d':' -f3").strip(),
        "usage": subprocess.getoutput("nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits").strip() + "%",
        "temp": subprocess.getoutput("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits").strip() + "°C"
    }
    return gpu_info

def get_disk_info():
    disk_info = []
    for partition in psutil.disk_partitions():
        usage = psutil.disk_usage(partition.mountpoint)
        disk_info.append({
            "device": partition.device,
            "mountpoint": partition.mountpoint,
            "total": f"{usage.total // (2**30)}GB",
            "used": f"{usage.used // (2**30)}GB",
            "free": f"{usage.free // (2**30)}GB",
            "percent": f"{usage.percent}%"
        })
    return disk_info


def get_network_info():
    network_info = []
    for interface, addrs in psutil.net_if_addrs().items():
        ip = "N/A"
        mac = "N/A"
        for addr in addrs:
            if addr.family == 2:
                ip = addr.address
            elif addr.family == 17:
                mac = addr.address
        network_info.append({
            "interface": interface,
            "ip": ip,
            "mac": mac
        })
    return network_info


def draw_frame(window, start_y, start_x, title, content):
    frame_width = 50
    frame_height = 15
    window.addstr(start_y, start_x, "#" * frame_width)
    window.addstr(start_y + 1, start_x, f"# {title.center(frame_width - 4)} #")
    window.addstr(start_y + 2, start_x, "#" * frame_width)
    for i, line in enumerate(content):
        if i < frame_height - 4:
            window.addstr(start_y + 3 + i, start_x, line.ljust(frame_width))
    window.addstr(start_y + frame_height - 1, start_x, "#" * frame_width)

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000)

    while True:
        stdscr.clear()


        cpu_info = get_cpu_info()
        gpu_info = get_gpu_info()
        disk_info = get_disk_info()
        network_info = get_network_info()

        frame1_content = [
            f"Дистрибутив: {os.uname().sysname}",
            f"Название устройства: {os.uname().nodename}",
            f"Учетная запись: {os.getlogin()}",
            f"Время работы: {get_uptime()}",
            f"Батарея: {get_battery_status()}",
            f"Модель устройства: {subprocess.getoutput('cat /sys/class/dmi/id/product_name')}"
        ]
        draw_frame(stdscr, 1, 1, "Общая информация", frame1_content)


        frame2_content = [
            f"Модель ЦП: {cpu_info['model']}",
            f"Загруженность ЦП: {cpu_info['usage']}",
            f"Температура ЦП: {cpu_info['temp']}",
            f"Модель GPU: {gpu_info['model']}",
            f"Загруженность GPU: {gpu_info['usage']}",
            f"Температура GPU: {gpu_info['temp']}"
        ]
        draw_frame(stdscr, 1, 60, "Компоненты системы", frame2_content)


        frame3_content = []
        for disk in disk_info:
            frame3_content.extend([
                f"Устройство: {disk['device']}",
                f"Точка монтирования: {disk['mountpoint']}",
                f"Всего: {disk['total']}",
                f"Использовано: {disk['used']}",
                f"Свободно: {disk['free']}",
                f"Заполнено: {disk['percent']}",
                "-" * 20
            ])
        draw_frame(stdscr, 17, 1, "Состояние диска и хранилища", frame3_content)


        frame4_content = []
        for net in network_info:
            frame4_content.extend([
                f"Интерфейс: {net['interface']}",
                f"IP: {net['ip']}",
                f"MAC: {net['mac']}",
                "-" * 20
            ])
        draw_frame(stdscr, 17, 60, "Данные о интерфейсах и подключениях", frame4_content)


        key = stdscr.getch()
        if key == ord('q'):
            break

        stdscr.refresh()
        time.sleep(1)


if __name__ == "__main__":
    curses.wrapper(main)
