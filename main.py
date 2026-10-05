from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

from database import SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends

products = {}
next_product_id = 1
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

class Product(BaseModel):
    name: str
    price: float = Field(gt=0)

@app.post("/products", status_code=201)
async def create_product(product: Product):
    global next_product_id

    products[next_product_id] = product
    next_product_id += 1
    
    return products[next_product_id - 1]
    
class ProductResponse(BaseModel):
    name: str
    price: float

@app.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    if product_id not in products:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return {
        "name": products[product_id].name,
        "price": products[product_id].price
    }
    
@app.delete("/products/{product_id}")
async def delete_product(product_id: int):
    if product_id not in products:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )
    
    del products[product_id]
    return f"Product with Product ID {product_id} deleted."

@app.put("/products/{product_id}")
async def update_product(product_id: int, product: Product):
    if product_id not in products:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    products[product_id] = product
    return {
        "name": products[product_id].name,
        "price": products[product_id].price
    }

class PatchUpdate(BaseModel):
    name: str | None = None
    price: float | None = Field(gt=0)

@app.patch("/products/{product_id}", response_model=ProductResponse)
async def patch_update_product(product_id: int, product: PatchUpdate):
    if product_id not in products:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    stored_product = products[product_id]
    updates = product.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(stored_product, field, value)

    products[product_id] = stored_product

    print(updates)
    return stored_product

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/db-test")
async def db_test(db: Session = Depends(get_db)):
    return {"message": "Database session received"}


