import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm
from CreateVideo import CreateVideo

"""
CREATE A HEATMAP OF GRID POLARISATIONS FOR EVERY TIMESTEP

reads the reservoir_output.txt file and for every line creates a heatmap with the polarisations.

currently not automated, requires user. Can easily be easily integrated into main.
"""

def create_cell_pics (get_path: str = None,
                      interactive: bool = False,
                      show: bool = False) -> list[plt.figure]:

    # uses tkinter to manually select reservoir_output.txt
    if interactive:
        main_win = tk.Tk()
        main_win.withdraw() # Hides Tk window
        main_win.geometry('0x0+0+0')
        main_win.deiconify()
        main_win.lift()
        main_win.focus_force()
        file = filedialog.askopenfilename(parent=main_win,
                                          initialdir=get_path,
                                          title= 'Please select file',
                                          filetypes=[('Text files', '*.txt')])

    with open(file, 'r') as f:
        all_lines = f.readlines()
        f.close()

    frame_list =list() # list of frames

    # make a frame from every line
    for linenum,lineval in tqdm(enumerate(all_lines)):

        current_line = lineval.split()

        # convert str to float
        for index , line in enumerate(current_line):
            current_line[index] = float(line)

        # plot heatmap
        grid_side = np.sqrt(len(current_line)).astype("int32")
        data = np.reshape(current_line , (grid_side , grid_side))
        fig = plt.figure()
        ax = plt.gca()
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_xticks(np.arange(grid_side))
        ax.set_yticks(np.arange(grid_side))
        im = ax.imshow(data, interpolation='none',animated=True)
        fig.colorbar(im, spacing='proportional')
        ax.set_title(f"frame: {linenum}")
        frame_list.append(fig)

        if show: # for debugging
            plt.show()
            input("Press any key for next image")

        plt.close() # must be closed or matplotlib will treat all as same image

    return frame_list

#----------------------------------------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------------------------------------------------#

frames = create_cell_pics(get_path="/home/matteo/Desktop/VAMPIRE_WORKDIR/" , interactive=True)
save_path = "/home/matteo/Desktop/VAMPIRE_TEST_RESULTS/Cellpics"
CreateVideo(save_path , frames)
