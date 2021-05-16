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
