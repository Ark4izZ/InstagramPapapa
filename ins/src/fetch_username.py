import random
import requests
import json
import time

# 粉丝列表的接口https://i.instagram.com/api/v1/friendships/6860189/followers/?count=12&max_id=QVFEbEptdjRCMUpoaHp4dVU5MW94amJXZ3JUZTBnSXZOcVJZYzBZTUJueGJOMjBpUWFEOEtZaFVGc2stUG4xTTlGZ0NQeUw2MVk5THhsUElhQVhFOTdtSw==&search_surface=follow_list_page
# count是每次获取的数目，max_id是当前表的最后一个用户，也就是新获取的第0个，即新列表从这个用户之后开始获取。
# 每次好像最多获取100个用户

# 5.14 写入文件，获取一万个用户名，但是没有查重
import urllib3.util
# lebron=7855453810, justinbieber=6860189
url = "https://i.instagram.com/api/v1/friendships/6860189/followers/?count=100&search_surface=follow_list_page"


def cookiejar():
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


def random_cookie():
    cookie=random.choice(cookiejar())
    return cookie


headers = {
    # 'path': '/api/v1/friendships/6860189/following/?count=100',
    'x-ig-app-id': '936619743392459', # 这个很重要，好好像是静态的
    'x-csrftoken': '1GwpnYao4lX9HauigN4hk0UDzGmrRxIz',
    'referer': 'https://www.instagram.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36',
}

cookie=random_cookie()

proxies={
    'http': 'http://127.0.0.1:7888',
    'https': 'http://127.0.0.1:7888'
}


def clean():
    l=[]
    with open("../lists/userList_clean1.txt", 'r') as f:
        users=f.readlines()
        for user in users:
            # user=user.strip('\n')
            if user not in l:
                l.append(user)
    f.close()
    with open("../lists/userList_clean1.txt", "w") as f2:
        f2.writelines(l)
        # print(l)
        print(len(l))
    f2.close()
    return l


def main(l):
    # l=[]
    next_max_id = ""
    f=open("../lists/userList_clean1.txt", 'a')
    while len(l)<=200:
        url0 = url + "&max_id=" + next_max_id
        res = requests.get(url0, proxies=proxies, headers=headers, cookies=cookie)
        # print(url0)
        # print(res.status_code)
        print(cookie)
        # print(res.content)
        json1=res.content.decode('utf-8')
        dict1=json.loads(json1)
        time.sleep(2)
        # print(dict1)
        next_max_id=dict1['next_max_id']
        print(next_max_id)
        for user in dict1['users']:
            if user['username'] not in l:
                l.append(user['username'])
                # print(user)
                print(user['username'])
                f.write(user["username"]+'\n')
        print(len(l))
    f.close()


def test():
    next_max_id = ""
    url0 = url + "&max_id=" + next_max_id
    res = requests.get(url0, proxies=proxies, headers=headers)
    json1 = res.content.decode('utf-8')
    dict1 = json.loads(json1)
    max_id=dict1['next_max_id']
    print(max_id)


# 最终修改2022/06/06
if __name__=="__main__":
    # test()
    L=clean()
    main(L)
