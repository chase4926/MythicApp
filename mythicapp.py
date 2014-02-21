

import os
import yaml
from tkinter import *
from tkinter import ttk


def find_data_file(filename):
  if getattr(sys, 'frozen', False):
    # The application is frozen
    datadir = os.path.dirname(sys.executable)
  else:
    # The application is not frozen
    # Change this bit to match where you store your data files:
    datadir = os.path.dirname(__file__)
  return os.path.join(datadir, filename)

with open(find_data_file('config.yml')) as f:
  config_file = yaml.safe_load(f)


class FateChart:
  #Holds data necessary for fatechart operations
  ranks = ('Miniscule', 'Weak', 'Low', 'Below Average', 'Average', 'Above Average', 'High', 'Exceptional', 'Incredible', 'Awesome', 'Superhuman')
  def __init__(self, fatechart):
    self.fatechart = fatechart
    self.low = 10
    self.mid = 50
    self.high = 91
    self.exc_yes = "Exceptional Yes: 1-10"
    self.yes = "Yes: 11-50"
    self.no = "No: 51-90"
    self.exc_no = "Exceptional No: 91-100"

  def update_strings(self):
    num_list = []
    for i in range(100):
      num = i + 1
      if num >= self.high:
        num_list.append(3)
      elif num > self.mid:
        num_list.append(2)
      elif num > self.low:
        num_list.append(1)
      else:
        num_list.append(0)
    num_list = [num_list.count(0), num_list.count(1), num_list.count(2), num_list.count(3)]
    if num_list[0] > 0:
      if num_list[0] == 1:
        self.exc_yes = "Exc. Yes: 1"
      else:
        self.exc_yes = "Exc. Yes: 1-%s" % (num_list[0])
    else:
      self.exc_yes = "Exc. Yes: --"
    if num_list[1] > 0:
      if num_list[0]+1 == num_list[0]+num_list[1]:
        self.yes = "Yes: %s" % (num_list[0]+1)
      else:
        self.yes = "Yes: %s-%s" % (num_list[0]+1, num_list[0]+num_list[1])
    else:
      self.yes = "Yes: --"
    if num_list[2] > 0:
      if num_list[0]+num_list[1]+1 == num_list[0]+num_list[1]+num_list[2]:
        self.no = "No: %s" % (num_list[0]+num_list[1]+1)
      else:
        self.no = "No: %s-%s" % (num_list[0]+num_list[1]+1, num_list[0]+num_list[1]+num_list[2])
    else:
      self.no = "No: --"
    if num_list[3] > 0:
      if num_list[0]+num_list[1]+num_list[2]+1 == num_list[0]+num_list[1]+num_list[2]+num_list[3]:
        self.exc_no = "Exc. No: %s" % (num_list[0]+num_list[1]+num_list[2]+1)
      else:
        self.exc_no = "Exc. No: %s-%s" % (num_list[0]+num_list[1]+num_list[2]+1, num_list[0]+num_list[1]+num_list[2]+num_list[3])
    else:
      self.exc_no = "Exc. No: --"

  def rank_within(self, rank_index):
    if 0 <= rank_index <= 12:
      return TRUE
    else:
      return FALSE

  def offchart_multiple(self, rank_index):
    if rank_index < 0:
      return abs(rank_index) * 20
    elif rank_index > 12:
      return (rank_index - 12) * 20
    else:
      return 0

  def get_prob(self, a_rank, d_rank):
    # a_rank (acting rank) & d_rank (difficulty rank) are the index of the rank with 0 being miniscule, and 10 being superhuman
    # anything below 0 is miniscule > 1 & anything above 10 is superhuman > 1
    a_rank += 1
    d_rank += 1
    if self.rank_within(a_rank) and self.rank_within(d_rank):
      return self.fatechart[a_rank][d_rank]
    elif self.rank_within(a_rank) and d_rank < 0:
      # Left case
      return self.fatechart[a_rank][0] + self.offchart_multiple(d_rank)
    elif self.rank_within(a_rank) and d_rank > 12:
      # Right case
      return self.fatechart[a_rank][12] - self.offchart_multiple(d_rank)
    elif a_rank < 0 and self.rank_within(d_rank):
      # Up case
      return self.fatechart[0][d_rank] - self.offchart_multiple(a_rank)
    elif a_rank > 12 and self.rank_within(d_rank):
      # Down case
      return self.fatechart[12][d_rank] + self.offchart_multiple(a_rank)
    elif a_rank < 0 and d_rank < 0:
      # top-left case
      return self.fatechart[0][0] - self.offchart_multiple(a_rank) + self.offchart_multiple(d_rank)
    elif a_rank < 0 and d_rank > 12:
      # top-right case
      return self.fatechart[0][12] - self.offchart_multiple(a_rank) - self.offchart_multiple(d_rank)
    elif a_rank > 12 and d_rank < 0:
      # bottom-left case
      return self.fatechart[12][0] + self.offchart_multiple(a_rank) + self.offchart_multiple(d_rank)
    elif a_rank > 12 and d_rank > 12:
      # bottom-right case
      return self.fatechart[12][12] + self.offchart_multiple(a_rank) - self.offchart_multiple(d_rank)

  def set_prob(self, a_rank, d_rank):
    self.mid = self.get_prob(a_rank, d_rank)
    self.low = round(float(self.mid) / 5.0)
    self.high = self.mid + round(float((100 - self.mid) * 4) / 5.0) + 1
    self.update_strings()

  def to_s(self):
    return "%s | %s | %s" % (self.low, self.mid, self.high)


