"""
Product service for managing product-related operations.
"""
import os
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from typing import List, Dict, Any, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class ProductService:
    """Service for handling product-related operations."""
    
    def __init__(self, data_service=None):
        """Initialize the product service with optional data service."""
        if data_service:
            self.data_service = data_service
        else:
            # Create a new data service if none is provided
            from services.data_service import DataService
            self.data_service = DataService()
        
        logger.info("ProductService initialized")
    
    def get_product(self, product_id: str) -> Dict[str, Any]:
        """
        Get a product by ID.
        
        Args:
            product_id: ID of the product to retrieve
            
        Returns:
            Dictionary with product information
        """
        try:
            product = self.data_service.get_product(product_id) if hasattr(self.data_service, 'get_product') else {}
            if not product:
                logger.warning(f"Product not found: {product_id}")
                return {}
                
            # Convert to dictionary if it's a model object
            if hasattr(product, 'to_dict'):
                product_dict = product.to_dict()
            else:
                product_dict = product
                
            return product_dict
        except Exception as e:
            logger.error(f"Error getting product {product_id}: {e}")
            return {}
    
    def get_products(self) -> List[Dict[str, Any]]:
        """
        Get all products.
        
        Returns:
            List of product dictionaries
        """
        try:
            products = self.data_service.get_products() if hasattr(self.data_service, 'get_products') else []
            
            # Convert to dictionaries if they're model objects
            result = []
            for product in products:
                if hasattr(product, 'to_dict'):
                    result.append(product.to_dict())
                else:
                    result.append(product)
            
            logger.info(f"Retrieved {len(result)} products")
            return result
        except Exception as e:
            logger.error(f"Error getting products: {e}")
            return []
    
    def get_all_products(self) -> List[Dict[str, Any]]:
        """
        Get all available products.
        
        Returns:
            List of product dictionaries
        """
        try:
            # Try to get products from data service first
            if hasattr(self.data_service, 'get_products'):
                products = self.data_service.get_products()
                if products:
                    result = []
                    for product in products:
                        if hasattr(product, 'to_dict'):
                            result.append(product.to_dict())
                        else:
                            result.append(product)
                    logger.info(f"Retrieved {len(result)} products from data service")
                    return result
            
            # Fallback to default products
            default_products = [
                {'id': 1, 'name': 'Kunststofffenster Standard', 'price': 249.99, 'category': 'Fenster'},
                {'id': 2, 'name': 'Aluminium-Fenster Premium', 'price': 499.99, 'category': 'Fenster'},
                {'id': 3, 'name': 'Holzfenster Natur', 'price': 399.99, 'category': 'Fenster'},
                {'id': 4, 'name': 'Rolllade Standard', 'price': 149.99, 'category': 'Rollladen'},
                {'id': 5, 'name': 'Rolllade Elektrisch', 'price': 299.99, 'category': 'Rollladen'},
                {'id': 6, 'name': 'Insektenschutz', 'price': 89.99, 'category': 'Zubehör'},
                {'id': 7, 'name': 'Fensterbrett innen', 'price': 59.99, 'category': 'Zubehör'},
                {'id': 8, 'name': 'Fensterbrett außen', 'price': 79.99, 'category': 'Zubehör'},
                {'id': 9, 'name': 'Plissee Standard', 'price': 129.99, 'category': 'Sonnenschutz'},
                {'id': 10, 'name': 'Markise Gelenkarm', 'price': 599.99, 'category': 'Sonnenschutz'}
            ]
            logger.info(f"Using default products: {len(default_products)} items")
            return default_products
        except Exception as e:
            logger.error(f"Error getting all products: {e}")
            return []
    
    def save_product(self, product_data: Dict[str, Any]) -> str:
        """
        Save a product (create or update).
        
        Args:
            product_data: Product data to save
            
        Returns:
            Product ID
        """
        try:
            if hasattr(self.data_service, 'save_product'):
                product_id = self.data_service.save_product(product_data)
                logger.info(f"Product saved with ID: {product_id}")
                return product_id
            else:
                logger.warning("save_product method not available in data_service")
                return ""
        except Exception as e:
            logger.error(f"Error saving product: {e}")
            return ""
    
    def delete_product(self, product_id: str) -> bool:
        """
        Delete a product.
        
        Args:
            product_id: ID of the product to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if hasattr(self.data_service, 'delete_product'):
                success = self.data_service.delete_product(product_id)
                if success:
                    logger.info(f"Product deleted: {product_id}")
                else:
                    logger.warning(f"Failed to delete product: {product_id}")
                return success
            else:
                logger.warning("delete_product method not available in data_service")
                return False
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return False