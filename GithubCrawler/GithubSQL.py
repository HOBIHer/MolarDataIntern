
import GithubStarAndForkCrawler as gc
import pymysql
#!/usr/bin/python
# -*- coding: UTF-8 -*-
conn = pymysql.connect(
    host="192.168.2.106",
    user="ljq", password="123456",
    database="github")


def ProgramAdd(projectInfo):
    cursor = conn.cursor()
    # 得到一个可以执行SQL语句并且将结果作为字典返回的游标
    #cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    proPrivate = 0 if projectInfo['private'] == False else 1
    proForkAllow = 1 if projectInfo['allow_forking'] == True else 0

    programSql = "INSERT INTO Programs(pRow, pid, pName, pPrivate, pDescription, pStar, pFork,\
    pAllowFork, pCreatedAt, pUpdatedAt, pTopics, dCreatedAt, dUpdatedAt) \
    VALUES (\"%s\", %d, \"%s\", %d, \"%s\", %d, %d, %d, \"%s\", \"%s\", \"%s\", CURRENT_TIMESTAMP,CURRENT_TIMESTAMP  )" % \
        (projectInfo, projectInfo['id'], projectInfo['full_name'],
         proPrivate, projectInfo['description'], projectInfo['stargazers_count'],
            projectInfo['forks_count'], proForkAllow, projectInfo['created_at'],
            projectInfo['updated_at'], projectInfo['topics'])
    cursor.execute(programSql)
    conn.commit()


def ProgramUpdate(projectInfo):
    cursor = conn.cursor()
    # 得到一个可以执行SQL语句并且将结果作为字典返回的游标
    #cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    proPrivate = 0 if projectInfo['private'] == False else 1
    proForkAllow = 1 if projectInfo['allow_forking'] == True else 0

    programSql = "UPDATE Programs SET pRow = \"%s\", pName = \"%s\", pPrivate = %d, \
    pDescription = \"%s\", pStar = %d, pFork = %d, pAllowFork = %d, pUpdatedAt = \"%s\", \
    pTopics = \"%s\", dUpdatedAt = CURRENT_TIMESTAMP\
    WHERE pid = %d" % \
        (projectInfo, projectInfo['full_name'], proPrivate, projectInfo['description'],
         projectInfo['stargazers_count'], projectInfo['forks_count'], proForkAllow,
         projectInfo['updated_at'], projectInfo['topics'], projectInfo['id'])
    cursor.execute(programSql)
    conn.commit()


def UserAdd(UserInfo):
    cursor = conn.cursor()
    userSql = "INSERT INTO Users(uRow, uid, uName, uNickName, uCompany, uLocation, uEmail,\
    uFollowers,uFollowings,uCreatedAt,uUpdatedAt,dCreatedAt,dUpdatedAt) \
    VALUES (\"%s\", %d, \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", %d, %d, \"%s\", \"%s\", CURRENT_TIMESTAMP,CURRENT_TIMESTAMP  )" % \
        (UserInfo, UserInfo['id'], UserInfo['login'],
         UserInfo['name'], UserInfo['company'], UserInfo['location'],
            UserInfo['email'], UserInfo['followers'], UserInfo['following'],
            UserInfo['created_at'], UserInfo['updated_at'])
    try:
        cursor.execute(userSql)
        conn.commit()
    except:
        conn.rollback()


def SqlCheck(CheckInfo, CheckType):
    cursor = conn.cursor()
    if CheckType.lower() == "project":
        sql = "SELECT pid FROM Programs \
        WHERE pid = %d " % CheckInfo["id"]
    elif CheckType.lower() == "user":
        sql = "SELECT uid FROM Users \
        WHERE uid = %d " % CheckInfo["id"]
    else:
        print("查询类型只能是project、user")
        return False

    cursor.execute(sql)
    results = cursor.fetchall()

    return results == ()


def RelationCheck(userInfo, projectInfo, Rtype):
    cursor = conn.cursor()
    checkSql = "SELECT * FROM StarAndFork \
        WHERE uid = %d AND Utype = \"%s\" AND pid = %d" % (userInfo["id"], Rtype, projectInfo["id"])
    cursor.execute(checkSql)
    RCheck = cursor.fetchall()
    return RCheck == ()  # True 表示该关系不存在，False表示该关系已存在


