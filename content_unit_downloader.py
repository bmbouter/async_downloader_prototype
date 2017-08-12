import aiohttp
import asyncio
import async_timeout
from collections import defaultdict
import os


async def ConcurrentHttpDownloader(url, timeout=600):
    async with aiohttp.ClientSession() as session:
        with async_timeout.timeout(timeout):
            async with session.get(url) as response:
                filename = os.path.basename(url)
                with open(filename, 'wb') as f_handle:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            print('Finished downloading {filename}'.format(filename=filename))
                            break
                        f_handle.write(chunk)
                        # push each chunk through the digest and size validators
            await response.release()
            return url, filename  # TODO have this return the digest and size validators


class DownloadAll(object):

    def __init__(self):
        self.downloads_not_done = []
        self.content_units_not_done = []
        self.urls = defaultdict(list) # dict of lists keyed on urls which point to a list of ContentUnitDownloader objects

    def register_for_downloading(self, content_unit):
        self.content_units_not_done.append(content_unit)
        for url in content_unit.urls:
            if len(self.urls[url]) == 0:
                # This is the first time we've seen this url so make a downloader
                downloader_for_url = ConcurrentHttpDownloader(url)
                self.downloads_not_done.append(downloader_for_url)
            self.urls[url].append(content_unit)

    async def __call__(self):
            while self.downloads_not_done:
                done_this_time, self.downloads_not_done = await asyncio.wait(self.downloads_not_done, return_when=asyncio.FIRST_COMPLETED)
                for task in done_this_time:
                    # TODO check for errors here in task.exception() or similar
                    url, filename = task.result()
                    for content_unit in self.urls[url]:
                        content_unit.finished_urls.append(url)
                for index, content_unit in enumerate(self.content_units_not_done):
                    if content_unit.done:
                        self.content_units_not_done.pop(index)
                        return content_unit


class ContentUnitDownloader(object):

    def __init__(self, name, urls):
        self.name = name
        self.urls = set(urls)
        self.finished_urls = []

    @property
    def done(self):
        return len(self.urls) == len(self.finished_urls)


def plugin_writers_code():
    content_unit_a = [
        "https://repos.fedorapeople.org/pulp/pulp/fixtures/file/1.iso",
    ]
    content_unit_b = [
        "https://repos.fedorapeople.org/pulp/pulp/fixtures/file/1.iso",
        "https://repos.fedorapeople.org/pulp/pulp/fixtures/file/2.iso",
        "https://repos.fedorapeople.org/pulp/pulp/fixtures/file/3.iso",
        "https://repos.fedorapeople.org/pulp/pulp/fixtures/file/1.iso",
        "https://repos.fedorapeople.org/pulp/pulp/fixtures/file/2.iso",
        "https://repos.fedorapeople.org/pulp/pulp/fixtures/file/3.iso",
    ]
    downloader_a = ContentUnitDownloader('a', content_unit_a)
    downloader_b = ContentUnitDownloader('b', content_unit_b)

    download_all = DownloadAll()
    download_all.register_for_downloading(downloader_a)
    download_all.register_for_downloading(downloader_b)

    loop = asyncio.get_event_loop()
    content_unit = True

    c = []
    while content_unit:
        content_unit = loop.run_until_complete(download_all())
        c.append(content_unit)
        print('content_unit = {0}'.format(content_unit))


if __name__ == '__main__':
    plugin_writers_code()
