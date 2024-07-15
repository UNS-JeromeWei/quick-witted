# ########################################################## #
# https://www.harrisgeospatial.com/docs/ENVIHeaderFiles.html #
# ########################################################## #

import os
import datetime
import numpy as np


class ENVI:

    # Additional fields for ENVI header (Not exists in ENVI header format)
    EXPOSURE_TIME = 'exposure time'
    EXPOSURE_TYPE = 'exposure type'
    TEMPERATURE_MEMSDRV = 'temperature memsDRV'
    GAIN = 'gain'
    SENSOR_ID = 'sensorid'
    MEMS_ID = 'memsid'
    MEMSDRV_ID = 'memsDRVid'
    #CUBE_RETURNS = 'cube returns'

    # Optional fields of ENVI header
    SENSOR_TYPE = 'sensor type'
    DEFAULT_BANDS = 'default bands'
    WAVELENGTH = 'wavelength'
    WAVELENGTH_UNITS = 'wavelength units'

    # Required fields of ENVI header
    FILE_TYPE = 'file type'
    LINES = 'lines'
    SAMPLES = 'samples'
    BANDS = 'bands'
    DATA_TYPE = 'data type'
    INTERLEAVE = 'interleave'
    BYTE_ORDER = 'byte order'
    BIT_DEPTH = 'bit depth'
    HEADER_OFFSET = 'header offset'

    def __init__(self, sensor_type): # , sensor_id, mems_id, memsDRV_id
        self.spectral_cube = np.array([])
        self.data_header = dict()
        self.bands_count = 0
        self.info_header = {
            ENVI.FILE_TYPE:         'ENVI Standard',
            ENVI.SENSOR_TYPE:       sensor_type,
            ENVI.WAVELENGTH_UNITS:  'nm',
            ENVI.DATA_TYPE:         12,
            ENVI.INTERLEAVE:        'BSQ',
            ENVI.BYTE_ORDER:        0,
            ENVI.BIT_DEPTH:         10,
            ENVI.HEADER_OFFSET:     0
        }
            # was inside info_header:
                #ENVI.SENSOR_ID:         sensor_id,
                #ENVI.MEMS_ID:           mems_id,
                #ENVI.MEMSDRV_ID:            memsDRV_id,
    def update_temperature(self,temp):
        self.info_header["temperature"]=temp
    def append_data(self, img, data):
        if self.bands_count == 0:
            self.spectral_cube = img.copy()
        else:
            self.spectral_cube = np.concatenate((self.spectral_cube, img), axis=0)
        self.bands_count += 1
        for key in data.keys():
            if key in self.data_header:
                self.data_header[key].append(data[key])
            else:
                self.data_header[key] = [data[key]]

    def save(self, directory):
        
        cube_shape = self.spectral_cube.shape

        #self.data_header[ENVI.DEFAULT_BANDS] = [self.data_header[ENVI.WAVELENGTH][0]]
        self.data_header[ENVI.DEFAULT_BANDS] = [self.data_header[ENVI.DEFAULT_BANDS][0]]
        self.data_header[ENVI.EXPOSURE_TYPE] = [self.data_header[ENVI.EXPOSURE_TYPE][0]]
        #self.data_header[ENVI.CUBE_RETURNS] = [self.data_header[ENVI.CUBE_RETURNS][0]]

        self.data_header[ENVI.LINES] = cube_shape[0] // self.bands_count
        self.data_header[ENVI.SAMPLES] = cube_shape[1]
        self.data_header[ENVI.BANDS] = self.bands_count
        
        header_string = self.create_header_string()

        #now = datetime.datetime.now()
        #file_name = 'ENVI_{}'.format(now.strftime("%Y%m%d_%H%M%S"))
        now = os.path.basename(directory)
        file_name = 'ENVI_{}'.format(now)

        file_path = os.path.normpath(os.path.join(directory, file_name))
        with open(file_path + '.raw', 'wb') as f:
            f.write(self.spectral_cube)
        with open(file_path + '.hdr', 'w') as f:
            f.write(header_string)
        self.clear()

    def create_header_string(self):
        header_string = 'ENVI\n'
        for header in [self.info_header, self.data_header]:
            for key, value in header.items():
                if isinstance(value, list):
                    header_string += '{} = {{\n'.format(key)
                    header_string += ',\n'.join(map(str, value))
                    header_string += '\n}\n'
                else:
                    header_string += '{} = {}\n'.format(key, value)
        return header_string

    def clear(self):
        self.spectral_cube = np.array([])
        self.data_header = dict()
        self.bands_count = 0
