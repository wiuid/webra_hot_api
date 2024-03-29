"""
@author: webra/lzm
@time: 2023/3/27 13:31
@description:  热榜
@update: 2024/02/14 15:54:34
"""
import glob
import re
import time
import datetime

import requests
import json
from lxml import etree
import random
import os
import urllib3

from flask import Flask
import logging

if not os.path.exists('./data'):
    os.makedirs('./data')

# 12小时更新一次
global_timeout_file = 24
# 讯代理
#proxy_address = "http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?spiderId=f1ed1b2a97294f74b34002bdccaedcd0&orderno=YZ2018954898PnB882&returnType=2&count=1"
proxy_address = ""
# web服务启动
app = Flask(__name__)
app.config['LOGGER_NAME'] = 'app'
app.config['LOGGER_LEVEL'] = logging.NOTSET

# 以utf-8编码读取文件
def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        return content


# 删除文件
def del_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


# 以utf-8编码写入文件
def write_file(file_path, content, type=None):
    type = 'w' if type is None else 'a'
    with open(file_path, type, encoding='utf-8') as f:
        f.write(content)

# 根目录提示
@app.route("/")
def index():
    data_dict = {"get_wuai_data": "吾爱热榜",
                 "get_zhihu_data": "知乎热榜",
                 "get_bilibili_data": "bilibili全站日榜",
                 "get_bilibili_hot": "bilibili热搜榜",
                 "get_acfun_data": "acfun热榜",
                 "get_hupu_data": "虎扑步行街热榜",
                 "get_smzdm_data": "什么值得买热榜",
                 "get_weibo_data": "微博热榜",
                 "get_tieba_data": "百度贴吧热榜",
                 "get_weixin_data": "微信热榜",
                 "get_ssp_data": "少数派热榜",
                 "get_36k_data": "36Kr热榜"}
    json_data = {}
    json_data["secure"] = True
    json_data["title"] = "热榜接口"
    json_data["update_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    json_data["data"] = data_dict
    return json.dumps(json_data, ensure_ascii=False)

# 随机UA
def random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 Edg/81.0.416.72",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36 Edg/84.0.522.40",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    ]
    return random.choice(user_agents)

# 获取代理IP
def get_proxy_ip():
    if proxy_address != "":
        url = proxy_address
        response = get_html(url, None, "dict")
        proxy_ip = response['data'][0]['ip'] + ":" + str(response['data'][0]['port'])
        app.logger.warning("获取到的代理ip：" + proxy_ip)
        return proxy_ip
    else:
        return None

"""
url：字符串类型，表示要访问的网址。
headers：字典类型，包含HTTP请求头信息，用于模拟浏览器发送请求。
res_data_type：字符串类型，指示响应数据类型，只能是html、dict
"""
def get_html(url, headers, res_data_type, proxy_ip=None):
    # 如果headers是字符串类型，则使用该字符串作为HTTP请求头referer的值
    if isinstance(headers, dict):
        pass
    elif isinstance(headers, str):
        headers = {
            'referer': headers,
            'User-Agent': random_user_agent()}
    # 如果headers为None，则headers中只有UA信息
    elif headers is None:
        headers = {'User-Agent': random_user_agent()}

    # 数据请求
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    if proxy_ip is None:
        response = requests.get(url, headers=headers, verify=False)
    else:
        try:
            proxy = {
                'https': proxy_ip
            }
            response = requests.get(url, headers=headers, verify=False, proxies=proxy)
        except:
            app.logger.warning("请求失败")
            return 1
    # 根据请求数据类型做数据处理
    if res_data_type == "html":
        return etree.HTML(response.text)
    elif res_data_type == "dict":
        return json.loads(response.text)
    elif res_data_type == "obj":
        return response

def post_html(url, headers, data, res_data_type="dict"):
    if isinstance(headers, str):
        headers = {
            'referer': headers,
            'User-Agent': random_user_agent()}
    # 如果headers为None，则headers中只有UA信息
    elif headers is None:
        headers = {'User-Agent': random_user_agent()}

    # 发送POST请求
    response = requests.post(url, headers=headers, json=data)

    if res_data_type == "html":
        return etree.HTML(response.text)
    elif res_data_type == "dict":
        return json.loads(response.text)



