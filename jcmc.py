from selenium import webdriver
import time
import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
import sys
import time
import os
import urllib
import csv
import pprint

"""
簡単な使い方
% python get_from_web.py
search key : hot,spring (複数キーワードで検索するときはカンマで区切る)

output.csvが存在しない場合 : 新規作成する
output.csvが存在する場合 : 追記
"""

class Color:
    CYAN  = '\033[36m'
    GREEN = '\033[32m'
    END   = '\033[0m'

keyword = input('search key : ') #検索キーワードを入力 (複数キーワードはカンマで)
keyword = keyword.replace(',','+') #検索できる形に変換
url = 'https://www.jcm.riken.jp/cgi-bin/jcm/jcm_kojin?ANY=' + keyword #URLをつくる
parent = url.split('/')[0]+'//'+url.split('/')[2]
html = urllib.request.urlopen(url) #指定したURLからhtmlをもってくる
soup = BeautifulSoup(html, 'html.parser')

def call_temp(url): #URLから温度の情報をもってくる関数を定義
    html = urllib.request.urlopen(url)
    data = BeautifulSoup(html, 'html.parser')
    text = data.get_text().splitlines() #テキストデータに変換
    for inf in text:
        if 'Temperature:' in inf: #Temperatureが存在する部分を抜き出す
            print(url,inf)
            return inf
            break

a = soup.find_all('a') #<a>タグで囲まれた部分の中身(JMC numberのURLが含まれる)を抜き出す
url_list = []
for tag in a:
    called = tag.get('href') #リンク先のURLのリストをもってくる
    if 'JCM=' in called:
        url_list.append(parent+called)

text = soup.get_text().splitlines()
name_list = []
for i in range(len(text)):
    if 'JCM number' in text[i]:
        name_list.append(text[i-1]) #賢いやり方かは怪しいが。

with open('output.csv', 'a', encoding='shift_jis') as f: #'a'を指定すると追記できる (ファイルがない場合は新規)
    k1 = 'Keyword'
    k2 = 'Speceis'
    k3 = 'JCM number'
    k4 = 'URL'
    k5 = 'Temperature'
    k6 = 'Information'
    filecheck = 0
    with open('output.csv', 'r', encoding='shift_jis') as c:
        if len([i for i in c.readlines()]) > 0:
            filecheck = 1
    fieldnames = [k1,k2,k3,k4,k5,k6]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    if filecheck == 0: writer.writeheader() #fileが空のときだけheaderを書き込む
    for line in url_list:
        ind = url_list.index(line)
        info = call_temp(line)
        spname = name_list[ind].replace('\xa0', '').replace('"','')
        JCMnumber = line.split('=')[1]
        tmp = float(info.split('°C')[0].split(':')[1])
        try:
            apx = ','.join(info.split(';')[1:]).replace('\xa0', '')
        except IndexError:
            apx = 'None.'
        print(Color.CYAN+'Calling... '+Color.GREEN+spname+Color.END)
        writer.writerow({k1:keyword,k2:spname,k3:JCMnumber,k4:line,k5:tmp,k6:apx}) #csvに書き込み
