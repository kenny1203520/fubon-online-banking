from datetime import datetime, timezone

def _now():
    return datetime.now(timezone.utc).isoformat()

PRODUCTS = [
    {"id": 1, "name": "富邦穩健收益基金", "risk_level": "低", "currency": "TWD", "min_amount": 1000.0, "description": "適合保守型投資者，追求穩定現金流。", "created_at": _now()},
    {"id": 2, "name": "全球成長股票型基金", "risk_level": "高", "currency": "TWD", "min_amount": 5000.0, "description": "投資於全球成長型企業，風險較高，但潛在報酬也高。", "created_at": _now()},
    {"id": 3, "name": "新興市場債券基金", "risk_level": "中", "currency": "TWD", "min_amount": 2000.0, "description": "配置於新興市場債券，追求利息收益與資本增值。", "created_at": _now()},
    {"id": 4, "name": "富邦平衡配置基金A", "risk_level": "中", "currency": "TWD", "min_amount": 3000.0, "description": "股票與債券平衡配置，風險與報酬居中。", "created_at": _now()},
    {"id": 5, "name": "環球科技成長基金", "risk_level": "高", "currency": "TWD", "min_amount": 10000.0, "description": "聚焦全球科技龍頭及創新企業。", "created_at": _now()},
    {"id": 6, "name": "富邦短期收益債券基金", "risk_level": "低", "currency": "TWD", "min_amount": 500.0, "description": "以短期債券為主，流動性佳且波動低。", "created_at": _now()},
    {"id": 7, "name": "區域新興股權基金", "risk_level": "高", "currency": "TWD", "min_amount": 4000.0, "description": "投資亞洲新興市場成長企業。", "created_at": _now()},
    {"id": 8, "name": "全球高收益債券基金", "risk_level": "中", "currency": "TWD", "min_amount": 2500.0, "description": "追求較高利息收益，適合承擔中度風險者。", "created_at": _now()},
    {"id": 9, "name": "富邦台灣優選基金", "risk_level": "中", "currency": "TWD", "min_amount": 2000.0, "description": "選股策略聚焦台灣優質企業。", "created_at": _now()},
    {"id": 10, "name": "全球小型股增長基金", "risk_level": "高", "currency": "TWD", "min_amount": 8000.0, "description": "專注小型成長股，波動高但成長潛力佳。", "created_at": _now()},
    {"id": 11, "name": "永續發展股票基金", "risk_level": "中", "currency": "TWD", "min_amount": 3000.0, "description": "投資於ESG評分優良之公司。", "created_at": _now()},
    {"id": 12, "name": "富邦高股息基金", "risk_level": "中", "currency": "TWD", "min_amount": 1500.0, "description": "以高股息股票為核心，追求現金收益。", "created_at": _now()},
    {"id": 13, "name": "全球醫療保健基金", "risk_level": "中", "currency": "TWD", "min_amount": 3500.0, "description": "聚焦醫療與生物科技領域。", "created_at": _now()},
    {"id": 14, "name": "環保綠能主題基金", "risk_level": "高", "currency": "TWD", "min_amount": 5000.0, "description": "投資於綠能與永續科技相關公司。", "created_at": _now()},
    {"id": 15, "name": "全球房地產投資信託基金", "risk_level": "中", "currency": "TWD", "min_amount": 2000.0, "description": "配置於國際不動產與REITs。", "created_at": _now()},
    {"id": 16, "name": "富邦退休目標基金2030", "risk_level": "低", "currency": "TWD", "min_amount": 1000.0, "description": "為退休目標設計的目標日期基金(2030)。", "created_at": _now()},
    {"id": 17, "name": "新興市場科技基金", "risk_level": "高", "currency": "TWD", "min_amount": 6000.0, "description": "投資於新興市場的科技與網路企業。", "created_at": _now()},
    {"id": 18, "name": "低波動股票基金", "risk_level": "低", "currency": "TWD", "min_amount": 1200.0, "description": "選擇波動率較低的股票以降低組合波動。", "created_at": _now()},
]