# 获取文件中的数据，如果是过期数据则删除返回None，
# 或者找不到文件，直接返回None
def get_file_data(filename):
    # 获取文件名称
    filename_re = filename.replace("*", "(.*?)")
    file_names = glob.glob('./data/' + filename)
    file_names_len = len(file_names)
    # 存在一个文件
    if file_names_len == 1:
        # 获取文件名及路径
        file_name = file_names[0]
        # 获取文件名中的unix 时间戳
        old_timestamp = int(re.findall(filename_re, file_name)[0])
        # 将unix时间戳转换为datetime对象
        old_timestamp_datetime_obj = datetime.datetime.fromtimestamp(int(old_timestamp))
        # 当前时间减去文件名中的unix时间戳，获取时间差
        time_diff = datetime.datetime.now() - old_timestamp_datetime_obj
        # 如果时间差大于1个小时，就删除当前查询到的文件，并返回None
        # 否则，返回文件中的数据
        # print(time_diff)
        # print(datetime.timedelta(hours=1))
        if time_diff > datetime.timedelta(hours=global_timeout_file):
            del_file(file_name)
            return None
        else:
            file_contant = json.loads(read_file(file_name))
            return None if len(file_contant['data']) == 0 else file_contant
    # 不存在文件，返回None
    else:
        # 多个文件，全部删除
        if file_names_len > 1:
            [del_file(file_name) for file_name in file_names]
        return None


# json数据初始化
def init_json_data(title):
    if title == "err":
        return {"secure": False, "title": "ERROR", "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    return {"secure": True, "title": title, "update_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}


# data_list 赋值
def headle_html_data_list(datas, url_prefix="", hot_prefix=None):
    num = 1
    data_list = []
    for title, url, hot in zip(datas[0], datas[1], datas[2]):
        data_dict = {"index": num, "title": title, "url": url_prefix + url}
        num += 1
        # 热度值均高于1W的情况，简化输出
        if hot_prefix == 10000:
            hot = "{}{}".format(round(int(hot.strip()) / 10000, 1), "W")
        # 需要删除前后字符的情况
        elif isinstance(hot_prefix, int):
            hot = hot[:hot_prefix]
        # 需要去除前后空白内容的情况
        elif hot_prefix == "bili":
            hot = hot.split()[0]
        # 需要删除指定字符的情况
        elif isinstance(hot_prefix, str):
            hot = hot.replace(hot_prefix, "")
        data_dict["hot"] = hot
        data_list.append(data_dict)
    return data_list


# json数据最后处理
def end_json_data(json_data, data_list, filename):
    json_data["data"] = data_list
    data = json.dumps(json_data, ensure_ascii=False)
    if len(data_list) > 0:
        filename_prefix = filename.split("*")[0]
        filename = filename_prefix + str(int(time.time())) + ".data"
        write_file("./data/" + filename, data)
    return data



@app.route("/ghbk")
def ghbk():
    filename = "ghbk_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("果核剥壳最新数据")
        request = get_html("https://www.ghxi.com/ghapi?type=query&n=new", None, "dict")
        data_list = []
        num = 1
        for key in request["data"]["list"]:
            data_dict = {"index": num,
                         "title": key["title"],
                         "url": key["url"],
                         "hot": ""}
            num += 1
            data_list.append(data_dict)
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content


@app.route("/csdn")
def csdn():
    filename = "csdn_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("csdn热榜")
        headers = {"user-agent": random_user_agent()}
        data_list = []
        num = 1
        for i in range(0, 4):
            url = "https://blog.csdn.net/phoenix/web/blog/hot-rank?page=" + str(i) + "&pageSize=25&type="
            request = get_html(url, headers, "dict")
            for key in request["data"]:
                data_dict = {"index": num,
                             "title": key["articleTitle"],
                             "url": key["articleDetailUrl"],
                             "hot": key["pcHotRankScore"]}
                num += 1
                data_list.append(data_dict)
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content

