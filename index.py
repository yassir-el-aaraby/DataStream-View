import tkinter as tk
from tkinter import Canvas, Entry, ttk, Button, PhotoImage, StringVar
from pathlib import Path
import json
import time
#custom classes
from mqtt_handling import *
from display_manager import DisplayManager
# Set paths for assets
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"./assets")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

#closing main window
def on_close():
    window.destroy()
#creating main window
window = tk.Tk()
window.protocol("WM_DELETE_WINDOW", on_close)
window.geometry("1920x1080")
window.resizable(True, True)
window.title("MQTT Data visualizer")
window.configure(bg="#FFFFFF")

# Create Canvas for GUI
canvas = Canvas(
    window,
    bg="#FFFFFF",
    height=1080,
    width=1920,
    bd=0,
    highlightthickness=0,
    relief="ridge"
)
canvas.place(x=0, y=0)
# input values
dynamic_gmac_var = StringVar()
dynamic_dmac_var = StringVar()
dynamic_rssi_var = StringVar()
# rectangles managemenet 
DisplayManager.canvas = canvas
DisplayManager.window = window
# Create GUI elements using Tkinter Designer output
# Entry widgets for filtering
rssi_input = Entry(bd=0, fg="#000716", highlightthickness=0, textvariable=dynamic_rssi_var)
rssi_input.place(x=1216.0, y=7.0, width=103.0, height=24.0)
entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
entry_bg_1 = canvas.create_image(1267.5, 20.0, image=entry_image_1)
canvas.create_text(1144.0, 7.0, anchor="nw", text="RSSI: ", fill="#000000", font=("Fira Code", 20 * -1))

dmac_input = Entry(bd=0, fg="#000716", highlightthickness=0, textvariable=dynamic_dmac_var)
dmac_input.place(x=728.0, y=7.0, width=400.0, height=24.0)
entry_image_2 = PhotoImage(file=relative_to_assets("entry_2.png"))
entry_bg_2 = canvas.create_image(928.0, 20.0, image=entry_image_2)
canvas.create_text(656.0, 7.0, anchor="nw", text="DMAC: ", fill="#000000", font=("Fira Code", 20 * -1))

gmac_input = Entry(bd=0, fg="#000716", highlightthickness=0, textvariable=dynamic_gmac_var)
gmac_input.place(x=239.0, y=7.0, width=400.0, height=24.0)
entry_image_3 = PhotoImage(file=relative_to_assets("entry_3.png"))
entry_bg_3 = canvas.create_image(439.0, 20.0, image=entry_image_3)
canvas.create_text(167.0, 7.0, anchor="nw", text="GMAC: ", fill="#000000", font=("Fira Code", 20 * -1))
canvas.create_text(18.0, 7.0, anchor="nw", text="filters:", fill="#000000", font=("Fira Code", 20 * -1))


# Image
image_image_1 = PhotoImage(file=relative_to_assets("image_1.png"))
image_1 = canvas.create_image(961.0, 419.0, image=image_image_1)

# Colored rectangles
Exit_gw = canvas.create_rectangle(1449.0, 313.0, 1479.0, 343.0, fill="#FF0000", outline="")
Entrance_gw = canvas.create_rectangle(353.0, 619.0, 383.0, 649.0, fill="#FF0000", outline="")
# rectangles = [Exit_gw,RC_gw,RF_gw,LF_gw,LC_gw,Entrance_gw]
rectangles = [Exit_gw,Entrance_gw]
for i in rectangles:
    DisplayManager.rectangle_instances.append(i)
# SECONDARY TABLES ######################################################################
secondary_tables_cols = ["dname", "rssi", "time"]
# frame 1 : Ex_gateway
frame1 = tk.Frame(window, bg="#FFFFFF")
frame1.place(x=1479, y=313, width=283)
frame1_treeview = DisplayManager(frame1, secondary_tables_cols, uniq_id="Exit_gateway_variable")
frame1_treeview.create_table(row=313, col=1479, col_width=80, table_name='Exit gateway')
# # frame 6 : Ent_gateway
frame6 = tk.Frame(window, bg="#FFFFFF")
frame6.place(x=72, y=500, width=283)
frame6_treeview = DisplayManager(frame6, secondary_tables_cols, uniq_id="Entrance_gateway_variable")
frame6_treeview.create_table(row=534, col=86, col_width=80, table_name='Entrance gateway')
#########################################################################################

# Create a frame for the main table
main_table = tk.Frame(window, bg="#FFFFFF")
main_table.place(x=0, y=750, width=1920)

# MAIN TABLE ######################################################
columns = ["gmac", "gname", "dmac", "dname", "majorID", "minorID", "refpower", "rssi", "time"]
main_table_frame = DisplayManager(main_table, columns, height=10)
main_table_frame.create_table(row=760, col=0, col_width=213)

# instances = [main_table_frame,frame1_treeview, frame2_treeview, frame3_treeview, frame4_treeview, frame5_treeview, frame6_treeview]
instances = [main_table_frame,frame1_treeview,  frame6_treeview]
for i in instances:
    DisplayManager.class_instances.append(i)
#########################################################################################
# Buttons #################################################################################################
# filter query text
initial_filter_text = 'No filters applied'
text_item = canvas.create_text(18.0, 42.0, anchor="nw", text=initial_filter_text, fill="#000000", font=("Fira Code", 20 * -1))

# filter button
button_image_1 = PhotoImage(file=relative_to_assets("button_1.png"))
filter_button = Button(image=button_image_1, borderwidth=0, highlightthickness=0, command=lambda: [FilterObjects.set_criteria(dynamic_gmac_var.get(),dynamic_dmac_var.get(), dynamic_rssi_var.get()),######
 DisplayManager.update_text(canvas,dynamic_gmac_var.get(),dynamic_dmac_var.get(),dynamic_rssi_var.get(), text_item)], relief="flat")
filter_button.pack()
filter_button.place(x=1352.0, y=7, width=72.0, height=26.0)

# clear filter button
button_image_2 = PhotoImage(file=relative_to_assets("button_2.png"))
clr_filter_button = Button(image=button_image_2, borderwidth=0, highlightthickness=0, command=lambda: [DisplayManager.clear_filter(dynamic_gmac_var,dynamic_dmac_var,dynamic_rssi_var), DisplayManager.update_tables_data(), DisplayManager.update_text(canvas,dynamic_gmac_var.get(),dynamic_dmac_var.get(),dynamic_rssi_var.get(), text_item)], relief="flat")
clr_filter_button.place(x=1467.0, y=7, width=60.0, height=26.0)

# pause button
button_image_3 = PhotoImage(file=relative_to_assets("button_3.png"))
pause_button = Button(image=button_image_3, borderwidth=0, highlightthickness=0, command=lambda:DisplayManager.pause_table(), relief="flat")
pause_button.place(x=1570.0, y=7, width=72.0, height=26.0)
#window close
try:
    window.mainloop()
except KeyboardInterrupt:
    window.destroy()
