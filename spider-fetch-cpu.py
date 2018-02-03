import requests
from bs4 import BeautifulSoup
import re
import sys


fetch_url = "http://www.cpu-world.com/Releases/Desktop_CPU_releases_({YEAR}).html"
month_dic = {
        "January": "Q1",
        "February": "Q1", 
        "March": "Q1",
        "April": "Q2",
        "May": "Q2",
        "June": "Q2",
        "July": "Q3",
        "August": "Q3",
        "September": "Q3",
        "October": "Q4",
        "November": "Q4",
        "December": "Q4"
}

def deal_cpu_name(name):
    return re.sub(r'\(.*\)$', "", name.strip()).strip()

def fetch_from_html(html, year_parttern):
    soup = BeautifulSoup(html, "lxml")
    ans = []
    try:
        table = soup.find("table", class_= "sh_table v_top")
        tr = table.find_all("tr")
        for i in range(1, len(tr)):
            month = tr[i].find("td").get_text().strip()
            season = month_dic[month]
            cpus = tr[i].find_all("div", class_="rel_ng")
            for url in cpus:
                urls = url.find_all("a")
                for u in urls:
                    ans.append((deal_cpu_name(u.get_text()), year_parttern + season))
    except Exception as e:
        print ('fetch cpu err: ', e)
    return ans

    
def fetch_cpu(year):
    url = fetch_url.replace("{YEAR}", str(year))
    header = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "max-age=0",
            "Cookie": "AZ=1; AW=; I=ATKGMDYGH; AK=D; XX=A; AT=I; AG=F; LG=420L/0/0",
            "Host": "www.cpu-world.com",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    }
    year_parttern = str(year)[2:4]
    r = requests.get(url, headers=header)
    print(r)
    print (r.text)
    soup = BeautifulSoup(r.text, "lxml")
    ans = []
    try:
        table = soup.find("table", class_= "sh_table v_top")
        tr = table.find_all("tr")
        for i in range(1, len(tr)):
            month = tr[i].find("td").get_text().strip()
            season = month_dic[month]
            cpus = tr[i].find_all("div", class_="rel_ng")
            for url in cpus:
                ans.append((deal_cpu_name(url.a.get_text()), year_parttern + season))
    except Exception as e:
        print ('fetch cpu err: ', e)
    return ans

def main():
    ans = []
    for i in range(2006, 2018):
        fileName = str(i) + ".html"
        year = str(i)[2:4]
        with open(fileName, "r") as f:
            ans = fetch_from_html(f.read(), year) + ans
    with open("all_pc.txt", "w") as f:
        for item in ans:
            f.write("+".join(item[0].split(" ")) + " " + item[1] + "\n")

if __name__ == "__main__":
    main()