@app.route('/wuai')
def wuai():
    filename = "wuai_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("吾爱热榜")
        # headers 信息
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "User-Agent": random_user_agent(),
            'Connection':'close'
        }
        request = get_html("https://www.52pojie.cn/forum.php?mod=guide&view=hot", headers, "html", get_proxy_ip())
        if request == 1:
            return file_content
        articles_title = request.xpath('/html/body/div[6]/div[2]/div/div/div[3]/div[2]/table/tbody/tr/th/a[1]/text()')
        articles_url = request.xpath('/html/body/div[6]/div[2]/div/div/div[3]/div[2]/table/tbody/tr/th/a[1]/@href')
        articles_hot = request.xpath('/html/body/div[6]/div[2]/div/div/div[3]/div[2]/table/tbody/tr/th/span[1]/text()')
        datas = [articles_title, articles_url, articles_hot]
        data_list = headle_html_data_list(datas, "https://www.52pojie.cn/", -2)
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content



# 知乎热榜
@app.route("/zhihu")
def zhihu():
    filename = "zhihu_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("知乎热榜")

        headers = {
            'Referer': 'https://www.zhihu.com/',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': random_user_agent()
        }
        reqiest = get_html("https://www.zhihu.com/billboard", headers, "html")
        all_content = reqiest.xpath('//*[@id="js-initialData"]/text()')
        all_content = json.loads("".join(all_content))["initialState"]["topstory"]["hotList"]
        data_list = []
        num = 1
        for key in all_content:
            hot = key["target"]["metricsArea"]["text"]
            hot = str(hot).replace(" 万热度", "W").replace("热度累计中", "1w")
            data_list.append({"index": num, "title": key["target"]["titleArea"]["text"], "url": key["target"]["link"]["url"], "hot": hot})
            num += 1
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content


# bilibili全站日榜，无got节点
@app.route("/bili/day")
def bili_day():
    filename = "bilibili_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("哔哩哔哩全站日榜")
        request = get_html("https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all", None, "dict")
        data_list = []
        num = 1
        for key in request["data"]["list"]:
            if key["stat"]["vv"] > 10000:
                hot = "{}{}".format(round(key["stat"]["vv"] / 10000, 1), "万")
            else:
                hot = key["stat"]["vv"]
            data_list.append({"index": num, "title": key["title"], "url": 'https://www.bilibili.com/video/' + key["short_link_v2"].split('/')[-1], "hot": hot})
            num += 1
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content


# bilibili热搜榜
@app.route("/bili/hot")
def bili_hot():
    filename = "bilibili_hot_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("bilibili热搜榜")
        data_list = []
        num = 1
        for index in range(1, 6):
            request = get_html(f"https://api.bilibili.com/x/web-interface/popular?ps=20&pn={index}", None, "dict")
            for key in request["data"]["list"]:
                if key["stat"]["vv"] > 10000:
                    hot = "{}{}".format(round(key["stat"]["vv"] / 10000, 1), "万")
                else:
                    hot = key["stat"]["vv"]
                data_list.append({"index": num, "title": key["title"], "url": 'https://www.bilibili.com/video/' + key["short_link_v2"].split('/')[-1], "hot": hot})
                num += 1
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content


# acfun热榜
@app.route("/acfun")
def acfun():
    filename = "acfun_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("acfun热榜")
        request = get_html(
            "https://www.acfun.cn/rest/pc-direct/rank/channel?channelId=&subChannelId=&rankLimit=30&rankPeriod=DAY",
            None, "dict")
        num = 1
        data_list = []
        for key in request["rankList"]:
            data_list.append({"index": num, "title": key["title"], "url": key["shareUrl"], "hot": key["viewCountShow"]})
            num += 1
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content


