# -*- coding: utf-8 -*-
from PIL.Image import NONE
from requests.models import stream_decode_response_unicode
from test01 import findCode
from numpy.lib.index_tricks import fill_diagonal
import requests
from numpy.core.fromnumeric import alltrue
from pandas.io import json
import json
import logging
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import urllib.request
import re

header = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36 Edg/92.0.902.67'}
logging.basicConfig(level=logging.INFO)

header['user-agent'] = UserAgent(verify_ssl=False).random


def url2Bs4(url):
    req = urllib.request.Request(url)
    webpage = urllib.request.urlopen(req)
    html = webpage.read()
    soup = BeautifulSoup(html, 'html.parser')
    return(soup)


def findCount(projects_name, need_type):
    # 函数功能：确定爬取对象的总数

    if need_type == "star":
        url = r"https://github.com/" + projects_name + r"/stargazers"
        soup = url2Bs4(url)
        count_star = soup.find_all(
            'a', class_="js-selected-navigation-item selected tabnav-tab")
        count_num = count_star[0].get_text()
        temp_num = ""
        for num in count_num:
            if(ord(num) <= 57 and ord(num) >= 48):
                temp_num = temp_num+num
        return temp_num
    elif need_type == "fork":
        url = r"https://github.com/" + projects_name + r"/network/members"
        soup = url2Bs4(url)
        count_fork = soup.find_all('a', class_="social-count")
        count_num = count_fork[1].get_text().strip()
        return count_num
    else:
        print("只能查找star or fork")
        return -1


def findAllFork(projects_name):

    projects_path_name = projects_name.split("/")[-1]
    fork_list = []
    url = r"https://github.com/" + projects_name + r"/network/members"
    soup = url2Bs4(url)
    all_forks = soup.find_all('img', class_="gravatar avatar-user")
    for i in range(1, len(all_forks)):
        path_name = "/" + all_forks[i]["alt"][1:] + "/" + projects_path_name
        fork_list.append(path_name)
    return fork_list


def findAllForkName(fork_list):
    fork_name_list = []
    for fork_path in fork_list:
        piece = fork_path.split("/")
        fork_name_list.append(piece[1])
    return fork_name_list


def findStar(projects_name, next_page_url="", num_page=0):
    # 函数功能：查找单页的star
    # 返回一个list
    star_list = []

    # 获取包含用户名的span框
    if num_page == 0:
        url = r"https://github.com/" + projects_name + r"/stargazers"
    else:
        url = next_page_url
    soup = url2Bs4(url)
    all_stars = soup.find_all('span', class_="Truncate-text")

    # special case
    if (all_stars is None):
        print("此人没有star")
        return -1

    # 取得单页用户名
    for each_star in all_stars:

        if(str(each_star)[-12:-8] != "</a>"):
            continue
        star_name = each_star.get_text()
        star_name = star_name[1:-1]
        star_list.append(star_name)

    #
    # 返回全部名字的list
    return star_list


def nextPage(url, multi=0):
    soup = url2Bs4(url)
    next_page = soup.find_all('a', class_="btn btn-outline BtnGroup-item")

    # 没有下一页的情况
    if next_page is None:
        print("没有下一页")
        return -1
    button_check = next_page[0].get_text()
    # 首页的情况
    if len(next_page) == 1 and button_check == "Next":
        next_page_url = next_page[0]["href"]
    # 非首页的情况
    elif len(next_page) == 2:
        next_page_url = next_page[1]["href"]
    else:
        return -1

    return next_page_url


def findAllStar(projects_name, num_of_page=0):
    all_star_list = []
    num_of_page = num_of_page
    # 第一页 一般在main函数里的调用为findAllStar(projects_name, num_need)
    if(num_of_page == 0):
        star_list = findStar(projects_name, num_of_page)
        all_star_list = all_star_list+star_list

    next_url = nextPage(r"https://github.com/" +
                        projects_name + r"/stargazers")

    while(next_url):

        if(next_url == -1):
            print("当前翻找到第", num_of_page+1, "页，仅找到", len(all_star_list), "个")
            return all_star_list
        # 若有下一页
        else:
            num_of_page += 1
            star_list_next = findStar(projects_name, next_url, num_of_page)
            all_star_list = all_star_list + star_list_next
            # if(len(all_star_list) == count_stars):
            #     return all_star_list
            next_url = nextPage(next_url)


def StarDict(star_list):
    star_dict = {}
    for star_name in star_list:
        info_json = {}
        info_json = UserInfo(star_name)
        star_dict[star_name] = info_json
    return star_dict


def UserInfo(users_name):
    url = r"https://api.github.com/users/" + users_name
    req = requests.get(url)
    if req.status_code == 200:
        info_json = json.loads(req.text)
    else:
        print("用户信息API调用失败")
    return info_json


def ProjectInfo(projects_name):
    url = r"https://api.github.com/repos" + projects_name
    req = requests.get(url)
    if req.status_code == 200:
        info_json = json.loads(req.text)
    else:
        print("项目信息API调用失败")
    return info_json


def Statis(projects_name, star_need=-1, fork_need=-1):
    count_stars = findCount(projects_name, "star")
    count_forks = findCount(projects_name, "fork")
    star_list = findAllStar(projects_name)
    fork_list = findAllFork(projects_name)
    if(star_need > len(star_list)):
        print("star需求大于star总人数，返回全部")
        star_need = -1
    if(fork_need > len(fork_list)):
        print("fork需求大于fork总人数，返回全部")
        fork_need = -1
    if(star_need != -1):
        star_list = star_list[0:star_need]
    if(fork_need != -1):
        fork_list = fork_list[0:fork_need]
    fork_name_list = findAllForkName(fork_list)
    print("----------爬取概况----------")
    print("star总计有：{count_stars}, forks总计有 {count_forks}".format(
        count_stars=count_stars, count_forks=count_forks))
    print("----------指定个数starList的前五个----------")
    print((star_list)[0:5])
    print("----------指定个数forkList的前五个----------")
    print((fork_name_list)[0:5])
    print("---------------------------")


# if __name__ == '__main__':
    # username = "Jamie-Yang"
    # UI = UserInfo(username)
    # print(UI)
    # # 示例（上为单页文件；下为多页文件）
    # # projectsName = r"/Jamie-Yang/vue3-boilerplate"
    # # projectsName = r"/vuejs/vue-cli"

    # # 功能1 爬取star：
    # # 输入的项目格式需为一个路径形式

    # # 统计总数
    # count_stars = findCount(projectsName, "star")
    # count_forks = findCount(projectsName, "fork")

    # # 获取名单，需要具体数目时切片即可
    # star_list = findAllStar(projectsName)

    # # 功能2 爬取fork,需要具体数目时切片即可：
    # fork_list = findAllFork(projectsName)

    # Statis(projectsName)

    # projectName = r"/Jamie-Yang/vue3-boilerplate"
    # fork_list = findAllFork(projectName)
    # print(fork_list[0:2])
    # Statis(projectName)
    # projectInfo = ProjectInfo(projectName)
    # print(projectInfo["id"])
    # star_list = findAllStar(projectsName)
    # star_dict = StarDict(star_list[0:3])
    # print(star_dict)
