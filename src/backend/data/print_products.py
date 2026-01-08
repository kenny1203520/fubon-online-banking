from sqlmodel import Session, select
from core.database import engine
from models.investment_product import InvestmentProduct

#test
with Session(engine) as session:
    stmt = select(InvestmentProduct)
    rows = session.exec(stmt).all()
    for r in rows:
        print(r)
