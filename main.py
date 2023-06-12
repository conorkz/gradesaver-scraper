from bs4 import BeautifulSoup
import re
import requests
import paramiko
from datetime import datetime
import pytz
dir = r'your_sftp_directory'
roi = 'no info on the website'
x = 1
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('server', username='', password='')
sftp = ssh.open_sftp()
def sftp_exists(sftp, path):
    try:
        sftp.stat(path)
        return True
    except:
        return False
skip = True
while True:
    if x == 225:
        break
    url = f'https://www.gradesaver.com/study-guides/newest?page={x}'
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.content, "html.parser")
    print(f'PAGE: {url}')
    x+=1
    for t in soup.find_all(class_='excerpt js--fluidType'):
        link = 'https://www.gradesaver.com' + t.find('a')['href']
        title = t.select_one('[itemprop=name]').text.strip()
        if t.select_one('[itemprop=author]'):
            author = t.select_one('[itemprop=author]').text.strip()
        else:
            author = roi
        if t.select_one('img'):
            cover = t.select_one('img')['src']
        else:
            cover = roi
        respons = requests.get(link, headers={'User-Agent': 'Mozilla/5.0'})
        sorpa = BeautifulSoup(respons.content, "html.parser")
        print(link)
        if sorpa.find(class_='cta--icon'):
            continue
        if sorpa.find(class_='navSection__list js--collapsible'):
            lnks = []
            for b in sorpa.find(class_='navSection__list js--collapsible').find_all('a'):
                if b.text == 'Essay Questions':
                    break
                lnks.append('https://www.gradesaver.com' + b['href'])
        else:
            continue
        berlin = datetime.now(pytz.timezone('Europe/Berlin')).strftime('%Y-%m-%d %H:%M:%S %Z')
        bf = re.sub(r"[^\w\s]", "", title)
        file_name = f'{dir}/{bf}.txt'
        suffix = 1
        while sftp_exists(sftp, file_name):
            file_name = f'{dir}/{bf}({suffix}).txt'
            suffix += 1
        with sftp.open(file_name, "w") as file:
            file.write(f"Link: {link}\n")
            file.write(f"Title: {title}\n")
            file.write(f"Author: {author}\n")
            file.write(f"Book cover: {cover}\n")
            file.write(f"Berlin time: {berlin}\n\n")
            for lnk in lnks:
                respon = requests.get(lnk, headers={'User-Agent': 'Mozilla/5.0'})
                sorp = BeautifulSoup(respon.content, "html.parser")
                if sorp.find(class_='cta--icon'):
                    continue
                if sorp.find(class_='l--contentAdBody'):
                    for s in sorp.find(class_='l--contentAdBody').find_all(['p','h1','h2']):
                        file.write(s.text.strip() + '\n\n')
sftp.close()
ssh.close()
        