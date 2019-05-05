# encoding: utf-8

"""
@version: 1.0
@author: LeungJain
@time: 2019-04-03 11:00
"""
import math
import numpy as np
import cv2 as cv


class BaseImageCV:

    def __init__(self, img=None, path=None, **kwargs):
        """

        :param img: numpy array with shape=(w, h, a) or cv-image
        :param path:
        """
        self._init_params(**kwargs)
        if img is not None:
            self.img = img
        elif path is not None:
            self.img = cv.imread(path, self.mode)
            if self.img is None:
                raise IOError('not find image from: {}'.format(path))
        else:
            pass
        pass

    def _init_params(self, **kwargs):
        keys = kwargs.keys()
        if 'mode' in keys:
            # 0 :cv.IMREAD_GRAYSCALE
            # 1 :cv.IMREAD_COLOR
            # -1:cv.IMREAD_UNCHANGED
            if kwargs['mode'] in (1, 0, -1):
                self.mode = kwargs['mode']
            else:
                self.mode = 0
        else:
            self.mode = 0
        if 'name' in keys:
            self.name = kwargs['name']
        else:
            self.name = 'image'
        pass

    def show(self):
        cv.imshow(self.name, self.img)
        cv.waitKey(27)  # Esc
        cv.destroyWindow(self.name)
        pass

    def save(self, path):
        cv.imwrite(path, self.img)
        pass

    @classmethod
    def draw(cls):
        pass

    def corp(self, shape='rectangle'):
        if shape in ('rectangle', 'circle'):
            pass
        else:
            raise ValueError('this shape must in (rectangle, circle)')
        img = self.img

        # mouse callback function
        def draw_circle(event, x, y, flags, param):
            if event == cv.EVENT_LBUTTONDOWN:
                param['drawing'] = True
                param['sx'], param['sy'] = x, y
            elif event == cv.EVENT_MOUSEMOVE:
                if param['drawing']:
                    if param['shape'] == 'rectangle':
                        cv.rectangle(img, (param['sx'], param['sy']), (x, y), (0, 255, 0), -1)
                    else:
                        radius = math.sqrt((x - param['sx']) ** 2 + (y - param['sy']) ** 2)
                        cv.circle(img, (param['sx'], param['sy']), int(radius), (0, 0, 255), 1)
            elif event == cv.EVENT_LBUTTONUP:
                param['drawing'] = False
                if param['shape'] == 'rectangle':
                    cv.rectangle(img, (param['sx'], param['sy']), (x, y), (0, 255, 0), -1)
                else:
                    radius = math.sqrt((x - param['sx']) ** 2 + (y - param['sy']) ** 2)
                    cv.circle(img, (param['sx'], param['sy']), int(radius), (0, 0, 255), 1)

        cv.namedWindow('image')
        p = {'shape': shape, 'drawing': False, 'sx': -1, 'sy': -1}
        cv.setMouseCallback('image', draw_circle, param=p)
        while 1:
            cv.imshow('image', img)
            k = cv.waitKey(1) & 0xFF
            if k == ord('r'):
                p['shape'] = 'rectangle'
            elif k == ord('c'):
                p['shape'] = 'circle'
            elif k == 27:
                break
        cv.destroyAllWindows()


# BaseImageCV(img=np.zeros((512, 512, 3), np.uint8)).corp()
