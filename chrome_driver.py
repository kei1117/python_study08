import os
import datetime
import time


from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class ChromeDriver:
    LOG_FILE_PATH = "logs/log_{datetime}.log"
    log_file_path = LOG_FILE_PATH.format(
        datetime=datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    )

    def __init__(self):
        self.driver = self.set_driver()
        self.success = 0
        self.fail = 0

    def set_driver(self):
        USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
        options = ChromeOptions()

        # 起動オプションの設定
        options.add_argument(f"--user-agent={USER_AGENT}")  # ブラウザの種類を特定するための文字列
        options.add_argument("log-level=3")  # 不要なログを非表示にする
        options.add_argument("--ignore-certificate-errors")  # 不要なログを非表示にする
        options.add_argument("--ignore-ssl-errors")  # 不要なログを非表示にする
        options.add_experimental_option(
            "excludeSwitches", ["enable-logging"]
        )  # 不要なログを非表示にする
        options.add_argument("--incognito")  # シークレットモードの設定を付与
        options.add_argument("--headless")  # ヘッドレスモードの設定を付与

        # ChromeのWebDriverオブジェクトを作成する。
        service = Service(ChromeDriverManager().install())
        return Chrome(service=service, options=options)

    def makedir_for_filepath(self, filepath):
        """
        ファイルを格納するフォルダを作成する
        """
        # exist_ok=Trueとすると、フォルダが存在してもエラーにならない
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    def log(self, txt):
        now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        logStr = "[%s: %s] %s" % ("log", now, txt)
        # ログ出力
        self.makedir_for_filepath(self.log_file_path)
        with open(self.log_file_path, "a", encoding="utf-8_sig") as f:
            f.write(logStr + "\n")
        print(logStr)

    def close_driver(self):
        self.driver.close()
        self.driver.quit()

    def open_url(self, url):
        self.driver.get(url)

    def close_modal(self):
        self.driver.execute_script('document.querySelector(".karte-close").click()')

    def get_element(self, target):
        element = self.driver.find_element(By.CLASS_NAME, target)

        if not element:
            self.log(f"エラー:{target}。エレメントが取得できませんでした。")
            return False

        return element

    def get_text(self, target):
        element = self.driver.find_element(By.CLASS_NAME, target)

        if not element:
            self.log(f"エラー:{target}。エレメントが取得できませんでした。")
            return ""

        return element.text.replace("\n", "")

    def get_data(self, url, page_count):
        driver = self.set_driver()
        driver.get(url)

        print(f"{page_count}ページ目を取得します。")

        result = []
        target_blocks = driver.find_elements(
            by=By.CLASS_NAME, value="cassetteRecruit__content"
        )

        for i, block in enumerate(target_blocks):
            try:

                company = (
                    block.find_element(
                        by=By.CLASS_NAME, value="cassetteRecruit__name"
                    ).text,
                )
                catch_copy = block.find_element(
                    by=By.CLASS_NAME, value="cassetteRecruit__copy"
                ).text

                data = {"ページ": page_count, "会社名": company, "キャッチコピー": catch_copy}

                self.log(f"[成功]{i+1} 件目 (page: {page_count}) : {company}")
                self.success += 1
                result.append(data)

            except Exception as e:
                self.log(f"[失敗]{i+1}  件目 (page: {page_count})")
                self.log(f"エラー:{e}")

                self.fail += 1
        return result
