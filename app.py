import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import threading
import os
import sys
import multiprocessing  # <-- Added for PyInstaller EXE fix

from rembg import remove
from pathlib import Path
import io

# ── Theme ──────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

ACCENT   = "#00D4AA"
SURFACE  = "#1A1A2E"
SURFACE2 = "#16213E"
SURFACE3 = "#0F3460"
TEXT     = "#E0E0E0"
MUTED    = "#666688"
DANGER   = "#FF4466"
SUCCESS  = "#00D4AA"

# ── App ────────────────────────────────────────────────────────────────────
class BGRemoverApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("BG Eraser — Offline AI Background Remover")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(fg_color=SURFACE)

        self.input_path  = None
        self.output_img  = None
        self.orig_pil    = None
        self.result_pil  = None
        self.processing  = False

        self._build_ui()

    # ── UI Construction ────────────────────────────────────────────────────
    def _build_ui(self):
        # ── Top bar ──
        topbar = ctk.CTkFrame(self, fg_color=SURFACE2, height=60, corner_radius=0)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        ctk.CTkLabel(
            topbar, text="✦  BG ERASER",
            font=ctk.CTkFont("Courier", 22, weight="bold"),
            text_color=ACCENT
        ).pack(side="left", padx=24, pady=15)

        ctk.CTkLabel(
            topbar, text="100% Offline · AI-Powered · No Data Leaves Your PC",
            font=ctk.CTkFont("Courier", 11),
            text_color=MUTED
        ).pack(side="left", padx=10, pady=15)

        # ── Main layout ──
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=20, pady=10)

        # Left panel
        left = ctk.CTkFrame(main, fg_color=SURFACE2, corner_radius=12, width=260)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)
        self._build_left_panel(left)

        # Center: before/after
        center = ctk.CTkFrame(main, fg_color="transparent")
        center.pack(side="left", fill="both", expand=True)
        self._build_canvas_area(center)

        # Bottom status bar
        self._build_status_bar()

    def _build_left_panel(self, parent):
        ctk.CTkLabel(
            parent, text="CONTROLS",
            font=ctk.CTkFont("Courier", 12, weight="bold"),
            text_color=MUTED
        ).pack(pady=(20, 10), padx=20, anchor="w")

        # Upload button
        self.btn_upload = ctk.CTkButton(
            parent, text="📂  Open Image",
            font=ctk.CTkFont("Courier", 13, weight="bold"),
            fg_color=SURFACE3, hover_color=ACCENT,
            text_color=TEXT, height=44, corner_radius=8,
            command=self.open_image
        )
        self.btn_upload.pack(fill="x", padx=16, pady=6)

        # Remove BG button
        self.btn_remove = ctk.CTkButton(
            parent, text="✦  Remove Background",
            font=ctk.CTkFont("Courier", 13, weight="bold"),
            fg_color=ACCENT, hover_color="#00B894",
            text_color="#000000", height=44, corner_radius=8,
            command=self.remove_background,
            state="disabled"
        )
        self.btn_remove.pack(fill="x", padx=16, pady=6)

        # Save button
        self.btn_save = ctk.CTkButton(
            parent, text="💾  Save PNG",
            font=ctk.CTkFont("Courier", 13, weight="bold"),
            fg_color=SURFACE3, hover_color="#334477",
            text_color=TEXT, height=44, corner_radius=8,
            command=self.save_image,
            state="disabled"
        )
        self.btn_save.pack(fill="x", padx=16, pady=6)

        # Separator
        ctk.CTkFrame(parent, fg_color=SURFACE3, height=1).pack(fill="x", padx=16, pady=18)

        # Output format
        ctk.CTkLabel(
            parent, text="OUTPUT FORMAT",
            font=ctk.CTkFont("Courier", 11, weight="bold"),
            text_color=MUTED
        ).pack(anchor="w", padx=20)

        self.fmt_var = ctk.StringVar(value="PNG (Transparent)")
        fmt_menu = ctk.CTkOptionMenu(
            parent, values=["PNG (Transparent)", "PNG (White BG)", "PNG (Black BG)"],
            variable=self.fmt_var,
            font=ctk.CTkFont("Courier", 12),
            fg_color=SURFACE3, button_color=SURFACE3,
            button_hover_color=ACCENT, text_color=TEXT
        )
        fmt_menu.pack(fill="x", padx=16, pady=8)

        ctk.CTkFrame(parent, fg_color=SURFACE3, height=1).pack(fill="x", padx=16, pady=18)

        # File info
        ctk.CTkLabel(
            parent, text="FILE INFO",
            font=ctk.CTkFont("Courier", 11, weight="bold"),
            text_color=MUTED
        ).pack(anchor="w", padx=20)

        self.lbl_filename = ctk.CTkLabel(
            parent, text="No file loaded",
            font=ctk.CTkFont("Courier", 11),
            text_color=TEXT, wraplength=220
        )
        self.lbl_filename.pack(anchor="w", padx=20, pady=4)

        self.lbl_size = ctk.CTkLabel(
            parent, text="",
            font=ctk.CTkFont("Courier", 11),
            text_color=MUTED
        )
        self.lbl_size.pack(anchor="w", padx=20)

        # Progress bar (hidden by default)
        self.progress = ctk.CTkProgressBar(
            parent, fg_color=SURFACE3, progress_color=ACCENT,
            height=6, corner_radius=3
        )
        self.progress.set(0)

        self.lbl_progress = ctk.CTkLabel(
            parent, text="",
            font=ctk.CTkFont("Courier", 11),
            text_color=ACCENT
        )

    def _build_canvas_area(self, parent):
        # Header row
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            header, text="ORIGINAL",
            font=ctk.CTkFont("Courier", 12, weight="bold"),
            text_color=MUTED
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            header, text="RESULT",
            font=ctk.CTkFont("Courier", 12, weight="bold"),
            text_color=MUTED
        ).pack(side="right", padx=10)

        # Canvas row
        canvas_row = ctk.CTkFrame(parent, fg_color="transparent")
        canvas_row.pack(fill="both", expand=True)

        # Original canvas
        orig_frame = ctk.CTkFrame(canvas_row, fg_color=SURFACE2, corner_radius=10)
        orig_frame.pack(side="left", fill="both", expand=True, padx=(0, 6))

        self.orig_canvas = tk.Canvas(
            orig_frame, bg="#0D0D1A", highlightthickness=0
        )
        self.orig_canvas.pack(fill="both", expand=True, padx=2, pady=2)
        self._draw_placeholder(self.orig_canvas, "Drop or open an image")

        # Result canvas
        res_frame = ctk.CTkFrame(canvas_row, fg_color=SURFACE2, corner_radius=10)
        res_frame.pack(side="left", fill="both", expand=True, padx=(6, 0))

        self.res_canvas = tk.Canvas(
            res_frame, bg="#0D0D1A", highlightthickness=0
        )
        self.res_canvas.pack(fill="both", expand=True, padx=2, pady=2)
        self._draw_placeholder(self.res_canvas, "Result appears here")

        # Bind resize
        self.orig_canvas.bind("<Configure>", self._on_resize)

        # Drag and drop hint
        self.orig_canvas.bind("<Button-1>", lambda e: self.open_image())

    def _build_status_bar(self):
        bar = ctk.CTkFrame(self, fg_color=SURFACE2, height=32, corner_radius=0)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        self.status_lbl = ctk.CTkLabel(
            bar, text="Ready — open an image to begin",
            font=ctk.CTkFont("Courier", 11),
            text_color=MUTED
        )
        self.status_lbl.pack(side="left", padx=20)

        ctk.CTkLabel(
            bar, text="Model: U²-Net (ONNX) · CPU/GPU auto-detect",
            font=ctk.CTkFont("Courier", 11),
            text_color=MUTED
        ).pack(side="right", padx=20)

    # ── Helpers ────────────────────────────────────────────────────────────
    def _draw_placeholder(self, canvas, text):
        canvas.delete("all")
        w = canvas.winfo_width() or 400
        h = canvas.winfo_height() or 400
        # Checkerboard for transparency hint
        size = 30
        for row in range(0, h // size + 1):
            for col in range(0, w // size + 1):
                color = "#111122" if (row + col) % 2 == 0 else "#0D0D1A"
                canvas.create_rectangle(
                    col * size, row * size,
                    (col + 1) * size, (row + 1) * size,
                    fill=color, outline=""
                )
        canvas.create_text(
            w // 2, h // 2, text=text,
            fill=MUTED, font=("Courier", 14)
        )

    def _show_image_on_canvas(self, canvas, pil_img):
        canvas.delete("all")
        cw = canvas.winfo_width()  or 400
        ch = canvas.winfo_height() or 400

        img = pil_img.copy()
        img.thumbnail((cw - 8, ch - 8), Image.LANCZOS)

        # Checkerboard behind transparent areas
        if img.mode == "RGBA":
            bg = Image.new("RGBA", img.size, (255, 255, 255, 0))
            checker = self._make_checker(img.size)
            checker.paste(img, mask=img.split()[3])
            img_show = checker
        else:
            img_show = img

        tk_img = ImageTk.PhotoImage(img_show)
        canvas._tkimg = tk_img  # prevent GC
        x = (cw - img_show.width)  // 2
        y = (ch - img_show.height) // 2
        canvas.create_image(x, y, anchor="nw", image=tk_img)

    def _make_checker(self, size):
        w, h = size
        checker = Image.new("RGB", (w, h))
        sq = 12
        for row in range(0, h, sq):
            for col in range(0, w, sq):
                c = (200, 200, 200) if (row // sq + col // sq) % 2 == 0 else (150, 150, 150)
                for y in range(row, min(row + sq, h)):
                    for x in range(col, min(col + sq, w)):
                        checker.putpixel((x, y), c)
        return checker

    def _on_resize(self, event):
        if self.orig_pil:
            self._show_image_on_canvas(self.orig_canvas, self.orig_pil)
        if self.result_pil:
            self._show_image_on_canvas(self.res_canvas, self.result_pil)

    def _set_status(self, msg, color=None):
        self.status_lbl.configure(text=msg, text_color=color or MUTED)

    # ── Actions ────────────────────────────────────────────────────────────
    def open_image(self):
        path = filedialog.askopenfilename(
            title="Select an image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.webp *.tiff"), ("All", "*.*")]
        )
        if not path:
            return

        self.input_path = path
        self.result_pil = None
        self.btn_save.configure(state="disabled")

        try:
            img = Image.open(path).convert("RGBA")
            self.orig_pil = img

            fname = os.path.basename(path)
            self.lbl_filename.configure(text=fname)
            self.lbl_size.configure(text=f"{img.width} × {img.height} px")

            self.after(50, lambda: self._show_image_on_canvas(self.orig_canvas, img))
            self._draw_placeholder(self.res_canvas, "Click 'Remove Background'")

            self.btn_remove.configure(state="normal")
            self._set_status(f"Loaded: {fname}", ACCENT)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image:\n{e}")

    def remove_background(self):
        if not self.orig_pil or self.processing:
            return

        self.processing = True
        self.btn_remove.configure(state="disabled", text="Processing…")
        self.btn_upload.configure(state="disabled")

        self.progress.pack(fill="x", padx=16, pady=(8, 0))
        self.lbl_progress.pack(padx=20, pady=2, anchor="w")
        self.progress.set(0)
        self.lbl_progress.configure(text="Starting AI model…")
        self._set_status("Running U²-Net inference…", ACCENT)

        self._animate_progress()
        thread = threading.Thread(target=self._do_remove, daemon=True)
        thread.start()

    def _animate_progress(self):
        if not self.processing:
            return
        cur = self.progress.get()
        # Fake progress up to 90%; real completion sets 100%
        if cur < 0.88:
            self.progress.set(cur + 0.012)
            stages = {
                0.1: "Loading model weights…",
                0.3: "Preprocessing image…",
                0.5: "Running neural inference…",
                0.7: "Generating alpha matte…",
                0.85: "Finalising mask…",
            }
            for threshold, msg in stages.items():
                if abs(cur - threshold) < 0.015:
                    self.lbl_progress.configure(text=msg)
                    break
            self.after(80, self._animate_progress)

    def _do_remove(self):
        try:
            buf = io.BytesIO()
            self.orig_pil.save(buf, format="PNG")
            buf.seek(0)

            output_bytes = remove(buf.read())
            result = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

            fmt = self.fmt_var.get()
            if "White BG" in fmt:
                bg = Image.new("RGBA", result.size, (255, 255, 255, 255))
                bg.paste(result, mask=result.split()[3])
                result = bg.convert("RGB")
            elif "Black BG" in fmt:
                bg = Image.new("RGBA", result.size, (0, 0, 0, 255))
                bg.paste(result, mask=result.split()[3])
                result = bg.convert("RGB")

            self.result_pil = result
            self.after(0, self._on_done)
        except Exception as e:
            self.after(0, lambda: self._on_error(str(e)))

    def _on_done(self):
        self.processing = False
        self.progress.set(1.0)
        self.lbl_progress.configure(text="✓ Done!", text_color=SUCCESS)

        self._show_image_on_canvas(self.res_canvas, self.result_pil)
        self.btn_remove.configure(state="normal", text="✦  Remove Background")
        self.btn_upload.configure(state="normal")
        self.btn_save.configure(state="normal")
        self._set_status("Background removed successfully!", SUCCESS)

        self.after(3000, lambda: [
            self.progress.pack_forget(),
            self.lbl_progress.pack_forget()
        ])

    def _on_error(self, msg):
        self.processing = False
        self.progress.pack_forget()
        self.lbl_progress.pack_forget()
        self.btn_remove.configure(state="normal", text="✦  Remove Background")
        self.btn_upload.configure(state="normal")
        self._set_status(f"Error: {msg}", DANGER)
        messagebox.showerror("Processing Error", msg)

    def save_image(self):
        if not self.result_pil:
            return

        fmt = self.fmt_var.get()
        ext = ".png"
        default = Path(self.input_path).stem + "_nobg" + ext

        path = filedialog.asksaveasfilename(
            defaultextension=ext,
            initialfile=default,
            filetypes=[("PNG Image", "*.png")]
        )
        if not path:
            return

        self.result_pil.save(path)
        self._set_status(f"Saved: {os.path.basename(path)}", SUCCESS)
        messagebox.showinfo("Saved", f"Image saved to:\n{path}")


# ── Entry ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    multiprocessing.freeze_support() # <-- Critical fix for PyInstaller
    app = BGRemoverApp()
    app.mainloop()