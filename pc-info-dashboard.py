#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PC-INFO-DASHBOARD
Interface Tkinter ultime affichant 100+ informations système.
Style hacker cyberpunk : barres de progression rouges/vertes, pourcentages dynamiques,
console Matrix, graphiques temps réel, détection GPU.
Créé par hackers_tchad — usage éducatif.
"""

import tkinter as tk
from tkinter import ttk
import platform
import psutil
import os
import socket
import time
import threading
import datetime
import random
import json

# Couleurs
BG = "#0d1117"
FG = "#c9d1d9"
ACCENT_RED = "#ff4d4d"
ACCENT_GREEN = "#3fb950"
ACCENT_BLUE = "#58a6ff"
ACCENT_PURPLE = "#bc8cff"
CARD_BG = "#161b22"
FONT_TITLE = ("Consolas", 18, "bold")
FONT_LABEL = ("Consolas", 10)
FONT_VALUE = ("Consolas", 11, "bold")

def format_bytes(num):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(num) < 1024.0:
            return f"{num:.2f} {unit}"
        num /= 1024.0
    return f"{num:.2f} PB"

GPU_INFO = {}
try:
    import GPUtil
    for g in GPUtil.getGPUs():
        GPU_INFO[g.id] = g
except Exception:
    pass

def get_cpu_info():
    try:
        import cpuinfo
        return cpuinfo.get_cpu_info()
    except Exception:
        return {}

CPU_INFO = get_cpu_info()


class CircularProgress(tk.Canvas):
    def __init__(self, parent, size=120, width=10, color=ACCENT_GREEN, **kwargs):
        super().__init__(parent, width=size, height=size, bg=CARD_BG, highlightthickness=0, **kwargs)
        self.size = size
        self.width = width
        self.color = color
        self.angle = 0
        self.text_id = self.create_text(size//2, size//2, text="0%", fill=FG, font=("Consolas", 14, "bold"))
        self.arc_id = None
        self.draw_arc(0)

    def draw_arc(self, percent):
        self.delete(self.arc_id)
        extent = percent * 360 / 100
        self.arc_id = self.create_arc(
            self.width, self.width, self.size - self.width, self.size - self.width,
            start=90, extent=-extent, style="arc", outline=self.color, width=self.width
        )
        self.itemconfig(self.text_id, text=f"{percent:.1f}%")


class LinearProgress(tk.Canvas):
    def __init__(self, parent, width=250, height=18, color=ACCENT_GREEN, **kwargs):
        super().__init__(parent, width=width, height=height, bg=CARD_BG, highlightthickness=0, **kwargs)
        self.color = color
        self.create_rectangle(0, 0, width, height, fill="#30363d", outline="")
        self.bar = self.create_rectangle(0, 0, 0, height, fill=color, outline="")
        self.text = self.create_text(width//2, height//2, text="0%", fill=FG, font=("Consolas", 9, "bold"))

    def set_value(self, percent):
        w = int(self["width"]) * percent / 100
        self.coords(self.bar, 0, 0, w, int(self["height"]))
        color = ACCENT_GREEN if percent < 70 else ("#f0883e" if percent < 90 else ACCENT_RED)
        self.itemconfig(self.bar, fill=color)
        self.itemconfig(self.text, text=f"{percent:.1f}%")


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PC INFO DASHBOARD — by hackers_tchad")
        self.geometry("1500x950")
        self.configure(bg=BG)
        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TNotebook", background=BG, tabmargins=[2, 5, 2, 0])
        self.style.configure("TNotebook.Tab", background=CARD_BG, foreground=FG, font=("Consolas", 10, "bold"), padding=10)
        self.style.map("TNotebook.Tab", background=[("selected", ACCENT_BLUE)], foreground=[("selected", "white")])
        self.style.configure("Horizontal.TScale", background=CARD_BG, troughcolor="#30363d", bordercolor=ACCENT_BLUE)

        self.header_frame = tk.Frame(self, bg=BG)
        self.header_frame.pack(fill="x", padx=10, pady=5)
        self.header = tk.Label(self.header_frame, text="◢ PC INFO DASHBOARD ◣", bg=BG, fg=ACCENT_RED, font=FONT_TITLE)
        self.header.pack(side="left")
        self.clock = tk.Label(self.header_frame, text="", bg=BG, fg=ACCENT_GREEN, font=("Consolas", 12, "bold"))
        self.clock.pack(side="right", padx=10)
        self.update_clock()

        self.sub = tk.Label(self, text="Surveillance temps réel — CPU / RAM / Disque / Réseau / GPU / Températures", bg=BG, fg=FG, font=("Consolas", 10))
        self.sub.pack()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_overview = tk.Frame(self.notebook, bg=BG)
        self.tab_cpu = tk.Frame(self.notebook, bg=BG)
        self.tab_memory = tk.Frame(self.notebook, bg=BG)
        self.tab_disk = tk.Frame(self.notebook, bg=BG)
        self.tab_network = tk.Frame(self.notebook, bg=BG)
        self.tab_battery = tk.Frame(self.notebook, bg=BG)
        self.tab_gpu = tk.Frame(self.notebook, bg=BG)
        self.tab_processes = tk.Frame(self.notebook, bg=BG)
        self.tab_matrix = tk.Frame(self.notebook, bg=BG)

        self.notebook.add(self.tab_overview, text="Vue d'ensemble")
        self.notebook.add(self.tab_cpu, text="CPU")
        self.notebook.add(self.tab_memory, text="Mémoire")
        self.notebook.add(self.tab_disk, text="Disques")
        self.notebook.add(self.tab_network, text="Réseau")
        self.notebook.add(self.tab_battery, text="Batterie")
        self.notebook.add(self.tab_gpu, text="GPU")
        self.notebook.add(self.tab_processes, text="Processus")
        self.notebook.add(self.tab_matrix, text="Matrix")

        self.history_cpu = []
        self.history_ram = []
        self.history_net_sent = []
        self.history_net_recv = []

        self.build_overview()
        self.build_cpu()
        self.build_memory()
        self.build_disk()
        self.build_network()
        self.build_battery()
        self.build_gpu()
        self.build_processes()
        self.build_matrix()

        self.running = True
        self.updater = threading.Thread(target=self.update_loop, daemon=True)
        self.updater.start()
        self.matrix_thread = threading.Thread(target=self.matrix_rain, daemon=True)
        self.matrix_thread.start()

    def update_clock(self):
        self.clock.config(text=datetime.datetime.now().strftime("%H:%M:%S"))
        self.after(1000, self.update_clock)

    def color_by_percent(self, p):
        if p < 50:
            return ACCENT_GREEN
        elif p < 80:
            return "#f0883e"
        return ACCENT_RED

    def card(self, parent, title):
        frame = tk.Frame(parent, bg=CARD_BG, bd=1, relief="solid")
        frame.grid_propagate(False)
        tk.Label(frame, text=title, bg=CARD_BG, fg=ACCENT_BLUE, font=("Consolas", 11, "bold")).pack(anchor="w", padx=8, pady=5)
        return frame

    def info_row(self, parent, label, var):
        f = tk.Frame(parent, bg=CARD_BG)
        f.pack(fill="x", padx=8, pady=1)
        tk.Label(f, text=label, bg=CARD_BG, fg=FG, font=FONT_LABEL, width=22, anchor="w").pack(side="left")
        tk.Label(f, textvariable=var, bg=CARD_BG, fg="white", font=FONT_VALUE, anchor="w").pack(side="left", fill="x", expand=True)

    def build_overview(self):
        frame = tk.Frame(self.tab_overview, bg=BG)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.cpu_circle = CircularProgress(frame, size=160, color=ACCENT_GREEN)
        self.ram_circle = CircularProgress(frame, size=160, color=ACCENT_BLUE)
        self.disk_circle = CircularProgress(frame, size=160, color=ACCENT_RED)

        self.cpu_circle.grid(row=0, column=0, padx=20, pady=20)
        tk.Label(frame, text="CPU", bg=BG, fg=FG, font=FONT_LABEL).grid(row=1, column=0)
        self.ram_circle.grid(row=0, column=1, padx=20, pady=20)
        tk.Label(frame, text="RAM", bg=BG, fg=FG, font=FONT_LABEL).grid(row=1, column=1)
        self.disk_circle.grid(row=0, column=2, padx=20, pady=20)
        tk.Label(frame, text="DISQUE", bg=BG, fg=FG, font=FONT_LABEL).grid(row=1, column=2)

        card = self.card(frame, "Informations système")
        card.config(width=500, height=260)
        card.grid(row=0, column=3, rowspan=2, padx=20, pady=20, sticky="n")

        vars = {
            "OS": f"{platform.system()} {platform.release()}",
            "Hostname": socket.gethostname(),
            "Utilisateur": os.getlogin() if hasattr(os, "getlogin") else "N/A",
            "Architecture": platform.architecture()[0],
            "Machine": platform.machine(),
            "Processeur": platform.processor() or CPU_INFO.get("brand_raw", "Inconnu"),
            "Nœuds CPU": str(psutil.cpu_count(logical=False)),
            "Threads CPU": str(psutil.cpu_count(logical=True)),
            "Démarrage": datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.overview_vars = {}
        for k, v in vars.items():
            var = tk.StringVar(value=v)
            self.overview_vars[k] = var
            self.info_row(card, f"{k} :", var)

        self.uptime_var = tk.StringVar(value="...")
        self.proc_var = tk.StringVar(value="...")
        self.info_row(card, "Uptime :", self.uptime_var)
        self.info_row(card, "Processus :", self.proc_var)

        # Graphique temps réel CPU/RAM
        self.graph_canvas = tk.Canvas(frame, width=500, height=150, bg=CARD_BG, highlightthickness=1, highlightbackground=ACCENT_BLUE)
        self.graph_canvas.grid(row=2, column=0, columnspan=4, pady=10)
        self.graph_canvas.create_text(60, 10, text="CPU", fill=ACCENT_GREEN, font=("Consolas", 9, "bold"), anchor="w")
        self.graph_canvas.create_text(60, 25, text="RAM", fill=ACCENT_BLUE, font=("Consolas", 9, "bold"), anchor="w")

    def build_cpu(self):
        frame = tk.Frame(self.tab_cpu, bg=BG)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        card = self.card(frame, "Processeur")
        card.config(width=600, height=300)
        card.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        cpu_info = {
            "Modèle": CPU_INFO.get("brand_raw", platform.processor() or "Inconnu"),
            "Architecture": CPU_INFO.get("arch", platform.machine()),
            "Cœurs physiques": str(psutil.cpu_count(logical=False)),
            "Threads logiques": str(psutil.cpu_count(logical=True)),
            "Fréquence max": f"{CPU_INFO.get('hz_advertised_friendly', 'N/A')}",
            "Flags": ", ".join(CPU_INFO.get("flags", ["N/A"])[:8]) + " ...",
        }
        self.cpu_vars = {}
        for k, v in cpu_info.items():
            var = tk.StringVar(value=v)
            self.cpu_vars[k] = var
            self.info_row(card, f"{k} :", var)

        self.cpu_usage_var = tk.StringVar(value="...")
        self.cpu_freq_var = tk.StringVar(value="...")
        self.info_row(card, "Utilisation :", self.cpu_usage_var)
        self.info_row(card, "Fréquence actuelle :", self.cpu_freq_var)

        self.cpu_history = []

        card2 = self.card(frame, "Utilisation par cœur")
        card2.config(width=600, height=300)
        card2.grid(row=0, column=1, padx=10, pady=10, sticky="ne")
        self.core_bars = []
        for i in range(min(psutil.cpu_count(logical=True), 32)):
            f = tk.Frame(card2, bg=CARD_BG)
            f.pack(fill="x", padx=8, pady=2)
            tk.Label(f, text=f"CPU {i}", bg=CARD_BG, fg=FG, width=8, anchor="w").pack(side="left")
            bar = LinearProgress(f, width=400, height=14)
            bar.pack(side="left")
            self.core_bars.append(bar)

        card3 = self.card(frame, "Statistiques CPU")
        card3.config(width=600, height=220)
        card3.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        self.ctx_switches = tk.StringVar(value="...")
        self.interrupts = tk.StringVar(value="...")
        self.soft_interrupts = tk.StringVar(value="...")
        self.syscalls = tk.StringVar(value="...")
        self.info_row(card3, "Changements contexte :", self.ctx_switches)
        self.info_row(card3, "Interruptions :", self.interrupts)
        self.info_row(card3, "Soft IRQ :", self.soft_interrupts)
        self.info_row(card3, "Appels système :", self.syscalls)

    def build_memory(self):
        frame = tk.Frame(self.tab_memory, bg=BG)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        card = self.card(frame, "RAM")
        card.config(width=600, height=300)
        card.grid(row=0, column=0, padx=10, pady=10)

        self.ram_total_var = tk.StringVar(value="...")
        self.ram_used_var = tk.StringVar(value="...")
        self.ram_free_var = tk.StringVar(value="...")
        self.ram_percent_var = tk.StringVar(value="...")

        self.info_row(card, "Total :", self.ram_total_var)
        self.info_row(card, "Utilisée :", self.ram_used_var)
        self.info_row(card, "Libre :", self.ram_free_var)
        self.info_row(card, "Pourcentage :", self.ram_percent_var)

        self.ram_bar = LinearProgress(frame, width=600, height=25)
        self.ram_bar.grid(row=1, column=0, pady=20)

        card2 = self.card(frame, "Swap")
        card2.config(width=600, height=200)
        card2.grid(row=0, column=1, padx=10, pady=10)

        self.swap_total_var = tk.StringVar(value="...")
        self.swap_used_var = tk.StringVar(value="...")
        self.swap_free_var = tk.StringVar(value="...")
        self.swap_percent_var = tk.StringVar(value="...")

        self.info_row(card2, "Total :", self.swap_total_var)
        self.info_row(card2, "Utilisé :", self.swap_used_var)
        self.info_row(card2, "Libre :", self.swap_free_var)
        self.info_row(card2, "Pourcentage :", self.swap_percent_var)

    def build_disk(self):
        frame = tk.Frame(self.tab_disk, bg=BG)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.disk_cards = []
        row, col = 0, 0
        for part in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(part.mountpoint)
                card = self.card(frame, f"Disque {part.device}")
                card.config(width=380, height=180)
                card.grid(row=row, column=col, padx=10, pady=10)
                total = tk.StringVar(value=f"{usage.total / (1024**3):.2f} Go")
                used = tk.StringVar(value=f"{usage.used / (1024**3):.2f} Go")
                free = tk.StringVar(value=f"{usage.free / (1024**3):.2f} Go")
                pct = tk.StringVar(value=f"{usage.percent}%")
                self.info_row(card, "Total :", total)
                self.info_row(card, "Utilisé :", used)
                self.info_row(card, "Libre :", free)
                self.info_row(card, "Pourcentage :", pct)
                bar = LinearProgress(card, width=340, height=18)
                bar.pack(padx=8, pady=10)
                bar.set_value(usage.percent)
                self.disk_cards.append((card, bar))
                col += 1
                if col > 2:
                    col = 0
                    row += 1
            except Exception:
                continue

    def build_network(self):
        frame = tk.Frame(self.tab_network, bg=BG)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        card = self.card(frame, "Interfaces réseau")
        card.config(width=700, height=400)
        card.pack(fill="both", expand=True)

        self.net_text = tk.Text(card, bg=CARD_BG, fg=FG, font=("Consolas", 10), wrap="word", state="disabled")
        self.net_text.pack(fill="both", expand=True, padx=8, pady=5)

    def build_battery(self):
        frame = tk.Frame(self.tab_battery, bg=BG)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        card = self.card(frame, "Batterie")
        card.config(width=500, height=250)
        card.pack()

        self.bat_percent_var = tk.StringVar(value="...")
        self.bat_plugged_var = tk.StringVar(value="...")
        self.bat_time_var = tk.StringVar(value="...")

        self.info_row(card, "Pourcentage :", self.bat_percent_var)
        self.info_row(card, "Branché :", self.bat_plugged_var)
        self.info_row(card, "Temps restant :", self.bat_time_var)

        self.bat_bar = LinearProgress(frame, width=500, height=25, color=ACCENT_GREEN)
        self.bat_bar.pack(pady=20)

    def build_misc(self):
        frame = tk.Frame(self.tab_misc, bg=BG)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        card = self.card(frame, "Divers")
        card.config(width=700, height=400)
        card.pack(fill="both", expand=True)

        self.misc_text = tk.Text(card, bg=CARD_BG, fg=FG, font=("Consolas", 10), wrap="word", state="disabled")
        self.misc_text.pack(fill="both", expand=True, padx=8, pady=5)

    def update_loop(self):
        while self.running:
            try:
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory()
                disk = psutil.disk_usage("/") if os.name != "nt" else psutil.disk_usage("C:\\")
                per_core = psutil.cpu_percent(interval=None, percpu=True)

                self.after(0, lambda: self.cpu_circle.draw_arc(cpu))
                self.after(0, lambda: self.ram_circle.draw_arc(ram.percent))
                self.after(0, lambda: self.disk_circle.draw_arc(disk.percent))

                self.after(0, lambda: self.cpu_usage_var.set(f"{cpu}%"))
                freq = psutil.cpu_freq()
                if freq:
                    self.after(0, lambda: self.cpu_freq_var.set(f"{freq.current:.0f} MHz"))

                for i, bar in enumerate(self.core_bars):
                    if i < len(per_core):
                        self.after(0, lambda b=bar, v=per_core[i]: b.set_value(v))

                self.after(0, lambda: self.ram_total_var.set(f"{ram.total / (1024**3):.2f} Go"))
                self.after(0, lambda: self.ram_used_var.set(f"{ram.used / (1024**3):.2f} Go"))
                self.after(0, lambda: self.ram_free_var.set(f"{ram.available / (1024**3):.2f} Go"))
                self.after(0, lambda: self.ram_percent_var.set(f"{ram.percent}%"))
                self.after(0, lambda: self.ram_bar.set_value(ram.percent))

                swap = psutil.swap_memory()
                self.after(0, lambda: self.swap_total_var.set(f"{swap.total / (1024**3):.2f} Go"))
                self.after(0, lambda: self.swap_used_var.set(f"{swap.used / (1024**3):.2f} Go"))
                self.after(0, lambda: self.swap_free_var.set(f"{swap.free / (1024**3):.2f} Go"))
                self.after(0, lambda: self.swap_percent_var.set(f"{swap.percent}%"))

                self.after(0, lambda: self.proc_var.set(str(len(psutil.pids()))))
                uptime = time.time() - psutil.boot_time()
                hours, rem = divmod(uptime, 3600)
                minutes, seconds = divmod(rem, 60)
                self.after(0, lambda: self.uptime_var.set(f"{int(hours)}h {int(minutes)}m {int(seconds)}s"))

                net_io = psutil.net_io_counters(pernic=True)
                net_info = ""
                for iface, counters in net_io.items():
                    net_info += f"{iface}:\n"
                    net_info += f"  Envoyé : {counters.bytes_sent / (1024**2):.2f} Mo\n"
                    net_info += f"  Reçu   : {counters.bytes_recv / (1024**2):.2f} Mo\n"
                    net_info += f"  Paquets envoyés : {counters.packets_sent}\n"
                    net_info += f"  Paquets reçus   : {counters.packets_recv}\n\n"
                self.after(0, lambda text=net_info: self.set_text(self.net_text, text))

                battery = psutil.sensors_battery()
                if battery:
                    self.after(0, lambda: self.bat_percent_var.set(f"{battery.percent}%"))
                    self.after(0, lambda: self.bat_plugged_var.set("Oui" if battery.power_plugged else "Non"))
                    secs = battery.secsleft
                    time_str = "Calcul..." if secs == psutil.POWER_TIME_UNLIMITED else f"{secs // 3600}h {(secs % 3600) // 60}m"
                    self.after(0, lambda: self.bat_time_var.set(time_str))
                    self.after(0, lambda: self.bat_bar.set_value(battery.percent))
                else:
                    self.after(0, lambda: self.bat_percent_var.set("Aucune batterie"))

                misc = []
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        for entry in entries:
                            misc.append(f"{name} [{entry.label or 'n/a'}] : {entry.current:.1f}°C")
                fans = psutil.sensors_fans()
                if fans:
                    for name, entries in fans.items():
                        for entry in entries:
                            misc.append(f"Ventilateur {name} [{entry.label or 'n/a'}] : {entry.current} RPM")
                misc.append(f"Utilisateurs connectés : {len(psutil.users())}")
                misc.append(f"Fichiers ouverts max : {psutil.Process().num_fds() if hasattr(psutil.Process(), 'num_fds') else 'N/A'}")
                self.after(0, lambda text="\n".join(misc): self.set_text(self.misc_text, text))

            except Exception as e:
                print("Erreur update :", e)
            time.sleep(1)

    def set_text(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("end", text)
        widget.config(state="disabled")

    def destroy(self):
        self.running = False
        super().destroy()


if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()
