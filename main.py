import tkinter as tk
from tkinter import messagebox, filedialog
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import random, math, json, os, glob, platform, subprocess, io
from PIL import Image, ImageTk

W, H = 200, 140
PLAZA = 40
GAP = 15
BOUND = 10
RAD = 60
GRID_SIZE = 50

BAD = "data/bad_spots.json"
for d in ["data", "data/correct", "data/failed"]:
    if not os.path.exists(d): os.mkdir(d)


class B:
    def __init__(self, x, y, t):
        self.x, self.y, self.t = x, y, t
        self.ok = False
        self.w = 30 if t == 'A' else 20
        self.h = 20

    def d(self): return {"t": self.t, "x": int(self.x), "y": int(self.y)}

    def center(self): return (self.x + self.w / 2, self.y + self.h / 2)


def get_bad():
    try:
        with open(BAD, 'r') as f:
            return set(tuple(x) for x in json.load(f))
    except:
        return set()


def save_bad(s):
    with open(BAD, 'w') as f: json.dump(list(s), f)


def is_dup(sig):
    files = glob.glob("data/correct/*.json") + glob.glob("data/failed/*.json")
    for f in files:
        try:
            if json.load(open(f)).get("sig") == sig: return True
        except:
            pass
    return False


def sig(arr):
    s = [f"{b.t}{int(b.x)}{int(b.y)}" for b in arr]
    s.sort()
    return "-".join(s)


def overlap(n, arr):
    px1, px2 = (W - PLAZA) / 2, (W + PLAZA) / 2
    py1, py2 = (H - PLAZA) / 2, (H + PLAZA) / 2
    if not (n.x + n.w < px1 or n.x > px2 or n.y + n.h < py1 or n.y > py2): return True
    for b in arr:
        if not (n.x + n.w + GAP <= b.x or n.x >= b.x + b.w + GAP or n.y + n.h + GAP <= b.y or n.y >= b.y + b.h + GAP):
            return True
    return False


def check_r4(arr):
    for b in arr:
        if b.t == 'A':
            c1 = b.center()
            b.ok = any(
                b2.t == 'B' and math.sqrt((c1[0] - b2.center()[0]) ** 2 + (c1[1] - b2.center()[1]) ** 2) <= RAD for b2
                in arr)
        else:
            b.ok = True


def gen(bad_zones):

    past_successes = glob.glob("data/correct/*.json")

    if past_successes and random.random() > 0.3:
        try:

            parent_file = random.choice(past_successes)
            with open(parent_file, 'r') as f:
                data = json.load(f)


            arr = []
            if "buildings" in data:
                for b_data in data["buildings"]:
                    arr.append(B(b_data["x"], b_data["y"], b_data["t"]))

            if arr:
                for _ in range(3):
                    idx = random.randint(0, len(arr) - 1)
                    victim = arr.pop(idx)  # Remove


                    w, h = victim.w, victim.h
                    for _ in range(20):
                        rx = random.uniform(BOUND, W - BOUND - w)
                        ry = random.uniform(BOUND, H - BOUND - h)
                        n = B(rx, ry, victim.t)
                        if not overlap(n, arr):
                            arr.append(n)
                            break

                check_r4(arr)
                valid = all(b.ok for b in arr)
                return arr, valid, []
        except:
            pass

    arr = []
    q = ['A'] * 12 + ['B'] * 20
    random.shuffle(q)
    mistakes = []

    for t in q:
        w = 30 if t == 'A' else 20
        h = 20
        for _ in range(50):
            rx = random.uniform(BOUND, W - BOUND - w)
            ry = random.uniform(BOUND, H - BOUND - h)
            k = (round(rx / 5) * 5, round(ry / 5) * 5)


            if k in bad_zones and random.random() > 0.2: continue

            n = B(rx, ry, t)
            if not overlap(n, arr):
                arr.append(n)
                break
            else:
                mistakes.append(k)

    check_r4(arr)
    valid = all(b.ok for b in arr)
    return arr, valid, mistakes