# 虎扑步行街热榜
@app.route("/hupu")
def hupu():
    filename = "hupu_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("虎扑步行街热榜")
        data_list = []
        request = get_html("https://bbs.hupu.com/all-gambia", None, "html")
        articles_title = request.xpath(
            '//*[@id="container"]/div/div[2]/div/div[2]/div/div[2]/div/div/div/div[1]/a/span/text()')
        articles_url = request.xpath(
            '//*[@id="container"]/div/div[2]/div/div[2]/div/div[2]/div/div/div/div[1]/a/@href')
        articles_hot = request.xpath(
            '//*[@id="container"]/div/div[2]/div/div[2]/div/div[2]/div/div/div/div[1]/span[1]/text()')
        datas = [articles_title, articles_url, articles_hot]
        data_list = headle_html_data_list(datas, "https://bbs.hupu.com/")
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content


# 什么值得买热榜（日榜）
@app.route("/smzdm")
def smzdm():
    filename = "smzdm_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("什么值得买热榜")
        request = get_html("https://post.smzdm.com/hot_1/", None, "html")
        articles_title = request.xpath('//*[@id="feed-main-list"]/li/div/div[2]/h5/a/text()')
        articles_url = request.xpath('//*[@id="feed-main-list"]/li/div/div[2]/h5/a/@href')
        articles_hot = request.xpath('//*[@id="feed-main-list"]/li/div/div[2]/div[2]/div[2]/a[1]/span[2]/text()')
        data_list = headle_html_data_list([articles_title, articles_url, articles_hot])
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content


# 微博热榜
@app.route("/weibo")
def weibo():
    filename = "weibo_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("微博热榜")
        request = get_html("https://weibo.com/ajax/statuses/hot_band", "https://weibo.com/", "dict")
        data_list = []

        for key in request["data"]["band_list"]:
            try:
                data_dict = {"index": key["realpos"],
                             "title": key["word"],
                             "url": "https://s.weibo.com/weibo?q=%23" + key["word"] + "%23",
                             "hot": str(round(key["raw_hot"] / 10000, 1)) + "万"
                             }
                data_list.append(data_dict)
            except KeyError:
                continue
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content


# 百度贴吧热议榜
@app.route("/tieba")
def tieba():
    filename = "tieba_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("百度贴吧热议榜")
        data_list = []
        request = get_html("https://tieba.baidu.com/hottopic/browse/topicList?res_type=1", None, "html")
        articles_title = request.xpath('/html/body/div[2]/div/div[2]/div/div[2]/div[1]/ul/li/div/div/a/text()')
        articles_url = request.xpath('/html/body/div[2]/div/div[2]/div/div[2]/div[1]/ul/li/div/div/a/@href')
        articles_hot = request.xpath('/html/body/div[2]/div/div[2]/div/div[2]/div[1]/ul/li/div/div/span[2]/text()')
        datas = [articles_title, articles_url, articles_hot]
        data_list = headle_html_data_list(datas, "", "实时讨论")
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content


# 少数派热榜
@app.route("/ssp")
def ssp():
    filename = "ssp_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("少数派热榜")
        request = get_html(
            "https://sspai.com/api/v1/article/tag/page/get?limit=100000&tag=%E7%83%AD%E9%97%A8%E6%96%87%E7%AB%A0",
            None,
            "dict")
        index = 1
        data_list = []
        for key in request["data"]:
            try:
                data_dict = {
                    "index": index,
                    "title": key["title"],
                    "url": "https://sspai.com/post/" + str(key["id"]),
                    "hot": key["like_count"]
                }
                index += 1
            except KeyError:
                continue
            data_list.append(data_dict)
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content


# 36Kr热榜
@app.route("/36k")
def html_get_36k_data():
    json_data = init_json_data("36Kr热榜")
    data = [
        {"type": "renqi"},
        {"type": "shoucang"},
        {"type": "zonghe"}
    ]
    json_data["data"] = data
    return json.dumps(json_data, ensure_ascii=False)


