import random
import os
import string
import re
import asyncio
import aiofiles
import aiohttp


async def send_requests(session,url):
    async with session.get(url = url) as response:
        return await response.text()


def _clear_url(any_quality,link_quality):
    for link in any_quality:
        split_url = link.split('"')
        cleaning_url = split_url[13].replace('\/','/')
        link_quality[split_url[3]] = cleaning_url
    return link_quality


async def merge_file(file_list):
    N = 7
    output_filename = ''.join(random.choices(string.ascii_uppercase +string.digits, k=N))
    async with aiofiles.open('reall'+output_filename+'.mp4','ab') as out:
         for file in file_list:
             data = open(file,'rb').read()
             await out.write(data)

def clear_download_url(url_list):
    puch = []
    for uri in url_list:
        if uri.startswith('seg') == True:
             puch.append(uri)
    return puch


def delete_ts_file():
    all_file = os.listdir('.')
    for f in all_file:
       if f.endswith('.ts'):os.remove(f)

async def download_content(session,link):
     N = 7
     res = ''.join(random.choices(string.ascii_uppercase +string.digits, k=N))
     async with session.get(url = link) as response:
        open(f'{res}.ts','wb').write(await response.read())
        return res+'.ts'


async def download_video(tmp_url,download_url):
    async with aiohttp.ClientSession() as session:
        task_download = [download_content(session,tmp_url+urls) for urls in download_url]
        return await asyncio.gather(*task_download)

def extract_quality(source):
    try:
        link_quality = {}
        search_1080p_quality = re.search(r'videoUrl":.*?"1080"',source)
        url_1080 = search_1080p_quality.group(0).split('"')[2].replace('\/','/')
        search_any_quality = re.findall(r'"quality":"\d\d\d".*?videoUrl":".*?"',source)
        link_quality['1080'] = url_1080
        return _clear_url(search_any_quality,link_quality)
    except:
        return _clear_url(search_any_quality,link_quality)


async def main():
    async with aiohttp.ClientSession() as session:
          video = input("get video: ")
          task1 = asyncio.create_task(send_requests(session,video))
          all_url = extract_quality(await task1)
          print ([int(qua) for qua in all_url.keys()])
          quality = input("want: ")
          tmp_url = all_url[quality].split('master')[0]
          get_m3u8_url = await send_requests(session,all_url[quality])
          add_url = get_m3u8_url.split('\n')[2]
          m3u8_url = await send_requests(session,tmp_url + add_url)
          url_list = m3u8_url.split('\n')
          download_url = clear_download_url(url_list)
          task2 = asyncio.create_task(download_video(tmp_url,download_url))
          await merge_file(await task2)
if __name__ == "__main__":
    asyncio.run(main())

