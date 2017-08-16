import aiohttp
import asyncio
import async_timeout
import os


async def ConcurrentHttpDownloader(url, timeout=10):
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
            return filename  # TODO have this return the digest and size validators


def main():
    urls = ["https://repos.fedorapeople.org/pulp/pulp/fixtures/file/1.iso",
            "https://repos.fedorapeople.org/pulp/pulp/fixtures/file/2.iso",
            "https://repos.fedorapeople.org/pulp/pulp/fixtures/file/3.iso"
            ]
    not_done = [ConcurrentHttpDownloader(url) for url in urls]

    loop = asyncio.get_event_loop()

    # to wait for all to finish without exception raising support
    # done, not_done = loop.run_until_complete(asyncio.wait(unfinished, return_when=asyncio.ALL_COMPLETED))

    # to stream process each result
    # will not raise an exception in the foreground, but done results will have the 'exception'
    # attribute set and not the 'result' attribute in the case of an exception
    while not_done:
        done, not_done = loop.run_until_complete(asyncio.wait(not_done, return_when=asyncio.FIRST_COMPLETED))
        print('finished = %s' % done)
        print('unfinished = %s' % not_done)


if __name__ == '__main__':
    main()