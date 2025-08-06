import serial
import serial.tools.list_ports
import threading
import atexit
import logging

logger = logging.getLogger(__name__)

class PhysicalLightControlService:
    """
    控制實體燈光亮度，長連線到 Pico，直接寫入 serial port。
    """
    _instance_lock = threading.Lock()
    _serial_instance = None
    _serial_port = None
    _baudrate = 115200
    _cleanup_registered = False

    def __init__(self):
        # 初始化時自動偵測 Pico 並建立 serial 連線
        if PhysicalLightControlService._serial_instance is None:
            port = self._find_pico()
            if not port:
                raise RuntimeError("找不到 Pico 裝置，請檢查連線！")
            PhysicalLightControlService._serial_port = port
            PhysicalLightControlService._serial_instance = serial.Serial(port, self._baudrate, timeout=1)
            logger.info(f"成功建立 serial 連線: {port}")
        
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
        for pattern in ['/dev/ttyACM*', '/dev/tty.usbmodem*', '/dev/ｓcu.usbmodem*']:
            found = glob.glob(pattern)
            if found:
                return found[0]
        return None

    def set_brightness(self, brightness: int) -> bool:
        if not (0 <= brightness <= 65535):
            raise ValueError("亮度必須在 0~65535 之間")
        try:
            with PhysicalLightControlService._instance_lock:
                ser = PhysicalLightControlService._serial_instance
                if ser is None or not ser.is_open:
                    # 嘗試重連
                    port = self._find_pico()
                    if not port:
                        logger.warning("找不到 Pico，無法重連 serial port")
                        return False
                    PhysicalLightControlService._serial_port = port
                    PhysicalLightControlService._serial_instance = serial.Serial(port, self._baudrate, timeout=1)
                    ser = PhysicalLightControlService._serial_instance
                    logger.info(f"成功重連 serial port: {port}")
                data = f"{brightness}\n"
                ser.write(data.encode())
                ser.flush()
            return True
        except Exception as e:
            logger.error(f"Serial 控制燈光失敗: {e}")
            # 發生錯誤時主動關閉連線，避免 port 被鎖死
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