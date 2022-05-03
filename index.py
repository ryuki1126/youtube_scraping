# 利用するライブラリ
import time
import requests
from bs4 import BeautifulSoup
import gspread
from oauth2client.service_account import ServiceAccountCredentials 
import json

# 変数
url_list = []
registrant_list = []
channel_list = []
domain = 'https://ytranking.net'

# スクレイピング処理(ランキング対象チャンネルの抽出)
for url_num in range(141, 150):
  print('ランキング対象チャンネルの抽出を開始')

  url = 'https://ytranking.net/ranking/mon/?p='+str(url_num)+'&mode=view'
  res = requests.get(url)
  soup = BeautifulSoup(res.text, 'html.parser')
  ul = soup.find('ul', class_='channel-list')
  
  # ランキングリストのaタグからhrefの情報を抽出する
  for a in ul.find_all('a'):
    rank_link = domain + a.get('href')
    url_list.append(rank_link)
  
  #DOM攻撃判定をされないようアクセス間隔を空ける
  print(str(url_num)+'回目のアクセス終了')
  time.sleep(2)
  print('待機終了')

# 抽出したチャンネルの数を取得
num = len(url_list)
print(num)

# チャンネル情報の取得
print('チャンネル情報の抽出を開始')
for ranker in url_list:
  print('アクセス開始')
  channel = {}
  res = requests.get(ranker)
  soup = BeautifulSoup(res.text, 'html.parser')
  span = soup.find('span', class_='subscriber-count').contents[0]
  if int(span) < 60000:
    header = soup.find('header', class_='header')
    h1 = header.find('h1')
    a = h1.find('a')
    channel['name'] = a.contents[0]
    channel['subscriber'] = span
    channel['url'] = a.attrs['href']
    channel_list.append(channel)
  #DOM攻撃判定をされないようアクセス間隔を空ける
  print(ranker+'の調査終了')
  time.sleep(2)
  print('待機終了')

# スクレイピングで取得したデータをスプレッドシートに入力する

#2つのAPIを記述しないとリフレッシュトークンを3600秒毎に発行し続けなければならない
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

#認証情報設定
#ダウンロードしたjsonファイル名をクレデンシャル変数に設定（秘密鍵、Pythonファイルから読み込みしやすい位置に置く）
credentials = ServiceAccountCredentials.from_json_keyfile_name('myproject-349013-13d753098859.json', scope)

#OAuth2の資格情報を使用してGoogle APIにログインします。
gc = gspread.authorize(credentials)

#共有設定したスプレッドシートキーを変数[SPREADSHEET_KEY]に格納する。
SPREADSHEET_KEY = '1ux0N_pvXZJLMO70JaCGFRuS7UxqoJEtLP6RAFHGxjyQ'

#共有設定したスプレッドシートのシート1を開く
worksheet = gc.open_by_key(SPREADSHEET_KEY).sheet1

for i in range(len(channel_list)):
  row = i + 2
  worksheet.update_cell(row,1, channel_list[i]['name'])
  worksheet.update_cell(row,2, channel_list[i]['subscriber'])
  worksheet.update_cell(row,3, channel_list[i]['url'])