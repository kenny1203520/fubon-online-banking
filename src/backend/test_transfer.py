"""
測試轉帳功能的腳本
Test script for transfer functionality
"""
import requests
import json
from datetime import datetime

# API 基礎 URL
BASE_URL = "http://localhost:8000/api/v1"

# 測試用戶登入資訊（需要先創建測試用戶）
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"

def print_section(title: str):
    """列印分隔線"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def login() -> str:
    """登入並獲取 token"""
    print_section("1. 用戶登入")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get("access_token")
        print(f"✓ 登入成功！Token: {token[:20]}...")
        return token
    else:
        print(f"✗ 登入失敗: {response.status_code}")
        print(response.text)
        return None

def get_accounts(token: str):
    """獲取帳戶列表"""
    print_section("2. 查詢帳戶列表")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/accounts", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        accounts = data.get("items", [])
        print(f"✓ 找到 {len(accounts)} 個帳戶：")
        for acc in accounts:
            print(f"  - ID: {acc['id']}")
            print(f"    帳號: {acc['account_number']}")
            print(f"    名稱: {acc['account_name']}")
            print(f"    餘額: {acc['balance']:,.2f} 元")
            print(f"    狀態: {acc['status']}")
            print()
        return accounts
    else:
        print(f"✗ 查詢失敗: {response.status_code}")
        print(response.text)
        return []

def test_transfer_by_id(token: str, from_account_id: str, to_account_id: str, amount: float):
    """測試使用帳戶ID轉帳"""
    print_section("3. 測試使用帳戶ID轉帳")
    
    headers = {"Authorization": f"Bearer {token}"}
    request_data = {
        "from_account": from_account_id,
        "to_account": to_account_id,
        "amount": amount,
        "description": "測試轉帳 - 使用ID"
    }
    
    print(f"轉帳資料:")
    print(f"  來源帳戶ID: {from_account_id}")
    print(f"  目標帳戶ID: {to_account_id}")
    print(f"  金額: {amount:,.2f} 元")
    print()
    
    response = requests.post(
        f"{BASE_URL}/transactions/transfer",
        headers=headers,
        json=request_data
    )
    
    print(f"狀態碼: {response.status_code}")
    print(f"回應:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    return response.status_code == 200

def test_transfer_by_number(token: str, from_number: str, to_number: str, amount: float):
    """測試使用帳號轉帳"""
    print_section("4. 測試使用帳號轉帳")
    
    headers = {"Authorization": f"Bearer {token}"}
    request_data = {
        "from_account_number": from_number,
        "to_account_number": to_number,
        "amount": amount,
        "description": "測試轉帳 - 使用帳號"
    }
    
    print(f"轉帳資料:")
    print(f"  來源帳號: {from_number}")
    print(f"  目標帳號: {to_number}")
    print(f"  金額: {amount:,.2f} 元")
    print()
    
    response = requests.post(
        f"{BASE_URL}/transactions/transfer",
        headers=headers,
        json=request_data
    )
    
    print(f"狀態碼: {response.status_code}")
    print(f"回應:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    return response.status_code == 200

def test_invalid_transfer(token: str, from_account_id: str, to_account_id: str):
    """測試無效的轉帳（餘額不足）"""
    print_section("5. 測試無效轉帳（餘額不足）")
    
    headers = {"Authorization": f"Bearer {token}"}
    request_data = {
        "from_account": from_account_id,
        "to_account": to_account_id,
        "amount": 99999999.99,  # 超大金額
        "description": "測試失敗轉帳"
    }
    
    print(f"嘗試轉帳 99,999,999.99 元（預期失敗）")
    print()
    
    response = requests.post(
        f"{BASE_URL}/transactions/transfer",
        headers=headers,
        json=request_data
    )
    
    print(f"狀態碼: {response.status_code}")
    print(f"錯誤訊息:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    
    return response.status_code == 400

def get_transactions(token: str, account_id: str):
    """查詢交易記錄"""
    print_section("6. 查詢交易記錄")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/transactions/",
        headers=headers,
        params={
            "account_id": account_id,
            "page": 1,
            "per_page": 10
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        transactions = data.get("items", [])
        print(f"✓ 找到 {len(transactions)} 筆交易記錄：")
        for txn in transactions[:5]:  # 只顯示前5筆
            print(f"  - 流水號: {txn['transaction_number']}")
            print(f"    類型: {txn['type']}")
            print(f"    金額: {txn['amount']:,.2f} 元")
            print(f"    手續費: {txn['fee']:,.2f} 元")
            print(f"    狀態: {txn['status']}")
            print(f"    描述: {txn['description']}")
            print(f"    時間: {txn['created_at']}")
            print()
        return transactions
    else:
        print(f"✗ 查詢失敗: {response.status_code}")
        print(response.text)
        return []

def main():
    """主測試流程"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "轉帳功能測試腳本" + " " * 27 + "║")
    print("╚" + "═" * 58 + "╝")
    
    # 1. 登入
    token = login()
    if not token:
        print("\n測試終止：無法登入")
        return
    
    # 2. 獲取帳戶
    accounts = get_accounts(token)
    if len(accounts) < 2:
        print(f"\n測試終止：需要至少2個帳戶進行測試（目前: {len(accounts)}個）")
        return
    
    # 使用前兩個帳戶進行測試
    account1 = accounts[0]
    account2 = accounts[1]
    
    # 3. 測試使用ID轉帳
    test_transfer_by_id(
        token,
        account1['id'],
        account2['id'],
        1000.0
    )
    
    # 4. 測試使用帳號轉帳
    test_transfer_by_number(
        token,
        account2['account_number'],
        account1['account_number'],
        500.0
    )
    
    # 5. 測試無效轉帳
    test_invalid_transfer(
        token,
        account1['id'],
        account2['id']
    )
    
    # 6. 查詢交易記錄
    get_transactions(token, account1['id'])
    
    print_section("測試完成")
    print("\n✓ 所有測試已完成！\n")

if __name__ == "__main__":
    main()
