# 必要なモジュールのimport
import pandas as pd
import tweepy
from pytz import timezone
import config
# import datetime


def main():
    """
    メインの実行部分
    ツイートデータの取得からデータの出力まで
    """
    items_cnt = 100
    refav_cnt = 1
    
    client = set_tweet_oauth()
    
    # today = datetime.date.today()
    
    # 調べる言語のリストの用意
    languages = ["JavaScript","Python","TypeScript","Java","C++","Go","Rust","C","Shell","Vue","Dart","CSS","PHP","C#","Clojure","Assembly","Ruby"]
    like_sum = []
    
    # for文を使って、リストに入っている言語ごとにデータを取得していく
    for language in languages:
        print(f'{language}を調査中')
        data = get_tweet(client, language, items_cnt, refav_cnt)
        
        # 取得したデータからデータフレームを作成
        df = make_df(data)
        
        # いいね数の総和を求めてリストに追加
        like_sum.append(df['いいね数'].sum())
        
        # 言語ごとのいいね数を出力する
        print(f'{language}の総いいね数は{df["いいね数"].sum()}')
        
    # 言語名といいね数の情報からデータフレームを作成する
    df = pd.DataFrame({'言語名': languages,
                       'いいね数': like_sum})
                       
    print('\n集計結果の出力')
    #　いいね数の多い順(降順)にデータを並べ変える
    print(df.sort_values(by = 'いいね数', ascending=False).reset_index().drop('index', axis=1))
    
    
def set_tweet_oauth():
# 各種Twitterのキーをセット
    consumer_key = config.CK
    consumer_secret = config.CS
    access_token = config.AT
    access_token_secret = config.ATS
    bearer_token = config.BT
    
    # tweepy.Clientでキーをセット
    client = tweepy.Client(
        bearer_token, consumer_key, consumer_secret, access_token, access_token_secret
    )
    
    return client


def get_tweet(client, search_key, items_cnt, refav_cnt):
    """
    ツイート情報を期間指定で収集
    取得できるのデータは直近1週間以内
    RT数＋いいね数の合計を超えるツイートを取得
    """
    # ツイートデータ取得部分 start_time, end_timeの期間で取得
    response = client.search_recent_tweets(
        query=search_key,
        start_time="2022-01-30T00:00:00Z",
        end_time="2022-02-05T00:00:00Z",
        expansions=["attachments.media_keys", "author_id"],
        tweet_fields=["created_at", "lang", "public_metrics"],
        #media_fields=["preview_image_url"],
        max_results=items_cnt,
    )

    # response.dataでツイート情報、response.includesで追加の情報を取得
    tweets = response.data
    includes = response.includes
    users = includes["users"]

    # ツイートのデータを取り出して、リストにまとめていく部分
    tweet_data = []  # ツイートデータを入れる空のリストを用意
    for user, tweet in zip(users, tweets):
        # いいねとリツイートの合計がrefav_cnt以上の条件
        if (
            tweet.public_metrics["like_count"] + tweet.public_metrics["retweet_count"]
            > refav_cnt
        ):
            # 空のリストtweet_dataにユーザーネーム、スクリーンネーム、RT数、いいね数、日付などを入れる
            tweet_data.append(
                [
                    user["name"],
                    user["username"],
                    tweet.public_metrics["retweet_count"],
                    tweet.public_metrics["like_count"],
                    tweet.public_metrics["quote_count"],
                    tweet.text.replace("\n", ""),
                    tweet.created_at.astimezone(timezone("Asia/Tokyo")).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                ]
            )
    return tweet_data


def make_df(tweet_data):
    """
    ツイートデーターからDataframeを作成する
    """
    # データを入れる空のリストを用意
    list_user_name = []
    list_user_id = []
    list_re_cnt = []
    list_fav_cnt = []
    list_quote_cnt = []
    list_date = []
    list_text = []

    # ツイートデータからユーザー名、ユーザーid、RT数、いいね数、日付け、ツイート本文のそれぞれをデータごとにまとめたリストを作る
    for i in range(len(tweet_data)):
        list_user_name.append(tweet_data[i][0])
        list_user_id.append(tweet_data[i][1])
        list_re_cnt.append(tweet_data[i][2])
        list_fav_cnt.append(tweet_data[i][3])
        list_quote_cnt.append(tweet_data[i][4])
        list_date.append(tweet_data[i][5])
        list_text.append(tweet_data[i][6])

    # 先ほど作ったデータごとにまとめたリストからDataframeの作成
    df = pd.DataFrame(
        {
            "ユーザー名": list_user_name,
            "ユーザーid": list_user_id,
            "RT数": list_re_cnt,
            "いいね数": list_fav_cnt,
            "引用数": list_quote_cnt,
            "日時": list_date,
            "本文": list_text,
        }
    )
    return df

# 実行部分
if __name__ == "__main__":
    main()
