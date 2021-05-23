import cv2
import numpy as np
from typing import Union

# https://jdhao.github.io/2019/07/06/python_opencv_pil_image_to_bytes/
def mat_to_bytes(mat: np.ndarray) -> Union[bytes, None]:
    is_success, im_buf_arr = cv2.imencode(".jpg", mat)

    if not is_success:
        return None

    byte_im = im_buf_arr.tobytes()

    return byte_im

def draw_detection(frame, detection):
        (label, confidence, box, color) = detection

        text = '{}: {:.2f}'.format(label, confidence)

        cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), color, 2)

        x, y = box[:2]

        if y - 10 > 0:
            Y = y - 10
            X = x
        else:
            Y = y + 10
            X = x + 10

        cv2.putText(frame, text, (X, Y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, color, 2)
