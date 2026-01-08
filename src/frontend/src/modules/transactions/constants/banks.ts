// 台灣銀行代碼與名稱
export interface BankInfo {
  code: string
  name: string
  shortName: string
}

export const TAIWAN_BANKS: BankInfo[] = [
  { code: '004', name: '臺灣銀行', shortName: '台銀' },
  { code: '005', name: '臺灣土地銀行', shortName: '土銀' },
  { code: '006', name: '合作金庫商業銀行', shortName: '合庫' },
  { code: '007', name: '第一商業銀行', shortName: '一銀' },
  { code: '008', name: '華南商業銀行', shortName: '華南' },
  { code: '009', name: '彰化商業銀行', shortName: '彰銀' },
  { code: '011', name: '上海商業儲蓄銀行', shortName: '上海' },
  { code: '012', name: '富邦商業銀行', shortName: '富邦' },
  { code: '013', name: '國泰世華商業銀行', shortName: '國泰' },
  { code: '016', name: '高雄銀行', shortName: '高雄' },
  { code: '017', name: '兆豐國際商業銀行', shortName: '兆豐' },
  { code: '018', name: '全國農業金庫', shortName: '農金' },
  { code: '021', name: '花旗（台灣）商業銀行', shortName: '花旗' },
  { code: '025', name: '首都銀行', shortName: '首都' },
  { code: '048', name: '王道商業銀行', shortName: '王道' },
  { code: '050', name: '臺灣中小企業銀行', shortName: '台企銀' },
  { code: '052', name: '渣打國際商業銀行', shortName: '渣打' },
  { code: '053', name: '台中商業銀行', shortName: '台中銀' },
  { code: '054', name: '京城商業銀行', shortName: '京城' },
  { code: '072', name: '德意志銀行', shortName: '德銀' },
  { code: '081', name: '匯豐（台灣）商業銀行', shortName: '匯豐' },
  { code: '101', name: '瑞興商業銀行', shortName: '瑞興' },
  { code: '102', name: '華泰商業銀行', shortName: '華泰' },
  { code: '103', name: '臺灣新光商業銀行', shortName: '新光' },
  { code: '108', name: '陽信商業銀行', shortName: '陽信' },
  { code: '118', name: '板信商業銀行', shortName: '板信' },
  { code: '147', name: '三信商業銀行', shortName: '三信' },
  { code: '700', name: '中華郵政', shortName: '郵局' },
  { code: '803', name: '聯邦商業銀行', shortName: '聯邦' },
  { code: '805', name: '遠東國際商業銀行', shortName: '遠東' },
  { code: '806', name: '元大商業銀行', shortName: '元大' },
  { code: '807', name: '永豐商業銀行', shortName: '永豐' },
  { code: '808', name: '玉山商業銀行', shortName: '玉山' },
  { code: '809', name: '凱基商業銀行', shortName: '凱基' },
  { code: '810', name: '星展（台灣）商業銀行', shortName: '星展' },
  { code: '812', name: '台新國際商業銀行', shortName: '台新' },
  { code: '814', name: '大眾商業銀行', shortName: '大眾' },
  { code: '815', name: '日盛國際商業銀行', shortName: '日盛' },
  { code: '816', name: '安泰商業銀行', shortName: '安泰' },
  { code: '822', name: '中國信託商業銀行', shortName: '中信' },
]

/**
 * 依代碼查詢銀行資訊
 */
export function getBankByCode(code: string): BankInfo | undefined {
  return TAIWAN_BANKS.find(bank => bank.code === code)
}

/**
 * 驗證台灣銀行帳號格式
 * 格式: XXX-XXXXXX (分行代碼3碼-帳號6碼，不含銀行代碼)
 */
export function validateAccountNumber(bankCode: string, accountNumber: string): boolean {
  // 移除可能的分隔符號
  const cleanNumber = accountNumber.replace(/[-\s]/g, '')
  
  // 基本長度檢查 (分行代碼3碼 + 帳號6碼 = 9碼)
  if (cleanNumber.length !== 9) {
    return false
  }
  
  // 檢查是否全為數字
  if (!/^\d+$/.test(cleanNumber)) {
    return false
  }
  
  return true
}

/**
 * 格式化帳號顯示 (加入分隔符號)
 * 輸入格式: 525947586 或 525-947586 (分行3碼+帳號6碼)
 * 輸出格式: 012-525-947586 (銀行3碼-分行3碼-帳號6碼)
 */
export function formatAccountNumber(bankCode: string, accountNumber: string): string {
  const cleanNumber = accountNumber.replace(/[-\s]/g, '')
  
  // 檢查長度是否正確 (分行3碼 + 帳號6碼 = 9碼)
  if (cleanNumber.length !== 9) {
    return accountNumber
  }
  
  // 格式: 分行代碼(3) + 帳號(6)
  const branch = cleanNumber.substring(0, 3)
  const account = cleanNumber.substring(3)
  
  return `${bankCode}-${branch}-${account}`
}

/**
 * 檢查是否為本行（富邦銀行）
 */
export function isInternalBank(bankCode: string): boolean {
  return bankCode === '012'
}
