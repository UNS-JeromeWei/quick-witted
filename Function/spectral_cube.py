import sys
import typing
import os
import spectral
import numpy as np
import copy
from unispectral.config import config_cube
from unispectral.datasets.geometry import RectRoi, MaskRoi, Size, Anno


class SpectralCube:
    def __init__(
        self,
        cube_path=None,
        envi=None,
        data=None,
        metadata=None,
        annos: typing.List[Anno] = [],
        cls_image=None,
    ):
        self.cube_path = cube_path
        if cube_path is not None:
            self.cube_dir, self.cube_name = os.path.split(cube_path)
        else:
            self.cube_dir, self.cube_name = None, None
        self._data = data  # cube data
        self.metadata = metadata or {}  # store accuracy for each peanut
        self.annos = annos
        self._envi = envi
        # if envi is None and cube_path is not None:
        #     hdr_path = os.path.join(
        #         self.cube_dir, self.cube_name, f"ENVI_{self.cube_name}.hdr"
        #     )
        #     raw_path = os.path.join(
        #         self.cube_dir, self.cube_name, f"ENVI_{self.cube_name}.raw"
        #     )
        #     self.envi = spectral.envi.open(hdr_path, raw_path)
        # else:
        #     self.envi = envi
        self.cls_image = cls_image  # store classification image

    def data_exposure(self, exposure_base=250, cube_dark_name='ref_dark'):
        # call copy func to fix joblib memory cache twice problem
        # Take exposure_base = 250ms as baseline of exposure time for training.
        # Take cube_dark_name='ref_dark' and put the data at the same folder with the object.
        self._data = self.envi.load(dtype=np.uint16).asarray().copy()  # ori method that not exposure normal
        X_dark_ref = get_ref_dark_data(self.cube_dir, cube_dark_name, smooth=False)
        exposure = get_exposure(self.cube_dir, self.cube_name)
        data_exposure = (self._data - X_dark_ref) / exposure * exposure_base
        # self._data = self._data / exposure * exposure_base  # already subtract 64
        return data_exposure

    @property
    def data(self):
        if self._data is None and self.envi is not None:
            if config_cube.data_mode == 'ori':
                # call copy func to fix joblib memory cache twice problem
                self._data = self.envi.load(dtype=np.uint16).asarray().copy()
            elif config_cube.data_mode == 'exposure':
                self._data = self.data_exposure()
            elif config_cube.data_mode == 'dark':
                self._data = self.data_ori_rem_dark
        return self._data

    @property
    def data_ori_rem_dark(self):
        X_dark_ref = get_ref_dark_data(self.cube_dir, cube_name='ref_dark', smooth=False)
        Xt = self.envi.load(dtype=np.uint16).asarray().copy() - X_dark_ref.astype(float)
        return Xt

    @property
    def data_ori_rem_dark_temperature(self):
        X_dark_ref = get_ref_dark_data(self.cube_dir, cube_name='ref_dark', smooth=False)
        Xt = self.envi.load(dtype=np.uint16).asarray().copy() - X_dark_ref.astype(float)
        X_temperature = get_temperature(self.cube_dir, self.cube_name)
        return Xt, X_temperature

    @property
    def data_ori(self):
        return self.envi.load(dtype=np.uint16).asarray().copy()

    @data.setter
    def data(self, new_data):
        if self._data is None:
            raise ValueError("data not load error")
        self._data = new_data

    @property
    def envi(self):
        if self._envi is None and self.cube_path is not None:
            hdr_path = os.path.join(
                self.cube_dir, self.cube_name, f"ENVI_{self.cube_name}.hdr"
            )
            raw_path = os.path.join(
                self.cube_dir, self.cube_name, f"ENVI_{self.cube_name}.raw"
            )
            self._envi = spectral.envi.open(hdr_path, raw_path)
        # else:
        #     self.envi = envi        
        return self._envi

    @classmethod
    def from_cube_path_roi(cls, cube_path: str, roi: typing.Union[RectRoi, MaskRoi]):
        return cls(cube_path, annos=[Anno(roi=roi)])

    def __deepcopy__(self, memo):
        """triggered by copy.deepcopy()"""
        return SpectralCube(
            cube_path=self.cube_path,
            envi=self.envi,
            data=self.data,
            metadata=self.metadata,
            annos=self.annos,
            cls_image=self.cls_image,
        )  # TODO: 自动遍历所有类属性，完成深度拷贝

    def __copy__(self):
        """triggered by copy.copy()"""
        return SpectralCube(
            cube_path=self.cube_path,
            envi=self.envi,
            data=self.data,
            metadata=self.metadata,
            annos=self.annos,
            cls_image=self.cls_image,
        )


class SpectralCubeGroup:
    def __init__(self, obj_spc: SpectralCube, ref_spc: SpectralCube) -> None:
        self.obj_spc = obj_spc  # object spectral cube
        # avoid same ref_spc being binned many times
        # self.ref_spc = ref_spc  # white referece spectral cube
        # deepcopy cannot directly work due to BsqFile
        self.ref_spc = copy.deepcopy(ref_spc)


def load_cube(cube_path=None, cube_dir=None, cube_name=None) -> SpectralCube:
    if cube_path is None:
        if cube_dir is None or cube_name is None:
            raise ValueError(f"Cannot load cube, invalid cube_path")
        cube_path = os.path.join(cube_dir, cube_name)
    return SpectralCube(cube_path=cube_path)


def get_exposure(cube_dir, cube_name):
    path = os.path.join(
        cube_dir, cube_name, f"ENVI_{cube_name}.hdr"
    )
    begin_label = 'exposure time'
    with open(path, "r") as f:
        content = f.readlines()
    collect_label = 0
    for line in content:
        line_strip = line.strip('\n')
        if collect_label == 1:
            exposure = float(line_strip[:-1])
            return exposure
        if begin_label in line_strip:
            collect_label = 1


def get_temperature(cube_dir, cube_name):
    path = os.path.join(
        cube_dir, cube_name, f"ENVI_{cube_name}.hdr"
    )
    begin_label = 'temperature'
    with open(path, "r") as f:
        content = f.readlines()
    collect_label = 0
    for line in content:
        line_strip = line.strip('\n')
        if begin_label in line_strip:
            temperature_spt = line_strip.split('= ')
            # print(begin_label_spt)
            return np.float(temperature_spt[1])


def get_ref_dark_data(cube_dir, cube_name, smooth=False):
    hdr_path = os.path.join(
        cube_dir, cube_name, f"ENVI_{cube_name}.hdr"
    )
    raw_path = os.path.join(
        cube_dir, cube_name, f"ENVI_{cube_name}.raw"
    )
    # X_dark = spectral.envi.open(hdr_path, raw_path).load(dtype=np.uint16).asarray().copy().astype(float)
    X_dark = spectral.envi.open(hdr_path, raw_path).load(dtype=np.uint16).asarray().copy()
    if smooth:
        from unispectral.preprocessing.smooth import Smooth  # can't be import outside
        X_dark = Smooth.smooth_by_filter(X_dark)
    return X_dark

