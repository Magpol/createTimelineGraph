import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.dates import DateFormatter
from datetime import timedelta
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

class GraphPlotterApp:
    def __init__(self, master):
        self.master = master
        master.title("TimeLine v1.0 - https://github.com/Magpol/createTimelineGraph")

        self.width_var = tk.DoubleVar(value=0.02)
        self.hours_var = tk.DoubleVar(value=0)
        self.file_path_var = tk.StringVar()
        self.graph_type_var = tk.StringVar(value='bars')
        self.resample_var = tk.StringVar(value='minutes')

        tk.Label(master, text="Stapelbredd (vid val av stapeldiagram):").grid(row=0, column=0, sticky=tk.W)
        tk.Scale(master, from_=0.01, to=0.5, resolution=0.01, variable=self.width_var, orient=tk.HORIZONTAL,
                 length=200, command=self.update_graph).grid(row=0, column=1)

        tk.Label(master, text="Tidskompensering:").grid(row=1, column=0, sticky=tk.W)
        tk.Scale(master, from_=0, to=24, resolution=1, variable=self.hours_var, orient=tk.HORIZONTAL,
                 length=200, command=self.update_graph).grid(row=1, column=1)

        tk.Button(master, text="Välj fil", command=self.choose_file).grid(row=2, column=0, columnspan=2)

        tk.Label(master, text="Fil med data:").grid(row=3, column=0, sticky=tk.W)
        tk.Entry(master, textvariable=self.file_path_var, state='readonly', width=30).grid(row=3, column=1, columnspan=2)

        tk.Label(master, text="Typ av diagram:").grid(row=4, column=0, sticky=tk.W)
        ttk.Combobox(master, values=['bars', 'dots', 'plots'], textvariable=self.graph_type_var).grid(row=4, column=1)
        self.graph_type_var.trace_add('write', self.update_graph)

        tk.Label(master, text="Val av tidsintervall:").grid(row=5, column=0, sticky=tk.W)
        ttk.Combobox(master, values=['minutes', 'hours', 'days'], textvariable=self.resample_var).grid(row=5, column=1)
        self.resample_var.trace_add('write', self.update_graph)

        self.ax = None

        self.fig, self.ax = plt.subplots(figsize=(15, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=6, column=0, columnspan=2)

        self.width_var.trace_add('write', self.update_graph)
        self.hours_var.trace_add('write', self.update_graph)

    def choose_file(self):
        file_path = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file_path_var.set(file_path)
            self.generate_graph()

    def update_graph(self, *args):
        self.generate_graph()

    def generate_graph(self):
        file_path = self.file_path_var.get()

        if not file_path:
            tk.messagebox.showerror("Error", "Please select a CSV file.")
            return

        df = pd.read_csv(file_path, header=None, names=['Dates'], parse_dates=['Dates'])

        df['Dates'] = df['Dates'] + timedelta(hours=self.hours_var.get())

        df['Count'] = 1

        # Resample the data based on the selected frequency
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
            self.ax.bar(df_resampled.index, df_resampled['Count'], width=width)
        elif self.graph_type_var.get() == 'dots':
            self.ax.plot(df_resampled.index, df_resampled['Count'], 'o')
        elif self.graph_type_var.get() == 'plots':
            self.ax.plot(df_resampled.index, df_resampled['Count'])

        self.ax.set_xlabel('Tid')
        self.ax.set_ylabel('Antal händelser')
        self.ax.set_title('Händelser över tid')
        self.ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))

        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = GraphPlotterApp(root)
    root.mainloop()
