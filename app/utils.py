import os
import pprint
import jwt
import datetime
import logging
from typing import Optional, Dict, Any
from pymongo.collection import Collection
from fastapi import HTTPException, status

from models import Catalog, Product

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
PER_PAGE = 50

# utils.py
def serialize_datetime_fields(item: Dict[str, Any]) -> Dict[str, Any]:
    """Convert all datetime fields in the dictionary to ISO 8601 strings."""
    for key, value in item.items():
        if key == "created_at" or key == "updated_at":
            item[key] = value.isoformat()
    return item

def paginate_and_sort(
    collection: Collection, 
    page: int = 1, 
    per_page: int = PER_PAGE, 
    sort_by: Optional[str] = "created_at", 
    query: Optional[Dict[str, Any]] = None,
    class_type: Optional[str] = "Product"
):
    
    logger.info(f"Paginating and sorting products with query: {query}")
    query = query or {}
    sort_order = -1 if sort_by.startswith("-") else 1
    sort_field = sort_by.lstrip("-")
    
    print("\n\n", page,per_page,sort_by, query )
    if sort_field not in {"name", "created_at", "updated_at"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid sort field."
        )

    skip = (page - 1) * per_page
    
    try:
        cursor = (
            collection.find(query)
            .sort(sort_field, sort_order)
            .skip(skip)
            .limit(per_page)
        )
        if class_type == "Catalog":
            results= [Catalog(**row).dict() for row in cursor]     
        else:
            results= [Product(**row).dict() for row in cursor]    
        total = collection.count_documents(query)
        total_pages = (total + per_page - 1) // per_page

        return {
            "items": results,
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": total_pages
        }
    
    except Exception as e:
        logger.info(f"Error during pagination: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"An error occurred during pagination: {str(e)}"
        )

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_jwt_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }
    logger.info(f"Generating JWT token for user: {user_id}")
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
    return token

def verify_jwt_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
