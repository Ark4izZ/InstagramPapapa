import os
import random
import sys
import time
import requests
import csv
import json

from PySide2.QtWidgets import QApplication, QMessageBox, QPushButton, QFileDialog
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
import analyse
from PySide2.QtCore import QEventLoop, QTimer
from PySide2 import QtCore, QtGui
from tqdm import tqdm


class MainWindow:
    textWritten = QtCore.Signal(str)  # 定义一个发送str的信号，这里用的方法名与PyQt5不一样

    def write(self, text):
        self.textWritten.emit(str(text))
        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec_()

    def outputWritten(self, text):
        # self.edt_log.clear()
        cursor = self.edt_log.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.edt_log.setTextCursor(cursor)
        self.edt_log.ensureCursorVisible()


class Ins:

    def __init__(self):
        self.url = "https://i.instagram.com/api/v1/users/web_profile_info/?username="
        self.headers = {
            # 'path': '/api/v1/friendships/6860189/following/?count=100',
            'x-ig-www-claim': 'hmac.AR2tgRJwCYQzi6DO7h4uWj2hc78T7cS_yYQJ56YKdyfY0EGJ',
            'x-ig-app-id': '936619743392459',  # 这个很重要，好好像是静态的
            'x-csrftoken': '1GwpnYao4lX9HauigN4hk0UDzGmrRxIz',
            'x-asbd-id': '198387',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
            'referer': 'https://www.instagram.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
        }
        self.cookie = {
            'mid': 'Yp1ayAALAAFnAGMcu1BRH1tuwYPV',
            'ig_did': '3E95A5C7-13EA-425E-B84E-E721B5562FF7',
            'ig_lang': 'en',
            'dpr': '1.125',
            'datr': 'm2SdYiMBQsEd6yFWdpL91vmz',
            'csrftoken': 'sH11QK0SEv5IUsZPCjHpDX9Y1u6MhgZy',
            'ds_user_id': '53631745473',
            'sessionid': '53631745473:m5KxNlN1E0k7mC:10',
            'rur': '"EAG\\05453631745473\\0541686098676:01f77eef008c358348f299fb2722351a07eb99db911ca1853a992b41ea30196cd557c191"'
        }
        self.proxies = {
            'http': 'http://127.0.0.1:7888',
            'https': 'http://127.0.0.1:7888'
        }
        self.cookiejar = self.gen_cookiejar()
        self.users_list = self.get_users_list()
        self.users = []
        self.posts = []
        self.finished = []
        # self.path2usercsv='../csv/user_info.csv'
        # self.path2postcsv='../csv/posts.csv'
        # qfile_stats = QFile('./uiFile/InsScrap.ui')
        # qfile_stats.open(QFile.ReadOnly)
        #
        # self.ui = QUiLoader().load(qfile_stats)
        # qfile_stats.close()
        # self.ui.start.clicked.connect(self.loop)

    # 从响应中获取cookie，返回cookie字典
    def get_cookie(self, res):
        # 变化的: csrftoken, expires(请求中不用发送), Max-Age(在请求中不用发送), ds_user_id (更新)，rur(更新)
        cookie = res.headers['Set-Cookie']
        cookie_dict = {}
        items = cookie.split(';')
        for item in items:
            try:
                key = item.split('=')[0].replace(' ', '')
                key = key.replace('Secure,', '')
                value = item.split('=')[1]
                cookie_dict[key] = value
            except Exception as e:
                # print(e)
                pass
        cookie_dict.pop('Max-Age')
        cookie_dict.pop('Domain')
        cookie_dict.pop('expires')
        cookie_dict.pop('Path')
        print(cookie_dict)
        return cookie_dict

    # 更新cookie值
    def update_cookie(self, cookie_dic):
        # old_cookie=self.cookie
        # old_cookie.update(cookie_dic)
        # print("self.cookie: ", self.cookie)
        # print("old_cookie: ", old_cookie)
        self.cookie.update(cookie_dic)

    # 从cookie池中选取cookie
    def gen_cookiejar(self):
        with open("../lists/cookie1.txt", "r") as f:
            text = f.readlines()
            f.close()
            cookies = []
            for cookie in text:
                cookie_dic = {}
                items = cookie.split(";")
                for item in items:
                    key = item.split("=")[0].replace(' ', '')
                    key = key.replace('Secure,', '')
                    # value = item.split('=')[1]
                    value = item.split('=')[1].strip('\n').strip(',')
                    cookie_dic[key] = value
                # print(cookie_dic)
                cookies.append(cookie_dic)
        return cookies

    def random_cookie(self):
        self.cookie = random.choice(self.cookiejar)

    def get_res(self, username, pbar):
        requests.adapters.DEFAULT_RETRIES = 5
        s = requests.session()
        s.keep_alive = False

        url = self.url + username
        # sys.stdout.write("\n"+url)
        try:
            res = requests.get(url=url, proxies=self.proxies, headers=self.headers, cookies=self.cookie)
            pbar.set_description("正在爬取 {} ".format(username))
            # self.ui.console.append("正在爬取 {} ".format(username))
            # self.ui.show()
            if res.status_code == 200:
                content = json.loads(res.content.decode())
                if content['data']['user'] is None:  # 连接成功也是200，但是该用户不存在或者无法获取
                    pbar.write("{} 用户不存在或已经改名，无法获取用户数据".format(username))
                    # self.ui.console.append("{} 用户不存在或已经改名，无法获取用户数据".format(username))
                    res.close()
                    return None
                res.close()
                return res
            elif res.status_code == 429:
                pbar.write("请求次数过多,换个号吧")
                res.close()
                return 429
            res.close()
        except Exception as e:
            # res.close()
            # print(e)
            return 'retry'
            # loop()

            # return e
        except requests.exceptions.ProxyError:
            print("连接错误")
            print(requests.exceptions.ProxyError)
            self.loop()

    # 读取用户列表
    def get_users_list(self):
        with open("../lists/userList_clean1.txt", "r") as f:
            users = f.readlines()
            f.close()
        users0 = []
        for user in users:
            user0 = user.replace("\n", "")
            # self.users_list.append(user0)
            users0.append(user0)
        return users0

    # 把self.posts和self.users分别保存到csv文件中
    def save_as_csv_users(self):
        # print(">>>>>>>>>>>>>>>>>>>>>.......")
        # sys.stdout.write("正在保存用户数据...")
        file_exists = os.path.isfile('../csv/user_info1.csv')
        try:
            labels = ['username', 'id', 'fans', 'follow', 'biography', 'posts_count']
            with open("../csv/user_info1.csv", "a", encoding="utf-8", newline='') as f:
                # 将用户信息表写入文件
                writer = csv.DictWriter(f, fieldnames=labels)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(self.users[-1])  # 写入user表的最后一条
                # for elem in self.users:
                #     writer.writerow(elem)
        except IOError as e:
            print("I/O error")
            print(e)

    def save_as_csv_posts(self):
        # print(dic_arr)
        # print("获取到的帖子数量：" + str(len(self.posts)))
        if len(self.posts) != 0:

            try:
                file_exists = os.path.isfile('../csv/posts1.csv')
                with open("../csv/posts1.csv", 'a', encoding="utf-8") as f2:
                    labels = ['username', 'user_id', 'likes', 'caption', 'url', 'typename', 'comment', 'time']
                    writer = csv.DictWriter(f2, fieldnames=labels, delimiter=',', lineterminator='\n')
                    if not file_exists:
                        writer.writeheader()
                    # 每次搜集的帖子都加入self.posts中，每次写入最新一组的每post
                    for post in self.posts[-1]:
                        writer.writerow(post)
            except IOError as e:
                print("I/O error")
                print(e)

    # 获取一个用户的信息
    def get_user_data(self, content):
        user = {}
        user_data = content['data']['user']
        # print(user_data)
        user["username"] = user_data['username']
        user["id"] = user_data['id']
        user["fans"] = user_data['edge_followed_by']['count']
        user["follow"] = user_data['edge_follow']['count']
        user["biography"] = user_data['biography']  # 没有的话就为空,以上数据是必有的
        user["posts_count"] = user_data['edge_owner_to_timeline_media']['count']  # 帖子数量
        # print(user)
        self.users.append(user)

    # 获取一个用户的帖子的信息，最终都加入到self.posts中
    def get_posts_data(self, content, pbar):
        user_data = content['data']['user']
        # 帖子的信息, 最终以列表形式返回
        edges_count = user_data['edge_owner_to_timeline_media']['count']  # 该用户发表帖子的数量
        if edges_count != 0:
            edges = user_data['edge_owner_to_timeline_media']['edges']
            post_list = []
            for edge in edges:
                post = {}
                # post['cover']=edegs[0]['node']["display_url"] 主页某帖子的封面
                post['username'] = user_data['username']  # 该帖子po主id
                post['user_id'] = user_data['id']  # 该帖子po主用户名
                post['likes'] = edge['node']["edge_liked_by"]['count']  # 该帖子的点赞数，类型是int
                post['comment'] = edge['node']["edge_media_to_comment"]['count']  # 评论数
                when = trans_time(edge['node']['taken_at_timestamp'])  # 时间戳转化为日期
                post['time'] = when  # 发布的时间
                try:
                    post['caption'] = edge['node']["edge_media_to_caption"]['edges'][0]['node']['text']
                except:
                    post['caption'] = "null"

                post['url'] = "https://www.instagram.com/p/" + edge['node']['shortcode']  # 该帖子的短链接，在数据库中是唯一的
                # post["video_url"]=edegs[0]['node']["video_url"] #该帖子的视频地址 若该帖子不是视频就没有这一项
                post['typename'] = edge['node']["__typename"]  # 该帖子的类型；GraphSidecar是多图帖，GraphImage是单图贴，GraphVideo是视频贴
                post_list.append(post)  # 字典列表

            self.posts.append(post_list)
        else:
            username = user_data['username']
            id = user_data['id']
            # pbar.write(username + "(id:{}) 没有发表帖子".format(id))

    def load(self):
        try:
            csvFile = open("../csv/user_info1.csv", "r", encoding="utf-8")
        except FileNotFoundError:
            return 0
        reader = csv.reader(csvFile)
        rows = [row for row in reader]
        # 如果csv中已经有文件写入了
        if len(rows) > 1:
            max_index = len(rows) - 1  # 第0行是header，那么如果有2行，则最后一行数据是第1行
            # self.users_list
            index = self.users_list.index(rows[max_index][0])
        else:
            # 如果没有写入数据，则index从0开始
            max_index = 0
            index = 0
            print(rows[max_index][0])
        return index

    def loop(self):
        p = tqdm(self.users_list[self.load() + 1:-1])
        for username in p:
            self.random_cookie()
            # self.ui.console.append("正在爬取 {}".format(username))
            p.set_description("正在爬取{}".format(username))
            res = self.get_res(username, p)  # 正常的响应，429,e
            if res == 'retry':
                self.loop()
            time.sleep(1)
            if (res is not None) and (res != 429):
                # p.write("\n"+res.url)
                content = json.loads(res.content.decode())
                # p.write("正在保存")
                self.get_posts_data(content, p)
                self.get_user_data(content)
                self.save_as_csv_posts()
                self.save_as_csv_users()
                # sys.stdout.flush()
            elif res == 429:
                print(429, "!!!")
                break


# 时间戳转换
def trans_time(timeStamp):
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
    return otherStyleTime


# 采集特定用户账号
def get_one(username):
    ins = Ins()
    pbar = tqdm(list(usern  ame))
    res = ins.get_res(username, pbar)
    if (res is not None) and (res != 429):
        content = json.loads(res.content.decode())
        ins.get_posts_data(content, pbar)
        ins.get_user_data(content)
        print(ins.users)
        print(ins.posts)


# 测试tqdm
def p_test():
    ins = Ins()
    p = tqdm(ins.users_list[9999:-1])
    for user in p:
        time.sleep(1)
        p.set_description("正在爬取 {} ".format(user))
        # print(user)


if __name__ == "__main__":
    ins=Ins()
    ins.loop()
