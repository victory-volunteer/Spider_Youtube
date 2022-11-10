import requests
import re
import json
from tqdm import tqdm
import os
from concurrent.futures import ThreadPoolExecutor


def video(url):
    try:
        result = s.get(url, headers=headers,
                       proxies={"https": "127.0.0.1:10809"}, timeout=20)
    except Exception as e:
        print('超时原因：', e)
    else:
        json_str = re.compile(r'var ytInitialPlayerResponse = (.*?);var')
        json_str = json_str.search(result.text).group(1)
        json_data = json.loads(json_str)

        # 提取最高画质1080p视频链接(video/mp4格式)
        video_url = json_data['streamingData']['adaptiveFormats'][0]['url']

        # 提取最高质量音频链接(audio/mp4格式)
        audio_url = json_data['streamingData']['adaptiveFormats'][12]['url']
        # 提取音频类型(仅用来测试确认)
        # audio_mimeType = json_data['streamingData']['adaptiveFormats'][12]['mimeType']
        # print(audio_mimeType)

        # 提取视频标题
        title = json_data['videoDetails']['title']
        # 替换掉标题当中的空格
        title = title.replace(' ', '')
        # 替换掉标题当中的非法字符
        title = re.sub(r'[\/:*?"<>|]', '_', title)

        # video_download(video_url, title)
        # audio_download(audio_url, title)

        # 创建线程池(使用线程池后进度条的打印会变乱, 暂时没有解决)
        with ThreadPoolExecutor(2) as t:
            # 把下载任务提交给线程池
            t.submit(video_download, video_url, title)
            t.submit(audio_download, audio_url, title)

        # 合并视频
        merge(title)


def video_download(video_url, title):
    try:
        video = requests.get(video_url, stream=True, proxies={"https": "127.0.0.1:10809"}, timeout=20)
    except Exception as e:
        print('超时原因：', e)
    else:
        # 获取视频大小
        file_size = int(video.headers.get('Content-Length'))
        # 初始化进度条大小
        video_pbar = tqdm(total=file_size)
        # 保存视频步骤
        with open(f'{title}.mp4', mode='wb') as f:
            # iter_content用来把视频分成 1024 * 1024 * 2 为等分的大小段(即每次在响应中迭代 1024 * 1024 * 2 字节), 然后一段一段进行遍历
            for video_chunk in video.iter_content(1024 * 1024 * 2):
                # 写入数据
                f.write(video_chunk)
                # 更新进度条
                video_pbar.set_description(f'正在下载{title}视频中......')
                # 更新进度条长度(进度条每迭代一次就增加 1024 * 1024 * 2 长度)
                video_pbar.update(1024 * 1024 * 2)
            # 下载完毕
            video_pbar.set_description('视频下载完成！')
            # 关闭进度条
            video_pbar.close()


def audio_download(audio_url, title):
    try:
        audio = requests.get(audio_url, stream=True, proxies={"https": "127.0.0.1:10809"}, timeout=20)
    except Exception as e:
        print('超时原因：', e)
    else:
        file_size = int(audio.headers.get('Content-Length'))
        audio_pbar = tqdm(total=file_size)
        with open(f'{title}.mp3', mode='wb') as f:
            for audio_chunk in audio.iter_content(1024 * 1024 * 2):
                f.write(audio_chunk)
                audio_pbar.set_description(f'正在下载{title}音频中......')
                audio_pbar.update(1024 * 1024 * 2)
            audio_pbar.set_description('音频下载完成！')
            audio_pbar.close()


def merge(title):
    ffmpeg = r'ffmpeg.exe -i ' + title + '.mp4 -i ' + title + '.mp3 -acodec copy -vcodec copy ' + title + '-out.mp4'
    os.popen(ffmpeg)


if __name__ == '__main__':
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
    }
    s = requests.session()

    url = 'https://www.youtube.com/watch?v=sZBP7lNtLuU'
    video(url)