# -*- coding: utf-8 -*-
__author__ = 'user'
import logging
import sqlite3
import pickle
import zipfile


logging.basicConfig(level=logging.INFO)

class News():
    def __init__(self,title,content,type,date,banci):
        self.title = title
        self.content = content
        self.type = type
        self.date = date
        self.banci = banci


if __name__=='__main__':
    newsList=[]
    conn = sqlite3.connect('test.db')
    rows=conn.execute(r"SELECT * FROM NEWS WHERE TITLE like '%习近平%'")

    for r in rows:
        newsList.append(News(r[1],r[2],r[3],r[4],r[5]))
    conn.close()
    with open('newslist','wb') as f:
        pickle.dump(newsList,f)

    with zipfile.ZipFile('news.zip','w',compression=zipfile.ZIP_BZIP2) as myzip:
        myzip.write('newslist')

