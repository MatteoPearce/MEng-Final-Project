import matplotlib.pyplot as plt
import cv2
import numpy as np
from PIL import Image
from tqdm import tqdm
def CreateVideo(save_path:str = None,
                frames:list[plt.figure] = None,
                fps: float = None) -> None:

    if fps is None:
        fps = len(frames)/10

    print("CREATING VIDEO! \n")

    video_name = save_path + 'polarisations.avi'

    width, height = frames[0].canvas.get_width_height()
    video = cv2.VideoWriter(video_name, 0, fps, (width, height))

    # Appending the images to the video one by one
    for index,image in tqdm(enumerate(frames)):
        image.canvas.draw()
        image_array = np.array(image.canvas.renderer.buffer_rgba())
        IMAGE = Image.fromarray(image_array)
        image_rgb = IMAGE.convert("RGB")
        video.write(cv2.cvtColor(np.array(image_rgb), cv2.COLOR_RGB2BGR))

        # Deallocating memories taken for window creation
    cv2.destroyAllWindows()
    video.release()  # releasing the video generated

    print("DONE! \n")