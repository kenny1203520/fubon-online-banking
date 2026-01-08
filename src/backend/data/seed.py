from sqlmodel import Session, select
from core.database import engine
from models.investment_product import InvestmentProduct
from data.investment_products import PRODUCTS


#test
def seed_products():
    with Session(engine) as session:
        for p in PRODUCTS:
            # try to find by id
            stmt = select(InvestmentProduct).where(InvestmentProduct.id == p['id'])
            existing = session.exec(stmt).first()
            if existing:
                # update fields
                existing.name = p['name']
                existing.risk_level = p['risk_level']
                existing.currency = p.get('currency', existing.currency)
                existing.min_amount = p.get('min_amount', existing.min_amount)
                existing.description = p.get('description', existing.description)
                existing.created_at = p.get('created_at', existing.created_at)
                session.add(existing)
            else:
                prod = InvestmentProduct(
                    id=p['id'],
                    name=p['name'],
                    risk_level=p['risk_level'],
                    currency=p.get('currency', 'TWD'),
                    min_amount=p.get('min_amount', 0),
                    description=p.get('description'),
                    created_at=p.get('created_at')
                )
                session.add(prod)
        session.commit()


def seed_all():
    seed_products()
