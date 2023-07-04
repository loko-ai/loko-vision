import logging
from pathlib import Path
from PIL import Image
import io
import zipfile

from loguru import logger
from sanic import SanicException

from utils.service_utils import send_message

img_format_accepted = [".jpg", "jpeg", ".png", ".tiff", ".bmp", ".svg"]


class ReadImgsException(Exception):
    pass


def read_imgs(f, predictor_name):
    bytes = f.body
    images = []
    labels = []
    fnames = []
    possible_labels = []
    temp = io.BytesIO(bytes)
    unsupported_images = 0
    if zipfile.is_zipfile(temp):
        logger.debug("Using zip file to extract and collect images..")
        with zipfile.ZipFile(temp) as zip:
            for name in zip.filelist:
                if not name.is_dir():
                    fname = Path(name.filename)
                    if fname.suffix in img_format_accepted:
                        img_labels = fname.parts[1:-1]
                        if img_labels not in possible_labels:
                            possible_labels.append(img_labels)
                        if not img_labels:
                            img_labels = fname.parts[0:-1]
                        try:
                            img = Image.open(io.BytesIO(zip.read(name.filename)))
                            images.append(img)
                            labels.append(img_labels)
                            fnames.append(fname.name)
                        except Exception as e:
                            unsupported_images += 1
                            logger.exception(e)
                            logger.error(f'ERROR reading img: {fname}')
                    else:
                        img_labels = fname.parts[1:-1]
                        if img_labels not in possible_labels:
                            possible_labels.append(img_labels)
                        unsupported_images += 1
    else:
        logger.debug("single file to extract and collect")
        fname = Path(f.name)
        img = Image.open(temp)
        images.append(img)
        img_label = (fname.stem,)
        logger.debug(img_label)
        fnames.append(f.name)
        labels.append(img_label)
    n_images = len(images)
    if n_images == 0:
        error_msg = f"Error with empty folder parsed or unsupported images type. N. of unsupported images {unsupported_images}. Please, check your input data."
        status_msg = "Empty Dataset: check the Logs section to know more about!"
        send_message(predictor_name, status_msg)

        raise SanicException(error_msg)  # aggiungere considerazione sui formati supportati da noi
    # elif n_images<=10 and task!="prediction":
    #     raise SanicException("error")
    logger.debug(f"unique labels: {list(set(labels))}, expected labels: {possible_labels}")
    logger.info(f"N. of unsupported images: {unsupported_images}. Note that this images will not be included in the dataset")
    # logger.debug(f'labels: {labels}')
    return images, labels, fnames


if __name__ == '__main__':
    a = Path("ciao/ciaoslls/mmmn.jpg")
    print(a.suffix)
