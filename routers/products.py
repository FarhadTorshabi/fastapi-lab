from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_db
from models import ProductDB
from schemas import Product, ProductPatch, ProductDBResponse

router = APIRouter()

@router.get("/db-products", response_model=list[ProductDBResponse])
async def db_products(db: Session = Depends(get_db)):
    results = db.execute(select(ProductDB))
    products = results.scalars().all()
    product_list = list()
    for product in products:
        prod = dict()
        prod["id"] = product.id
        prod["name"] = product.name
        prod["price"] = product.price
        prod["secret"] = "ABC123"
        product_list.append(prod)

    return product_list

@router.get("/db-products/{product_id}", response_model=ProductDBResponse)
async def get_db_product(product_id: int, db: Session = Depends(get_db)):
    result = db.execute(select(ProductDB).where(ProductDB.id == product_id))
    product = result.scalar_one_or_none()

    if product:
        return {
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )

@router.post("/db-products", status_code=201, response_model=ProductDBResponse)
async def create_db_product(product: Product, db: Session = Depends(get_db)):

    db_product = ProductDB(
        name=product.name,
        price=product.price
    )
    db.add(db_product)
    db.commit()

    return db_product

@router.put("/db-products/{product_id}", response_model=ProductDBResponse)
async def update_db_product(product_id: int, product: Product, db: Session = Depends(get_db)):

    result=db.execute(select(ProductDB).where(ProductDB.id == product_id))
    db_product = result.scalar_one_or_none()

    if not db_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db_product.name = product.name
    db_product.price = product.price

    db.commit()

    return db_product

@router.delete("/db-products/{product_id}")
async def delete_db_product(product_id: int, db: Session = Depends(get_db)):

    result = db.execute(select(ProductDB).where(ProductDB.id == product_id))
    db_product = result.scalar_one_or_none()

    if not db_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    db.delete(db_product)
    db.commit()

    return{
        "message": f"Product with product id {product_id} deleted successfully."
    }
