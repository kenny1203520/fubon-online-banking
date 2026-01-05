# 生活繳費模組

生活繳費模組提供水、電、瓦斯、電話等日常繳費功能。

## 功能

- 🏠 **服務管理** - 查看可用的繳費服務
- 📄 **帳單管理** - 查看和管理繳費帳單
- 💳 **線上繳費** - 支持多種繳費方式
- 📊 **繳費紀錄** - 查看繳費歷史記錄
- 📈 **統計分析** - 帳單統計和趨勢分析

## 使用方式

### 在組件中使用

```vue
<script setup lang="ts">
import { useUtilityStore } from '@/modules/utilities'
import { onMounted } from 'vue'

const utilityStore = useUtilityStore()

onMounted(async () => {
  // 取得服務列表
  await utilityStore.fetchServices()
  
  // 取得帳單
  await utilityStore.fetchBills()
})
</script>

<template>
  <div>
    <h1>生活繳費</h1>
    
    <!-- 帳單列表 -->
    <div v-for="bill in utilityStore.bills" :key="bill.id">
      {{ bill.bill_type }} - {{ bill.provider }}: {{ bill.amount }}
    </div>
  </div>
</template>
```

## Store API

### 狀態

- `services` - 可用的繳費服務列表
- `bills` - 繳費帳單列表
- `paymentHistory` - 繳費記錄列表
- `isLoading` - 加載狀態
- `error` - 錯誤信息

### 計算屬性

- `billStats` - 帳單統計信息（待繳、已繳、逾期數量及總額）

### 方法

- `fetchServices()` - 取得繳費服務列表
- `fetchBills(options?)` - 取得帳單列表
- `payBill(data)` - 支付帳單
- `fetchPaymentHistory(options?)` - 取得支付歷史
- `clearError()` - 清除錯誤信息
- `reset()` - 重置狀態

## 目錄結構

```
utilities/
├── index.ts                 # 模組導出
├── README.md               # 文檔
├── types/
│   └── index.ts            # 類型定義
├── services/
│   └── utility.ts          # API 服務
├── stores/
│   └── utility.ts          # Pinia 狀態管理
└── views/
    ├── UtilitiesPage.vue   # 主頁面
    ├── BillsPage.vue       # 帳單列表
    └── HistoryPage.vue     # 繳費記錄
```

## 相關路由

- `/utilities` - 生活繳費主頁
- `/utilities/bills` - 繳費帳單
- `/utilities/history` - 繳費紀錄