# 36Kr热榜二级分类
@app.route("/36k/<type>")
def get_36k_data_type(type):
    types = ["renqi", "shoucang", "zonghe"]
    if type in types:
        return get_36k_data(type)
    else:
        return json.dumps(init_json_data("err"), ensure_ascii=False)


# type =  renqi|  zonghe| shoucang
def get_36k_data(type):
    data_list = []
    filename = "36kr_" + type + "_data_*.data"
    type_title_dict = {"renqi": "36Kr人气榜", "zonghe": "36Kr综合榜", "shoucang": "36Kr收藏榜"}
    if type in type_title_dict:
        title = type_title_dict[type]
    else:
        return json.dumps(init_json_data("err"), ensure_ascii=False)
    json_data = init_json_data(title)
    file_content = get_file_data(filename)
    if file_content is None:
        url = "https://www.36kr.com/hot-list/" + type + "/" + datetime.datetime.now().strftime("%Y-%m-%d") + "/1"
        request = get_html(url, 'https://www.36kr.com/', "html")
        articles_title = request.xpath(
            '//*[@id="app"]/div/div[2]/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[2]/div[2]/a/text()')
        articles_url = request.xpath(
            '//*[@id="app"]/div/div[2]/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[2]/div[2]/a/@href')
        articles_hot = request.xpath(
            '//*[@id="app"]/div/div[2]/div[3]/div/div/div[2]/div[1]/div/div/div/div/div[2]/div[2]/div/span/span/text()')
        datas = [articles_title, articles_url, articles_hot]
        data_list = headle_html_data_list(datas, "https://www.36kr.com", "热度")
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content


# 抖音热榜
@app.route("/douyin")
def douyin():
    filename = "douyin_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("抖音热榜")
        request = get_html('https://www.douyin.com/aweme/v1/web/hot/search/list/',
                           'https://www.douyin.com/', "dict")
        data_list = []
        for key in request["data"]["word_list"]:
            data_dict = {"index": key["position"],
                         "title": key["word"],
                         "url": "https://www.douyin.com/hot/" + key["sentence_id"],
                         "hot": str(round(key["hot_value"] / 10000, 1)) + "万"}
            data_list.append(data_dict)
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content


# 百度热榜
@app.route("/baidu")
def baidu():
    filename = "baidu_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("百度热榜")
        request = get_html('https://top.baidu.com/board?tab=realtime', 'https://www.baidu.com/', "html")
        articles_title = request.xpath('//*[@id="sanRoot"]/main/div[2]/div/div[2]/div/div[2]/a/div[1]/text()')
        articles_url = request.xpath('//*[@id="sanRoot"]/main/div[2]/div/div[2]/div/div[2]/a/@href')
        articles_hot = request.xpath('//*[@id="sanRoot"]/main/div[2]/div/div[2]/div/div[1]/div[2]/text()')
        datas = [articles_title, articles_url, articles_hot]
        data_list = headle_html_data_list(datas, "", 10000)
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content


# 历史上的今天
def get_history_data(filename, curr_month, curr_day):
    filename_re = filename.replace("*", "(.*?)")
    file_names = glob.glob(
        './data/' + filename)
    file_names_len = len(file_names)
    if file_names_len == 1:
        # 获取文件名及路径
        file_name = file_names[0]
        # 获取文件名中的unix 时间戳
        old_timestamp = int(re.findall(filename_re, file_name)[0])
        # 将unix时间戳转换为datetime对象
        old_timestamp_datetime_obj = datetime.datetime.fromtimestamp(int(old_timestamp))
        if curr_month == old_timestamp_datetime_obj.month and curr_day == old_timestamp_datetime_obj.day:
            return read_file(file_name)
        else:
            del_file(file_name)
    return None

