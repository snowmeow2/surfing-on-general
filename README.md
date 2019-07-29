# general-related
## 目的
蒐集綜合版的發言，以便後續進行Data mining與NLP的處理。

**請勿大量向伺服器發送請求。過快的爬取會被拒絕訪問。**

## 說明
執行`Komica_crawler.py`來爬取綜合版最近的討論串，若全數爬取約花費4.5-5小時。

爬蟲會由檔案區取得爬取的範圍（預設為只爬取第0頁），請自行依需求調整。

爬取結果包括內容，文章編號、ID、時間等metadata，儲存於`Full_thread.json`中。
以下文字內容不收錄其中：
+ 換行符號等字元
+ 諸如>>11451419等回應
+ 此外，也不會爬取圖片
