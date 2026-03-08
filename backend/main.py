from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .database import init_db, SessionLocal, Product, PriceHistory
from .scraper import scrape_coupang
from .scheduler import start_scheduler
from pydantic import BaseModel
import os

# Initialize Database
init_db()

# Start Scheduler
start_scheduler()

app = FastAPI(title="Coupang Price Bot API")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ProductCreate(BaseModel):
    url: str

@app.get("/api/products")
def list_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.post("/api/products")
def add_product(item: ProductCreate, db: Session = Depends(get_db)):
    # Check if exists
    existing = db.query(Product).filter(Product.url == item.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Product already registered")
    
    # Scrape initial data
    result = scrape_coupang(item.url)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=f"Failed to fetch product data: {result.get('error')}")
    
    new_product = Product(
        url=item.url,
        name=result["name"],
        thumbnail=result["thumbnail"],
        current_price=result["price"]
    )
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    # Save initial history
    history = PriceHistory(product_id=new_product.id, price=result["price"])
    db.add(history)
    db.commit()
    
    return new_product

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(product)
    db.commit()
    return {"message": "Deleted successfully"}

@app.get("/api/history/{product_id}")
def get_history(product_id: int, db: Session = Depends(get_db)):
    return db.query(PriceHistory).filter(PriceHistory.product_id == product_id).order_by(PriceHistory.timestamp.desc()).all()

@app.post("/api/scan-now")
async def scan_now(db: Session = Depends(get_db)):
    """Manually trigger a price check scan."""
    from .scheduler import check_prices
    import threading
    # Run in a separate thread to avoid blocking FastAPI
    thread = threading.Thread(target=check_prices)
    thread.start()
    return {"message": "전체 스캔이 시작되었습니다. 잠시 후 텔레그램을 확인해주세요."}

# Serve Frontend
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
