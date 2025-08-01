import subprocess
import os

class PhysicalLightControlService:
    """
    控制實體燈光亮度，呼叫 picoled script。
    """
    def __init__(self):
        # picoled script 路徑
        self.script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../physical_light_control_temp/picoled'))

    def set_brightness(self, brightness: int) -> bool:
        if not (0 <= brightness <= 65535):
            raise ValueError("亮度必須在 0~65535 之間")
        try:
            # 呼叫 picoled script，傳遞亮度參數
            result = subprocess.run([
                'python3', self.script_path, str(brightness)
            ], capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            # 可根據需要記錄錯誤日誌
            print(f"picoled 控制失敗: {e.stderr}")
            return False