## Asyncio Concurrent Downloading Prototypes
This repo contains some asyncio based prototypes for the [Pulp](http://pulpproject.org/) project.


### The basic downloader

The [first prototype](https://github.com/bmbouter/asyncio_downloader_prototype/blob/master/async.py)
is a basic concurrent downloader using asyncio and aiohttp. One of the goals is to have control
returned to the caller with each content unit that finishes.


### A "Content Unit" downloader

The [second prototype](https://github.com/bmbouter/asyncio_downloader_prototype/blob/master/content_unit_downloader.py)
is a content unit downloader. This builds on top of the first, but instead of returning control to
the caller with each download, it returns control when all downloads associate with a content unit
are completed.

#### Features:
* all urls are downloaded in parallel
* the content units are emitted only when all downloads are completed
* content units are emitted via looping
* additional content units can be registered for downloading after downloading has begun
* urls are de-duplicated, so even if urls belong to multiple content units, files are only downloaded once
* correctly handles cases where a file is needed by multiple content units
