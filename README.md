###### Osusume_Joyuu_with_Flask

# 傑哥のおすすめ女優

## 後端
使用 Flask

|   檔案                |  用途    |
|-----------------------|---------|
|run_app.py             |程式開始點|
|library/db_ctl.py      |資料庫控制|
|library/routing_user.py| Route   |

## 資料庫
使用 SQLite

若 `data` 資料夾內尚未有 `data.db` 檔案，需先執行 `jsonToDB.py` 以初始化資料庫，後方能執行 `run_app.py`。

**`jsonToDB.py`**：創建 `data.db` 檔案，並將 `data` 資料夾內的 **JSON** 資料插入。
