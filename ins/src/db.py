import MySQLdb
import pymysql


class DataBase:

    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "password"
        self.charset = "utf-8"
        self.database = 'ins'
        try:
            self.db = pymysql.connect(host=self.host, user=self.user, password=self.password, charset='utf8',
                                      database=self.database)
            self.cursor = self.db.cursor()
            print("连接数据库成功")
        except MySQLdb.Error as e:
            print(e)

    def save(self, data):

        if type(data) == dict:
            # 如果是字典，就说明是user_info，应该插入user表
            print("用户表！")
            try:
                insert_profile = "INSERT INTO user(id,user_name, fans_count, follow, bio)VALUES (%d, %s, %d, %d, %s)" % (
                    int(data['id']), str(data['full_name']), int(data['fans']), int(data['follow']),
                    self.db.escape_string(data['biography']))
                print(insert_profile)
                self.cursor.execute(insert_profile)
                print('插入用户信息成功')
            except MySQLdb.Error as e:
                print('插入用户信息时出错')
                print(e)
        elif type(data) == list:
            # 如果是列表，则是post信息，应该插入posts表
            print("posts表！")
            for post in data:
                insert_post = "INSERT INTO POST(post_url, id, type, likes, caption, text) VALUE( '%s',%d, '%s', %d, '%s', '%s')" % (post['post_url'], int(post['id']), post['is_video'], int(post['likes']),self.db.escape_string(post['caption']), self.db.escape_string(post['text']))
                print(insert_post)

                try:
                    self.cursor.execute(insert_post)
                    print("插入帖子信息成功！")
                except pymysql.err.IntegrityError as e:
                    print("插入post数据时发生错误！")
                    print(e)

        else:
            print("存入数据类型出错")

# 删除某个user的数据
    def delete(self, id):  # 通过id删除用户以及所有帖子信息
        delete_user = ""
        delete_posts = ""
        self.cursor.execute(delete_posts)
        self.cursor.execute(delete_user)

# 搜索一个用户 如果没有，就添加
    def search(self, id):  # 通过id查询所有信息
        search_posts = "select * from posts where id = {}".format(id)
        search_user = "select * from users where id = {}".format(id)
        self.cursor.execute(search_user)
        user = self.cursor.fetchone()
        self.cursor.execute(search_posts)
        posts = self.cursor.fetchall()
        print(user)
        print(posts)


    # 断开连接
    def close(self):
        self.cursor.close()


if __name__ == '__main__':
    db = DataBase()

