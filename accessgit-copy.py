# 必要なライブラリのimport
import json
import os

import pandas as pd
import requests
from dotenv import load_dotenv


def main():
    """
    メインの実行部分
    """
    # Github APIを使って言語とスター数のデータフレームの作成
    df = get_stars_repos()
    # 言語でグループ化して、スター数の和を求め、スター数の多さで並べ替え
    df = df.groupby("language").sum().sort_values(by="stars", ascending=False)
    # 並べ替えたデータフレームを出力
    print(df)


def get_api_repos(endpoint):
    """
    エンドポイントにGETリクエストを送って得られたデータから
    言語ごとのスター数をまとめたデータフレームを作る
    """

    # エンドポイントにGETリクエストを送ってデータを取得
    r = requests.get(endpoint)
    # ステータスコードが200じゃない（アクセスできない）場合の
    if r.status_code != 200:
        print("Failed to access API")
        return
    # json文字列をjson.loads()でPythonで扱える辞書形式に変換する
    repos_dict = json.loads(r.content)
    # 辞書からアイテムを取り出す
    # リポジトリのデータが入った100個の辞書を要素に持つリストを取り出す
    repos_list = repos_dict["items"]
    # language(言語)とstargazers_count(スター数)のリストを作成する
    languages = []
    stars = []

    for repo_dict in repos_list:
        # 言語がnullの場合は"None"とする
        if repo_dict["language"] is None:
            languages.append("None")
        else:
            languages.append(repo_dict["language"])
        stars.append(repo_dict["stargazers_count"])

    # languagesとstarsのリストからデータフレームの作成
    df = pd.DataFrame({"language": languages, "stars": stars})
    return df


def get_stars_repos():
    """
    アクセストークンを取得して、エンドポイントを指定して、
    get_api_repos関数を使ってスター数が多いリポジトリから言語とスター数の
    スター数が多い順のデータフレームを作成
    """
    # リポジトリーを検索するエンドポイントを指定する
    repo_stars_endpoint = "https://api.github.com/search/repositories?q=stars:>0&sort=stars&order=desc&per_page=100"
    # エンドポイントを引数にget_api_repos関数でスターが多いリポジトリ数のデータフレームを取得
    df_repos = get_api_repos(repo_stars_endpoint)
    return df_repos


if __name__ == "__main__":
    main()
