from sqlalchemy import create_engine, String, Float, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = "sqlite:///./products.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

class Base(DeclarativeBase):
    pass

class ProductDB(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[float] = mapped_column(Float)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()

""" product = ProductDB(
    name="Keyboard",
    price=49.99
)

db.add(product)
db.commit()

print(product.id) """

""" result = db.execute(select(ProductDB))

products = result.scalars().all() """

# print(result)
# print(products)

""" for product in products:
    print(product.id)
    print(product.name)
    print(product.price)

db.close() """

""" result = db.execute(select(ProductDB).where(ProductDB.id == 1))

product = result.scalar_one_or_none()

print(product)

if product:
    print(product.id)
    print(product.name)
    print(product.price)

db.close() """

""" product = ProductDB(
    name="Monitor",
    price=49.99
)

db.add(product)
db.commit()

print(product.id)
print(product.name)
print(product.price)

db.close() """

""" result = db.execute(select(ProductDB).where(ProductDB.id == 2))

product = result.scalar_one_or_none()

if product:
    product.price = 179.99
    db.commit()

    print(product.id)
    print(product.name)
    print(product.price)

db.close()
 """

""" result = db.execute(select(ProductDB).where(ProductDB.id == 2))

product = result.scalar_one_or_none()

if product:
    db.delete(product)
    db.commit()
    print("Product deleted")

db.close()
 """

result = db.execute(select(ProductDB).where(ProductDB.id == 2))

product = result.scalar_one_or_none()

db.close()

