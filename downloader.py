from thirdpart.prettytable import PrettyTable
import sys
import time
import json
import urllib.request
from thirdpart.termcolor import cprint
import os


def wget(url):
    header = {
        'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    request = urllib.request.Request(url, headers=header)
    reponse = urllib.request.urlopen(request).read()
    return reponse


class Vulhub_downloader(object):

    def __init__(self):
        self.origin = "https://raw.githubusercontent.com/vulhub/vulhub-org/master/src/environments.json"
        self.api = "https://api.github.com/repos/vulhub/vulhub/contents/"
        self.directory = ""     # 初始化目录

        self.originText = json.loads(wget(self.origin).decode("utf8"))

    def parse_github(self, path):
        url = self.api + path
        apiText = json.loads(wget(url).decode("utf8"))
        return apiText

    def download(self, directory, data):
        for item in data:
            name = item.get("name")
            app = item.get("app")
            cve = item.get("cve")
            path = item.get("path")
            api = self.parse_github(path)
            download_directory = os.path.join(directory, path)
            total = len(api)
            index = 0
            for temp in api:
                name = temp.get("name")
                download_url = temp.get("download_url")

                type = temp.get("type")
                if type == "file":
                    print("download:{}".format(name))
                    content = wget(download_url)
                    if not os.path.exists(download_directory):
                        os.makedirs(download_directory)
                    with open(os.path.join(download_directory, name), 'wb') as f:
                        f.write(content)

                index += 1
            print("下载成功:{}".format(download_directory))

    def search(self, keywords):
        '''
        支持关键词搜索(可搜索app、name、cve)，可使用g/进行正则搜索，返回搜索到的数据
        :param keywords:
        :return:
        '''
        result = []
        for item in self.originText:
            name = item.get("name")
            app = item.get("app")
            cve = item.get("cve")
            if cve is None:
                cve = ""
            path = item.get("path")
            keylower = keywords.lower()
            if keylower in name.lower() or keylower in app.lower() or keylower in cve.lower():
                result.append(item)
        return result


if __name__ == '__main__':
    down = Vulhub_downloader()
    print("logo")
    print("已加载漏洞环境:{}".format(len(down.originText)))
    print("请输入关键词搜索(可搜索app、name、cve)")
    k = input("> ")
    data = down.search(k)
    print("已搜索到{}个环境".format(len(data)))
    if len(data) == 0:
        exit()

    x = PrettyTable(["id", "name", "app", "cve"])
    x.align["name"] = "l"  # 以name字段左对齐
    x.padding_width = 1  # 填充宽度
    index = 1
    for item in data:
        x.add_row([index, item["name"], item["app"], item["cve"]])
        index += 1
    print(x)
    print("输入欲下载的id号（多个可用,分割）")
    id = input("> ")
    ids = id.split(",")
    downdata = []
    for item in ids:
        item_id = int(item)
        downdata.append(data[item_id-1])
    # 下载目录:（有默认目录）
    directory = os.path.join(os.getcwd(), "vulhub")
    print("下载目录:(默认:{})".format(directory))
    directory = input("> ")
    if directory == "":
        directory = os.path.join(os.getcwd(), "vulhub")
    # 进度条下载
    down.download(directory, downdata)
    # 下载完成[保存目录 绿色] /下载失败[原因 红色]
