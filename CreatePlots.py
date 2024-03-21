import matplotlib.pyplot as plt
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm
import cv2
from PIL import Image
def CreatePlot(get_path: str = None, save_path: str = None, savefile: bool = False, interactive: bool = False, show: bool = False) -> None:

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

    video_name = save_path + 'polarisations.avi'

    width, height = frames[0].canvas.get_width_height()
    video = cv2.VideoWriter(video_name, 0, 5, (width, height))

    # Appending the images to the video one by one
    for index,image in enumerate(frames):
        image.canvas.draw()
        image_array = np.array(image.canvas.renderer.buffer_rgba())
        IMAGE = Image.fromarray(image_array)
        image_rgb = IMAGE.convert("RGB")
        video.write(cv2.cvtColor(np.array(image_rgb), cv2.COLOR_RGB2BGR))

        # Deallocating memories taken for window creation
    cv2.destroyAllWindows()
    video.release()  # releasing the video generated

CreatePlot(get_path="/home/matteo/Desktop/VAMPIRE_WORKDIR/",
           save_path="/home/matteo/Desktop/VAMPIRE_WORKDIR/",
           interactive=True,
           show=0)