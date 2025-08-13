import serial
import serial.tools.list_ports
import threading
import atexit
import logging

logger = logging.getLogger(__name__)

class PhysicalLightControlService:
    """
    控制實體燈光亮度，長連線到 Pico，直接寫入 serial port。
    
    新協定：
    - 共有 4 組燈通道，使用兩段式參數："<channel> <value>\n"
      - channel: 0,1,2,3
      - value: channel 0 僅接受 0/1（關/開）；channel 1-3 接受 0~65535
    
    兼容 API：
    - set_brightness(value) 保持既有 HTTP 參數不變，但會同步將 value 套用到通道 1,2,3（語音閃爍用途）
    """
    _instance_lock = threading.Lock()
    _serial_instance = None
    _serial_port = None
    _baudrate = 115200
    _cleanup_registered = False

    def __init__(self):
        # 延後連線：初始化不做任何序列埠掃描，避免阻塞 API 啟動或狀態查詢
        pass
        
        # 註冊程式結束時的清理函數
        if not PhysicalLightControlService._cleanup_registered:
            atexit.register(PhysicalLightControlService.cleanup_all)
            PhysicalLightControlService._cleanup_registered = True

    def _find_pico(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if port.vid == 0x2E8A:
                return port.device
        # Try common ports
        import glob
        for pattern in ['/dev/ttyACM*', '/dev/tty.usbmodem*', '/dev/cu.usbmodem*']:
            found = glob.glob(pattern)
            if found:
                return found[0]
        return None

    def is_connected(self) -> bool:
        try:
            ser = PhysicalLightControlService._serial_instance
            return ser is not None and ser.is_open
        except Exception:
            return False

    def set_brightness(self, brightness: int) -> bool:
        """維持舊 API（只有亮度參數），內部同步套用到通道 1、2、3（新協定）。"""
        if not (0 <= brightness <= 65535):
            raise ValueError("亮度必須在 0~65535 之間")
        try:
            success = True
            for channel in (1, 2, 3):
                ok = self.set_channel_brightness(channel, brightness)
                success = success and ok
            return success
        except Exception as e:
            logger.error(f"Serial 控制燈光失敗: {e}")
            self._close_serial_connection()
            return False

    def set_channel_brightness(self, channel: int, brightness: int) -> bool:
        """設定單一路燈的亮度。
        channel 0: 僅接受 0 或 1（招牌燈開關）
        channel 1-3: 接受 0~65535
        """
        if channel not in (0, 1, 2, 3):
            raise ValueError("channel 必須為 0~3")
        if channel == 0:
            if brightness not in (0, 1):
                raise ValueError("通道 0 僅接受 0 或 1")
            # 實務對接：多數韌體將 0/65535 視為關/開
            send_value = 65535 if brightness == 1 else 0
        else:
            if not (0 <= brightness <= 65535):
                raise ValueError("亮度必須在 0~65535 之間")
            send_value = brightness

        try:
            with PhysicalLightControlService._instance_lock:
                ser = PhysicalLightControlService._serial_instance
                opened_new = False
                if ser is None or not ser.is_open:
                    # 嘗試重連（非阻塞快速掃描：只看已知 port，找不到就快速返回）
                    port = PhysicalLightControlService._serial_port or self._find_pico()
                    if not port:
                        logger.warning("找不到 Pico，無法重連 serial port")
                        return False
                    PhysicalLightControlService._serial_port = port
                    PhysicalLightControlService._serial_instance = serial.Serial(port, self._baudrate, timeout=1)
                    ser = PhysicalLightControlService._serial_instance
                    logger.info(f"成功重連 serial port: {port}")
                    opened_new = True

                # 若剛開連線，給韌體一點時間初始化
                if opened_new:
                    try:
                        import time
                        time.sleep(1.0)
                    except Exception:
                        pass

                # 依照新版 demo：以逗號分隔並以 \n 結尾
                # 格式："<channel>,<value>\n"
                data = f"{channel},{send_value}\n"
                ser.write(data.encode())
                ser.flush()
                logger.info(f"已送出燈控: '{data.strip()}' 到 {self._serial_port}")
            return True
        except Exception as e:
            logger.error(f"Serial 控制燈光失敗 (channel={channel}, brightness={brightness}): {e}")
            self._close_serial_connection()
            return False

    @classmethod
    def _close_serial_connection(cls):
        """安全地關閉 serial 連線"""
        try:
            with cls._instance_lock:
                if cls._serial_instance is not None:
                    if cls._serial_instance.is_open:
                        cls._serial_instance.close()
                        logger.info(f"已關閉 serial 連線: {cls._serial_port}")
                    cls._serial_instance = None
                    cls._serial_port = None
        except Exception as e:
            logger.error(f"關閉 serial 連線時發生錯誤: {e}")

    @classmethod
    def cleanup_all(cls):
        """清理所有資源，程式結束時自動呼叫"""
        logger.info("清理物理燈控制服務資源...")
        cls._close_serial_connection()

    @classmethod
    def force_reset_connection(cls):
        """強制重置 serial 連線，可用於手動恢復"""
        logger.info("強制重置 serial 連線...")
        cls._close_serial_connection()
        return True