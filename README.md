# youtube
Youtube UP信息及视频爬取
项目介绍：爬取国外网站时需要使用代理，对于UP下面的第一页视频信息在不规范的源码中，使用正则来解析。往下滑动加载出的第二段数据，第二段及后几段数据均由二次请求得到，请求参数中设置hl来控制语言类型。爬取视频时，令视频开始播放，并从众多请求中找到规律，通过正则获取json数据，其中视频的每个分辨率都分别对应两个链接，最终爬取mp4最高质量视频和mp3音频，使用ffmpeg将它们合并，并使用stream参数和tqdm库来实现进度条的展示。
