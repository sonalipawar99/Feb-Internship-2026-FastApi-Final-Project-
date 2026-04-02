# main.py

# 1. Import FastAPI
from fastapi import FastAPI

# 2. Create app instance
app = FastAPI()

# 3. Define routes
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI!"}


@app.get("/")
def home():
    return {"message": "Welcome to my FastAPI Project"}
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# -------------------------------
# Dummy Database
# -------------------------------
menu = []
cart = []
orders = []

# -------------------------------
# Pydantic Models
# -------------------------------
class Item(BaseModel):
    id: int
    name: str = Field(..., min_length=3)
    price: float = Field(..., gt=0)
    category: str

class CartItem(BaseModel):
    item_id: int
    quantity: int = Field(..., gt=0)

# -------------------------------
# Helper Functions
# -------------------------------
def find_item(item_id: int):
    for item in menu:
        if item["id"] == item_id:
            return item
    return None

def calculate_total():
    total = 0
    for c in cart:
        item = find_item(c["item_id"])
        if item:
            total += item["price"] * c["quantity"]
    return total

# -------------------------------
# Day 1 – GET APIs
# -------------------------------
@app.get("/")
def home():
    return {"message": "Food Delivery API Running 🍕"}

@app.get("/menu")
def get_menu():
    return menu

@app.get("/menu/{item_id}")
def get_item(item_id: int):
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/menu-summary")
def summary():
    return {"total_items": len(menu)}

# -------------------------------
# Day 2 – POST
# -------------------------------
@app.post("/menu", status_code=201)
def add_item(item: Item):
    if find_item(item.id):
        raise HTTPException(status_code=400, detail="Item already exists")

    menu.append(item.dict())
    return item

# -------------------------------
# Day 4 – CRUD
# -------------------------------
@app.put("/menu/{item_id}")
def update_item(item_id: int, updated: Item):
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")

    item.update(updated.dict())
    return item

@app.delete("/menu/{item_id}")
def delete_item(item_id: int):
    item = find_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")

    menu.remove(item)
    return {"message": "Deleted successfully"}

# -------------------------------
# Day 5 – Cart Workflow
# -------------------------------
@app.post("/cart")
def add_to_cart(cart_item: CartItem):
    item = find_item(cart_item.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    cart.append(cart_item.dict())
    return {"message": "Added to cart"}

@app.get("/cart")
def view_cart():
    return {
        "cart_items": cart,
        "total": calculate_total()
    }

@app.post("/order")
def place_order():
    if not cart:
        raise HTTPException(status_code=400, detail="Cart is empty")

    order = {
        "order_id": len(orders) + 1,
        "items": cart.copy(),
        "total": calculate_total()
    }

    orders.append(order)
    cart.clear()
    return order

# -------------------------------
# Day 6 – Search + Sort + Pagination
# -------------------------------
@app.get("/search")
def search_items(keyword: str):
    result = [item for item in menu if keyword.lower() in item["name"].lower()]
    if not result:
        return {"message": "No items found"}
    return result

@app.get("/sort")
def sort_items(order: str = "asc"):
    return sorted(menu, key=lambda x: x["price"], reverse=(order=="desc"))

@app.get("/paginate")
def paginate(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    end = start + limit
    return {
        "page": page,
        "items": menu[start:end]
    }