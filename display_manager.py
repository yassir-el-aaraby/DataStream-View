import tkinter as tk
from tkinter import ttk
from data.gatway_vars import *
import json
import time
# custom class
from filter_objects import FilterObjects

class DisplayManager:
    canvas = None
    window = None
    paused = False
    full_data_loaded = False
    rectangle_instances=[]
    class_instances = []
    data = FilterObjects.filtered_data
    def __init__(self, master, columns, height=5, uniq_id=None):
        self.master = master
        self.columns = columns
        self.uniq_id = uniq_id
        self.displayed_entries = set()
        self.tree = ttk.Treeview(self.master, columns=self.columns, show="headings", height=height)

    def display_data_in_treeview(self, tree, data=None):
        print(len(FilterObjects.filtered_data_large))
        # Clear existing data in the treeview
        for item in tree.get_children():
            tree.delete(item)

        # Use the provided data or the class attribute if None
        data_to_display = data if data is not None else FilterObjects.filtered_data

        # Insert new data into the treeview
        if self.uniq_id is None:
            for row in data_to_display:
                values = [row.get(col_name, "") for col_name in self.columns]
                tree.insert('', 'end', values=values)
        else:
            for row in data_to_display:
                # Check if uniq_id matches the gmac in the object
                if row.get('gmac') == globals()[self.uniq_id]:
                    values = [row.get(col_name, "") for col_name in self.columns]
                    tree.insert('', 'end', values=values)


    def create_table(self, row, col, col_width, table_name=''):
        table_label = tk.Label(self.master, text=table_name, font=("Fira Code", 8, "bold"))
        table_label.grid(row=row - 1, column=col, pady=(0, 0))
        column_ids = {}
        for i, col_name in enumerate(self.columns):
            column_ids[col_name] = i
            self.tree.heading(col_name, text=col_name)
            print(col_name)
            if col_name == "rssi"and table_name is not '':
                self.tree.column(column_ids[col_name], width=35, anchor=tk.CENTER, stretch=False)
            elif col_name== "time" and table_name is not '':
                self.tree.column(column_ids[col_name], width=168, anchor=tk.CENTER, stretch=False)
            else:
                self.tree.column(column_ids[col_name], width=col_width, anchor=tk.CENTER, stretch=False)
        self.tree.grid(row=row, column=col, pady=(0, 0), sticky='nsew')
        self.master.columnconfigure(col, weight=1)

        # Add scrollbar for Treeview
        scroll_y = ttk.Scrollbar(self.master, orient="vertical", command=self.tree.yview)
        scroll_y.grid(row=row, column=col + 2, sticky='ns')
        self.tree.configure(yscrollcommand=scroll_y.set)

        # Get the current scrollbar position
        scroll_position = scroll_y.get()

        # Display data in the Treeview
        self.display_data_in_treeview(self.tree)

        # Set the scrollbar position to the previous value
        scroll_y.set(*scroll_position)


    # a function to update filtering query text
    def update_text(canvas, g,d,r,text):
        if g == '' and d == '' and r == '':
            canvas.itemconfig(text, text='No filters applied')
        else:
            canvas.itemconfig(text, text=f'filter query: {g}, {d}, {r}')
    
    # filters tables data
    def update_tables_data():
        for i in DisplayManager.class_instances:
            if not DisplayManager.paused:
                i.display_data_in_treeview(i.tree)
            elif not DisplayManager.full_data_loaded:
                i.display_data_in_treeview(i.tree, data=FilterObjects.filtered_data_large)

    
    def filter(gmac_var, dmac_var, rssi_var):
        FilterObjects.filter(gmac_var,dmac_var,rssi_var)
        # print(DisplayManager.class_instances)

    def clear_filter(gmac_var, dmac_var, rssi_var):
        FilterObjects.clear_filter(gmac_var,dmac_var,rssi_var)
        DisplayManager.paused= False
        DisplayManager.full_data_loaded = False
        if len(FilterObjects.filtered_data) >= 100:
            FilterObjects.filtered_data = [] 
    # update tables data
        
    def validate_gmac(gmac):
        with open("./data/name_mappings.yaml", 'r') as file:
            data = yaml.safe_load(file)
        value = data.get('gmac', {}).get(gmac, None)
        if "Exit" in value:
            return DisplayManager.rectangle_instances[0]
        elif "Entrance" in value:
            return DisplayManager.rectangle_instances[1]

    def change_color(gmac, message_type):
        if message_type == "alive":
            DisplayManager.canvas.itemconfig(DisplayManager.validate_gmac(gmac), fill="white")  # Changement de couleur en noir
            DisplayManager.window.after(100, lambda: DisplayManager.canvas.itemconfig(DisplayManager.validate_gmac(gmac), fill="yellow"))
        elif message_type == "advData":
            DisplayManager.canvas.itemconfig(DisplayManager.validate_gmac(gmac), fill="white")  # Changement de couleur en noir
            DisplayManager.window.after(100, lambda: DisplayManager.canvas.itemconfig(DisplayManager.validate_gmac(gmac), fill="green"))

    def pause_table():
        DisplayManager.paused = True
        DisplayManager.update_tables_data()
        DisplayManager.full_data_loaded = True
        print("paused")