# 富邦網路銀行系統架構設計

## 1. 架構總覽

### 1.1 系統宏觀架構
```
┌─────────────────────────────────────────────────────────────┐
│                      終端使用者層                              │
│  ┌─────────────────┐              ┌──────────────────┐     │
│  │   網頁瀏覽器      │              │  行動應用 (iOS/Android) │     │
│  └────────┬────────┘              └────────┬─────────┘     │
└───────────┼─────────────────────────────────┼────────────────┘
            │                                 │
            │ HTTPS                           │ HTTPS
            │                                 │
┌───────────┼─────────────────────────────────┼────────────────┐
│           │                                 │                │
│   ┌──────▼──────────┐           ┌──────────▼────────┐       │
│   │   API閘道層      │           │   API閘道層        │       │
│   │ (Kong/AWS API GW)           │ (Kong/AWS API GW) │       │
│   └──────┬──────────┘           └──────────┬────────┘       │
│          │                                 │                │
│          └────────────┬────────────────────┘                │
│                       │                                     │
│            ┌──────────▼──────────┐                          │
│            │  負載均衡器          │                          │
│            │ (Nginx/HAProxy)     │                          │
│            └──────────┬──────────┘                          │
│                       │                                     │
│  ┌────────────────────┼────────────────────┐              │
│  │                    │                    │              │
│  ▼                    ▼                    ▼              │
│ ┌──────────┐      ┌──────────┐      ┌──────────┐         │
│ │ Django   │      │ Django   │      │ Django   │         │
│ │ 應用服務  │      │ 應用服務  │      │ 應用服務  │ (Pod集群) │
│ │ Pod 1    │      │ Pod 2    │      │ Pod N    │         │
│ └────┬─────┘      └────┬─────┘      └────┬─────┘         │
│      │                 │                 │               │
└──────┼─────────────────┼─────────────────┼───────────────┘
       │                 │                 │
       │  ┌──────────────┴─────────────────┐
       │  │                               │
       ▼  ▼                               ▼
   ┌──────────────┐              ┌──────────────┐
   │  PostgreSQL  │◄────────────►│  Redis快取   │
   │  (主從複製)   │              │  (分層快取)   │
   └──────────────┘              └──────────────┘
       │
       ▼
   ┌──────────────┐
   │  消息隊列    │
   │ (RabbitMQ)   │
   └──────────────┘
```

---

## 2. 分層架構設計

### 2.1 表示層 (Presentation Layer)
**職責**：用戶介面、請求路由、響應序列化

**技術棧**：
- React.js + TypeScript
- Redux 狀態管理
- Material-UI/Ant Design 元件庫
- Axios HTTP 客戶端

**主要模組**：
```
src/frontend/
├── components/          # UI 元件
│   ├── auth/           # 認證元件
│   ├── accounts/       # 帳戶元件
│   ├── transactions/   # 交易元件
│   └── ...
├── pages/              # 頁面
├── services/           # API 調用服務
├── store/              # Redux 狀態
├── hooks/              # React Hooks
└── utils/              # 工具函數
```

### 2.2 業務邏輯層 (Business Logic Layer)
**職責**：核心業務邏輯、驗證、授權、流程控制

**技術棧**：
- Django 框架
- Django REST Framework
- Celery 異步任務隊列

**主要模組**：
```
src/backend/
├── fubon/              # Django 專案配置
│   ├── settings.py     # 專案設置
│   ├── urls.py         # URL 路由
│   └── wsgi.py         # WSGI 應用
├── accounts/           # 帳戶應用
│   ├── models.py       # 資料模型
│   ├── views.py        # 視圖（API）
│   ├── serializers.py  # 序列化器
│   ├── urls.py         # URL 路由
│   ├── services.py     # 業務服務
│   └── tests.py        # 測試
├── transactions/       # 交易應用
├── investments/        # 投資應用
├── security/           # 安全認證應用
└── utils/              # 共享工具
```

### 2.3 資料層 (Data Layer)
**職責**：資料持久化、查詢、快取管理

**技術棧**：
- PostgreSQL 關聯式資料庫
- Redis 快取層
- SQLAlchemy ORM (Django ORM)

**主要元件**：
```
src/database/
├── migrations/         # 資料庫遷移腳本
├── init_db.sql         # 初始化腳本
├── schema/             # 資料庫設計文件
└── procedures/         # 存儲過程
```

---

## 3. 微服務分解架構

系統可按以下邊界分解為微服務：

