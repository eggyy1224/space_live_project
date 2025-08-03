import serial
import serial.tools.list_ports
import threading

class PhysicalLightControlService:
    """
    控制實體燈光亮度，長連線到 Pico，直接寫入 serial port。
    """
    _instance_lock = threading.Lock()
    _serial_instance = None
    _serial_port = None
    _baudrate = 115200

    def __init__(self):
        # 初始化時自動偵測 Pico 並建立 serial 連線
        if PhysicalLightControlService._serial_instance is None:
            port = self._find_pico()
            if not port:
                raise RuntimeError("找不到 Pico 裝置，請檢查連線！")
            PhysicalLightControlService._serial_port = port
            PhysicalLightControlService._serial_instance = serial.Serial(port, self._baudrate, timeout=1)

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
                        print("找不到 Pico，無法重連 serial port")
                        return False
                    PhysicalLightControlService._serial_port = port
                    PhysicalLightControlService._serial_instance = serial.Serial(port, self._baudrate, timeout=1)
                    ser = PhysicalLightControlService._serial_instance
                data = f"{brightness}\n"
                ser.write(data.encode())
                ser.flush()
            return True
        except Exception as e:
            print(f"Serial 控制燈光失敗: {e}")
            return False