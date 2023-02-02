import logging
from pathlib import Path
from PIL import Image
import io
import zipfile

from utils.logger_utils import logger

img_format_accepted = [".jpg", "jpeg", ".png", ".tiff", ".bmp", ".svg"]

class ReadImgsException(Exception):
    pass

def read_imgs(f):
    bytes = f.body
    images = []
    labels = []
    fnames = []
    temp = io.BytesIO(bytes)
    if zipfile.is_zipfile(temp):
        logger.debug("zip file to extract and collect")
        with zipfile.ZipFile(temp) as zip:
            for name in zip.filelist:
                if not name.is_dir():
                    fname = Path(name.filename)
                    if fname.suffix in img_format_accepted:
                        img_labels = fname.parts[1:-1]
                        if not img_labels:
                            img_labels = fname.parts[0:-1]
                        try:
                            img = Image.open(io.BytesIO(zip.read(name.filename)))
                            images.append(img)
                            labels.append(img_labels)
                            fnames.append(fname.name)
                            logger.debug(f'LABEL: {img_labels} - NAME: {fname.name}')
                            # logger.debug(fname)
                            # logger.debug('NAME: %s'%fname.name)
                            # logger.debug('LABEL: %s'%str(img_labels))
                        except Exception as e:
                            logger.exception(e)
                            logger.error(f'ERROR reading img: {fname}')

    else:
        logger.debug("single file to extract and collect")
        fname = Path(f.name)
        logger.debug(f"fname {fname}")
        logger.debug(f"fname.name :::: {fname.stem}")
        img = Image.open(temp)
        images.append(img)
        img_label = (fname.stem,)
        logger.debug(img_label)
        fnames.append(f.name)
        labels.append(img_label)

    return images, labels, fnames


if __name__ == '__main__':
    a = Path("ciao/ciaoslls/mmmn.jpg")
    print(a.suffix)
