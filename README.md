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
# jcmcの説明書
jcmc.pyの中身をつくっていきます。まずは必要なモジュールをインポートしておきます。
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
ここまでで一度実行してみます。別のファイル (main.pyなど)をつくって、`class JCMC`を呼び出してみます。
```python
from jcmc import JCMC #ここでclass JCMCがjcmc.pyからインポートします。
JCMC = JCMC('test.csv') #test.csvがclass JCMCの__init__で用意したnameに渡されてself.onameに格納されます。
```
ここでは何も起きないですが、先程作成した`class JCMC`を呼び出してtest.csvという名前を用意できました。試しに、新しい関数`def test`を作ってみましょう。
```python
class JCMC:
    def __init__(self,name):
        self.oname = name
        
    def test(self, data):
        return data * 2 #引数dataを2倍した値を返します
```
ここでmain.pyに戻って、作成した`test`関数を使ってみます。
```python
from jcmc import JCMC 
JCMC = JCMC('test.csv') 

a = JCMC.test(2) #test関数のdataに2を渡します。返ってきた4 (2倍された数)がaに格納されます。
print(a)

b = JCMC.test(3) #test関数のdataに3を渡します。返ってきた6 (2倍された数)がbに格納されます。
print(b)

c = JCMC.test(2) * JCMC.test(3) #関数どうしの積をとることもできます
print(c)
```
`test`関数と同じようにしてjcmcを関数として作っていくことで、mian.pyから呼び出して処理することができるようになります。`export`関数をつくって実際に出力してみましょう。
```python
class JCMC:
    def __init__(self,name):
        self.oname = name

    def export(self,keyword):
        keyword = keyword.replace(',','+') #検索できる形に変換
        url = 'https://www.jcm.riken.jp/cgi-bin/jcm/jcm_kojin?ANY=' + keyword #URLをつくる
        print(url)
```
`keyword = keyword.replace(',','+')`をなぜやるのかですが、例えば"hydrothermal vent"をJCMで検索すると、検索結果のURLは`https://www.jcm.riken.jp/cgi-bin/jcm/jcm_kojin?ANY=hydrothermal+vent`となっていました。ここから、2つ以上の単語でつくられた語句で検索すると`+`で繋がれて検索にかけられることがわかります。スペースはやや扱いにくいので、このソフトウェアでは2つ以上の単語はカンマで区切る方式をとります。`keyword`には検索したい1つの単語またはカンマで区切られた2つ以上の単語が渡されているので、`keyword = keyword.replace(',','+')`で処理することでとりあえず検索キーワードを準備することができました。この検索キーワードを`url = 'https://www.jcm.riken.jp/cgi-bin/jcm/jcm_kojin?ANY='`に繋げることで、検索するURLを準備できました。`print(url)`して確認してみましょう。
```python
from jcmc import JCMC 
JCMC = JCMC('test.csv') 
JCMC.export('hydrothermal,vent')
```
```
% python main.py
https://www.jcm.riken.jp/cgi-bin/jcm/jcm_kojin?ANY=hydrothermal+vent
```
このURLをコピーしてgoogleで見てみましょう。目的の検索結果のページが表示されていてば成功です。生成したURLから、そのページのhtmlファイルを取得するプログラムを作っていきます。`urllib.request.urlopen(url)`を用いると簡単に書けます。続いて`BeautifulSoup()`で持ってきたhtmlを使いやすい形にパースします。
```python
class JCMC:
    def __init__(self,name):
        self.oname = name

    def export(self,keyword):
        keyword = keyword.replace(',','+') #検索できる形に変換
        url = 'https://www.jcm.riken.jp/cgi-bin/jcm/jcm_kojin?ANY=' + keyword #URLをつくる
        parent = https://www.jcm.riken.jp #親URLを指定しておきます (今後つかいます)
        html = urllib.request.urlopen(url) #指定したURLからhtmlをもってくる
        soup = BeautifulSoup(html, 'html.parser')
        a = soup.find_all('a') #<a>タグで囲まれた部分の中身(JMC numberのURLが含まれる)を抜き出す
        url_list = []
        for tag in a:
            called = tag.get('href') #リンク先のURLのリストをもってくる
            if 'JCM=' in called:
                url_list.append(parent+called)
        print(url_list)
        print(len(url_list)) #何個のURLが取得できたか確認する
```      
一気に書いてしまいました。まずはもってきたhtmlの中身を見てみましょう。
```html
<H1>Strain data</H1>
Search for keyword=[hydrothermal vent].

<HR>
<FONT FACE="Arial,Helvetica"> <I>Thermococcus</I> <I>profundus</I></FONT><BR>
JCM number: <a href="/cgi-bin/jcm/jcm_number?JCM=9378">9378</a> #これが目的のURL
 &lt;--&nbsp;T. Kobayashi DT5432.<br>
Source: <STRONG>Hydrothermal vent at the Mid-Okinawa Trough [<a href="/cgi-bin/jcm/jcm_ref?REF=3633">3633</a>]</STRONG>.<BR>
Morphology: [<a href="/cgi-bin/jcm/jcm_ref?REF=3633">3633</a>].<BR>
Biochemistry/Physiology: [<a href="/cgi-bin/jcm/jcm_ref?REF=3633">3633</a>].<BR>
G+C (mol%): 52.5 (HPLC) [<a href="/cgi-bin/jcm/jcm_ref?REF=3633">3633</a>].<BR>
```
こんな感じに、`<a>`タグの中にリンク先のurlの情報が含まれていることがわかります。この中で、JCM番号にリンクされているものは全て`JMC=`の後にJMC番号がついている形をしたURLで共通しています。`if`文で`JMC=`が含まれるURLを全て`url_list`に追加していくことで、検索ワードで検索した結果のページからJCM番号へのリンクが含まれる全てのURLを取得することができました。何個のURLが取得できたか確認し、漏れなく取得できているか確認しておきましょう。
```python
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
                
                
             def call_temp(self,url): #URLから温度の情報をもってくる関数を定義
        html = urllib.request.urlopen(url)
        data = BeautifulSoup(html, 'html.parser')
        text = data.get_text().splitlines() #テキストデータに変換
        for inf in text:
            if 'Temperature:' in inf: #Temperatureが存在する部分を抜き出す
                print(url,inf)
                return inf
                break
```
