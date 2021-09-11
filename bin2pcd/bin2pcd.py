import numpy as np
import struct
import open3d

binPath = r"1577845009.700.bin"
pcdPath = binPath[:-4]+".pcd"
# 自定义路径

orderFlag = 0
# 如果这是一个有序点云集，即点云的width和height已知，改用如下代码，并请注释上一行代码
# orderFlag = [width,height] #width与height为具体数值


def convert_kitti_bin_to_pcd(binFilePath):
    size_float = 4
    list_pcd = []
    with open(binFilePath, "rb") as f:
        byte = f.read(size_float * 4)
        while byte:
            x, y, z, intensity = struct.unpack("ffff", byte)
            list_pcd.append([x, y, z, intensity])
            byte = f.read(size_float * 4)
    np_pcd = np.asarray(list_pcd)

    HEADER = '''\
# .PCD v0.7 - Point Cloud Data file format
VERSION 0.7
FIELDS x y z intensity
SIZE 4 4 4 4 
TYPE F F F F 
COUNT 1 1 1 1 
WIDTH {}
HEIGHT {}
VIEWPOINT 0 0 0 1 0 0 0
POINTS {}
DATA ascii
'''

    n = len(np_pcd)
    lines = []
    for i in range(n):
        x, y, z, intensity = np_pcd[i]
        lines.append('{} {} {} {}'.format(
            x, y, z, intensity))
    with open(pcdPath, 'w') as f:
        if orderFlag != 0:
            f.write(HEADER.format(orderFlag[0], orderFlag[1], n))
        else:
            f.write(HEADER.format(n, 1, n))
            f.write('\n'.join(lines))


convert_kitti_bin_to_pcd(binPath)
