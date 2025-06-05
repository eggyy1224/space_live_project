# Camera Control API

本文件說明後端提供的相機控制 API，允許精確設定前端相機角度與管理預設鏡位。

## 端點一覽

| 方法 | 路徑 | 說明 |
|------|------|------|
|`POST`|`/api/control/camera/set-angle`|立即設定相機的 pitch、yaw、roll 角度|
|`POST`|`/api/control/camera/transition`|在指定時間內平滑轉換至目標角度|
|`POST`|`/api/control/camera/save-preset`|儲存或更新一組自定義相機預設|
|`POST`|`/api/control/camera/load-preset`|載入先前儲存的預設並套用到前端|
|`POST`|`/api/control/camera/set-frontend-preset`|命令前端切換到指定的相機預設|

所有角度以 **度** 為單位。`transition` 與 `load-preset` 端點可透過 `duration` 參數調整過渡時間。

## 可用的前端相機預設

以下是前端 `resources.ts` 中定義的可用相機預設名稱列表，可供 `/api/control/camera/set-frontend-preset` 端點使用：

- `overview`
- `head_close_up`
- `dance_circle_view`
- `side_view`
- `low_angle_head`
- `center_orbit_high_1`
- `center_orbit_high_2`
- `center_orbit_low_1`
- `center_orbit_low_2`
- `top_down_center`
- `dramatic_angle_1`
- `dramatic_angle_2`
- `behind_head_looking_out`
- `fly_by_left`
- `fly_by_right`
- `frontal_dynamic_low`
- `frontal_dynamic_high`
- `orbit_head_1`
- `orbit_head_2`
- `full_shot_dancers`

### 範例請求

```bash
curl -X POST \
  http://localhost:8000/api/control/camera/set-angle \
  -H 'Content-Type: application/json' \
  -d '{"pitch": 0, "yaw": 45, "roll": 0}'
```

命令前端切換至名為 `head_close_up` 的鏡位，過渡時間 2.5 秒：

```bash
curl -X POST \
  http://localhost:8000/api/control/camera/set-frontend-preset \
  -H 'Content-Type: application/json' \
  -d '{"name": "head_close_up", "duration": 2.5}'
```
