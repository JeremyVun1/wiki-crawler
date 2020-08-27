from argparse import ArgumentParser
from bs4 import BeautifulSoup
import time, requests, re


def get_next_link(body, links_seen, regex):
    for p in body.find_all('p'):
        for link in p.find_all('a', href=regex):
            link_topic = link["href"].split("/")[-1]
            if link_topic not in links_seen:
                return link_topic

    return None


def crawl(next_link, end_topic):
    baseUrl = "https://en.wikipedia.org"
    link_regex = re.compile("^/wiki/[A-Za-z1-10_% ]*$")

    links_seen = {}
    trace_history = []

    while(next_link):
        req_start = time.time()

        src = requests.get(f"{baseUrl}/wiki/{next_link}").text
        soup = BeautifulSoup(src, "lxml")
        links_seen[next_link] = True

        topic_title = soup.title.string.replace(" - Wikipedia", "")
        trace_history.append(topic_title)

        # goal check
        if topic_title == end_topic:
            req_end = time.time()
            print(f"{topic_title} - {int((req_end-req_start)*1000)}ms")
            return True, trace_history
        
        next_link = get_next_link(soup.body, links_seen, link_regex)

        req_end = time.time()
        print(f"{topic_title} ({int((req_end-req_start)*1000)}ms)")

    return False, trace_history


if __name__ == "__main__":
    parser = ArgumentParser(description='Find trace from given page to another page')
    parser.add_argument('--start', type=str, default="Main_Page", metavar="TOPIC", help="start topic")
    parser.add_argument('--end', type=str, default="Philosophy", metavar="TOPIC", help="end topic")
    args = parser.parse_args()

    try:
      result, trace = crawl(args.start, args.end)
      
      with open('trace.txt', 'w') as f:
          for topic in trace:
              f.write("%s\n" % topic)
    except Exception as e:
      print(e)