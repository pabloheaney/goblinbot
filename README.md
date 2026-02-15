## 🛠 事前準備

在開始部署之前，請確保你擁有以下資訊：

1. **Telegram Bot Token (x2)**：
   * 請向 [@BotFather](https://t.me/BotFather) 申請兩個機器人。
   * 一個用於管理 (Admin Bot)，一個用於顯示 (Display Bot)。
2. **Telegram User ID (Admin ID)**：
   * 管理員的個人 Telegram ID（可透過 [@userinfobot](https://t.me/userinfobot) 查詢）。
3. **GitHub Token (Classic)**：
   * 到 GitHub Settings -> Developer settings -> Personal access tokens -> Tokens (classic)。
   * 建立一個新 Token，必須勾選 `repo` (Full control of private repositories) 權限。
4. **GitHub Repository**：
   * 將github文件夾下的data.json和index.html 上傳到你的 GitHub 帳號（建議設為 Public，若設為 Private 則需付費版 GitHub 才能使用 GitHub Pages）。

---

## 🚀 安裝與部署 (Docker)

本專案建議使用 Docker 進行部署，確保環境一致性。

### 1. 設定環境變數

在專案根目錄建立一個 `.env` 檔案，填入以下內容：

```env
# Display Bot 的 Token (給用戶看的)
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrs...

# Admin Bot 的 Token (管理員用的)
ADMIN_BOT_TOKEN=987654321:ZYXwvutsRQPonml...

# GitHub Personal Access Token (用於寫入 data.json)
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxx

# 你的 GitHub 倉庫名稱 (格式: 使用者/倉庫名)
REPO_NAME=yourname/goblinportal

# 指定分支 (通常為 main 或 master)
BRANCH_NAME=main

# 管理員的 Telegram ID (只有此 ID 能使用 Admin Bot)
ADMIN_ID=123456789
```
### 2. 建立並運行Docker
```
docker build -t telegram-portal-bot .

docker run -d \
  --name portal-bot \
  --env-file .env \
  --restart unless-stopped \
  telegram-portal-bot
```
---

## 🌐 設定 Telegram Mini App (GitHub Pages)

本github文件下包含一個 `index.html`，這是一個靜態網頁，用於作為 Telegram Mini App (Web App) 顯示群組列表。為了讓用戶能透過漂亮的網頁介面查看列表，我們需要啟用 GitHub Pages 來託管這個網頁。

### 1. 啟用 GitHub Pages (託管網頁)

1.  進入你的 GitHub Repository 頁面。
2.  點選上方選單的 **Settings** (設定)。
3.  在左側側邊欄尋找並點選 **Pages**。
4.  在 **Build and deployment** 區塊下的 **Source** 下拉選單中，選擇 `Deploy from a branch`。
5.  在 **Branch** 區塊：
    * 選擇你的主要分支（通常是 `main` 或 `master`）。
    * 資料夾選擇 `/ (root)`。
    * 點擊 **Save**。
6.  等待約 1~3 分鐘後，重新整理頁面。你會在上方看到一段訊息：「Your site is live at...」，並獲得一個網址（例如：`https://yourname.github.io/goblinportal/`）。請複製這個網址。

### 2. 綁定 Mini App 到 Display Bot (設定選單按鈕)

這一步驟將會把剛才產生的網址設定為機器人的「Menu Button」，讓用戶可以在聊天室左下角直接開啟。

1.  在 Telegram 開啟 **[@BotFather](https://t.me/BotFather)**。
2.  輸入 `/mybots` 並選擇你的 **Display Bot**（請勿選擇 Admin Bot）。
3.  點選 **Bot Settings**。
4.  點選 **Menu Button**。
5.  點選 **Configure Menu Button**。
6.  BotFather 會要求你傳送網址。請貼上你在步驟 1 獲得的 **GitHub Pages 網址**。
7.  BotFather 會要求你輸入按鈕名稱。請輸入你喜歡的名稱（例如：「開啟傳送門」或是「查看群組列表」）。

### ✅ 測試

現在，回到你的 Display Bot 聊天室：
1.  你應該會看到輸入框左下角（或鍵盤區域）出現了你剛才設定的按鈕。
2.  點擊按鈕，應該會彈出一個全螢幕的視窗，並載入 `index.html` 顯示群組列表。
3.  如果列表顯示空白，請確認你的 Repo 根目錄下是否有 `data.json` 檔案。

> **⚠️ 注意事項**：
> 當 Admin Bot 更新了 `data.json` 後，GitHub Pages 可能會有 **1~5 分鐘的 CDN 快取延遲**。雖然 `index.html` 內已有防止瀏覽器快取的機制 (`?t=timestamp`)，但 GitHub 伺服器端的更新仍需少許時間，這是正常現象。

