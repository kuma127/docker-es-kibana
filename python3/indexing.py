import re
from elasticsearch import Elasticsearch
import datetime
import argparse

columns = "AUTHOR|TITLE|BASENAME|STATUS|ALLOW COMMENTS|CONVERT BREAKS|DATE|CATEGORY|IMAGE"

blog_host = "https://kumappp.hatenablog.com/entry/"

class MovableParser(object):
    def __init__(self, host, port):
        """
        ElasticSearchと接続する
        """
        # 1 ElasticSearchクライアントの初期化
        self.es = Elasticsearch(hosts=["{}:{}".format(host, port)])
        self.document = {}
        self.seq = ""
    
    def read_file(self, filename):
        """
        ファイルを読む

        :param filename: データファイル名
        """
        # 2 ファイル解析
        with open(filename, encoding="utf-8") as f:
            for line in f:
                if line == "--------\n":
                    self.parse()
                    self.seq = ""
                else:
                    self.seq += line
    
    def parse(self):
        """
        MovableTypeをパースする
        """

        # 3 メタ情報の解析
        elements = self.seq.split("-----\n")
        meta = elements[0]
        body = elements[1]

        meta_pattern = re.compile("({0}): (.*)".format(columns), flags=(re.MULTILINE | re.DOTALL))
        for metaline in meta.split("\n")[:-1]:
            matches = re.match(meta_pattern, metaline)
            print(matches)
            if matches.group(1).lower() in self.document:
                self.document[matches.group(1).lower()] = ",{0}".format(matches.group(2))
            else:
                self.document[matches.group(1).lower()] = matches.group(2)
            
        if "category" in self.document:
            self.document["category"] = self.document["category"].split(",")
            print(self.document["category"])
        
        body = re.sub("BODY:", "", body)
        self.document["body"] = body

        # 4 取得データの加工
        print("4 取得データの加工 開始")
        url = blog_host + self.document["basename"]
        self.document["source"] = url
        self.document["date"] = datetime.datetime.strptime(self.document["date"], "%m/%d/%Y %H:%M:%S")
        print("4 取得データの加工 終了")

        # 5 ElasticSearchへのデータ投入
        print("5 ElasticSearchへのデータ投入　開始")
        self.es.index(index="blog", doc_type="blog", body=self.document)
        print(self.document)
        self.document = {}
        print("5 ElasticSearchへのデータ投入　終了")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="es")
    parser.add_argument("--port", type=int, default="9200")
    parser.add_argument("--file", type=str, default="kumappp.hatenablog.com.export.txt")
    args = parser.parse_args()

    parser = MovableParser(host=args.host, port=args.port)
    parser.read_file(args.file)