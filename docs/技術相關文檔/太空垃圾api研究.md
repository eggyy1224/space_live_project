# 即時衛星與太空垃圾資料來源與 API 深度調查報告

為了在互動式藝術網頁中整合即時**太空軌道資料**，需要可靠的資料來源與 API。以下整理了可提供「1) 即時衛星軌道與位置」以及「2) 太空垃圾位置、密度資訊與碰撞預警」的主要來源。每個來源列出其使用條件、資料更新頻率與格式、前端(WebGL)整合性，以及推薦用途。此外，最後也將說明適合此類創作應用的整合方式與框架建議。

## 即時衛星軌道與位置資料 API

即時衛星位置資料通常以軌道兩行元素（Two-Line Element, **TLE**）或直接計算出的座標提供。以下是幾個常用的衛星資料來源與 API：

- **Space-Track API（美國太空監視網資料）** – 美國官方的軌道數據資料庫。提供所有公開衛星（包括 Starlink、ISS 等）的軌道要素資料。使用條件：需要**免費註冊帳號**並登入使用，其API有頻率與流量限制。資料以**TLE**為主，亦可選擇 JSON 格式輸出。TLE數據由美國太空軍持續更新（通常每日多次）確保相對即時。由於需要帳號與驗證，通常需要在後端服務中調用API，再提供給前端使用。整合難度較高，但提供**最全面且科學精確**的軌道數據，適合需要高準確性或完整星群資料的應用。
    
    [discourse.threejs.org](https://discourse.threejs.org/t/side-project-a-3d-satellite-tracker/48002#:~:text=I%20have%20used%20javascript%20for,js)
    
    [space-track.org](https://www.space-track.org/documentation#:~:text=To%20prevent%20excess%20bandwidth%20costs%2C,emails%20to%20satellite%20owners%2Foperators)
    
- **CelesTrak 衛星數據（Kelso 博士提供）** – CelesTrak整理了Space-Track的公開數據並免費提供多種介面。無需註冊，**開放使用**。可透過簡單的 HTTP GET 請求取得資料，格式支援**TLE、3LE、XML、KVN、JSON**等（預設為TLE）。例如：可用 `GROUP=STARLINK` 參數取得整批Starlink衛星的TLE，或 `CATNR=25544` 取得國際太空站(ISS)的TLE。資料更新頻率與Space-Track同步（通常幾小時內更新）。CelesTrak提供的分類相當豐富，包括**太空站、Starlink、OneWeb**等星座分類，以及特定**碎片事件**等。由於提供JSON等格式，非常適合直接在前端透過AJAX/Fetch取得並結合Three.js使用。**推薦用途**：即時可視化、大量衛星軌道展示（如Starlink全星座）、教育與藝術展示等，方便取得且整合容易。
    
    celestrak.org
    
    celestrak.org
    
    celestrak.org
    
    celestrak.org
    
- **N2YO 衛星追蹤 API** – N2YO.com 提供**免費**的REST API（需註冊取得API Key），每小時限制約1000次請求。它可以直接返回衛星的位置及相關資訊。主要端點包含：取得特定衛星的**TLE**資料、未來軌跡位置列表、可見通過預報等。資料格式為**JSON**（例如ISS位置會包含經緯度、高度、時間戳等）。N2YO的API非常簡單易用、適合在前端直接呼叫，每次請求計算並返回衛星即時位置，不需要自行實現軌道計算。整合時只需注意將API Key保密。**推薦用途**：需要迅速上手的即時衛星位置查詢（例如顯示**單一或少量衛星**的即時位置軌跡），或在地圖/球體上呈現衛星當前所在位置。也可用於抓取特定類別衛星清單（N2YO也涵蓋常見衛星與部分太空垃圾）。
    
    [n2yo.com](https://www.n2yo.com/api/#:~:text=The%20REST%20API%20v1%20is,will%20be%20limited%20or%20blocked)
    
    [n2yo.com](https://www.n2yo.com/api/#:~:text=)
    
    [n2yo.com](https://www.n2yo.com/api/#:~:text=)
    
    [heavy.ai](https://www.heavy.ai/blog/analyzing-real-time-satellite-locations-with-omnisci#:~:text=We%20started%20digging%20into%20various,straightforward%20and%20easy%20to%20query)
    
    [n2yo.com](https://www.n2yo.com/api/#:~:text=)
    
    [heavy.ai](https://www.heavy.ai/blog/analyzing-real-time-satellite-locations-with-omnisci#:~:text=satellites%2C%20and%20space%20debris,straightforward%20and%20easy%20to%20query)
    
- **Open Notify ISS 即時位置 API** – 一個專門提供**國際太空站**(ISS)位置的開放API。無需鑰匙，免費使用。輸出格式為JSON，提供ISS當前經度、緯度和時間。官方建議輪詢間隔不小於每5秒一次。這個API只涵蓋ISS，但非常簡單：例如 GET `http://api.open-notify.org/iss-now.json` 即可取得 ISS 即時座標。整合在前端非常容易，可用於在Three.js地球上標示ISS位置或做簡易追蹤。**推薦用途**：只關注ISS的應用（如ISS位置提示、與使用者所在位置互動等），或作為初學者練習即時資料串流的範例。
    
    [freepublicapis.com](https://www.freepublicapis.com/iss-current-location#:~:text=Description)
    
    [freepublicapis.com](https://www.freepublicapis.com/iss-current-location#:~:text=Description)
    
    [freepublicapis.com](https://www.freepublicapis.com/iss-current-location#:~:text=GET)
    
- **SpaceX Starlink 官網資料** – SpaceX並未公開提供Starlink衛星位置的官方API，一般是透過上述Space-Track/CelesTrak取得Starlink的軌道資料。部分第三方網站（如 findstarlink.com 或 satellitemap.space）提供可視化查詢，但資料源仍是TLE。建議直接使用CelesTrak的Starlink分類TLE。
- **Aviation Edge Satellite Tracker API** – 付費商業API，提供衛星即時位置和豐富的背景資訊（例如發射日期、軌道參數）。格式為JSON，需註冊並付費訂閱（有折扣試用期)。特色是可以按公司、國家、年份等篩選衛星，並直接提供軌道位置（經緯度、高度、速度等）以及TLE、地心慣性座標(ECI)等資訊。更新頻率實時連續，適合需要**商業級支持**或特定查詢功能的情境。整合方面，有清晰的文件和支援，開發相對方便。**推薦用途**：如果藝術專案需要非常詳細的衛星資訊或商業服務保障，或想減少自己處理軌道計算，此API可作為方案。但一般而言，自由及非商業專案可優先考慮免費的開放資料來源。
    
    [medium.com](https://medium.com/@AviationEdgeAPI/satellite-tracker-api-track-satellite-data-in-real-time-27e125a0222d#:~:text=Did%20you%20know%20that%20Aviation,Let%E2%80%99s%20talk%20about%20it%20more)
    
    [medium.com](https://medium.com/@AviationEdgeAPI/satellite-tracker-api-track-satellite-data-in-real-time-27e125a0222d#:~:text=is%20perfectly%20possible%20to%20build,Let%20the%20data%20inspire%20you)
    
    [medium.com](https://medium.com/@AviationEdgeAPI/satellite-tracker-api-track-satellite-data-in-real-time-27e125a0222d#:~:text=The%20position%20data%20can%20be,the%20example%20output%20to%20help)
    

下面的表格彙總上述即時衛星資料 API 的比較：

| **資料來源/API** | **使用條件** | **更新頻率與格式** | **Web 整合性** | **推薦用途** |
| --- | --- | --- | --- | --- |
| **Space-Track** | 免費註冊帳號，需登入使用[discourse.threejs.org](https://discourse.threejs.org/t/side-project-a-3d-satellite-tracker/48002#:~:text=I%20have%20used%20javascript%20for,js)；API有查詢頻率限制[space-track.org](https://www.space-track.org/documentation#:~:text=To%20prevent%20excess%20bandwidth%20costs%2C,emails%20to%20satellite%20owners%2Foperators) | 提供 TLE 為主（亦可 JSON）；軌道數據每日持續更新（官方雷達網即時追蹤） | 需後端串接（HTTP Basic 認證）；回傳JSON/TLE需自行解析 | 最權威完整的軌道資料庫，科學準確性高，適合大量衛星/星座或需要歷史數據的應用 |
| **CelesTrak** | 完全開放免費，無需註冊 | TLE、3LE、XML、JSON 等celestrak.org；與Space-Track同步更新（頻率數小時級） | 可直接前端請求 JSON/TLEcelestrak.org；有多種現成分類 | 即時視覺化、教學演示；快速取得特定類別衛星（如Starlink、OneWeb）或全部活動衛星清單 |
| **N2YO API** | 免費（需註冊取得 API Key）；每小時最多1000請求[n2yo.com](https://www.n2yo.com/api/#:~:text=The%20REST%20API%20v1%20is,will%20be%20limited%20or%20blocked) | JSON 格式；即時計算衛星位置及預測軌跡[n2yo.com](https://www.n2yo.com/api/#:~:text=) | 前端可直接Fetch（附帶API Key）；返回經緯度等資訊易於繪製 | 單一或少量衛星的即時位置、過境預報；快速開發原型（免自行推演軌道） |
| **Open Notify ISS** | 免費公開，無需鑰匙 | JSON 格式；約每秒更新一次[freepublicapis.com](https://www.freepublicapis.com/iss-current-location#:~:text=Description)（建議≤0.2Hz 輪詢） | 前端直接請求 JSON；無需解析複雜資料 | ISS 即時位置追蹤；簡易網頁或裝置顯示、互動藝術中的ISS元素 |
| **Aviation Edge** | 付費訂閱（可申請試用）[medium.com](https://medium.com/@AviationEdgeAPI/satellite-tracker-api-track-satellite-data-in-real-time-27e125a0222d#:~:text=is%20perfectly%20possible%20to%20build,Let%20the%20data%20inspire%20you) | JSON 格式；即時位置＋豐富元資料[medium.com](https://medium.com/@AviationEdgeAPI/satellite-tracker-api-track-satellite-data-in-real-time-27e125a0222d#:~:text=Did%20you%20know%20that%20Aviation,Let%E2%80%99s%20talk%20about%20it%20more) | REST API 文件齊全；支持按條件查詢衛星清單 | 商業專案或需完整衛星資訊的應用；減少自行維護數據和演算，即時監測眾多衛星 |

## 太空垃圾位置、密度資訊與碰撞預警資料來源

太空垃圾（軌道碎片）的資料相對複雜。追蹤到的碎片往往也以TLE軌道參數提供，其數量龐大（超過**28,000**個碎片在軌道上被持續追蹤

[esa.int](https://www.esa.int/Space_Safety/Space_Debris/About_space_debris#:~:text=About%20space%20debris%20,about%2028160%20remain%20in%20space)

）。此外，碰撞預警通常由專業機構計算生成。以下是可能的資料來源：

- **Space-Track（碎片 & 碰撞預警）** – 除了衛星，Space-Track也包含火箭殘骸、解體碎片等所有已編號的物體資料（即**SATCAT**目錄）。開放使用條件同前：需要註冊帳號登入。可透過API取得特定物體的TLE資料，或查詢整體統計（如各國在軌碎片數量統計 **Boxscore**）。此外，Space-Track 提供**「Conjunction Data Messages (CDM)」**的預警資料：每天針對潛在碰撞計算多次報告（全目錄每8小時一次，每具體事件每小時更新）。CDM包含兩物體最近接近距離、碰撞概率等資訊。這部分資料也需經API取得，格式為專門的CDM標準（XML/JSON）。整合方面，由於CDM計算複雜，一般需要後端獲取後處理。但有了此資料，可在前端標示**潛在碰撞事件**或高風險碎片區域。推薦用途：科研或進階作品中，需要**精確碰撞風險分析**時使用。例如提示ISS在未來幾天內需閃避碎片的警報等。但由於資料敏感和龐大，開發時須考量API調用頻率及資料篩選。
    
    [**space-track.org**](https://www.space-track.org/documentation#:~:text=To%20prevent%20excess%20bandwidth%20costs%2C,emails%20to%20satellite%20owners%2Foperators)
    
- **CelesTrak（碎片軌道 & SOCRATES報告）** – CelesTrak將碎片也分類整理。例如提供**特定事件**的碎片TLE清單（如 *「COSMOS 2251 碰撞碎片」*、*「中國FENGYUN-1C ASAT碎片」* 等)。這些清單可直接下載TLE（無需驗證）。更新頻率取決於Space-Track對該碎片的追蹤更新，通常每日有更新。對於碎片**總體分布與碰撞預警**，CelesTrak提供名為**SOCRATES** (Satellite Orbital Conjunction Reports) 的服務，每日三次使用所有在軌TLE計算未來7天內的潛在相撞事件，針對每一對接近物體給出最近距離和最大碰撞概率等。SOCRATES結果以網頁表格發布（如「最小距離前10名」），目前沒有直接的API，但開發者可抓取解析其結果。整合建議：可利用CelesTrak的碎片TLE資料在Three.js中可視化**碎片雲分布**，例如將特定事件的碎片以不同顏色點呈現。顯示了將某次碰撞事件的碎片與其他衛星以不同顏色標示的效果。另外，可結合SOCRATES報告，高亮近期有風險接近的碎片（例如以連線或特別標記顯示將發生近距離經過的兩物體）。**推薦用途**：想要在藝術作品中呈現**軌道碎片密度**（如常見碎片雲、特定高度殘渣帶）或提醒觀眾注意**潛在碰撞**事件。CelesTrak資料開放易取得，非常適合即時視覺化，但碰撞數據需自行解析運用。
    
    celestrak.org
    
    celestrak.org
    
    [github.com](https://github.com/dsuarezv/satellite-tracker#:~:text=Active%20objects%20from%20CELESTRAK%20%28http%3A%2F%2Fwww)
    
- **LeoLabs 商業追蹤服務** – LeoLabs是一家私營公司，運營地面雷達網追蹤太空垃圾，提供**高精度**的即時軌道數據和碰撞警報服務。他們的資料比傳統TLE精度高10到100倍。LeoLabs提供的資料需付費訂閱，他們有自己的可視化平台展示低軌道物體分布。對開發者而言，LeoLabs可能提供API或資料介接服務，但價格和取得需聯繫廠商。由於精度更高、更新頻率極高（幾乎實時刷新軌道解算），適合科學準確性要求極高或商業監測需要。如果創作應用追求**極度逼真的即時碎片動態**，且有資源，可考慮LeoLabs。一般情況下，開源的Space-Track/CelesTrak已足夠使用。
    
    [leolabs.space](https://leolabs.space/tracking/#:~:text=Tracking%20,line%20elements%20%28TLEs)
    
    [leolabs.space](https://leolabs.space/tracking/#:~:text=Tracking%20,line%20elements%20%28TLEs)
    
    [platform.leolabs.space](https://platform.leolabs.space/visualization#:~:text=Low%20Earth%20Orbit%20Visualization%20,LeoLabs%20in%20low%20earth%20orbit)
    

> 註：NASA/ESA 等機構也有專門的軌道碎片研究部門（例如NASA軌道碎片辦公室ODPO、ESA Space Debris Office），它們定期發布碎片環境報告和統計，但沒有提供公開的即時查詢API。NASA和ESA通常使用美國Space-Track數據進行分析，同時發展碎片環境模型（如NASA ORDEM、ESA MASTER）供研究用途。這些模型可用於模擬不同軌道高度的碎片密度分布（流量），但模型輸出屬於靜態資料，難以整合到Three.js做動態即時可視化。如果創作重在科普，可引用這些機構發布的統計（例如不同高度的碎片數量分布）作為輔助圖表。
> 

下表彙總太空垃圾與碰撞預警資料來源的比較：

| **資料來源** | **使用與存取** | **提供資料內容** | **格式與更新** | **整合與用途** |
| --- | --- | --- | --- | --- |
| **Space-Track 碎片** | 與Space-Track衛星相同（需註冊帳號） | 全部已追蹤物體的TLE軌道；SATCAT資訊；Boxscore統計；碰撞預警CDM | TLE/JSON（軌道）實時更新；CDM預警約每8小時更新[space-track.org](https://www.space-track.org/documentation#:~:text=To%20prevent%20excess%20bandwidth%20costs%2C,emails%20to%20satellite%20owners%2Foperators) | 後端抓取資料量大；前端可視化碎片位置、熱區；依CDM提示標示高風險接近 |
| **CelesTrak 碎片** | 開放免費（特定碎片清單TLE，SOCRATES網頁） | 特定事件碎片TLE清單；全部有效衛星 vs 碎片清單；SOCRATES碰撞報告 | TLE（文本/JSON）每日更新；報告每日3次刷新celestrak.org | 前端直接取TLE繪製碎片雲；解析報告以顯示將相撞物件、距離等，增強互動性 |
| **LeoLabs** | 商業服務（需洽詢授權） | 高精度軌道數據；碰撞風險警報；歷史碎片事件分析 | 專有格式/儀表板；更新頻率極高（接近即時） | 透過自家平台或API獲取；適合需要精確監視特定物件、專業展示的應用（成本高） |

## 整合與視覺化框架建議

*圖：開源的3D衛星軌道視覺化示例顯示了Starlink衛星群（橙色點）與其他物體在地球周圍的即時分布*

[*github.com*](https://github.com/dsuarezv/satellite-tracker#:~:text=StarLink%20satellites%20highlighted%20in%20orange%2C,some%20of%20them%20displaying%20orbits)

*。此應用使用Three.js渲染，整合了即時軌道數據並支持與使用者互動。*

如上圖所示，要將即時太空數據整合進Web前端（Three.js / React Three Fiber），需要解決兩部分：**資料推演/獲取**與**WebGL渲染**。以下是具體建議：

- **軌道資料獲取與推演**：若使用TLE等元素資料，前端需要藉助程式庫將其轉換為當前空間座標。建議使用成熟的開源函式庫 **`satellite.js`**（JavaScript實現的SGP4軌道推算演算法）。例如Marko Andlar的24k衛星可視化項目即使用`satellite.js`每幾十毫秒計算所有衛星的新位置。`satellite.js`可直接將TLE轉換成地心慣性(ECI)座標，然後轉成地球固定(ECEF)或經緯度，用於繪製軌跡。對於**少量衛星**（如只追蹤ISS或幾顆星），可以直接利用諸如N2YO這類API，每隔幾秒請求一次即時座標，減少自行計算。而**大量物件**（成百上千）時，傳輸和API請求開銷變大，更高效的方法是**一次性抓取TLE**清單（例如透過CelesTrak提供的整批JSON），在客戶端週期性自行推算位置。這樣只需每隔數小時更新軌道要素，而位置插值由客戶端完成，可實現近乎即時的效果。
    
    [discourse.threejs.org](https://discourse.threejs.org/t/side-project-a-3d-satellite-tracker/48002#:~:text=I%20have%20used%20javascript%20for,js)
    
    [discourse.threejs.org](https://discourse.threejs.org/t/side-project-a-3d-satellite-tracker/48002#:~:text=So%20each%20fraction%20of%20a,is%20finished%2C%20the%20next%20frame)
    
    [github.com](https://github.com/dsuarezv/satellite-tracker#:~:text=Here%20is%20a%20nice%20screenshot,reference%20frame)
    
- **前端繪製與效能**：Three.js 能夠繪製地球模型和衛星軌道/位置。建議使用 **React Three Fiber (R3F)** 來管理Three.js元件，這樣可以將地球、衛星作為React元件控制，增加開發便利性。在繪製大量衛星/碎片時，注意效能優化：可以使用 **點雲(PointCloud)** 或 **粒子** 形式渲染衛星，而非為每個衛星使用高細節網格模型。上述24k衛星示例將每顆衛星繪製為帶材質的2D點，利用GPU一次性繪製數千點，極大提升了帧率。此外，可採用 **Web Workers** 將繁重的軌道計算移至背景執行緒，主執行緒專注渲染。例如可開數個Worker，各自計算部分衛星位置，完成後再把結果傳回主執行緒更新Three.js場景。這種多執行緒方式能保持動畫流暢。React Three Fiber本身也能與Hooks結合，在每帧更新時從狀態獲取最新座標並更新衛星對象的位置屬性。
    
    [discourse.threejs.org](https://discourse.threejs.org/t/side-project-a-3d-satellite-tracker/48002#:~:text=I%20split%20the%20data%20between,is%20finished%2C%20the%20next%20frame)
    
    [discourse.threejs.org](https://discourse.threejs.org/t/side-project-a-3d-satellite-tracker/48002#:~:text=So%20each%20fraction%20of%20a,is%20finished%2C%20the%20next%20frame)
    
    [discourse.threejs.org](https://discourse.threejs.org/t/side-project-a-3d-satellite-tracker/48002#:~:text=So%20each%20fraction%20of%20a,is%20finished%2C%20the%20next%20frame)
    
- **協同現有框架/範例**：在整合時，可參考現有的開源項目或框架。例如上文圖片出自的**Satellite Tracker**開源庫 – 它使用Three.js + React + satellite.js，內建載入CelesTrak的即時數據並繪製軌道。該項目支持按名稱搜尋衛星並高亮顯示軌道，說明了如何將資料、演算和視覺化串接在一起。使用此類現成方案能快速構建原型。此外，若專案需要地球的真實紋理或地理座標投影，可結合**CesiumJS**或**WebGL Earth**等工具。不過CesiumJS屬於獨立的3D地球引擎，如果主要目的在藝術表現和客製渲染效果，Three.js的靈活性更高。透過載入高解析度地球貼圖到Three.js球體上，再將衛星位置轉換為地球半徑以上的XYZ座標放置，即可製作一個基於真實地球的衛星分布圖。
    
    [github.com](https://github.com/dsuarezv/satellite-tracker#:~:text=Javascript%203D%20satellite%20tracker%20with,js%20for%20orbit%20prediction)
    
- **資料更新與同步**：由於衛星和碎片持續運動，確保**時間同步**非常重要。可以使用`Date.now()`或從服務器獲取的標準時間來推算軌道，使得不同資料源之間保持同步基準。例如，每隔1秒計算一次所有衛星於當前UTC時刻的位置，以避免不同步飄移。如果要強調**即時**，也可以考慮加快時間步調（例如每實際1秒模擬軌道運行10秒的速度）來誇張顯示軌跡，但要清楚標示，避免混淆真實時間。

總而言之，推薦的整合方案是：**利用CelesTrak等免費來源取得所需衛星/碎片的TLE資料**，在前端通過`satellite.js`等推算出即時位置，使用Three.js或React Three Fiber將地球與物體繪製出來，並實施必要的效能優化與多執行緒處理。這種方式在社群中已有成功案例

[discourse.threejs.org](https://discourse.threejs.org/t/side-project-a-3d-satellite-tracker/48002#:~:text=I%20have%20used%20javascript%20for,js)

[github.com](https://github.com/dsuarezv/satellite-tracker#:~:text=Javascript%203D%20satellite%20tracker%20with,js%20for%20orbit%20prediction)

且技術堆疊開源透明，非常適合創作互動式的太空主題藝術作品。在保有視覺表現力的同時，亦能確保資料的

**即時性與科學根據**

，讓觀眾直觀感受到頭頂上繁忙的太空景象。引用資料來源並善用上述工具，您將能順利打造出結合即時太空資訊的創意網頁裝置。

**參考來源：** 本報告內容參考並引用了Space-Track官方文件

[space-track.org](https://www.space-track.org/documentation#:~:text=To%20prevent%20excess%20bandwidth%20costs%2C,emails%20to%20satellite%20owners%2Foperators)

、CelesTrak資料說明

celestrak.org

、N2YO API 文件

[n2yo.com](https://www.n2yo.com/api/#:~:text=The%20REST%20API%20v1%20is,will%20be%20limited%20or%20blocked)

[n2yo.com](https://www.n2yo.com/api/#:~:text=)

、Open Notify說明

[freepublicapis.com](https://www.freepublicapis.com/iss-current-location#:~:text=Description)

、Aviation Edge官方介紹

[medium.com](https://medium.com/@AviationEdgeAPI/satellite-tracker-api-track-satellite-data-in-real-time-27e125a0222d#:~:text=Did%20you%20know%20that%20Aviation,Let%E2%80%99s%20talk%20about%20it%20more)

、ESA公佈的碎片數據

[esa.int](https://www.esa.int/Space_Safety/Space_Debris/About_space_debris#:~:text=About%20space%20debris%20,about%2028160%20remain%20in%20space)

，以及相關開源項目經驗分享

[discourse.threejs.org](https://discourse.threejs.org/t/side-project-a-3d-satellite-tracker/48002#:~:text=I%20have%20used%20javascript%20for,js)

[discourse.threejs.org](https://discourse.threejs.org/t/side-project-a-3d-satellite-tracker/48002#:~:text=So%20each%20fraction%20of%20a,is%20finished%2C%20the%20next%20frame)

[github.com](https://github.com/dsuarezv/satellite-tracker#:~:text=Javascript%203D%20satellite%20tracker%20with,js%20for%20orbit%20prediction)

等。在此一併致謝。
