import cv2
import numpy as np
import os


PROTOTXT_PATH = 'models/colorization_deploy_v2.prototxt'
MODEL_PATH = 'models/colorization_release_v2.caffemodel'
KERNEL_PATH = 'models/pts_in_hull.npy'

if not os.path.exists(PROTOTXT_PATH):
    raise FileNotFoundError(f"Missing file: {PROTOTXT_PATH}")

if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Missing file: {MODEL_PATH}")

if not os.path.exists(KERNEL_PATH):
    raise FileNotFoundError(f"Missing file: {KERNEL_PATH}")


net = cv2.dnn.readNetFromCaffe(PROTOTXT_PATH, MODEL_PATH)

points = np.load(KERNEL_PATH)
points = points.transpose().reshape(2, 313, 1, 1)

net.getLayer(net.getLayerId("class8_ab")).blobs = [points.astype(np.float32)]
net.getLayer(net.getLayerId("conv8_313_rh")).blobs = [
    np.full([1, 313], 2.606, dtype="float32")
]

def colorize_image(input_path: str, output_path: str) -> str:


    
    image = cv2.imread(input_path)

    if image is None:
        raise ValueError(f"Could not read image: {input_path}")

  
    normalized = image.astype("float32") / 255.0


    lab = cv2.cvtColor(normalized, cv2.COLOR_BGR2LAB)


    resized = cv2.resize(lab, (224, 224))

    L = cv2.split(resized)[0]
    L -= 50  # mean-centering


    net.setInput(cv2.dnn.blobFromImage(L))
    ab = net.forward()[0, :, :, :].transpose((1, 2, 0))


    ab = cv2.resize(ab, (image.shape[1], image.shape[0]))


    L_original = cv2.split(lab)[0]


    colorized = np.concatenate((L_original[:, :, np.newaxis], ab), axis=2)


    colorized = cv2.cvtColor(colorized, cv2.COLOR_LAB2BGR)


    colorized = np.clip(colorized, 0, 1)


    colorized = (255 * colorized).astype("uint8")


    cv2.imwrite(output_path, colorized)

    return output_path


if __name__ == "__main__":
    input_img = "images/black_n_white_lion.jpg"
    output_img = "images/colorized_output.jpg"

    try:
        result = colorize_image(input_img, output_img)
        print(f" Colorized image saved at: {result}")
    except Exception as e:
        print(f" Error: {e}")