@app.route("/history")
def history():
    filename = "history_data_*.data"
    # 获取当天 月、日
    today = datetime.date.today()
    curr_month = today.month
    curr_day = today.day
    file_content = get_history_data(filename, curr_month, curr_day)
    if file_content is None:
        base_url = "https://zh.wikipedia.org/wiki/{}%E6%9C%88{}%E6%97%A5".format(curr_month, curr_day)
        json_data = init_json_data("历史上的今天")
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Cache-Control': 'max-age=0',
            'Cookie': 'WMF-Last-Access=28-Nov-2023; WMF-Last-Access-Global=28-Nov-2023; GeoIP=KR:11:Seoul:37.52:126.87:v4; NetworkProbeLimit=0.001; zhwikimwuser-sessionId=01024758f6f7520b528f'
        }

        request = get_html(base_url, header, "html")
        articles_title = request.xpath('//*[@id="mw-content-text"]/div[1]/h3/following-sibling::ul[1]/li')
        num = 0
        data_list = []
        articles_title_num = len(articles_title)
        for title in articles_title:
            title = etree.tostring(title, encoding='unicode')
            cleaned_text = re.sub(r'<.*?>|\n', '', title)
            data_dict = {"index": articles_title_num - num,
                             "title": cleaned_text}
            data_list.insert(0, data_dict)
            num += 1
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content
    filename = "history_data_*.data"

@app.route("/douban")
def douban():
    filename = "douban_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("豆瓣新片榜")
        request = get_html('https://movie.douban.com/chart', 'https://movie.douban.com/chart', "html")
        articles_title = request.xpath('//*[@id="content"]/div/div[1]/div/div/table/tr/td[1]/a/@title')
        articles_url = request.xpath('//*[@id="content"]/div/div[1]/div/div/table/tr/td[2]/div/a/@href')
        articles_hot = request.xpath('//*[@id="content"]/div/div[1]/div/div/table/tr/td[2]/div/div/span[2]/text()')
        c1 = []
        c2 = []
        c3 = []
            
        for title,url,hot in zip(articles_title, articles_url, articles_hot):
            c1.append(str(title))
            c2.append(str(url))
            c3.append(str(hot))
        datas = [c1, c2, c3]
        data_list = headle_html_data_list(datas, "")
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content

@app.route("/it/<rank>")
def it_home(rank):
    if rank == "day":
        rank_num = "2"
        rank_name = "日"
    elif rank == "week":
        rank_num = "4"
        rank_name = "周"
    elif rank == "hot":
        rank_num = "6"
        rank_name = "热评"
    else:
        rank = "month"
        rank_num = "8"
        rank_name = "月"
    # 2 是日榜
    # 4 是周榜
    # 6 是热评榜
    # 8 是月榜
    filename = "it_" + rank + "_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("IT之家_" + rank_name + "榜")
        request = get_html('https://m.ithome.com/rankm/', 'https://m.ithome.com/rankm/', "html")
        articles_title = request.xpath('/html/body/div[1]/div[2]/div[' + rank_num + ']/div/a/div[2]/p[1]/text()')
        articles_url = request.xpath('/html/body/div[1]/div[2]/div[' + rank_num + ']/div/a/@href')
        articles_hot = request.xpath('/html/body/div[1]/div[2]/div[' + rank_num + ']/div/a/div[2]/p[2]/span[3]/span/text()')
        datas = [articles_title, articles_url, articles_hot]
        return end_json_data(json_data, headle_html_data_list(datas), filename)
    else:
        return file_content


@app.route("/tencent")
def tencent():
    filename = "tennet_new_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("腾讯新闻热点榜")
        request = get_html("https://i.news.qq.com/gw/event/pc_hot_ranking_list?ids_hash=&offset=0&page_size=50&appver=15.5_qqnews_7.1.60&rank_id=hot", None, "dict")
        data_list = []
        for key in request["idlist"][0]["newslist"][1:51]:
            data_dict = {"index": key["ranking"],
                         "title": key["title"],
                         "url": key["url"],
                         "hot": "{}{}".format(round(int(key["hotEvent"]["hotScore"]) / 10000, 1), "W")}
            # hot = "{}{}".format(round(int(key["hotEvent"]["hotScore"]) / 10000, 1), "W")
            data_list.append(data_dict)
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content


