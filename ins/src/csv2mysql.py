import MySQLdb
import pymysql
import pandas as pd

# 统计和导入mysql
pd.options.display.max_columns = None


# ——————————————————database————————————————————————————
class DataBase:

    def __init__(self):
        self.host = "localhost"
        self.user = "root"
        self.password = "password"
        self.charset = "utf-8"
        self.database = 'ins'
        try:
            self.connect = pymysql.connect(host=self.host, user=self.user, password=self.password, charset='utf8',
                                           database=self.database)
            self.cursor = self.connect.cursor()
            print("连接数据库成功")
        except MySQLdb.Error as e:
            print(e)


db = DataBase()


# 填补空缺值
def fillna(path):
    data = pd.read_csv(path, index_col=False, delimiter=',')
    data = data.fillna(value="none")

    return data


def insert_post_table():
    data = fillna('../csv/posts.csv')
    for i, row in data.iterrows():
        try:
            sql = "INSERT INTO ins.posts VALUES (%s,%s,%s,%s,%s,%s,%s,%s)"
            db.cursor.execute(sql, tuple(row))
            print("Record inserted")
            db.connect.commit()
        except Exception as e:
            print("Error while insert to MySQL", e)
            continue


def insert_user_table():
    data = fillna('../csv/user_info.csv')
    for i, row in data.iterrows():
        try:
            sql = "INSERT INTO ins.users VALUES (%s,%s,%s,%s,%s,%s)"
            db.cursor.execute(sql, tuple(row))
            print("Record inserted")
            db.connect.commit()
        except Exception as e:
            print("Error while insert to MySQL", e)
            continue


def insert_main():
    insert_post_table()
    insert_user_table()


# 清除表
def truncate(tablename):
    sql = 'truncate table {}'.format(tablename)
    db.cursor.execute(sql)
    db.connect.commit()


# —————————————————统计—————————————————————————————

if __name__ == '__main__':
    # truncate('users')
    # truncate('posts')
    # insert_main()
    # insert_post_table()
    insert_user_table()
