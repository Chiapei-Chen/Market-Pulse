# Market-Pulse
Market Pulse 是一個專為台股交易者設計的即時動能監測儀表板。不同於傳統券商軟體粗糙的產業分類，本專案透過 自定義深度族群標籤 (Niche Tags)，自動解構盤中成交量/成值前 100 名，幫助使用者在資金湧入初期，精準捕捉「族群性集體起漲」的訊號。

💡 為什麼開發這個專案？
傳統軟體告訴你「2330 漲了」，但 Market Pulse 告訴你：「前 100 名成值排行中，有 12 檔屬於『CPO 矽光子』，且其中 5 檔是今天新進榜的。」

透過將交易者的「盤感」數位化，我們讓資金流向變得肉眼可見。

✨ 核心功能 (Core Features)
📂 超詳細族群標籤 (Deep Tagging)
超越傳統分類： 捨棄「電子」、「電機」等籠統類別，細分至 CPO 矽光子、CoWoS 設備、散熱液冷、重電 等實戰級族群。

自定義 Mapping： 透過 JSON 字典維護精準的股票與族群對應關係。

📊 即時排行與異動統計 (Ranking & Analytics)
成值/成交量 Top 100： 即時監控盤中資金最集中的標的。

昨日 vs 今日差異： 自動對比名次變動（Rank Change），捕捉「名次竄升」或「新入榜」的異動股。

族群集中度偵測： 自動計算前 100 名中各族群的佔比，識別今日最強勢的「兵團」。

🧹 純淨數據過濾 (Noise Filtering)
ETF 一鍵切換： 可自由選擇是否顯示 ETF，排除被動資金干擾，專注於主動型主力資金。

🛠 技術架構 (Tech Stack)
Frontend (Vue 3 Ecosystem)
Framework: Vue 3 (Composition API)

Language: TypeScript (強型別確保數據處理穩定)

Store: Pinia (管理即時排行與歷史快照)

Styling: Tailwind CSS

Backend (Python Ecosystem)
Framework: FastAPI (非同步架構，適合處理即時數據)

Data Processing: Pandas (高效能排行榜比對與聚合運算)

Logic: * RankDiff Engine: 比對兩日數據的 Set 運算。

GroupAggregator: 根據自定義標籤進行族群熱度計算。

📂 核心邏輯範例
族群定義 (Mapping Structure)
JSON
{
  "2317": { "code": "2317", "industry": "電子組裝", "tag": "AI伺服器" },
  "1513": { "code": "1513", "industry": "電機機械", "tag": "重電" }
}
差異分析 (Ranking Comparison)
系統會自動識別：

New Entry: 昨日不在前 100 名，今日強勢衝入。

Fast Climber: 名次較昨日大幅提升（例如：從 90 名爬升至 10 名）。

🚀 快速啟動 (Quick Start)
Backend
Bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
Frontend
Bash
cd frontend
npm install
npm run dev
📈 未來規劃 (Roadmap)
[ ] 支援 WebSocket 盤中毫秒級跳動。

[ ] 視覺化熱圖 (Treemap) 呈現族群資金佔比。

[ ] 歷史強勢族群紀錄與回測。