class FateChartApp(ttk.Frame):
  #This frame contains the entire fatechart app

  class ModifierFrame(ttk.Frame):
    # This frame holds the modifiers buttons & label
    def __init__(self, parent, mod_var):
      super().__init__(parent, padding="3 3 12 12")
      self.parent = parent
      self.mod_var = mod_var
      ttk.Button(self, text='-', width=2, command=lambda: self.lower_modifier(self.mod_var)).grid(column=0, row=0, sticky=W)
      ttk.Button(self, text='+', width=2, command=lambda: self.raise_modifier(self.mod_var)).grid(column=1, row=0, sticky=W)
      ttk.Label(self, textvariable=self.mod_var).grid(column=2, row=0, sticky=W)
    def lower_modifier(self, modifier):
      if modifier.get() <= 1:
        pass
      else:
        modifier.set(modifier.get() - 1)
        self.parent.listbox_update()
    def raise_modifier(self, modifier):
      modifier.set(modifier.get() + 1)
      self.parent.listbox_update()

  def __init__(self, parent):
    super().__init__(parent, padding="3 3 12 12")
    # Initialize & set the required variables
    self.fatechart = FateChart(config_file['fatechart'])
    self.fatechart.set_prob(4, 4)
    self.tk_mythic_ranks = StringVar(value=FateChart.ranks)
    self.act_mini_mod = IntVar(value=1)
    self.act_super_mod = IntVar(value=1)
    self.diff_mini_mod = IntVar(value=1)
    self.diff_super_mod = IntVar(value=1)
    self.exc_yes = StringVar(value=self.fatechart.exc_yes)
    self.yes = StringVar(value=self.fatechart.yes)
    self.no = StringVar(value=self.fatechart.no)
    self.exc_no = StringVar(value=self.fatechart.exc_no)
    # Create & configure the widgets
    self.create_widgets()
    # Add some padding
    for child in self.winfo_children(): child.grid_configure(padx=4, pady=4)

  def create_widgets(self):
    # Static Labels
    ttk.Label(self, text='Acting Rank:', font=('', 24)).grid(column=0, row=0, sticky=W)
    ttk.Label(self, text='Difficulty Rank:', font=('', 24)).grid(column=1, row=0, sticky=W)
    ttk.Separator(self, orient=HORIZONTAL).grid(column=0, row=1, sticky=(W, E), columnspan=3)
    # Acting miniscule modifiers
    self.acting_miniscule_frame = FateChartApp.ModifierFrame(self, self.act_mini_mod)
    self.acting_miniscule_frame.grid(column=0, row=2, sticky=(N, W, E, S))
    for child in self.acting_miniscule_frame.winfo_children(): child.grid_configure(padx=4, pady=4)
    # Difficulty miniscule modifiers
    self.difficulty_miniscule_frame = FateChartApp.ModifierFrame(self, self.diff_mini_mod)
    self.difficulty_miniscule_frame.grid(column=1, row=2, sticky=(N, W, E, S))
    for child in self.difficulty_miniscule_frame.winfo_children(): child.grid_configure(padx=4, pady=4)
    # Acting superhuman modifiers
    self.acting_superhuman_frame = FateChartApp.ModifierFrame(self, self.act_super_mod)
    self.acting_superhuman_frame.grid(column=0, row=8, sticky=(N, W, E, S))
    for child in self.acting_superhuman_frame.winfo_children(): child.grid_configure(padx=4, pady=4)
    # Difficulty superhuman modifiers
    self.difficulty_superhuman_frame = FateChartApp.ModifierFrame(self, self.diff_super_mod)
    self.difficulty_superhuman_frame.grid(column=1, row=8, sticky=(N, W, E, S))
    for child in self.difficulty_superhuman_frame.winfo_children(): child.grid_configure(padx=4, pady=4)
    # Acting listbox
    self.act_lbox = Listbox(self, listvariable=self.tk_mythic_ranks, height=11, exportselection=0, font=('', 24), selectbackground='#808080')
    self.act_lbox.grid(column=0, row=3, rowspan=4, sticky=(N,S,E,W))
    self.act_lbox.selection_set(4)
    self.act_lbox.bind('<<ListboxSelect>>', self.listbox_update)
    for i in range(0, len(FateChart.ranks), 2):
      self.act_lbox.itemconfigure(i, background='#f0f0ff')
    # Difficulty listbox
    self.diff_lbox = Listbox(self, listvariable=self.tk_mythic_ranks, height=11, exportselection=0, font=('', 24), selectbackground='#808080')
    self.diff_lbox.grid(column=1, row=3, rowspan=4, sticky=(N,S,E,W))
    self.diff_lbox.selection_set(4)
    self.diff_lbox.bind('<<ListboxSelect>>', self.listbox_update)
    for i in range(0, len(FateChart.ranks), 2):
      self.diff_lbox.itemconfigure(i, background='#f0f0ff')
    # String labels
    ttk.Label(self, textvariable=self.exc_yes, font=('', 24)).grid(column=2, row=3, sticky=E)
    ttk.Label(self, textvariable=self.yes, font=('', 24)).grid(column=2, row=4, sticky=E)
    ttk.Label(self, textvariable=self.no, font=('', 24)).grid(column=2, row=5, sticky=E)
    ttk.Label(self, textvariable=self.exc_no, font=('', 24)).grid(column=2, row=6, sticky=E)

  def listbox_update(self, *args):
    active_rank = int(self.act_lbox.curselection()[0])
    if active_rank == 0:
      active_rank -= self.act_mini_mod.get() - 1
    elif active_rank == 10:
      active_rank += self.act_super_mod.get() - 1
    difficulty_rank = int(self.diff_lbox.curselection()[0])
    if difficulty_rank == 0:
      difficulty_rank -= self.diff_mini_mod.get() - 1
    elif difficulty_rank == 10:
      difficulty_rank += self.diff_super_mod.get() - 1
    self.fatechart.set_prob(active_rank, difficulty_rank)
    self.exc_yes.set(self.fatechart.exc_yes)
    self.yes.set(self.fatechart.yes)
    self.no.set(self.fatechart.no)
    self.exc_no.set(self.fatechart.exc_no)


root = Tk()
root.title('Mythic App')

fatechartapp = FateChartApp(root)
fatechartapp.grid(column=0, row=0, sticky=(N, W, E, S))

root.columnconfigure(0, weight=1)
fatechartapp.columnconfigure(0, weight=2)
fatechartapp.columnconfigure(1, weight=2)
fatechartapp.columnconfigure(2, weight=1)
fatechartapp.rowconfigure(0, weight=1)

root.mainloop()