```
┌──────────────────────────────────────────────┐
│           API 閘道 (Gateway)                   │
│        (認證、路由、限流、紀錄)                  │
└──────────┬───────────────────────────────────┘
           │
    ┌──────┼──────┬──────┬──────┬──────┐
    │      │      │      │      │      │
    ▼      ▼      ▼      ▼      ▼      ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│ 帳戶    │ │ 交易   │ │ 投資   │ │ 安全   │ │ 支付   │
│ 服務    │ │ 服務   │ │ 服務   │ │ 服務   │ │ 服務   │
├────────┤ ├────────┤ ├────────┤ ├────────┤ ├────────┤
│PostgreSQL│PostgreSQL│PostgreSQL│Redis   │PostgreSQL│
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘
    │      │      │      │      │      │
    └──────┼──────┴──────┴──────┴──────┘
           │
    ┌──────▼──────┐
    │ 消息隊列    │
    │(RabbitMQ)   │
    └─────────────┘
```

---

## 4. 核心業務模組架構

### 4.1 帳戶管理模組
```
┌─────────────────────────────────┐
│      帳戶管理 API 層              │
├─────────────────────────────────┤
│  GET  /accounts                 │
│  POST /accounts                 │
│  GET  /accounts/{id}            │
│  PUT  /accounts/{id}            │
└────────┬────────────────────────┘
         │
┌────────▼────────────────────────┐
│      帳戶業務邏輯層               │
├─────────────────────────────────┤
│ • 帳戶驗證                       │
│ • 帳戶開戶流程                   │
│ • KYC 檢查                      │
│ • 帳戶狀態管理                   │
└────────┬────────────────────────┘
         │
┌────────▼────────────────────────┐
│      資料模型層                   │
├─────────────────────────────────┤
│ • User 模型                     │
│ • Account 模型                  │
│ • AccountType 模型              │
│ • Profile 模型                  │
└─────────────────────────────────┘
         │
┌────────▼────────────────────────┐
│      PostgreSQL 資料庫           │
└─────────────────────────────────┘
```

### 4.2 交易處理模組
```
┌─────────────────────────────────┐
│      交易 API 層                  │
├─────────────────────────────────┤
│  POST /transfers                │
│  GET  /transactions             │
│  POST /currency-exchange        │
│  POST /bill-payment             │
└────────┬────────────────────────┘
         │
┌────────▼────────────────────────┐
│      交易業務邏輯層               │
├─────────────────────────────────┤
│ • 交易驗證                       │
│ • 金額檢查                       │
│ • 限額檢查                       │
│ • 風險評估                       │
│ • 交易執行                       │
│ • 對帳與補償                     │
└────────┬────────────────────────┘
         │
┌────────▼────────────────────────┐
│      交易日誌與稽核               │
├─────────────────────────────────┤
│ • Transaction 表                │
│ • TransactionLog 表             │
│ • AuditLog 表                   │
└─────────────────────────────────┘
```

---

## 5. 資料流架構

### 5.1 同步交易流
```
客戶端
  │
  │ HTTP POST /transfers
  │
▼
API 閘道
  │ 驗證 & 授權
  │
▼
Django 應用
  ├─ 請求驗證
  ├─ 資料檢查
  ├─ 金額驗證
  └─ 風險評估
  │
▼
資料庫事務
  ├─ 扣款 (UPDATE accounts SET balance = balance - amount)
  ├─ 入帳 (UPDATE accounts SET balance = balance + amount)
  └─ 記錄交易 (INSERT INTO transactions)
  │
▼
API 響應
  │
▼
客戶端顯示結果
```

### 5.2 非同步交易流 (高額轉帳、審批流程)
```
客戶端
  │
  │ HTTP POST /transfers (高額)
  │
▼
API 閘道 & Django 應用
  ├─ 驗證與初步檢查
  ├─ 建立交易紀錄 (status=pending)
  └─ 將資訊推送至資訊隊列
  │
▼ (非同步處理)
資訊隊列 (RabbitMQ)
  │
▼
後台工作進程 (Celery)
  ├─ 詳細風險評估
  ├─ 人工審批流程 (如需)
  ├─ 執行交易
  └─ 更新交易狀態
  │
▼
通知系統
  │
▼
客戶端推送通知
```

---

## 6. 高可用性設計

### 6.1 應用層冗餘
```
┌─────────────────────────────┐
│     負載均衡器 (Active)      │
│                             │
└────────────┬────────────────┘
             │
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
  Pod 1    Pod 2    Pod 3
  (Django) (Django) (Django)
```

### 6.2 資料庫高可用
```
┌────────────────────────┐
│   PostgreSQL 主節點     │
│   (Primary)            │
└────────────┬───────────┘
             │ 同步複製
    ┌────────┼────────┐
    │        │        │
    ▼        ▼        ▼
 從節點1   從節點2   從節點3
 (Standby) (Standby) (Standby)
```

### 6.3 快取層策略
```
L1: 本地快取 (Process Memory)
  ├─ 使用 Django Cache Framework
  ├─ TTL: 1-5 分鐘
  └─ 儲存：使用者設定、常用帳號等

L2: 分布式快取 (Redis)
  ├─ Session 快取
  ├─ 匯率快取
  ├─ 利率快取
  └─ TTL: 5-30 分鐘

L3: CDN 快取
  ├─ 靜態資源 (JS、CSS、圖片)
  └─ TTL: 1-7 天
```