@app.route("/wx")
def wx():
    filename = "wx_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("微信热点榜")
        headers = {
            'Authorization': "5daa2667123e702941a6d2bd7a5868ab",
            'User-Agent': random_user_agent()}
        # WnBe01o371
        # https://api.tophubdata.com/nodes/@hashid
        for i in range(0, 200):
            request = get_html("https://api.tophubdata.com/nodes?p=" + str(i), headers, "dict")
            
            write_file("./request.txt", bytes(json.dumps(request), 'utf-8').decode('unicode_escape'), "a")

        # data_list = []
        # for key in request["idlist"][0]["newslist"][1:51]:
        #     data_dict = {"index": key["ranking"],
        #                  "title": key["title"],
        #                  "url": key["url"],
        #                  "hot": "{}{}".format(round(int(key["hotEvent"]["hotScore"]) / 10000, 1), "W")}
        #     # hot = "{}{}".format(round(int(key["hotEvent"]["hotScore"]) / 10000, 1), "W")
        #     data_list.append(data_dict)
        # return end_json_data(json_data, data_list, filename)
    else:
        return file_content



@app.route("/wxbook/<rank>")
def wxbook(rank):
    if rank == "soar":
        rank_name = "飙升"
        rank_url = "https://weread.qq.com/web/category/rising"
    elif rank == "new":
        rank_name = "新书"
        rank_url = "https://weread.qq.com/web/category/newbook"
    elif rank == "god":
        rank_name = "神作"
        rank_url = "https://weread.qq.com/web/category/newrating_publish"
    elif rank == "novel":
        rank_name = "小说"
        rank_url = "https://weread.qq.com/web/category/general_novel_rising"
    elif rank == "hot":
        rank_name = "热搜"
        rank_url = "https://weread.qq.com/web/category/hot_search"
    elif rank == "potential":
        rank_name = "潜力"
        rank_url = "https://weread.qq.com/web/category/newrating_potential_publish"
    else:
        rank = "all"
        rank_name = "总"
        rank_url = "https://weread.qq.com/web/category/all"

    filename = "wx_book_" + rank + "_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("微信读书_" + rank_name + "榜")
        request = get_html(rank_url, rank_url, "html")
        articles_title = request.xpath('//*[@id="routerView"]/div[2]/div[2]/ul/li/div[1]/div[2]/p[1]/text()')
        articles_url = request.xpath('//*[@id="routerView"]/div[2]/div[2]/ul/li/a/@href')
        articles_hot = request.xpath('//*[@id="routerView"]/div[2]/div[2]/ul/li/div[1]/div[2]/p[3]/span[3]/span/text()')
        datas = [articles_title, articles_url, articles_hot]
        return end_json_data(json_data, headle_html_data_list(datas, "https://weread.qq.com/"), filename)
    else:
        return file_content




