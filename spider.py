import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import sys



#benchmark_url = "https://browser.geekbench.com/geekbench3/singlecore?dir=desc&page="
url_launch_date = "https://www.cpubenchmark.net/cpu.php?cpu="
benchmark_url = "http://browser.geekbench.com/geekbench3/search?&q=intel&page="
search_url = "https://ark.intel.com/search?q="
proxy = {'http': '127.0.0.1:8050'}
ans_single = {}
ans_multiple = {}
bad_data = []
all_name = {}

def run_fetch(page_id):
    print('Get benchmark page %d' % (page_id))
    url = benchmark_url + str(page_id)
    #r = requests.get(url, proxies=proxy)
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
        search = search_url + "+".join(core_name.split(" "))
        b = requests.get(search)
        search_soup = BeautifulSoup(b.text, 'lxml')
        try:
            release_date = search_soup.find("div", class_="search-result").find('div', class_="result-description").find('div', class_="result-details").find('ul', class_="list-status").find_all("li")[2].find('span', class_="value").get_text().strip()
            release_date = release_date.split("'")
            release_date = str(release_date[1] + release_date[0])
            all_name[core_name] = release_date
        except Exception as e:
            bad_data.append((core_name, int(single_score), int(multiple_score)))
            release_date = "N/A"
            print("Can't find the cpu which name is " + core_name)
            all_name[core_name] = release_date
            ret.append((core_name, single_score, multiple_score, release_date))
            continue
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
    bad_data = []
    ans_single, ans_multiple = init_score()
    with open("bad_data.txt", "r") as f:
        for d in f.readlines():
            d = d.strip().split(" ")
            bad_data.append((d[0], int(d[1]), int(d[2])))

    for i in range(10000, 40000):
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







