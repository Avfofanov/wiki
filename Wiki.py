import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import deque
import time
import threading

class WikipediaSixDegrees:
    def __init__(self, rate_limit=5):
        self.rate_limit = rate_limit
        self.semaphore = threading.Semaphore(rate_limit)
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'SixDegreesOfSeparation/1.0'})
        self.visited = set()

    def get_links(self, url):
        with self.semaphore:
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')

                content = soup.find(id='mw-content-text')
                if not content:
                    return []

                links = set()

                for paragraph in content.find_all('p'):
                    for link in paragraph.find_all('a', href=True):
                        href = link['href']
                        if href.startswith('/wiki/') and ':' not in href:
                            full_url = urljoin('https://en.wikipedia.org', href)
                            links.add(full_url)

                references = soup.find(id='references') or soup.find(class_='reflist')
                if references:
                    for link in references.find_all('a', href=True):
                        href = link['href']
                        if href.startswith('/wiki/') and ':' not in href:
                            full_url = urljoin('https://en.wikipedia.org', href)
                            links.add(full_url)

                return list(links)
            except Exception as e:
                print(f"Ошибка загрузки {url}: {e}")
                return []

    def find_path(self, start_url, target_url):
        queue = deque()
        queue.append((start_url, [start_url]))
        self.visited.add(start_url)

        while queue:
            current_url, path = queue.popleft()

            if len(path) > 5:
                continue

            links = self.get_links(current_url)

            for link in links:
                if link == target_url:
                    return path + [link]

                if link not in self.visited:
                    self.visited.add(link)
                    queue.append((link, path + [link]))

            time.sleep(0.2)

        return None

    def find_path_bidirectional(self, url1, url2):
        self.visited = set()
        path1 = self.find_path(url1, url2)

        self.visited = set()
        path2 = self.find_path(url2, url1)

        return path1, path2

def main():
    url1 = "https://en.wikipedia.org/wiki/Six_degrees_of_separation"
    url2 = "https://en.wikipedia.org/wiki/American_Broadcasting_Company"
    rate_limit = 5

    checker = WikipediaSixDegrees(rate_limit)

    print("Поиск пути от  URL1 до URL2 и обратно...")
    path1, path2 = checker.find_path_bidirectional(url1, url2)

    print("\nResults:")
    if path1:
        print(f"Путь от URL1 до URL2: {path1}")
    else:
        print("Путь от URL1 до URL2 не найден")

    if path2:
        print(f"Путь от URL2 до URL1: {path2}")
    else:
        print("Путь от URL2 до URL1 не найден")

if __name__ == "__main__":
    main()
