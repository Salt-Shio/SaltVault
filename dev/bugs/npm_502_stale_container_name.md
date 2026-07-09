# NPM 502 Bad Gateway — Proxy Host 仍指向改名前的舊 Container 名稱

## 1. 錯誤現象與症狀
專案從 `file-explorer` 改名為 `SaltVault` 後（`docker-compose.yml` 的 5 個 `container_name` 全部從 `file-explorer-*` 改成 `salt-vault-*`），重新 `docker compose --profile deploy down` + `up --build -d`，5 個 container 都正常 `Up`，但瀏覽器打正式網域出現 **502 Bad Gateway**。

診斷方式：NPM 的 Proxy Host 各自有獨立的 access/error log，存在 container 內的 `/data/logs/`（對應主機上的 `./npm-data/logs/`）：
```bash
docker exec -it salt-vault-npm sh -c "tail -n 50 /data/logs/proxy-host-<編號>_error.log"
```
error log 會直接寫出 NPM 嘗試連線但連不到的 upstream host。

## 2. 根本原因 (Root Cause)
NPM 後台「Edit Proxy Host」畫面裡的 **Forward Hostname / IP 是使用者手動填寫的字串**，只在建立/編輯當下寫死存進 NPM 自己的資料庫（`./npm-data`），**不會**因為 `docker-compose.yml` 改了 `container_name` 就自動同步更新。

這次改名前，Forward Hostname/IP 填的是 `file-explorer-web`；改名後實際 container 叫 `salt-vault-web`，NPM 在 docker 內部網路用舊名稱做 DNS 查詢找不到對應 container，於是回應 502 Bad Gateway。

（Port 本身沒填錯：`web` container 內的 nginx 監聽 `80`，負責回傳前端靜態檔案 + 轉發 `/api/*` 給 `server:8000`；若誤填成 `8000` 會直接跳過前端靜態檔案這一層，等於繞過 `web`，也是常見的誤設，但這次不是這個原因。）

## 3. 解決方案 (Solution)
進 NPM 後台（`http://<主機 IP 或 Tailscale IP>:81`）→ Hosts → Proxy Hosts → 編輯對應網域 → 把 **Forward Hostname / IP** 改成新的 container 名稱（本例是 `salt-vault-web`），**Forward Port 維持 `80`** → Save。

**注意事項**：往後只要 `docker-compose.yml` 裡任何 container 的 `container_name` 被改掉（例如專案又改名、或調整服務拆分方式），一定要同步手動去 NPM 後台把對應 Proxy Host 的 Forward Hostname/IP 一起改掉，這一步不會自動連動，也不會有任何錯誤提示，只會在使用者訪問時默默變成 502。