@app.route("/qidian/<rank>")
def qidian(rank):
    if rank == "yuepiao":
        rank_name = "月票"
        rank_num = "1"
    elif rank == "changxiao":
        rank_name = "畅销"
        rank_num = "2"
    elif rank == "zhisu":
        rank_name = "阅读指数"
        rank_num = "3"
    elif rank == "tuijina":
        rank_name = "推荐"
        rank_num = "4"
    elif rank == "shoucang":
        rank_name = "收藏"
        rank_num = "5"
    elif rank == "new":
        rank_name = "签约作者新书"
        rank_num = "6"
    elif rank == "new_2":
        rank_name = "公众作家新书"
        rank_num = "7"
    else:
        rank = "yuepiao_vip"
        rank_name = "月票_vip"
        rank_num = "8"

    filename = "qidian_" + rank + "_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("起点中文网_" + rank_name + "榜")
        request = get_html("https://www.qidian.com/rank/", "https://www.qidian.com/rank/", "html")
        articles_title_1 = request.xpath('/html/body/div[1]/div[6]/div[2]/div[2]/div/div[' + rank_num + ']/div/ul/li/div/div[1]/h2/a/text()')
        articles_title_2 = request.xpath('/html/body/div[1]/div[6]/div[2]/div[2]/div/div[' + rank_num + ']/div/ul/li/div[2]/a/h2/text()')
        articles_url_1 = request.xpath('/html/body/div[1]/div[6]/div[2]/div[2]/div/div[' + rank_num + ']/div/ul/li/div/div[1]/h2/a/@href')
        articles_url_2 = request.xpath('/html/body/div[1]/div[6]/div[2]/div[2]/div/div[' + rank_num + ']/div/ul/li/div[2]/a/@href')
        articles_hot_1 = request.xpath('/html/body/div[1]/div[6]/div[2]/div[2]/div/div[' + rank_num + ']/div/ul/li/div/div[1]/p[1]/em/text()')
        articles_hot_2 = request.xpath('/html/body/div[1]/div[6]/div[2]/div[2]/div/div[' + rank_num + ']/div/ul/li/div[2]/i/text()')
        articles_title = articles_title_1 + articles_title_2
        articles_url = articles_url_1 + articles_url_2
        articles_hot = articles_hot_1 + articles_hot_2
        if len(articles_hot) != 10:
            articles_hot = [""] * 10
        datas = [articles_title, articles_url, articles_hot]
        return end_json_data(json_data, headle_html_data_list(datas), filename)
    else:
        return file_content





@app.route("/zongheng/<rank>")
def zongheng(rank):
    if rank == "yuepiao":
        rank_name = "月票"
        rank_url = "https://www.zongheng.com/rank?nav=monthly-ticket&rankType=1"
        现在 = datetime.datetime.now()
        rank_on = now.strftime("%Y") + str(now.month)
        data = {"cateFineId": 0,"cateType": 0,"pageNum": 1,"pageSize": 20,"period": 0,"rankNo": rank_on,"rankType": 1}
    elif rank == "24h":
        rank_name = "24h畅销"
        rank_url = "https://www.zongheng.com/rank?nav=one-day&rankType=3"
        data = {"cateFineId": 0,"cateType": 0,"pageNum": 1,"pageSize": 20,"period": 0,"rankNo": "","rankType": 3}
    elif rank == "new":
        rank_name = "新书"
        rank_url = "https://www.zongheng.com/rank?nav=new-book&rankType=4"
        data = {"cateFineId": 0,"cateType": 0,"pageNum": 1,"pageSize": 20,"period": 0,"rankNo": "","rankType": 4}
    elif rank == "tuijian":
        rank_name = "推荐"
        rank_url = "https://www.zongheng.com/rank?nav=recommend&rankType=6"
        data = {"cateFineId": 0,"cateType": 0,"pageNum": 1,"pageSize": 20,"period": 0,"rankNo": "","rankType": 6}
    elif rank == "new_dingyue":
        rank_name = "新书订阅"
        rank_url = "https://www.zongheng.com/rank?nav=new-book-subscribe&rankType=9"
        data = {"cateFineId": 0,"cateType": 0,"pageNum": 1,"pageSize": 20,"period": 0,"rankNo": "","rankType": 9}
    else:
        rank = "dianji"
        rank_name = "点击"
        rank_url = "https://www.zongheng.com/rank?nav=click&rankType=5"
        data = {"cateFineId": 0,"cateType": 0,"pageNum": 1,"pageSize": 20,"period": 0,"rankNo": "","rankType": 5}

    filename = "zongheng_" + rank + "_data_*.data"
    file_content = get_file_data(filename)
    if file_content is None:
        json_data = init_json_data("纵横中文网_" + rank_name + "榜")
        request = post_html("https://www.zongheng.com/api/rank/details", rank_url, data)
        data_list = []
        for key in request["result"]["resultList"]:
            data_dict = {"index": key["orderNo"],
                         "title": key["bookName"],
                         "url": "https://www.zongheng.com/detail/" + str(key["bookId"]),
                         "hot": ""}
            data_list.append(data_dict)
        return end_json_data(json_data, data_list, filename)
    else:
        return file_content



if __name__ == "__main__":
    app.run()




