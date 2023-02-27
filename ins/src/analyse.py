import csv
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt

plt.rcParams['figure.dpi']=1000


def wc_of_posts():
    with open("../csv/posts.csv",'r',encoding='utf-8') as fp:
        reader = csv.DictReader(fp)
        with open("posts.txt",'a',encoding='utf-8') as f:
            for x in reader:
                if(x['caption']!= "null" and x['caption']!="."):
                    f.write(x['caption'])
    with open("posts.txt", 'r', encoding='utf-8') as fp:
        w = fp.read()

    wb = WordCloud(height=2000,width=2000,scale=2,min_font_size=2)
    wb.generate(w)
    plt.imshow(wb, interpolation="bilinear")

    plt.axis("off")
    plt.show()
    wb.to_file("../../web/flask/ins_flask/static/assets/img/word.jpg")
    if os.path.exists("posts.txt"):
        os.remove("posts.txt")
    else:
        print("The file does not exist")


def user():
    with open("../csv/user_info.csv", 'r', encoding='utf-8') as fp:
            reader = csv.DictReader(fp)
            fans,follow=[],[]
            for x in reader:
                if(int(x['fans'])<10000):
                    fans.append(int(x['fans']))
                    follow.append(int(x['follow']))

    plt.title("Fans-Follow")
    plt.scatter(fans,follow)
    plt.xlabel("fans")
    plt.ylabel("follow")
    plt.savefig("../../web/flask/ins_flask/static/assets/img/user.jpg")
    plt.show()


if __name__=='__main__':
    wc_of_posts()
    user()