def draw_blueprint(ax, layout, valid, idx, batch_num):
    ax.clear()
    ax.set_xlim(0, W)
    ax.set_ylim(-40, H)
    ax.axis('off')

    site_rect = patches.Rectangle((0, 0), W, H, fill=True, facecolor='white', edgecolor='#7f8c8d', linewidth=1)
    ax.add_patch(site_rect)
    ax.add_patch(patches.Rectangle((0, -40), W, 40, fill=True, facecolor='#f9f9f9', edgecolor='#bdc3c7', linewidth=1))
    ax.plot([0, W], [0, 0], color='#bdc3c7', linewidth=1)

    px, py = (W - PLAZA) / 2, (H - PLAZA) / 2
    ax.add_patch(
        patches.Rectangle((px, py), PLAZA, PLAZA, linewidth=1, edgecolor='#95a5a6', facecolor='#f0f3f4', hatch='///'))
    ax.text(W / 2, H / 2, "PLAZA\n40m", ha='center', va='center', fontsize=6, color='#7f8c8d', fontweight='bold')

    # Gap Lines
    for i, b1 in enumerate(layout):
        for j, b2 in enumerate(layout):
            if i >= j: continue

            c1, c2 = b1.center(), b2.center()
            dist_center = math.sqrt((c1[0] - c2[0]) ** 2 + (c1[1] - c2[1]) ** 2)
            if dist_center > 45: continue

            real_dist = dist_center - (b1.w / 2 + b2.w / 2)
            if real_dist < 0: real_dist = 0

            if real_dist < 25:
                line_col = '#e74c3c' if real_dist < 15 else '#bdc3c7'
                style = ':' if real_dist < 15 else '--'
                lw = 0.8 if real_dist < 15 else 0.4

                line, = ax.plot([c1[0], c2[0]], [c1[1], c2[1]], color=line_col, linestyle=style, linewidth=lw, zorder=1)
                line.set_clip_path(site_rect)

                mx, my = (c1[0] + c2[0]) / 2, (c1[1] + c2[1]) / 2
                ax.text(mx, my, f"{int(real_dist)}m", fontsize=5, color='#333', ha='center', va='center',
                        bbox=dict(facecolor='white', edgecolor=line_col, alpha=0.9, pad=0.3, linewidth=0.2), zorder=2)


    count_A = 0
    count_B = 0
    total_area = 0

    for b in layout:
        total_area += b.w * b.h
        if b.t == 'A':
            count_A += 1
            color = '#3498db' if b.ok else '#e74c3c'
            edge = '#2980b9' if b.ok else '#c0392b'
            if not b.ok:
                err = patches.Circle(b.center(), RAD, fill=False, edgecolor='#e74c3c', linestyle='--', linewidth=1.5,
                                     zorder=5)
                ax.add_patch(err)
                err.set_clip_path(site_rect)
        else:
            count_B += 1
            color, edge = '#9b59b6', '#8e44ad'

        ax.add_patch(patches.Rectangle((b.x, b.y), b.w, b.h, linewidth=0.5, edgecolor=edge, facecolor=color, alpha=0.9,
                                       zorder=3))
        ax.text(b.center()[0], b.center()[1], b.t, color='white', ha='center', va='center', fontsize=7,
                fontweight='bold', zorder=4)

        if b.x < 15:
            ax.annotate(text=f"{int(b.x)}m", xy=(b.x, b.center()[1]), xytext=(0, b.center()[1]),
                        arrowprops=dict(arrowstyle='->', color='#7f8c8d', lw=0.5), fontsize=5, color='#555', ha='left',
                        va='center')
        if W - (b.x + b.w) < 15:
            dist = W - (b.x + b.w)
            ax.annotate(text=f"{int(dist)}m", xy=(b.x + b.w, b.center()[1]), xytext=(W, b.center()[1]),
                        arrowprops=dict(arrowstyle='->', color='#7f8c8d', lw=0.5), fontsize=5, color='#555', ha='right',
                        va='center')


    ax.text(5, -10, f"Tower A: {count_A}", fontsize=9, fontweight='bold', color='#2980b9', va='center')
    ax.text(5, -25, f"Tower B: {count_B}", fontsize=9, fontweight='bold', color='#8e44ad', va='center')

    status = "VALID" if valid else "INVALID"
    stat_col = '#27ae60' if valid else '#c0392b'
    ax.text(W - 5, -10, f"Total Area: {total_area} m²", fontsize=9, color='#555', ha='right', va='center')
    ax.text(W - 5, -25, status, fontsize=10, fontweight='bold', color=stat_col, ha='right', va='center')

    if idx == 0:
        ax.text(W / 2, -35, f"BATCH #{batch_num}", fontsize=8, color='#95a5a6', ha='center', fontweight='bold')



