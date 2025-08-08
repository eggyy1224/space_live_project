import asyncio
import logging
from typing import List, Optional

import aiohttp

from config.video_resources import ALL_VIDEOS


logger = logging.getLogger(__name__)


class VideoRotationService:
    """集中管理展場螢幕（screen1-3）的影片輪播與隱藏顯示。

    - 單例服務，避免多處同時建立重複任務
    - 提供 hide_all_monitors / start_rotation / stop_rotation 三個操作
    - 使用後端註冊的 ALL_VIDEOS 清單，確保檔名可被驗證
    """

    def __init__(self) -> None:
        self._monitor_ids: List[str] = ["screen1", "screen2", "screen3"]
        self._rotation_task: Optional[asyncio.Task] = None
        self._rotation_interval_seconds: float = 45.0
        self._inhibit: bool = False
        self._enforce_hidden_task: Optional[asyncio.Task] = None

    async def hide_all_monitors(self) -> None:
        """關閉所有螢幕顯示（停止播放並隱藏）。"""
        try:
            async with aiohttp.ClientSession() as session:
                tasks = []
                for monitor_id in self._monitor_ids:
                    url = f"http://localhost:8000/api/monitors/{monitor_id}"
                    payload = {"visible": False}
                    tasks.append(session.put(url, json=payload))
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                for i, resp in enumerate(responses):
                    if isinstance(resp, Exception):
                        logger.warning("隱藏螢幕失敗: %s - %s", self._monitor_ids[i], resp)
                    else:
                        if resp.status != 200:
                            text = await resp.text()
                            logger.warning("隱藏螢幕失敗: %s - %s %s", self._monitor_ids[i], resp.status, text)
                logger.info("所有螢幕已關閉 (visible=False, playing=False)")
        except Exception as e:
            logger.error("批次隱藏螢幕時發生錯誤: %s", e)

    async def start_rotation(self) -> None:
        """啟動背景影片輪播（三個螢幕不同影片並定時切換）。"""
        await self.stop_rotation()
        self._rotation_task = asyncio.create_task(self._rotation_loop())
        logger.info("已啟動螢幕影片輪播任務")

    async def stop_rotation(self) -> None:
        """停止背景螢幕輪播任務。"""
        if self._rotation_task and not self._rotation_task.done():
            self._rotation_task.cancel()
            try:
                await self._rotation_task
            except asyncio.CancelledError:
                pass
        self._rotation_task = None
        logger.info("螢幕輪播任務已停止")

    async def enable_inhibit(self) -> None:
        """啟用抑制模式：持續確保所有螢幕保持隱藏。"""
        self._inhibit = True
        await self.hide_all_monitors()
        if self._enforce_hidden_task and not self._enforce_hidden_task.done():
            self._enforce_hidden_task.cancel()
            try:
                await self._enforce_hidden_task
            except asyncio.CancelledError:
                pass
        self._enforce_hidden_task = asyncio.create_task(self._enforce_hidden_loop())
        logger.info("已啟用螢幕抑制模式（持續確保隱藏）")

    async def disable_inhibit(self) -> None:
        """停用抑制模式：允許螢幕顯示與輪播。"""
        self._inhibit = False
        if self._enforce_hidden_task and not self._enforce_hidden_task.done():
            self._enforce_hidden_task.cancel()
            try:
                await self._enforce_hidden_task
            except asyncio.CancelledError:
                pass
        self._enforce_hidden_task = None
        logger.info("已停用螢幕抑制模式")

    async def _enforce_hidden_loop(self) -> None:
        try:
            while self._inhibit:
                await self.hide_all_monitors()
                await asyncio.sleep(10.0)
        except asyncio.CancelledError:
            pass

    async def _rotation_loop(self) -> None:
        import random

        try:
            if not ALL_VIDEOS:
                logger.warning("沒有可用影片，輪播任務結束")
                return

            playlist = list(ALL_VIDEOS)
            random.shuffle(playlist)
            base_index = 0

            while True:
                async with aiohttp.ClientSession() as session:
                    tasks = []
                    for offset, monitor_id in enumerate(self._monitor_ids):
                        video = playlist[(base_index + offset) % len(playlist)]
                        url = f"http://localhost:8000/api/monitors/{monitor_id}"
                        payload = {"content": video, "visible": True}
                        tasks.append(session.put(url, json=payload))
                    responses = await asyncio.gather(*tasks, return_exceptions=True)
                    for i, resp in enumerate(responses):
                        if isinstance(resp, Exception):
                            logger.warning("設定螢幕內容失敗: %s - %s", self._monitor_ids[i], resp)
                        else:
                            if resp.status != 200:
                                text = await resp.text()
                                logger.warning("設定螢幕內容失敗: %s - %s %s", self._monitor_ids[i], resp.status, text)

                base_index = (base_index + len(self._monitor_ids)) % len(playlist)
                await asyncio.sleep(self._rotation_interval_seconds)
        except asyncio.CancelledError:
            logger.info("螢幕輪播任務被取消")
        except Exception as e:
            logger.error("螢幕輪播任務錯誤: %s", e)


video_rotation_service = VideoRotationService()


