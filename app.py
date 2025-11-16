import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import math
from datetime import datetime

from storage import load_data, save_data
from routes import (
    wow_curve_map_smooth, percent_to_level, pick_step_for_level,
    route_steps, clamp
)
from images import pick_random_zone_image
from ui_theme import setup_theme

APP_TITLE = "WoW Classic-style Weight Tracker"

class WowWeightTracker:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("560x790")
        self.root.minsize(520, 720)

        setup_theme()
        self.data = load_data()
        self._build_ui()
        self._load_initial()

    def _build_ui(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.pack(fill="both", expand=True)

        # Title
        tk.Label(frm, text="World of Weightcraft", font=("Segoe UI", 16, "bold")).pack(pady=(0, 8))

        # Inputs row
        inrow = ttk.Frame(frm)
        inrow.pack(fill="x", pady=6)

        self.start_var = tk.DoubleVar(value=self.data.get("start") or 0.0)
        self.current_var = tk.DoubleVar(value=self.data.get("current") or 0.0)
        self.goal_var = tk.DoubleVar(value=self.data.get("goal") or 0.0)

        def add_field(parent, label, var):
            box = ttk.Frame(parent)
            ttk.Label(box, text=label).pack(anchor="w")
            e = ttk.Entry(box, textvariable=var)
            e.pack(fill="x")
            box.pack(side="left", expand=True, fill="x", padx=(0, 8))
            return e

        e1 = add_field(inrow, "Start weight", self.start_var)
        e2 = add_field(inrow, "Current weight", self.current_var)
        e3 = add_field(inrow, "Goal weight", self.goal_var)

        # Buttons
        btnrow = ttk.Frame(frm)
        btnrow.pack(fill="x", pady=6)
        ttk.Button(btnrow, text="Update (Enter)", command=self.update_progress).pack(side="left")
        ttk.Button(btnrow, text="Export History CSV", command=self.export_history).pack(side="left", padx=6)
        ttk.Button(btnrow, text="Reset History", command=self.reset_history).pack(side="right")

        # Summary
        self.summary_label = tk.Label(frm, text="", justify="left", font=("Consolas", 10))
        self.summary_label.pack(pady=(6, 2), anchor="w")


        # Next zone hint
        self.next_zone_label = tk.Label(frm, text="", font=("Segoe UI", 10))
        self.next_zone_label.pack(pady=(2, 8), anchor="w")

        # BIG level number (centered)
        self.big_level_label = tk.Label(frm, text="", font=("Segoe UI", 44, "bold"), fg="#6b59b3")
        self.big_level_label.pack(pady=(0, 4))  # sits just above the image

        # Zone image
        self.zone_label = tk.Label(frm)
        self.zone_label.pack(pady=6)

        # Progress bar
        self.progress = ttk.Progressbar(
            frm, orient="horizontal", length=520, mode="determinate",
            style="Purple.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=10, fill="x")

        # History
        ttk.Label(frm, text="History (latest first):").pack(anchor="w", pady=(12, 0))
        self.history_box = tk.Listbox(frm, height=8)
        self.history_box.pack(fill="both", expand=False, pady=4)

        # Keyboard: Enter triggers update
        for entry in (e1, e2, e3):
            entry.bind("<Return>", lambda *_: self.update_progress())

    def _load_initial(self):
        # initial render without appending to history
        self.update_progress(initial=True)

    # ------------- UX helpers -------------
    def _validate(self, start, current, goal):
        if not all(isinstance(x, float) for x in (start, current, goal)):
            messagebox.showerror("Invalid input", "Please enter numeric weights.")
            return False
        if not all(math.isfinite(x) for x in (start, current, goal)):
            messagebox.showerror("Invalid input", "Please enter valid numeric weights.")
            return False
        if start == goal:
            messagebox.showerror("Invalid input", "Start and goal cannot be equal.")
            return False
        return True

    def _progress_linear(self, start, current, goal):
        """Return linear 0..100 progress, auto-handling loss or gain goals."""
        if goal < start:
            frac = (start - current) / (start - goal)  # weight loss
        else:
            frac = (current - start) / (goal - start)  # weight gain
        return clamp(frac * 100.0, 0.0, 100.0)

    # ------------- Buttons -------------
    def export_history(self):
        hist = self.data.get("history") or []
        if not hist:
            messagebox.showinfo("Export", "No history to export yet.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")],
            initialfile="weight_history.csv",
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "weight"])
            w.writerows(hist)
        messagebox.showinfo("Export", f"Saved to:\n{path}")

    def reset_history(self):
        if messagebox.askyesno("Reset", "Clear history? This cannot be undone."):
            self.data["history"] = []
            save_data(self.data)
            self.history_box.delete(0, tk.END)

    # ------------- Core update -------------
    def update_progress(self, initial=False):
        try:
            start = float(self.start_var.get() or 0.0)
            current = float(self.current_var.get() or 0.0)
            goal = float(self.goal_var.get() or 0.0)
        except Exception:
            messagebox.showerror("Invalid input", "Please enter numeric weights.")
            return

        if not self._validate(start, current, goal):
            return

        # Linear progress (0..100) and Classic visual map
        linear_pct = self._progress_linear(start, current, goal)
        classic_pct = wow_curve_map_smooth(linear_pct)

        # Level approximation
        lvl = percent_to_level(classic_pct)

        # Big level number (rounded)
        display_level = int(round(lvl))
        self.big_level_label.config(text=str(display_level))

        # Zone (strict route)
        idx, zone_key, L0, L1 = pick_step_for_level(lvl)


        # Next zone hint
        if idx < len(route_steps) - 1:
            next_zone, next_L0, _ = route_steps[idx + 1]
            # Switch occurs at current step's end level, which equals next step's start level
            switch_level = L1
            self.next_zone_label.config(
                text=f"Next: {next_zone.replace('_',' ').title()} at ~Level {switch_level:.1f}"
            )
        else:
            self.next_zone_label.config(text="Final zone — keep pushing to 60!")

        # Progress bar
        self.progress['value'] = classic_pct

        # Zone image
        zone_img = pick_random_zone_image(zone_key, target_width=520, target_height=260)
        if zone_img is None:
            self.zone_label.config(image="", text=f"[Put images in zones/{zone_key}/]")
        else:
            self.zone_label.config(image=zone_img, text="")
            self.zone_label.image = zone_img

        # Save data + history (only when not initial and weight changed)
        if not initial:
            prev = self.data.get("current")
            if (prev is None) or (abs(prev - current) > 1e-9):
                self.data.setdefault("history", []).insert(
                    0, [datetime.now().strftime("%Y-%m-%d"), current]
                )
                self.data["history"] = self.data["history"][:200]

        self.data["start"] = start
        self.data["goal"] = goal
        self.data["current"] = current
        save_data(self.data)

        # Update history listbox
        self.history_box.delete(0, tk.END)
        for ts, wt in (self.data.get("history") or [])[:80]:
            self.history_box.insert(tk.END, f"{ts}  —  {wt}")

def main():
    root = tk.Tk()
    app = WowWeightTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()

