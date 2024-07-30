
## 对于 2nd order 的 MEMS
indx 在 band =1 的时候，在LUT 表中的索引就是1
但是在2nd order 的电压有更接近 band 1 wanted 的条件
是否可以单独这个 电压设置成 2nd order ？

- E.g. Solomon Camera2420019B_NIR_temp=35_B_SSSSSSSS


***
## Voltage setting 算法优化建议 - 20240711
- ✅ 1、边界条件下，如果正好是 abs(value)=5, abs(differ)=3 
- ✅ 2、对于 MEMS LUT 表中 CWL 间隙过大的问题，中间考虑增加判据并增加局部插值计算
- ✅ 3、对于 MEMS LUT 表中 电压与 CWL 关系收敛，考虑最低的电压情况的判据

**
## Voltage setting 优化建议 - 20240730
- ✅ 1、autotune 的 json 复制后修改后缀为 「***_opt_0.json」在判定 optimise 文件夹不存在时一起处理
- ✅ 2、电压插值法优化处理完毕后，在 optimise 文件夹中保留最新的 「***_opt_N.json」并将最新的 json 文件复制并移动到上级目录 「\InUse」中，重命名为 「***_for_calib_Tune.json」替换原来的文件