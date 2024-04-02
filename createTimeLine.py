import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
from datetime import timedelta
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
    
class GraphPlotterApp:
    def __init__(self, master):
        self.master = master
        master.title("createTimelineGraph v1.0 - https://github.com/magpol")
        
        self.width_var = tk.DoubleVar(value=0.01)
        self.hours_var = tk.DoubleVar(value=0)
        self.file_path_var = tk.StringVar()
        self.graph_type_var = tk.StringVar(value='bars')
        self.resample_var = tk.StringVar(value='minutes')

        tk.Label(master, text="Width of bars (valid when bars is selected):").grid(row=0, column=0, sticky=tk.W)
        tk.Scale(master, from_=0.01, to=0.5, resolution=0.01, variable=self.width_var, orient=tk.HORIZONTAL,
                 length=200, command=self.update_graph).grid(row=0, column=1, sticky=tk.W)

        tk.Label(master, text="Time adjustment:").grid(row=1, column=0, sticky=tk.W)
        tk.Scale(master, from_=-12, to=12, resolution=1, variable=self.hours_var, orient=tk.HORIZONTAL,
                 length=200, command=self.update_graph).grid(row=1, column=1, sticky=tk.W)

        tk.Button(master, text="File path:", command=self.choose_file).grid(row=3, column=0, sticky=tk.E)
        tk.Entry(master, textvariable=self.file_path_var, state='readonly', width=60).grid(row=3, column=1, sticky=tk.W)


        tk.Label(master, text="Type of graph:").grid(row=4, column=0, sticky=tk.W)
        ttk.Combobox(master, values=['bars', 'dots', 'plots'], textvariable=self.graph_type_var).grid(row=4, column=1, sticky=tk.W)
        self.graph_type_var.trace_add('write', self.update_graph)

        tk.Label(master, text="Timeunit:").grid(row=5, column=0, sticky=tk.W)
        ttk.Combobox(master, values=['minutes', 'hours', 'days'], textvariable=self.resample_var).grid(row=5, column=1, sticky=tk.W)
        self.resample_var.trace_add('write', self.update_graph)

        self.ax = None

        self.fig, self.ax = plt.subplots(figsize=(15, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=6, column=0, columnspan=3)

        #self.first_last_label = tk.StringVar()
        #tk.Label(master, textvariable=self.first_last_label).grid(row=7, column=0, rowspan=2)


        self.width_var.trace_add('write', self.update_graph)
        self.hours_var.trace_add('write', self.update_graph)
       # Quit button
        tk.Button(master, text="Quit", command=master.quit).grid(row=8, column=0, sticky=tk.E)
        tk.Button(master, text="Save as JPG", command=self.save_as_jpg).grid(row=8, column=1, sticky=tk.W)


    def choose_file(self):
        file_path = filedialog.askopenfilename(title="Choose CSV File", filetypes=[("CSV file", "*.csv")])
        if file_path:
            self.file_path_var.set(file_path)
            self.generate_graph()

    def update_graph(self, *args):
        self.generate_graph()

    def generate_graph(self):
        file_path = self.file_path_var.get()

        if not file_path:
            tk.messagebox.showerror("Error!", "Please select a valid CSV file.")
            return

        df = pd.read_csv(file_path, header=None, names=['Dates'], parse_dates=['Dates'])
        df['Dates'] = pd.to_datetime(df['Dates'])  # Ensure 'Dates' column is in datetime format
        df['Dates'] = df['Dates'] + timedelta(hours=self.hours_var.get())

        first_date = df['Dates'].min()
        last_date = df['Dates'].max()
        date_range = last_date - first_date

        df['Count'] = 1

        resample_freq = self.resample_var.get()
        if resample_freq == 'minutes':
            resample_freq = 'T'  # 'T' is the code for minutes
        elif resample_freq == 'hours':
            resample_freq = 'H'  # 'H' is the code for hours
        elif resample_freq == 'days':
            resample_freq = 'D'  # 'D' is the code for days
        df_resampled = df.resample(resample_freq, on='Dates').count()

        width = self.width_var.get()

        self.ax.clear()

        if self.graph_type_var.get() == 'bars':
            self.ax.bar(df_resampled.index.to_numpy(), df_resampled['Count'].to_numpy(), width=width)
        elif self.graph_type_var.get() == 'dots':
            self.ax.plot(df_resampled.index.to_numpy(), df_resampled['Count'].to_numpy(), 'o')
        elif self.graph_type_var.get() == 'plots':
            self.ax.plot(df_resampled.index.to_numpy(), df_resampled['Count'].to_numpy())

        self.ax.set_xlabel(f"Time in {self.resample_var.get()}")
        self.ax.set_ylabel('Number of events')
        self.ax.set_title(f"Date range: {first_date.strftime('%Y-%m-%d %H:%M:%S')} - {last_date.strftime('%Y-%m-%d %H:%M:%S')}")

        # Adjust the DateFormatter based on the date range
        if date_range > timedelta(days=3):
            self.ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
        else:
            self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))

        self.canvas.draw()


    def save_as_jpg(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".jpg", filetypes=[("JPEG files", "*.jpg")])
        if file_path:
            self.fig.savefig(file_path, format='jpg', bbox_inches='tight')
            tk.messagebox.showinfo("Save as JPG", "Image saved!")

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphPlotterApp(root)
    root.mainloop()