def RelationAdd(userInfo, projectInfo, Rtype):
    # 每次关系做一个check

    if(RelationCheck(userInfo, projectInfo, Rtype) == False):
        print("该关系已存在,已调用关系更新接口")
        RelationUpdate(userInfo, projectInfo, Rtype)
        return

    if (Rtype == "Owner"):
        RSql = "INSERT INTO StarAndFork(uid, uName, uType, pid, pName, dCreatedAt, dUpdatedAt) \
        VALUES (%d, \"%s\", \"%s\", %d, \"%s\",  CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)" % \
            (userInfo['id'], userInfo['login'], "Owner",
             projectInfo['id'], projectInfo['full_name'])

    elif (Rtype == "Star"):
        RSql = "INSERT INTO StarAndFork(uid, uName, uType, pid, pName, dCreatedAt, dUpdatedAt) \
        VALUES (%d, \"%s\", \"%s\", %d, \"%s\", CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)" % \
            (userInfo['id'], userInfo['login'], "Star",
             projectInfo['id'], projectInfo['full_name'])

    elif (Rtype == "Fork"):
        RSql = "INSERT INTO StarAndFork(uid, uName, uType, pid, pName, dCreatedAt, dUpdatedAt) \
        VALUES (%d, \"%s\", \"%s\", %d, \"%s\", CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)" % \
            (userInfo['id'], userInfo['login'], "Fork",
             projectInfo['id'], projectInfo['full_name'])
    else:
        print("输入的参数Rtype不对，只能是Owner、Star、Fork")
        return
    cursor = conn.cursor()
    cursor.execute(RSql)
    conn.commit()


def RelationUpdate(userInfo, projectInfo, Rtype):
    if(RelationCheck(userInfo, projectInfo, Rtype) == True):
        print("该关系不存在，已调用关系新增接口")
        RelationAdd(userInfo, projectInfo, Rtype)
        return

    sql = "UPDATE StarAndFork SET uName "


def AddAPI(projectName, star_need=-1, fork_need=-1):
    # 项目信息：
    projectInfo = gc.ProjectInfo(projectName)
    if (SqlCheck(projectInfo, "project")):
        ProgramAdd(projectInfo)
    else:
        print("该项目已在数据库中，新增接口（AddAPI）调用失败,已自动调用UpdateAPI")
        UpdateAPI(projectName)

    # 作者信息：
    ownerName = projectName.split("/")[1]
    ownerInfo = gc.UserInfo(ownerName)
    if (SqlCheck(ownerInfo, "user")):
        UserAdd(ownerInfo)
    else:
        print("该作者已在User表中，仅记录关系数据")
    RelationAdd(ownerInfo, projectInfo, Rtype="Owner")

    # N个star信息
    star_list = gc.findAllStar(projectName)
    if(star_need > len(star_list)):
        print("star需求大于star总人数，返回全部")
        star_need = -1
    if star_need != -1:
        star_list = star_list[0:star_need]
    for each_star in star_list:
        each_starInfo = gc.UserInfo(each_star)
        if (SqlCheck(each_starInfo, "user")):
            UserAdd(each_starInfo)
        RelationAdd(each_starInfo, projectInfo, Rtype="Star")

    # N个fork信息
    fork_list = gc.findAllFork(projectName)
    fork_name_list = gc.findAllForkName(fork_list)
    if(fork_need > len(fork_name_list)):
        print("fork需求大于fork总人数，返回全部")
        fork_need = -1
    if fork_need != -1:
        fork_name_list = fork_name_list[0:fork_need]
    for each_fork in fork_name_list:
        each_forkInfo = gc.UserInfo(each_fork)
        if (SqlCheck(each_forkInfo, "user")):
            UserAdd(each_forkInfo)
        RelationAdd(each_forkInfo, projectInfo, Rtype="Fork")


def UpdateAPI(projectName):
    projectInfo = gc.ProjectInfo(projectName)
    if (SqlCheck(projectInfo, "project")):
        print("无该项目，请使用新增接口AddAPI")
        return
    ProgramUpdate(projectInfo)


if __name__ == '__main__':
    projectName = r"/Jamie-Yang/vue3-boilerplate"
    AddAPI(projectName, 3, 3)
    # projectInfo = gc.ProjectInfo(projectName)
    # ProgramAdd(projectInfo)
    # a = SqlCheck(projectInfo, "project")
    # print(a)