class CanvasImage:
    def __init__(self, canvas, item_id, pil_image, original_x, original_y):
        self.canvas = canvas
        self.item_id = item_id
        self.pil_image = pil_image
        self.pil_proxy = pil_image.resize((pil_image.width // 8, pil_image.height // 8), Image.Resampling.NEAREST)
        self.orig_w, self.orig_h = pil_image.size
        self.tk_image = None
        self.is_high_quality = False



class InfiniteCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.config(bg='#eaeaea', highlightthickness=0)
        self.total_scale = 1.0
        self.images_on_canvas = {}
        self.zoom_timer = None
        self.draw_grid()

        self.bind("<ButtonPress-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<MouseWheel>", self.on_zoom)  # Windows
        self.bind("<Button-4>", self.on_zoom)  # Linux Up
        self.bind("<Button-5>", self.on_zoom)  # Linux Down

    def draw_grid(self):
        size = 50000
        step = GRID_SIZE
        for i in range(-size, size, step):
            color = "#dcdcdc" if i % (step * 4) != 0 else "#bbbbbb"
            self.create_line(i, -size, i, size, fill=color, tags="grid")
            self.create_line(-size, i, size, i, fill=color, tags="grid")
        self.tag_lower("grid")

    def on_click(self, event):
        self.scan_mark(event.x, event.y)

    def on_drag(self, event):
        self.scan_dragto(event.x, event.y, gain=1)
        if not self.zoom_timer:
            self.zoom_timer = self.after(200, self.render_high_quality)

    def on_zoom(self, event):
        if event.num == 5 or event.delta < 0:
            step_scale = 0.9
        else:
            step_scale = 1.1

        new_total = self.total_scale * step_scale
        if new_total < 0.1 or new_total > 5.0: return
        self.total_scale = new_total

        mouse_x = self.canvasx(event.x)
        mouse_y = self.canvasy(event.y)
        self.scale("all", mouse_x, mouse_y, step_scale, step_scale)

        for item_id, img_obj in self.images_on_canvas.items():
            new_w = int(img_obj.orig_w * self.total_scale)
            new_h = int(img_obj.orig_h * self.total_scale)
            if new_w <= 10 or new_h <= 10: continue

            resized_pil = img_obj.pil_proxy.resize((new_w, new_h), Image.Resampling.NEAREST)
            new_tk_img = ImageTk.PhotoImage(resized_pil)
            self.itemconfig(item_id, image=new_tk_img)
            img_obj.tk_image = new_tk_img
            img_obj.is_high_quality = False

        if self.zoom_timer: self.after_cancel(self.zoom_timer)
        self.zoom_timer = self.after(300, self.render_high_quality)

    def render_high_quality(self):
        x1 = self.canvasx(0)
        y1 = self.canvasy(0)
        x2 = self.canvasx(self.winfo_width())
        y2 = self.canvasy(self.winfo_height())

        for item_id, img_obj in self.images_on_canvas.items():
            new_w = int(img_obj.orig_w * self.total_scale)
            new_h = int(img_obj.orig_h * self.total_scale)
            if new_w <= 10 or new_h <= 10: continue

            coords = self.coords(item_id)
            if not coords: continue
            img_cx, img_cy = coords

            img_x1 = img_cx - new_w / 2
            img_y1 = img_cy - new_h / 2
            img_x2 = img_cx + new_w / 2
            img_y2 = img_cy + new_h / 2

            is_visible = not (img_x2 < x1 or img_x1 > x2 or img_y2 < y1 or img_y1 > y2)

            if is_visible:
                if not img_obj.is_high_quality:
                    resized_pil = img_obj.pil_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    new_tk_img = ImageTk.PhotoImage(resized_pil)
                    self.itemconfig(item_id, image=new_tk_img)
                    img_obj.tk_image = new_tk_img
                    img_obj.is_high_quality = True
            else:
                if img_obj.is_high_quality:
                    resized_pil = img_obj.pil_proxy.resize((new_w, new_h), Image.Resampling.NEAREST)
                    new_tk_img = ImageTk.PhotoImage(resized_pil)
                    self.itemconfig(item_id, image=new_tk_img)
                    img_obj.tk_image = new_tk_img
                    img_obj.is_high_quality = False

        self.zoom_timer = None


# MAIN
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Layout Generator Assignment ")
        self.root.geometry("1400x900")
        self.batch_count = 0
        self.all_batches = []
        self.batch_data_map = {}

        # Layout
        self.sidebar = tk.Frame(root, bg="white", width=250)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.toolbar = tk.Frame(root, bg="#2c3e50", height=60)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.canvas = InfiniteCanvas(root)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        tk.Label(self.sidebar, text="PROJECT NAVIGATOR", bg="white", fg="#2c3e50",
                 font=("Segoe UI", 10, "bold")).pack(pady=10)

        search_frame = tk.Frame(self.sidebar, bg="white", padx=10)
        search_frame.pack(fill=tk.X)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_list)
        tk.Entry(search_frame, textvariable=self.search_var, bg="#f0f0f0", relief=tk.FLAT).pack(fill=tk.X, pady=5,
                                                                                                ipady=3)
        tk.Label(search_frame, text="Right-click to save", bg="white", fg="#aaa", font=("Arial", 8)).pack(anchor="w")

        list_frame = tk.Frame(self.sidebar, bg="white")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.scrollbar = tk.Scrollbar(list_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.batch_listbox = tk.Listbox(list_frame, yscrollcommand=self.scrollbar.set,
                                        bg="white", relief=tk.FLAT, font=("Segoe UI", 10),
                                        selectbackground="#3498db", selectforeground="white", activestyle="none")
        self.batch_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.batch_listbox.yview)

        self.batch_listbox.bind('<<ListboxSelect>>', self.on_batch_select)
        if platform.system() == "Darwin":
            self.batch_listbox.bind("<Button-2>", self.show_context_menu)
        else:
            self.batch_listbox.bind("<Button-3>", self.show_context_menu)

        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Save as Image...", command=self.save_batch_image)

        # Toolbar
        tk.Button(self.toolbar, text="GENERATE NEW", command=self.generate,
                  bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), relief=tk.FLAT, padx=15).pack(side=tk.LEFT,
                                                                                                         padx=20,
                                                                                                         pady=10)

        self.status_lbl = tk.Label(self.toolbar, text="Ready.", bg="#2c3e50", fg="#bdc3c7")
        self.status_lbl.pack(side=tk.LEFT, padx=10)

        tk.Button(self.toolbar, text="Open Folder", command=self.open_folder,
                  bg="#34495e", fg="white", relief=tk.FLAT).pack(side=tk.RIGHT, padx=20, pady=10)

        self.canvas.xview_moveto(0.5)
        self.canvas.yview_moveto(0.5)
        self.generate()

    def update_list(self, *args):
        search_term = self.search_var.get().lower()
        self.batch_listbox.delete(0, tk.END)
        for item in self.all_batches:
            if search_term in item.lower():
                self.batch_listbox.insert(tk.END, item)

    def show_context_menu(self, event):
        try:
            self.batch_listbox.selection_clear(0, tk.END)
            self.batch_listbox.selection_set(self.batch_listbox.nearest(event.y))
            self.batch_listbox.activate(self.batch_listbox.nearest(event.y))
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def save_batch_image(self):
        selection = self.batch_listbox.curselection()
        if not selection: return

        batch_name = self.batch_listbox.get(selection[0])
        try:
            batch_num = int(batch_name.split("#")[1])
            pil_img = self.batch_data_map.get(batch_num)

            if pil_img:
                filename = filedialog.asksaveasfilename(
                    defaultextension=".png", filetypes=[("PNG files", "*.png")],
                    initialfile=f"Batch_{batch_num}.png", title=f"Save {batch_name}"
                )
                if filename:
                    pil_img.save(filename)
                    messagebox.showinfo("Success", f"Saved {batch_name}!")
        except Exception:
            messagebox.showerror("Error", "Could not save.")

    def on_batch_select(self, event):
        selection = self.batch_listbox.curselection()
        if not selection: return

        batch_name = self.batch_listbox.get(selection[0])
        batch_num = batch_name.split("#")[1]
        tag = f"batch_{batch_num}_ref"
        coords = self.canvas.coords(tag)
        if not coords: return

        target_x, target_y = coords[0], coords[1]
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        screen_center_x, screen_center_y = self.canvas.canvasx(w / 2), self.canvas.canvasy(h / 2)

        self.canvas.move("all", screen_center_x - target_x, screen_center_y - target_y)

    def generate(self):
        self.batch_count += 1
        self.status_lbl.config(text="Processing High-Res Image...")
        self.root.update_idletasks()

        bad = get_bad()
        fig, ax_arr = plt.subplots(1, 4, figsize=(16, 4.5), dpi=140)
        fig.patch.set_alpha(0)
        axes = ax_arr.flatten()

        for i in range(4):
            ax = axes[i]
            while True:
                l, v, err = gen(bad)
                s = sig(l)
                if not is_dup(s): break
                if len(l) == 0: break

            folder = "data/correct" if v else "data/failed"
            try:

                b_data = [{"t": b.t, "x": b.x, "y": b.y} for b in l]
                with open(f"{folder}/{random.randint(11111, 99999)}.json", "w") as f:
                    json.dump({"sig": s, "buildings": b_data}, f)
            except:
                pass
            if not v:
                for e in err: bad.add(e)

            draw_blueprint(ax, l, v, i, self.batch_count)

        save_bad(bad)
        plt.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=140, bbox_inches='tight')
        buf.seek(0)
        pil_img = Image.open(buf)
        plt.close(fig)

        self.batch_data_map[self.batch_count] = pil_img


        current_zoom = self.canvas.total_scale
        display_w = int(pil_img.width * current_zoom)
        display_h = int(pil_img.height * current_zoom)

        x0, y0 = self.canvas.canvasx(0), self.canvas.canvasy(0)
        view_w, view_h = self.canvas.winfo_width(), self.canvas.winfo_height()
        cx, cy = x0 + (view_w / 2), y0 + (view_h / 2)

        step_x = display_w + 50
        step_y = display_h + 50

        found_x, found_y = cx, cy
        x, y = 0, 0
        dx, dy = 0, -1

        for _ in range(100):
            test_x = cx + (x * step_x)
            test_y = cy + (y * step_y)

            x1, y1 = test_x - display_w / 2, test_y - display_h / 2
            x2, y2 = test_x + display_w / 2, test_y + display_h / 2

            overlaps = self.canvas.find_overlapping(x1 + 20, y1 + 20, x2 - 20, y2 - 20)
            content_hits = [t for t in overlaps if "content" in self.canvas.gettags(t)]

            if not content_hits:
                found_x, found_y = test_x, test_y
                break

            if x == y or (x < 0 and x == -y) or (x > 0 and x == 1 - y):
                dx, dy = -dy, dx
            x, y = x + dx, y + dy

        init_tk_img = ImageTk.PhotoImage(
            pil_img.resize((display_w // 8, display_h // 8), Image.Resampling.NEAREST).resize((display_w, display_h),
                                                                                              Image.Resampling.NEAREST))

        batch_tag = f"batch_{self.batch_count}_ref"
        item_id = self.canvas.create_image(found_x, found_y, image=init_tk_img, anchor="center",
                                           tags=(batch_tag, "content"))

        self.canvas.images_on_canvas[item_id] = CanvasImage(self.canvas, item_id, pil_img, found_x, found_y)
        self.canvas.images_on_canvas[item_id].tk_image = init_tk_img

        self.canvas.after(300, self.canvas.render_high_quality)

        batch_name = f"Batch #{self.batch_count}"
        self.all_batches.append(batch_name)
        if self.search_var.get() == "":
            self.batch_listbox.insert(tk.END, batch_name)
            self.batch_listbox.yview(tk.END)
        else:
            self.update_list()

        self.status_lbl.config(text=f"Generated {batch_name}")

    def open_folder(self):
        path = os.path.abspath("data")
        try:
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception:
            messagebox.showerror("Error", "Could not open folder.")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()