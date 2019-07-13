# JCM Catalogueに検索をかけてcsvに出力します
#### jcmcのインストール
- setup.pyとjcmc.pyをダウンロードし、1つのディレクトリ内に配置します。
- `python setup.py install`を実行してください。

#### jcmcの簡単な使用方法
解析ファイルを作成し、jcmcをインポートして用います。
```python
from jcmc import JCMC
JCMC = JCMC('20190711.csv') #出力ファイル名を決めておきます
JCMC.export('hydrothermal')
JCMC.export('hot,spring') #複数キーワードはカンマで区切る
```
#### jcmcの説明書
必要なモジュールのインストール
```python
import requests
import json
from bs4 import BeautifulSoup
import pandas as pd
import sys
import os
import urllib
import csv
import pprint
```
ターミナルに出力するときに色をつけられるようにします。`Color`クラスを作成して、色を指定しておきます。
```python
class Color:
    BLACK     = '\033[30m'
    RED       = '\033[31m'
    GREEN     = '\033[32m'
    YELLOW    = '\033[33m'
    BLUE      = '\033[34m'
    PURPLE    = '\033[35m'
    CYAN      = '\033[36m'
    WHITE     = '\033[37m'
    END       = '\033[0m'
    BOLD      = '\038[1m'
    UNDERLINE = '\033[4m'
    INVISIBLE = '\033[08m'
    REVERCE   = '\033[07m'
```
JCMCクラスの作成を始めます。まず最初に、`class JCMC`を呼び出した時に一度だけ読み込まれる`__init__`を作っておきます。引数は`name`だけ要求しておき、これには保存するcsvの名前を入れておきましょう。
```python
class JCMC:
    def __init__(self,name):
        self.oname = name
```
`class JCMC`の続き
```pyhthon
    def call_temp(self,url): #URLから温度の情報をもってくる関数を定義
        html = urllib.request.urlopen(url)
        data = BeautifulSoup(html, 'html.parser')
        text = data.get_text().splitlines() #テキストデータに変換
        for inf in text:
            if 'Temperature:' in inf: #Temperatureが存在する部分を抜き出す
                print(url,inf)
                return inf
                break

    def export(self,keyword):
        #keyword = input('search key : ') #検索キーワードを入力 (複数キーワードはカンマで)
        keyword = keyword.replace(',','+') #検索できる形に変換
        url = 'https://www.jcm.riken.jp/cgi-bin/jcm/jcm_kojin?ANY=' + keyword #URLをつくる
        parent = url.split('/')[0]+'//'+url.split('/')[2]
        html = urllib.request.urlopen(url) #指定したURLからhtmlをもってくる
        soup = BeautifulSoup(html, 'html.parser')

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

        with open(self.oname, 'a', encoding='shift_jis') as f: #'a'を指定すると追記できる (ファイルがない場合は新規)
            k1 = 'Keyword'
            k2 = 'Speceis'
            k3 = 'JCM number'
            k4 = 'URL'
            k5 = 'Temperature'
            k6 = 'Information'
            filecheck = 0
            with open(self.oname, 'r', encoding='shift_jis') as c:
                if len([i for i in c.readlines()]) > 0:
                    filecheck = 1
            fieldnames = [k1,k2,k3,k4,k5,k6]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if filecheck == 0: writer.writeheader() #fileが空のときだけheaderを書き込む
            for line in url_list:
                ind = url_list.index(line)
                info = self.call_temp(line)
                spname = name_list[ind].replace('\xa0', '').replace('"','')
                JCMnumber = line.split('=')[1]
                tmp = float(info.split('°C')[0].split(':')[1])
                try:
                    apx = ','.join(info.split(';')[1:]).replace('\xa0', '')
                except IndexError:
                    apx = 'None.'
                print(Color.CYAN+'Calling... '+Color.GREEN+spname+Color.END)
                writer.writerow({k1:keyword,k2:spname,k3:JCMnumber,k4:line,k5:tmp,k6:apx}) #csvに書き込み
```
