"""
VFS API 自訂響應模組 (VFS API Responses)
職責：
1. 定義 MonitoredFileResponse，繼承自原生 FileResponse
2. 覆寫 ASGI __call__ 生命週期，在控制台輸出下載連線狀態日誌
3. 檔案傳送期間定期為下載憑證續命 (Heartbeat)，讓憑證存活時間與連線是否還「活著」掛鉤，
   而不是被單一固定 TTL 天花板卡死；連線一旦結束 (傳完或斷線)，Heartbeat 停止，
   憑證改回單純依 TTL 自動過期，安全意圖 (未使用/已斷線的憑證要盡快失效) 不變
"""
import asyncio
import logging

from fastapi.responses import FileResponse

logger = logging.getLogger("vfs_download")


class MonitoredFileResponse(FileResponse):
    """
    自訂 FileResponse，用於偵測下載連線的連上與斷開/關閉，
    並在檔案持續傳送期間透過 Heartbeat 為下載憑證續命。
    """

    def __init__(self, *args, redis_client=None, ticket_key: str | None = None,
                 ticket_ttl: int | None = None, heartbeat_interval: int | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._redis_client = redis_client
        self._ticket_key = ticket_key
        self._ticket_ttl = ticket_ttl
        self._heartbeat_interval = heartbeat_interval

    async def _heartbeat(self):
        """每隔 heartbeat_interval 秒，把憑證 TTL 刷新回滿額，只要這個迴圈還在跑就代表連線仍在傳送資料"""
        while True:
            await asyncio.sleep(self._heartbeat_interval)
            await self._redis_client.expire(self._ticket_key, self._ticket_ttl)

    async def __call__(self, scope, receive, send):
        logger.info("[Download] 連線建立，開始檔案發送。")

        heartbeat_task = None
        if self._redis_client and self._ticket_key and self._heartbeat_interval:
            heartbeat_task = asyncio.create_task(self._heartbeat())

        try:
            await super().__call__(scope, receive, send)
        except Exception as e:
            logger.warning(f"[Download] 檔案發送中途連線中斷。詳情: {str(e)}")
            raise
        finally:
            if heartbeat_task:
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass
            logger.info("[Download] 連線結束/已關閉。")
