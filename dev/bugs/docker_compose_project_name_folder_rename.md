# `docker compose down` 空白無反應 — Project Name 跟著資料夾改名跑掉

## 1. 錯誤現象與症狀
專案資料夾從 `~/Project/FileBrowser` 搬到 `~/Project/SaltVault` 後，在 Linux 正式機上執行：
```bash
docker compose --profile deploy down
```
指令**完全沒有任何輸出**（正常應該會印出 `Stopping ...` / `Removing ...`），執行完 `docker ps -a` 一看，原本五個容器（`salt-vault-web`、`salt-vault-server`、`salt-vault-redis`、`salt-vault-tailscale`、`salt-vault-npm`）完全沒被動到，`STATUS` 還是 `Up 6 hours`，好像 `down` 指令根本沒執行過一樣。

診斷關鍵：`docker ps -a` 的 `IMAGE` 欄位顯示的是 `filebrowser-web`、`filebrowser-server`，不是預期的 `salt-vault-*`。

## 2. 根本原因 (Root Cause)
Docker Compose 有兩個容易搞混的「名字」：

- **`container_name`**：本專案已經手動釘死成 `salt-vault-*`，不會因為資料夾改名而變。
- **Project Name（專案名稱）**：`docker-compose.yml` 沒有指定的話，Compose 預設會拿「執行指令當下所在的資料夾名稱」當作 project name，並把這個名字當成 label 貼在容器上（`com.docker.compose.project`），也是 image 自動命名的來源（`<project name>-<service name>`）。

當初在 `~/Project/FileBrowser` 資料夾下第一次 `up` 時，project name 自動變成 `filebrowser`，所以 build 出來的 image 才叫 `filebrowser-web` / `filebrowser-server`，容器身上也貼著 `filebrowser` 這個 project label。

後來資料夾改名為 `SaltVault`，再執行 `docker compose --profile deploy down` 時，Compose 這次讀到的預設 project name變成 `saltvault`，於是它去找「屬於 `saltvault` 這個 project 的容器」——一個都找不到（現有容器貼的是 `filebrowser`），所以判定沒有東西要處理，安靜結束，完全不會報錯，也不會動到正在跑的舊容器。

## 3. 解決方案 (Solution)

**立即解法**（把舊的一批容器停掉）：明確指定舊的 project name 執行 down：
```bash
docker compose -p filebrowser --profile deploy down
```
確認 `docker ps -a` 那五個容器都消失後，再從新資料夾正常重建：
```bash
docker compose --profile deploy up --build -d
```

**根本解法**（避免以後又因為改資料夾名稱/搬家而重演）：在 `docker-compose.yml` 最上方加一行，把 project name 手動釘死，不再依賴資料夾名稱：
```yaml
name: salt-vault
```
加了這行之後，不管專案資料夾未來搬到哪裡、叫什麼名字，Compose 永遠認定 project name 是 `salt-vault`，跟 `container_name` 一樣徹底跟資料夾路徑脫鉤。

**注意事項**：這個問題不會有任何錯誤訊息提示，`down`/`up`/`ps` 都會「看似正常」地跑完，只是完全沒抓到既有容器，非常容易被誤判成「指令沒用」或「服務本身有問題」。往後如果又要動到專案資料夾路徑（改名、搬家、換使用者家目錄），先確認 `docker-compose.yml` 裡有沒有 `name:` 這行、值是否正確，比反覆重跑 down/up 更快定位問題。
