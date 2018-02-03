import requests
from bs4 import BeautifulSoup
import sys

url = "https://www.cpubenchmark.net/cpu.php?cpu="
multi_benchmark= "http://browser.geekbench.com/geekbench3/search?dir=desc&sort=multicore_score&q="
benchmark = "http://browser.geekbench.com/geekbench3/search?dir=desc&sort=score&q="

def fetch_score(cpu_name):
    r = requests.get(benchmark + cpu_name)
    soup = BeautifulSoup(r.text, "lxml")
    scores = soup.find("td", class_="model").find_next_siblings("td", class_="score")

    b = requests.get(multi_benchmark + cpu_name)
    soup2 = BeautifulSoup(b.text, 'lxml')
    scores2 = soup2.find("td", class_="model").find_next_siblings("td", class_="score")
    return (int(scores[0].get_text().strip()), int(scores2[1].get_text().strip()))

def fetch_launch_date(cpu_name):
    r = requests.get(url + cpu_name)
    soup = BeautifulSoup(r.text, "lxml")
    try:
        td = soup.find("table", class_="desc").find_all("tr")[1].find("td")
        it = td.contents
        date = ""
        for i in range(len(it)):
            try:
                if it[i].get_text().strip() == "CPU First Seen on Charts:":
                    date = it[i + 1].string.strip()
                    date = date.split(" ")
                    date = date[1][2:4] + date[0]
                    break;
            except Exception as e:
                date = ""

            if date == "":
                date = "N/A"
    except Exception as e:
        print ("find td err:", e)
        return "N/A"
    return date



def main():
    fileName = sys.argv[1]
    single_ans = {}
    multiple_ans = {}
    bad_data = []
    with open(fileName, "r") as f:
        for line in f.readlines():
            line = line.strip()
            print ("fetch %s data " % (line))
            try:
                scores = fetch_score(line)
            except Exception as e:
                print ("fetch score err:", e)
                continue
            date = fetch_launch_date(line)
            if date == "N/A":
                bad_data.append((date, scores[0], scores[1]))
                continue
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

    single_ans = sorted(single_ans.items(), key=lambda item:item[0])
    multiple_ans = sorted(multiple_ans.items(), key = lambda item:item[0])
    name = fileName.split(".")[0]
    with open(name + "_single_score.txt", 'w') as f:
        for s in single_ans:
            f.write(s[0] + ' ' + str(s[1]) + "\n")
    with open(name + "_multiple_score.txt", 'w') as f:
        for s in multiple_ans:
            f.write(s[0] + ' ' + str(s[1]) + "\n")
    with open("bad_data.txt", 'w') as f:
        for s in bad_data:
            f.write(s[0] + ' ' + str(s[1]) + ' ' + str(s[2]) + "\n")

def test_bad_data():
    fileName = sys.argv[1]
    bad_data = []
    with open(fileName, "r") as f:
        for line in f.readlines():
            line = line.strip()
            date = fetch_launch_date(line)
            if date == "N/A":
                try:
                    scores = fetch_score(line)
                except Exception as e:
                    print ("fetch score err:", e)
                    continue
                bad_data.append((line, scores[0], scores[1]))
    with open("bad_data.txt", 'w') as f:
        for s in bad_data:
            f.write(s[0] + ' ' + str(s[1]) + ' ' + str(s[2]) + "\n")
if __name__ == "__main__":
    test_bad_data()



