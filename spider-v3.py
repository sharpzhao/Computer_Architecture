import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import sys

multi_benchmark= "http://browser.geekbench.com/geekbench3/search?dir=desc&sort=multicore_score&q="
benchmark = "http://browser.geekbench.com/geekbench3/search?dir=desc&sort=score&q="
def fetch_score(arg):
    print ("fetch_score name: %s, season: %s" % arg)
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
    cpu_name = arg[0]
    date = arg[1]
    r = requests.get(benchmark + cpu_name, headers=header)
    soup = BeautifulSoup(r.text, "lxml")
    try:
        score1 = soup.find("td", class_="model").find_next_siblings("td", class_="score")[0].get_text().strip()
    except:
        score1 = 0

    b = requests.get(multi_benchmark + cpu_name)
    soup2 = BeautifulSoup(b.text, 'lxml')
    try:
        score2 = soup2.find("td", class_="model").find_next_siblings("td", class_="score")[1].get_text().strip()
    except:
        score2 = 0
    return (int(score1), int(score2), date)

def init_score():
    single_score = {}
    multiple_score = {}
    with open("single_score.txt", "r") as f:
        for d in f.readlines():
            d = d.strip().split(" ")
            single_score[d[0][0:2] + "Q" + d[0][-1]] = int(d[1])
    with open("multiple_score.txt", "r") as f:
        for d in f.readlines():
            d = d.strip().split(" ")
            multiple_score[d[0][0:2] + "Q" + d[0][-1]] = int(d[1])
    return single_score, multiple_score

def write_to_file(single_ans, multiple_ans, fileName):
    single_ans = sorted(single_ans.items(), key=lambda item:item[0])
    multiple_ans = sorted(multiple_ans.items(), key = lambda item:item[0])
    name = fileName.split(".")[0]
    with open(name + "_single_score.txt", 'w') as f:
        for s in single_ans:
            f.write(s[0] + ' ' + str(s[1]) + "\n")
    with open(name + "_multiple_score.txt", 'w') as f:
        for s in multiple_ans:
            f.write(s[0] + ' ' + str(s[1]) + "\n")


def main():
    fileName = sys.argv[1]
    single_ans, multiple_ans= init_score()
    ans = []
    pool = ThreadPoolExecutor(5)
    with open (fileName, "r") as f:
        for line in f.readlines():
            cpu_name, date = line.split(" ")
            cpu_name = cpu_name.strip()
            date = date.strip()
            try:
                ans.append(pool.submit(fetch_score, (cpu_name, date)))
            except Exception as e:
                print("err:", e)
    for a in ans:
        result = a.result()
        scores = (result[0], result[1])
        date = result[2]
        if date in single_ans:
            if scores[0] > single_ans[date]:
                single_ans[date] = scores[0]
        else:
            single_ans[date] = scores[0]
        if date in multiple_ans:
            if scores[1] > multiple_ans[date]:
                multiple_ans[date] = scores[1]
        else:
            multiple_ans[date] = scores[1]
    write_to_file(single_ans, multiple_ans, fileName)
    

if __name__ == "__main__":
    main()