---

## 7. 安全架構

### 7.1 認證流程
```
使用者登入
  │
  ├─ 輸入帳號密碼
  │
  ▼
OAuth 2.0 認證服務器
  │
  ├─ 驗證認證資訊
  ├─ 檢查 MFA (如啟用)
  └─ 簽發 JWT Token
  │
  ▼
API 閘道
  │
  ├─ 驗證 JWT Token
  ├─ 檢查 Token 過期
  └─ 提取使用者身份
  │
  ▼
後端服務 (已認證)
```

### 7.2 授權模型 (RBAC + ABAC)
```
角色 (Role)
├─ 個人客戶 (Personal Customer)
├─ 企業客戶 (Corporate Customer)
├─ 客服人員 (Customer Service)
└─ 管理員 (Administrator)
   │
   ├─ 權限 (Permission)
   │  ├─ account.view
   │  ├─ account.transfer
   │  ├─ account.withdraw
   │  └─ ...
   │
   ├─ 屬性 (Attribute)
   │  ├─ department = "Finance"
   │  ├─ location = "Taipei"
   │  └─ clearanceLevel = "High"
```

### 7.3 傳輸安全
```
客戶端
  │
  │ TLS 1.3 + mTLS (用於內部服務)
  │
▼
API 閘道
  ├─ SSL/TLS 終止
  ├─ 憑證驗證
  └─ 強制 HTTPS
  │
▼
後端服務
```

---

## 8. 監控與日誌架構

### 8.1 日誌層次
```
應用日誌 (Application Logs)
  ├─ Django Logging
  ├─ 業務事件日誌
  └─ 儲存：ELK Stack (Elasticsearch + Logstash + Kibana)

審計日誌 (Audit Logs)
  ├─ 使用者操作
  ├─ 權限變更
  ├─ 資料修改
  └─ 儲存：PostgreSQL (不可竄改)

效能日誌 (Performance Logs)
  ├─ API 響應時間
  ├─ 資料庫查詢時間
  └─ 儲存：Prometheus + Grafana
```

### 8.2 監控指標
```
系統指標 (System Metrics)
├─ CPU 使用率
├─ 記憶體使用率
├─ 磁盤 I/O
└─ 網絡頻寬

應用指標 (Application Metrics)
├─ API 吞吐量 (Throughput)
├─ 錯誤率 (Error Rate)
├─ P95/P99 延遲
└─ 活躍用戶數

業務指標 (Business Metrics)
├─ 交易成功率
├─ 轉帳成功率
├─ 平均交易時間
└─ 客戶滿意度
```

---

## 9. 災難復原 (DR) 架構

```
RTO: Recovery Time Objective ≤ 1 小時
RPO: Recovery Point Objective ≤ 5 分鐘

┌─────────────────────────────┐
│      主生產中心 (Primary)    │
│    (北京)                    │
└────────────┬────────────────┘
             │ 資料同步 & 心跳
             │ (每5分鐘一次)
┌────────────▼────────────────┐
│      備用中心 (Backup)       │
│    (深圳)                    │
│    (Hot Standby)            │
└─────────────────────────────┘

故障檢測 (30秒內)
  │
  ▼
自動故障轉移 (2分鐘內)
  │
  ├─ DNS 重指向
  ├─ 應用切換
  └─ 資料庫切換
  │
  ▼
從備用中心繼續提供服務
```

---

## 10. 部署拓撲 (Kubernetes)

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: fubon-banking

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: django-app
  namespace: fubon-banking
spec:
  replicas: 3
  selector:
    matchLabels:
      app: django
  template:
    metadata:
      labels:
        app: django
    spec:
      containers:
      - name: django
        image: fubon-banking:django-latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secrets
              key: url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10

---
apiVersion: v1
kind: Service
metadata:
  name: django-service
  namespace: fubon-banking
spec:
  type: ClusterIP
  selector:
    app: django
  ports:
  - port: 80
    targetPort: 8000
```

---

## 11. 技術棧總結

| 層級 | 技術 | 功能 |
|------|------|------|
| **表示層** | React + TypeScript | 用戶界面 |
| **API 閘道** | Kong / AWS API Gateway | 路由、認證、限流 |
| **業務邏輯** | Django + DRF | RESTful API 服務 |
| **應用伺服器** | Gunicorn + Nginx | WSGI 應用容器 |
| **資訊隊列** | RabbitMQ | 非同步任務 |
| **快取** | Redis | Session、熱資料快取 |
| **關係資料庫** | PostgreSQL | 主要資料存儲 |
| **搜尋引擎** | Elasticsearch | 日誌搜尋 |
| **監控** | Prometheus + Grafana | 指標監控 |
| **容器化** | Docker + Kubernetes | 應用部署 |
| **版本控制** | Git | 代碼管理 |
| **CI/CD** | Jenkins / GitHub Actions | 自動化部署 |

---

Last Updated: 2025年12月28日
