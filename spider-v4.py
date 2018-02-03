import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import sys



url_launch_date = "https://www.cpubenchmark.net/cpu.php?cpu="
benchmark_url = "http://browser.geekbench.com/geekbench3/search?&q=AMD&page="
proxy = {'http': '127.0.0.1:8050'}
ans_single = {}
ans_multiple = {}
bad_data = []
all_name = {}

def fetch_launch_date(cpu_name):
    r = requests.get(url_launch_date + cpu_name)
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

def run_fetch(page_id):
    print('Get benchmark page %d' % (page_id))
    url = benchmark_url + str(page_id)
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "lxml")
    #find all score line
    lines = soup.find_all("td", class_="model")
    if len(lines) == 0:
        print ("rejected by remote server....")
    ret = []
    for line in lines:
        core_name = line.find('span').get_text().split("\n")[1]
        scores = line.find_next_siblings('td', class_="score")
        single_score = int(scores[0].get_text().strip())
        multiple_score = int(scores[1].get_text().strip())
        if core_name in all_name:
            ret.append((core_name, single_score, multiple_score, all_name[core_name]))
            continue
        release_date = fetch_launch_date("+".join(core_name.split(" ")))
        all_name[core_name] = release_date
        print ("benchmark, name = %s, single_score = %s, multiple_score = %s, release_date = %s" % (core_name, single_score, multiple_score, release_date))
        ret.append((core_name, single_score, multiple_score, release_date))
    return ret


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

def main():
    thread_num = int(sys.argv[1])
    ans = []
    pool = ThreadPoolExecutor(thread_num)
    single_score = {}
    multiple_score = {}
    bad_data = []
    single_score, multiple_score = init_score()
    with open("bad_data.txt", "r") as f:
        for d in f.readlines():
            d = d.strip().split(" ")
            bad_data.append((d[0], int(d[1]), int(d[2])))

    for i in range(1, 10):
        ans.append(pool.submit(run_fetch, i))
    for a in ans:
        result = a.result()
        for itr in result:
            core_name, single_score, multiple_score, release_date = itr
            if release_date == "N/A":
                bad_data.append((core_name, single_score, multiple_score))
                continue
            if release_date in ans_single:
                if ans_single[release_date] < single_score:
                    ans_single[release_date] = single_score
            else:
                ans_single[release_date] = single_score
            if release_date in ans_multiple:
                if ans_multiple[release_date] < multiple_score:
                    ans_multiple[release_date] = multiple_score
            else: 
                ans_multiple[release_date] = multiple_score
    single_ans = sorted(ans_single.items(), key=lambda item:item[0])
    multiple_ans = sorted(ans_multiple.items(), key = lambda item:item[0])
    with open("single_score2.txt", 'w') as f:
        for s in single_ans:
            f.write(s[0] + ' ' + str(s[1]) + "\n")

    with open("multiple_score2.txt", 'w') as f:
        for s in multiple_ans:
            f.write(s[0] + ' ' + str(s[1]) + "\n")

    with open("bad_data2.txt", 'w') as f:
        for s in bad_data:
            f.write(s[0] + ' ' + str(s[1]) + ' ' + str(s[2]) + "\n")

if __name__ == "__main__":
    main()







