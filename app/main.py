
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from . import models, schemas, crud
from .database import engine
from .dependencies import get_db
from typing import List, Optional
from datetime import date as dt_date

# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Expense Tracker API!"}

# Category endpoints
@app.get("/categories", response_model=list[schemas.Category])
def read_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_categories(db, skip=skip, limit=limit)

@app.post("/categories", response_model=schemas.Category)
def create_category(category: schemas.CategoryCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Category).filter(models.Category.name == category.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="Category with this name already exists.")
    try:
        return crud.create_category(db=db, category=category, user_id=None)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")

@app.get("/categories/{category_id}", response_model=schemas.Category)
def read_category(category_id: int, db: Session = Depends(get_db)):
    db_category = crud.get_category(db, category_id=category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@app.put("/categories/{category_id}", response_model=schemas.Category)
def update_category(category_id: int, category_update: schemas.CategoryUpdate, db: Session = Depends(get_db)):
    try:
        db_category = crud.update_category(db, category_id=category_id, category_update=category_update)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

@app.delete("/categories/{category_id}", response_model=schemas.Category)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    try:
        db_category = crud.delete_category(db, category_id=category_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    if db_category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return db_category

# Expense endpoints
@app.get("/expenses")
def read_expenses(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    category_id: Optional[int] = None,
    date_from: Optional[dt_date] = None,
    date_to: Optional[dt_date] = None,
    db: Session = Depends(get_db),
    request: Request = None
):
    query = db.query(models.Expense)
    if user_id is not None:
        query = query.filter(models.Expense.user_id == user_id)
    if category_id is not None:
        query = query.filter(models.Expense.category_id == category_id)
    if date_from is not None:
        query = query.filter(models.Expense.date >= date_from)
    if date_to is not None:
        query = query.filter(models.Expense.date <= date_to)
    total = query.count()
    expenses = query.offset(skip).limit(limit).all()
    base_url = str(request.url).split('?')[0] if request else ''
    def build_link(new_skip):
        params = []
        if user_id is not None:
            params.append(f'user_id={user_id}')
        if category_id is not None:
            params.append(f'category_id={category_id}')
        if date_from is not None:
            params.append(f'date_from={date_from}')
        if date_to is not None:
            params.append(f'date_to={date_to}')
        params.append(f'skip={new_skip}')
        params.append(f'limit={limit}')
        return base_url + '?' + '&'.join(params)
    next_link = build_link(skip + limit) if skip + limit < total else None
    prev_link = build_link(max(skip - limit, 0)) if skip > 0 else None
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "next": next_link,
        "prev": prev_link,
        "items": expenses
    }

