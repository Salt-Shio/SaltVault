"""
VFS API 自訂響應模組 (VFS API Responses)
職責：
1. 定義 MonitoredFileResponse，繼承自原生 FileResponse
2. 覆寫 ASGI __call__ 生命週期，在控制台輸出下載連線狀態日誌
3. 與 Redis 徹底解耦，不執行任何 Redis 操作
"""
import logging

from fastapi.responses import FileResponse

logger = logging.getLogger("vfs_download")


class MonitoredFileResponse(FileResponse):
    """
    自訂 FileResponse，用於偵測下載連線的連上與斷開/關閉。
    不干涉 Redis 狀態，所有快取清理完全依靠 TTL 自動過期完成。
    """
    async def __call__(self, scope, receive, send):
        logger.info("[Download] 連線建立，開始檔案發送。")
        try:
            await super().__call__(scope, receive, send)
        except Exception as e:
            logger.warning(f"[Download] 檔案發送中途連線中斷。詳情: {str(e)}")
            raise
        finally:
            logger.info("[Download] 連線結束/已關閉。")
