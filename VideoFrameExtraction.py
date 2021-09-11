import cv2
import os

videoDir = '/mnt/d/code'  # 视频路径
imgSaveDir = './result0830'  # 图片存放文件夹
extList = ['mp4', 'MP4']  # 视频格式后缀
frameInterval = 0.1  # 每一帧的时间间隔 单位 秒


def getFrame(videoName, sec):
    imgPath = f'{imgSaveDir}/{videoName}-{sec}.jpg'
    video.set(cv2.CAP_PROP_POS_MSEC, (sec * 1000))
    hasFrames, image = video.read()
    if hasFrames:
        cv2.imwrite(imgPath, image)
    return hasFrames


# 最简单的单目录文件夹结构
videoPathList = []  # 存储符合格式的视频地址
for videoFile in os.listdir(videoDir):
    if videoFile.split('.')[-1] in extList:
        videoFilePath = f'{videoDir}/{videoFile}'
        videoPathList.append(videoFilePath)

for videoPath in videoPathList:
    videoName = videoPath.split('/')[-1].split('.')[0]
    video = cv2.VideoCapture(videoPath)

    sec = 0
    hasFrames = getFrame(videoName, sec)
    while hasFrames:
        sec += float(frameInterval)
        print(sec)
        hasFrames = getFrame(videoName, sec)
