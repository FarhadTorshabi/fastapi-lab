from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from database import get_db
from models import ProductDB
from schemas import Product, ProductPatch, ProductDBResponse

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/about")
async def about():
    return {"message": "This is my FastAPI learning project."}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/hello")
async def hello():
    return {"message": "Hello!"}


@app.get("/items/{item_id}")
async def get_item(item_id: int, name: str=""):
    if not name.strip():
        return {
            "item_id": item_id,
            "name": "Unknown"
        }

    return {
        "item_id": item_id,
        "name": name
    }

def my_dependency():
    return {"message": "Hello from dependency"}

@app.get("/test")
async def dependency_test(data = Depends(my_dependency)):
    return data

def my_dependecy_2():
    return {
        "username": "admin"
    }

@app.get("/test2")
async def dependecy_test_2(user_data = Depends(my_dependecy_2)):
    if user_data["username"] == "admin":
        return {
            "message": "Welcome admin"
        }

def my_dependency_3(username: str):
    return {
        "username": username
    }

@app.get("/test3")
async def dependency_test_3(username: dict = Depends(my_dependency_3)):
    return {
        "message": f"Welcome {username['username']}"
    }

@app.get("/test4")
async def dependency_admin_test(username: dict = Depends(my_dependency_3)):
    if username["username"] == "admin":
        return {
            "message": f"Welcome admin"
        }

    raise HTTPException(status_code=403, detail="Forbidden")

def admin_check(username: str):
    if username != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return {
        "username": username
    }

@app.get("/test5")
async def dependency_admin_without_check(username: dict = Depends(admin_check)):
    return {
        "message": "Welcome admin"
    }

@app.delete("/test6")
async def test6(username: dict = Depends(admin_check)):
    return {
        "message": "Admin can delete"
    }

def get_current_user(username: str):
    if username == "alice":
        role = "admin"
    else:
        role = "user"
    return {
        "username": username,
        "role": role
    }

@app.get("/profile")
async def profile(user: dict = Depends(get_current_user)):
    return {
        "username": user["username"],
        "role": user["role"]
    }

def get_admin_user(user: dict = Depends(get_current_user)):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")

    return user

@app.get("/admin-profile")
async def admin_profile(user: dict = Depends(get_admin_user)):
    return {
        "username": user["username"],
        "role": user["role"]
    }


@app.get("/db-test")
async def db_test(db: Session = Depends(get_db)):
    return {"message": "Database session received"}

@app.get("/db-products", response_model=list[ProductDBResponse])
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

@app.get("/db-products/{product_id}", response_model=ProductDBResponse)
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

@app.post("/db-products", status_code=201, response_model=ProductDBResponse)
async def create_db_product(product: Product, db: Session = Depends(get_db)):

    db_product = ProductDB(
        name=product.name,
        price=product.price
    )
    db.add(db_product)
    db.commit()

    return db_product

@app.put("/db-products/{product_id}", response_model=ProductDBResponse)
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

@app.delete("/db-products/{product_id}")
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

@app.patch("/db-products/{product_id}", response_model=ProductDBResponse)
async def patch_update_db_product(product_id: int, product: ProductPatch, db: Session = Depends(get_db)):

    result = db.execute(select(ProductDB).where(ProductDB.id == product_id))
    db_product = result.scalar_one_or_none()

    if not db_product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    updates = product.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(db_product, field, value)

    db.commit()

    return db_product



