import time
import datetime
import math
import eel
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

from chrome_driver import ChromeDriver

EXP_CSV_PATH = "results/exp_list_{search_keyword}_{datetime}.csv"
PAGE_URL = "https://tenshoku.mynavi.jp/list/kw{search_keyword}/pg{page_count}/?jobsearchType=14&searchType=18"


@eel.expose
def scrape_mynavi(search_keyword):

    # driverを起動
    chrome_driver = ChromeDriver()
    chrome_driver.open_url(PAGE_URL.format(search_keyword=search_keyword, page_count=1))

    time.sleep(5)

    chrome_driver.log(f"処理開始")
    chrome_driver.log("検索キーワード:{}".format(search_keyword))

    # ポップアップを閉じる
    chrome_driver.close_modal()
    time.sleep(5)
    chrome_driver.close_modal()

    # 最大件数取得
    max_data = int(chrome_driver.get_text("result__num").replace("件", ""))

    # 最大ページ数を計算
    max_page = math.ceil(max_data / 50)
    print(f"全{max_data}件,{max_page}ページあります")

    # jsへ情報を渡す
    eel.to_js_process_doing(max_page, max_data)  # type: ignore

    futures = []
    executor = ThreadPoolExecutor(max_workers=max_page)
    page_count = 1

    while page_count <= max_page:

        url = PAGE_URL.format(search_keyword=search_keyword, page_count=page_count)
        future = executor.submit(chrome_driver.get_data, url, page_count)
        futures.append(future)
        page_count += 1

    wait(futures, return_when=ALL_COMPLETED)
    print("全ページスクレイピング処理完了")
    executor.shutdown()
    chrome_driver.log("処理終了")

    # # futureオブジェクトから取得結果を抽出
    data = []
    for future in futures:
        data.extend(future.result())

    # # DataFrame作成
    now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    df = pd.DataFrame(data)
    chrome_driver.makedir_for_filepath(EXP_CSV_PATH)
    df.to_csv(
        EXP_CSV_PATH.format(search_keyword=search_keyword, datetime=now),
        header=False,
        index=False,
        encoding="utf_8_sig",
    )

    msg = f"csv書き込み処理完了 成功件数: {chrome_driver.success} 件 / 失敗件数: {chrome_driver.fail} 件"
    chrome_driver.log(msg)

    # jsへ情報を渡す
    eel.to_js_process_end(msg)  # type: ignore


def start_web():
    # ウエブコンテンツを持つフォルダー
    eel.init("web")

    # 最初に表示するhtmlページ
    eel.start("index.html", size=(750, 600))


if __name__ == "__main__":
    start_web()
