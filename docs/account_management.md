# 帳戶管理 — 使用案例與 API 規格

本檔描述專案中「帳戶管理」相關的三項功能：

- 線上開戶申請
- 線上信用卡申請
- 註冊網路銀行

接受準則：每項功能應包含 API 端點、必要欄位、基本驗證與範例回應；並可由輕量後端（示範用）處理請求與回傳狀態。

1) 線上開戶申請
- 目的：使用者送出個人資訊與初始存款以申請帳戶。
- API：
  - POST /api/accounts/open
  - Request JSON:
    {
      "full_name": "王小明",
      "id_number": "A123456789",
      "email": "user@example.com",
      "initial_deposit": 1000.0
    }
  - Response (201 created):
    {
      "account_id": 1,
      "status": "pending",
      "message": "申請已建立，等待審核"
    }

2) 線上信用卡申請
- 目的：使用者提交信用卡申請資料由系統記錄並觸發審核流程（示範為記錄案例）。
- API：
  - POST /api/creditcards/apply
  - Request JSON:
    {
      "full_name": "王小明",
      "id_number": "A123456789",
      "annual_income": 800000,
      "card_type": "gold"
    }
  - Response (201 created):
    {
      "application_id": 1,
      "status": "received",
      "message": "信用卡申請已收到"
    }

3) 註冊網路銀行
- 目的：使用者建立網路銀行登入帳號（示範不包含完整 OAuth/2FA，僅示範註冊/雜湊密碼）。
- API：
  - POST /api/users/register
  - Request JSON:
    {
      "username": "user01",
      "password": "Secret123",
      "email": "user@example.com"
    }
  - Response (201 created):
    {
      "user_id": 1,
      "username": "user01",
      "message": "註冊成功"
    }

資料模型（示範）
- accounts: id, full_name, id_number, email, balance, status, created_at
- credit_card_applications: id, full_name, id_number, annual_income, card_type, status, created_at
- users: id, username, password_hash, email, created_at

安全與下一步建議
- 生產系統應加入：輸入驗證、身分證明文件上傳、風控審核、OTP/Passkeys、強密碼與速率限制。
- 可延伸：Webhook 給審核系統、背景工作（Celery）處理高額審核。
