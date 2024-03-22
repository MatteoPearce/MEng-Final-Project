import matplotlib.pyplot as plt
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm
from CreateVideo import CreateVideo

def CreateCellPics(get_path: str = None,
                   save_path: str = None,
                   savefile: bool = False,
                   interactive: bool = False,
                   show: bool = False) -> list[plt.figure]:

    filename = "reservoir_output.txt"

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

    frames =list()

    for linenum,lineval in tqdm(enumerate(all_lines)):

        current_line = lineval.split()

        for index,line in enumerate(current_line):
            current_line[index] = float(line)

        grid_side = np.sqrt(len(current_line)).astype("int32")
        data = np.reshape(current_line,(grid_side,grid_side))
        fig = plt.figure()
        ax = plt.gca()
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_xticks(np.arange(grid_side))
        ax.set_yticks(np.arange(grid_side))
        im = ax.imshow(data, interpolation='none',animated=True)
        fig.colorbar(im, spacing='proportional')
        ax.set_title(f"frame: {linenum}")
        frames.append(fig)

        if show:
            plt.show()
            input("Press any key for next image")

    #plt.savefig(save_path + f"{linenum+1}.png")
        plt.close()

    return frames

save_path = "/home/matteo/Desktop/VAMPIRE_WORKDIR/"

stuff = CreateCellPics(get_path="/home/matteo/Desktop/VAMPIRE_WORKDIR/",
           save_path=save_path,
           interactive=True,
           show=0)

CreateVideo(save_path,stuff)

