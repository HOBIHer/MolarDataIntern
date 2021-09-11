import os
from pandas.io import json
import json
import Cloud
path = r"iData"
count = 0
file = open(path, "rb")
fileJson = json.load(file)
sum = 0
linkList = []
linkList2 = []
pwList = []
# 提取有效的对象
effectItem = []
effectTH = []
for itemJson in fileJson:
    if ('twoHall' in itemJson.keys()):
        effectItem.append(itemJson)


for listTH in effectItem:
    if(listTH["twoHall"]):
        for item in listTH["twoHall"]:
            effectTH.append(item)


for listETH in effectTH:
    for itemETH in listETH:
        if (type(itemETH["link"]) == list):
            temp = itemETH["link"][0][0]
            linkList.append(temp)
            pwList.append(itemETH["pw"])
        else:
            linkList.append(itemETH["link"])
            pwList.append(itemETH["pw"])
B = Cloud.BaiDuPan()

startLink = 547

for i in range(startLink, 1000):

    print("第", i, "号链接是：", linkList[i], "\n", "密码是：", pwList[i])
    try:
        B.saveShare(linkList[i], pwd=pwList[i])
    except FileNotFoundError as F:
        continue
