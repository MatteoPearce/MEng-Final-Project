
import matplotlib.pyplot as plt
import matplotlib.animation as animation
def CreateGif(save_path: str = None, frames:list[plt.figure] = None, fps:float = None) -> None:

    if fps is None:
        fps = len(frames)/10

    print("CREATING GIF! \n")

    vid = animation.ArtistAnimation(frames[0],
                                    frames,
                                    interval=fps,
                                    blit=True,
                                    repeat_delay=1000)

    writer = animation.PillowWriter(fps=fps,
                                    metadata=dict(artist='Me'),
                                    bitrate=1800)

    vid.save(save_path + 'cell_magnetisation.gif', writer=writer)

    print("DONE! \n")