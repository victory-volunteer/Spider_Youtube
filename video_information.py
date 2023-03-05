# coding:utf-8
import re
import requests
import xlwt

PROXY = {"https": "127.0.0.1:7890"}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.24",
    "accept-language": "zh-CN,zh;q=0.9"
}
# 统计爬取条目
x = 1


def first_page(s, url):
    '''
    获取第一段数据（前30个）信息
    :return: 其他段数据的请求url中的一个参数
    '''
    try:
        result = s.get(url, headers=headers, proxies=PROXY, timeout=20)
    except Exception as e:
        print('超时原因：', e)
    else:
        count = 0
        # 获取下一次请求需要的continuation参数
        continuation = re.search(r'"continuationCommand":\{"token":"(.*?)","request":".*?"}}}}]', result.text).group(1)
        # 获取前30个视频的标题，发布时间，时长，观看数 以及视频链接
        label_obj = re.compile(
            r'}],"accessibility":{"accessibilityData":{"label":"(.*?)"}.*?","commandMetadata":{"webCommandMetadata":{"url":"(/watch.*?)",')
        labels = label_obj.finditer(result.text)
        for i in labels:
            label_list = i.group(1).rsplit(" ", 4)
            title = label_list[0]
            release_time = label_list[2]
            duration = label_list[3]
            watch = label_list[4]
            video_url = 'https://www.youtube.com' + i.group(2)
            data_storage(title, release_time, duration, watch, video_url)
            count += 1
        print(f"前{count}条视频信息获取成功")

        # 实测得知后面的请求不需要这个参数
        # innertubeApiKey = re.search(r'"innertubeApiKey":"(.*?)"', result.text).group(1)

        return continuation


def other_page(s, url, continuation):
    '''
    获取其余数据信息
    :param continuation: post表单中的可变参数, 待解决
    :return:
    '''
    headers['referer'] = url
    headers['content-type'] = 'application/json'

    # real_url = f'https://www.youtube.com/youtubei/v1/browse?key={innertubeApiKey}&prettyPrint=false'
    # 实测得知后面的参数没用，仅需要https://www.youtube.com/youtubei/v1/browse
    real_url = 'https://www.youtube.com/youtubei/v1/browse'

    data = {
        "context": {
            "client": {
                "hl": "zh-CN",  # 控制着响应语言类型
                "clientName": "WEB",
                "clientVersion": "2.20221026.05.00",
            },
        },
        "continuation": continuation
    }
    try:
        result = s.post(real_url, json=data, headers=headers, proxies=PROXY, timeout=20)
    except Exception as e:
        print('超时原因：', e)
    else:
        information = result.json()['onResponseReceivedActions'][0]['appendContinuationItemsAction'][
            'continuationItems']
        if len(information) == 31:
            continuation = information[-1]['continuationItemRenderer']['continuationEndpoint']['continuationCommand'][
                'token']
            information = information[:-1]
        else:
            continuation = None
        count = 0
        for i in information:
            all = i['richItemRenderer']['content']['videoRenderer']
            title = all['title']['runs'][0]['text']
            release_time = all['publishedTimeText']['simpleText']
            duration = all['lengthText']['accessibility']['accessibilityData']['label']
            watch = all['viewCountText']['simpleText']
            video_url = 'https://www.youtube.com' + all['navigationEndpoint']['commandMetadata']['webCommandMetadata'][
                'url']
            data_storage(title, release_time, duration, watch, video_url)
            count += 1
        print(f"处理完{count}条数据")
        return continuation


def data_storage(title, release_time, duration, watch, video_url):
    """
    保存数据信息
    :param title:
    :param release_time:
    :param duration:
    :param watch:
    :param video_url:
    :return:
    """
    global x
    # 写入execl文件
    worksheet.write(x, 0, title)
    worksheet.write(x, 1, release_time)
    worksheet.write(x, 2, duration)
    worksheet.write(x, 3, watch)
    worksheet.write(x, 4, video_url)
    workbook.save("油管.xls")
    print(f'-------第{x}条写入------')

    x += 1


if __name__ == '__main__':
    s = requests.session()

    # 表头数据预处理
    workbook = xlwt.Workbook(encoding='ascii')
    worksheet = workbook.add_sheet("data1")
    worksheet.write(0, 0, "标题")
    worksheet.write(0, 1, "发布时间")
    worksheet.write(0, 2, "时长")
    worksheet.write(0, 3, "观看数")
    worksheet.write(0, 4, "url")
    workbook.save("油管.xls")

    username = '@qiongren'
    url = f'https://www.youtube.com/{username}/videos'
    # 处理前30个数据
    continuation = first_page(s, url)

    # 处理后面的数据
    while True:
        if continuation is not None:
            continuation = other_page(s, url, continuation)
        else:
            break
    print(f"{x-1}条数据爬取完毕")