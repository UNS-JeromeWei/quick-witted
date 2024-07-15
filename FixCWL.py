# -*- coding: utf-8 -*-
# @Time    : 7/3/2024 4:17 PM
# @Author  : super
# @Site    : 
# @File    : tunability.py
# @Software: PyCharm
import json
import pandas as pd
import numpy as np
import openpyxl
import shutil
import os
from scipy.interpolate import interp1d

class Tunability:
    def __init__(self,camera_path,mems_type):
        self.camera_path=camera_path
        self.mems_type=mems_type
        self.main_folder = os.path.join(self.camera_path, f"WithMEMS/SystemResponse/{mems_type}_InUse")
        self.InUse_folder = os.path.join(self.camera_path, "WithMEMS/SystemResponse/InUse")
        self.backup_InUse_folder = os.path.join(self.camera_path, "WithMEMS/SystemResponse/InUse_bk")
        self.backup_main_folder = os.path.join(self.camera_path, f"WithMEMS/SystemResponse/{mems_type}_InUse_bk")
        self.energeFactor_data=np.zeros((0,0))
        self.energeFactor_path=os.path.join(self.backup_main_folder,"energyFactor.csv")
        self.tuned_json_path=os.path.join(self.backup_InUse_folder,"camera24200196_for_calib_Tune.json")


    '''
    assigned_voltages: {"920":[V1,V2,V3,V4]}
    '''
    def fix(self,assigned_voltages=None):
        self.__backup_data()
        self.__delete_states_cube()
        self.__create_new_tuned_json(assigned_voltages)

    #把InUse和NIR/VIS_InUse备份
    def __backup_data(self):

        if not os.path.exists(self.backup_InUse_folder):
            shutil.copytree(self.InUse_folder, self.backup_InUse_folder)

        if not os.path.exists(self.backup_main_folder):
            shutil.copytree(self.main_folder, self.backup_main_folder)

    #删掉之前的state cube文件夹
    def __delete_states_cube(self):
        for folder in os.listdir(self.main_folder):
            if folder.startswith("state"):
                shutil.rmtree(os.path.join(self.main_folder,folder))


    #生成新的tuned json文件
    '''
    需要考虑:
    1. 可以指定某个波段的电压
    2. 支持通过插值法修正电压
    '''
    def __create_new_tuned_json(self,assigned_voltages):
        self.__load_tuned_energeFactor()
        self.__load_tuned_voltages()
        self.__generate_new_voltages(assigned_voltages)


    def __load_tuned_energeFactor(self):
        df = pd.read_csv(self.energeFactor_path)
        self.energeFactor_data = df.to_numpy()


    def __generate_new_voltages(self,assigned_voltages):
        #选出10个锚点中哪些abs(cwl_dif)≥5的
        need_fix_energeFactor=self.energeFactor_data[abs(self.energeFactor_data[:, 2]) >= 5]
        corrected_Modes={}
        for index in range(need_fix_energeFactor.shape[0]):
            #如果传入指定波段的电压，优先使用传入的
            cwl=need_fix_energeFactor[index,1]
            diff=need_fix_energeFactor[index,2]
            old_voltages=[mode["Voltages"] for mode in self.tuned_json_data[self.mems_type]["MEMS"]["Modes"] if mode["CWL"]==cwl][0]
            if assigned_voltages and assigned_voltages.__contains__(str(int(cwl))):
                voltages=assigned_voltages[str(int(cwl))]
            else:
                voltages=self.__get_voltages_for_cwl(cwl,diff,old_voltages)
            corrected_Modes[cwl]=voltages


        # workbook = openpyxl.Workbook()
        # sheet = workbook.active
        # sheet.append(["cwl_cal", "V1", "V2", "V3", "V4"])
        # for i in range(ret.shape[0]):
        #     sheet.append(ret[i, :].tolist())
        # workbook.save(output)
        return True

    def __get_voltages_for_cwl(self,cwl,diff,old_voltages):
        '''
        支持两个策略:
        1.如果在插值[min,max]之间，可使用插值法
        2.如果不再区间之内,从120组LUT表中寻找电压
        :param cwl:
        :return:
        '''
        _min=min(self.energeFactor_data[:, 0].tolist())
        _max=max(self.energeFactor_data[:, 0].tolist())

        if cwl >= _min and cwl <= _max:
            return self.__get_voltages_by_interpolation(cwl)
        else:
            print(f"cwl:{cwl} is out of the range of interpolation:[{_min},{_max}]")

            # 需要考虑从120组电压中选择。
            return self.__get_voltages_by_MEMS_sorting(cwl,diff,old_voltages)


    def __get_voltages_by_interpolation(self,cwl):
        voltages = []
        for i in range(1, 5):
            x = self.tuned_voltages[:, 0]
            y = self.tuned_voltages[:, i]
            f = interp1d(x, y)
            v = f([cwl])
            voltages.append(v[0])
        return voltages

    def __get_voltages_by_MEMS_sorting(self,cwl,diff,old_voltages):
        pass


    def __load_tuned_voltages(self):
        with open(self.tuned_json_path,"r",encoding="utf8") as f:
            self.tuned_json_data=json.load(f)

        self.tuned_voltages=[]

        for index,mode in enumerate(self.tuned_json_data[self.mems_type]["MEMS"]["Modes"]):
            tmp=[self.energeFactor_data[:,0].tolist()[index]]
            tmp.extend(mode["Voltages"])
            self.tuned_voltages.append(tmp)

        self.tuned_voltages=np.asarray(self.tuned_voltages)

if __name__ == '__main__':
    camera_path=r"E:\output_data_for_production\Solomon\Characterization\Camera24200196_20240708_162223"
    t = Tunability(camera_path,"NIR")
    t.fix()


