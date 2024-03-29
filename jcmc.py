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
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

class Color:
    CYAN  = '\033[36m'
    GREEN = '\033[32m'
    END   = '\033[0m'

class JCMC:
    def __init__(self,name):
        self.oname = name

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
        name_list,GC_list = [],[]
        frag = 0
        for i in range(len(text)):
            if 'JCM number:' in text[i]:
                name_list.append(text[i-1]) #賢いやり方かは怪しいが。
                frag = 1
            if frag == 1:
                if 'G+C' in text[i]:
                    GC_list.append(text[i].split(' ')[2])
                    frag = 0
                elif 'JCM number:' in text[i+1]:
                    GC_list.append('None.')
                    frag = 0

        with open(self.oname, 'a', encoding='shift_jis') as f: #'a'を指定すると追記できる (ファイルがない場合は新規)
            k1 = 'Keyword'
            k2 = 'Species'
            k3 = 'JCM number'
            k4 = 'URL'
            k5 = 'Temperature'
            k6 = 'GC content'
            k7 = 'Information'
            filecheck = 0
            with open(self.oname, 'r', encoding='shift_jis') as c:
                if len([i for i in c.readlines()]) > 0:
                    filecheck = 1
            fieldnames = [k1,k2,k3,k4,k5,k6,k7]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if filecheck == 0: writer.writeheader() #fileが空のときだけheaderを書き込む
            for line in url_list:
                ind = url_list.index(line)
                info = self.call_temp(line)
                spname = name_list[ind].replace('\xa0', '').replace('"','')
                JCMnumber = line.split('=')[1]
                tmp = float(info.split('°C')[0].split(':')[1])
                gc = GC_list[ind].split(' ')
                print(gc)
                try:
                    apx = ','.join(info.split(';')[1:]).replace('\xa0', '')
                except IndexError:
                    apx = 'None.'
                print(Color.CYAN+'Calling... '+Color.GREEN+spname+Color.END)
                writer.writerow({k1:keyword,k2:spname,k3:JCMnumber,k4:line,k5:tmp,k6:gc,k7:apx}) #csvに書き込み

    def summary(self,keywords):
        data,cpalette = pd.read_csv(self.oname),'Dark2'
        print(data)
        sns.set(palette=cpalette);cmap = plt.get_cmap(cpalette);plt.figure(figsize=(14, 9))
        gs = gridspec.GridSpec(nrows=len(keywords),ncols=3,hspace=0.3)
        for i in range(len(keywords)):
            plt.subplot(gs[i, 0])
            sns.distplot(data[data["Keyword"]==keywords[i].replace(',','+')].Temperature,kde=True,rug=True,color=cmap(i))
            plt.title(keywords[i].replace(',','+'))
            plt.xlabel('')
            plt.xlim(0,data.Temperature.max()+10)
        plt.subplot(gs[:, 1]);sns.boxplot(x="Keyword", y="Temperature", data=data)
        plt.subplot(gs[:, 2]);sns.swarmplot(x="Keyword", y="Temperature", data=data)
        plt.savefig(self.oname.replace('csv','png'))
        os.system('open '+self.oname.replace('csv','png'))
