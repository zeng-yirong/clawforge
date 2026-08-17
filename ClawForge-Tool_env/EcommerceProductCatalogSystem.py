"""
E-commerce Product Catalog System Environment API

An e-commerce product catalog system manages structured data about items available for sale,
including names, categories, prices, and collections. It maintains persistent state and
supports operations like searching, filtering, and retrieving product details.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime


DEFAULT_STATE: Dict[str, Any] = {
    # Products: items available for sale
    "products": {
        "prod_001": {
            "product_id": "prod_001",
            "name": "Wooden Puzzle Box",
            "price": 29.99,
            "category": "Toys > Puzzles",
            "collection_name": "Mysterious Treasures",
            "stock_quantity": 50
        },
        "prod_002": {
            "product_id": "prod_002",
            "name": "Crystal Ball Decoration",
            "price": 45.50,
            "category": "Home Decor",
            "collection_name": "Mysterious Treasures",
            "stock_quantity": 20
        },
        "prod_003": {
            "product_id": "prod_003",
            "name": "Running Shoes Pro",
            "price": 89.99,
            "category": "Sports > Footwear",
            "collection_name": "Summer Athletics",
            "stock_quantity": 100
        },
        "prod_004": {
            "product_id": "prod_004",
            "name": "Organic Green Tea",
            "price": 12.00,
            "category": "Food & Beverages",
            "collection_name": None,
            "stock_quantity": 200
        },
        "prod_005": {
            "product_id": "prod_005",
            "name": "Wireless Headphones",
            "price": 150.00,
            "category": "Electronics > Audio",
            "collection_name": "Tech Essentials",
            "stock_quantity": 0
        }
    },
    
    # Collections: curated groups of products
    "collections": {
        "Mysterious Treasures": {
            "collection_name": "Mysterious Treasures",
            "description": "A curated collection of intriguing and mystical items",
            "product_count": 2
        },
        "Summer Athletics": {
            "collection_name": "Summer Athletics",
            "description": "Sports gear for the summer season",
            "product_count": 1
        },
        "Tech Essentials": {
            "collection_name": "Tech Essentials",
            "description": "Must-have technology products for everyday use",
            "product_count": 1
        }
    },
    
    # Categories: hierarchical classification
    "categories": {
        "Toys": {
            "category_name": "Toys",
            "parent_category": None,
            "description": "Toys and games for all ages"
        },
        "Toys > Puzzles": {
            "category_name": "Toys > Puzzles",
            "parent_category": "Toys",
            "description": "Brain teasers and puzzle games"
        },
        "Home Decor": {
            "category_name": "Home Decor",
            "parent_category": None,
            "description": "Decorative items for home and office"
        },
        "Sports": {
            "category_name": "Sports",
            "parent_category": None,
            "description": "Sports equipment and gear"
        },
        "Sports > Footwear": {
            "category_name": "Sports > Footwear",
            "parent_category": "Sports",
            "description": "Athletic shoes and footwear"
        },
        "Food & Beverages": {
            "category_name": "Food & Beverages",
            "parent_category": None,
            "description": "Food items and drinks"
        },
        "Electronics": {
            "category_name": "Electronics",
            "parent_category": None,
            "description": "Electronic devices and accessories"
        },
        "Electronics > Audio": {
            "category_name": "Electronics > Audio",
            "parent_category": "Electronics",
            "description": "Audio equipment and accessories"
        }
    },
    
    # Session and user context
    "current_user": "admin",
    "session_id": "session_001",
    "last_updated": "2024-01-15T10:00:00"
}


class EcommerceProductCatalogSystem:
    """
    E-commerce Product Catalog System API.
    
    Manages structured data about items available for sale, including names,
    categories, prices, and collections. Supports searching, filtering,
    and retrieving product details.
    """
    
    def __init__(self) -> None:
        """
        Initialize the E-commerce Product Catalog System.
        
        Declares all state attributes with type hints and sets the API description.
        
        Args:
            None
            
        Returns:
            None
        """
        self.products: Dict[str, Dict[str, Any]] = {}
        self.collections: Dict[str, Dict[str, Any]] = {}
        self.categories: Dict[str, Dict[str, Any]] = {}
        self.current_user: str = ""
        self.session_id: str = ""
        self.last_updated: str = ""
        
        self._api_description: str = (
            "E-commerce product catalog system for managing products, collections, "
            "and categories with search and filter capabilities."
        )
    
    def _timestamp(self) -> str:
        """
        Generate a unified ISO format timestamp string.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format.
        """
        return datetime.now().isoformat()
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state values.
            long_context: Flag for long context handling (unused in base implementation).
            
        Returns:
            None
        """
        if not scenario:
            scenario = {}
        for key in DEFAULT_STATE:
            if key in scenario:
                setattr(self, key, deepcopy(scenario[key]))
            else:
                setattr(self, key, deepcopy(DEFAULT_STATE[key]))
    
    def get_env_state(self) -> Dict[str, Any]:
        """
        Return the current environment state as a dictionary.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all internal state variables:
                - products: All products in the catalog
                - collections: All product collections
                - categories: Category hierarchy
                - current_user: Current user identifier
                - session_id: Current session identifier
                - last_updated: Timestamp of last state update
        """
        return {
            "products": deepcopy(self.products),
            "collections": deepcopy(self.collections),
            "categories": deepcopy(self.categories),
            "current_user": self.current_user,
            "session_id": self.session_id,
            "last_updated": self.last_updated
        }
    
    # ==================== Query Operations ====================
    
    def get_collection_by_name(self, collection_name: str) -> Dict[str, Any]:
        """
        Retrieve information about a collection by its unique name.
        
        Args:
            collection_name: The unique name of the collection to retrieve.
            
        Returns:
            Dict[str, Any]: Collection details including description and product count,
                or an error dictionary if collection not found.
        """
        if not isinstance(collection_name, str) or not collection_name:
            return {"error": "Collection name must be a non-empty string"}
        
        if collection_name not in self.collections:
            return {"error": f"Collection '{collection_name}' not found"}
        
        return deepcopy(self.collections[collection_name])
    
    def get_products_by_collection(self, collection_name: str) -> Dict[str, Any]:
        """
        List all products belonging to a specific collection.
        
        Args:
            collection_name: The name of the collection to retrieve products from.
            
        Returns:
            Dict[str, Any]: Dictionary containing list of products in the collection,
                or an error dictionary if collection not found.
        """
        if not isinstance(collection_name, str) or not collection_name:
            return {"error": "Collection name must be a non-empty string"}
        
        if collection_name not in self.collections:
            return {"error": f"Collection '{collection_name}' not found"}
        
        products = [
            deepcopy(p) for p in self.products.values()
            if p.get("collection_name") == collection_name
        ]
        
        return {
            "collection_name": collection_name,
            "products": products,
            "count": len(products)
        }
    
    def get_product_price(self, product_id: str) -> Dict[str, Any]:
        """
        Retrieve the current price of a product by product_id.
        
        Args:
            product_id: The unique identifier of the product.
            
        Returns:
            Dict[str, Any]: Dictionary containing product_id and price,
                or an error dictionary if product not found.
        """
        if not isinstance(product_id, str) or not product_id:
            return {"error": "Product ID must be a non-empty string"}
        
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
        
        product = self.products[product_id]
        return {
            "product_id": product_id,
            "name": product["name"],
            "price": product["price"]
        }
    
    def get_product_by_id(self, product_id: str) -> Dict[str, Any]:
        """
        Retrieve full details of a product by its unique product_id.
        
        Args:
            product_id: The unique identifier of the product.
            
        Returns:
            Dict[str, Any]: Full product details or an error dictionary if not found.
        """
        if not isinstance(product_id, str) or not product_id:
            return {"error": "Product ID must be a non-empty string"}
        
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
        
        return deepcopy(self.products[product_id])
    
    def get_product_by_name(self, name: str) -> Dict[str, Any]:
        """
        Search for products by name (may return multiple if not unique).
        
        Args:
            name: The product name to search for (case-insensitive partial match).
            
        Returns:
            Dict[str, Any]: Dictionary containing list of matching products.
        """
        if not isinstance(name, str) or not name:
            return {"error": "Product name must be a non-empty string"}
        
        matching_products = [
            deepcopy(p) for p in self.products.values()
            if name.lower() in p["name"].lower()
        ]
        
        return {
            "search_term": name,
            "products": matching_products,
            "count": len(matching_products)
        }
    
    def list_all_products(self) -> Dict[str, Any]:
        """
        List all products in the catalog.
        
        Args:
            None
            
        Returns:
            Dict[str, Any]: Dictionary containing list of all products.
        """
        products = [deepcopy(p) for p in self.products.values()]
        return {
            "products": products,
            "count": len(products)
        }
    
    def list_products_by_category(self, category_name: str) -> Dict[str, Any]:
        """
        Retrieve all products under a given category or subcategory.
        
        Args:
            category_name: The category name to filter products by.
            
        Returns:
            Dict[str, Any]: Dictionary containing list of products in the category,
                or an error dictionary if category not found.
        """
        if not isinstance(category_name, str) or not category_name:
            return {"error": "Category name must be a non-empty string"}
        
        if category_name not in self.categories:
            return {"error": f"Category '{category_name}' not found"}
        
        # Include products in this category and all subcategories
        products = [
            deepcopy(p) for p in self.products.values()
            if p["category"] == category_name or p["category"].startswith(category_name + " > ")
        ]
        
        return {
            "category": category_name,
            "products": products,
            "count": len(products)
        }
    
    def get_category_hierarchy(self, category_name: str) -> Dict[str, Any]:
        """
        Retrieve the parent-child structure of a category.
        
        Args:
            category_name: The category name to get hierarchy for.
            
        Returns:
            Dict[str, Any]: Dictionary containing category hierarchy information,
                or an error dictionary if category not found.
        """
        if not isinstance(category_name, str) or not category_name:
            return {"error": "Category name must be a non-empty string"}
        
        if category_name not in self.categories:
            return {"error": f"Category '{category_name}' not found"}
        
        category = self.categories[category_name]
        
        # Build hierarchy path
        hierarchy = [category_name]
        current = category
        while current.get("parent_category"):
            parent_name = current["parent_category"]
            hierarchy.insert(0, parent_name)
            current = self.categories.get(parent_name, {})
        
        # Find children
        children = [
            cat["category_name"] for cat in self.categories.values()
            if cat.get("parent_category") == category_name
        ]
        
        return {
            "category_name": category_name,
            "hierarchy_path": hierarchy,
            "parent": category.get("parent_category"),
            "children": children,
            "description": category["description"]
        }
    
    def list_all_categories(self) -> Dict[str, Any]:
        """
        Retrieve all available categories and their descriptions.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing list of all categories.
        """
        categories = [
            {
                "category_name": cat["category_name"],
                "parent_category": cat.get("parent_category"),
                "description": cat["description"]
            }
            for cat in self.categories.values()
        ]
        
        return {
            "categories": categories,
            "count": len(categories)
        }
    
    def list_all_collections(self) -> Dict[str, Any]:
        """
        Retrieve names and basic info of all available collections.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing list of all collections.
        """
        collections = [
            deepcopy(col) for col in self.collections.values()
        ]
        
        return {
            "collections": collections,
            "count": len(collections)
        }
    
    def get_products_by_price_range(self, min_price: float, max_price: float) -> Dict[str, Any]:
        """
        Get products within a specific price range.
        
        Args:
            min_price: Minimum price.
            max_price: Maximum price.
            
        Returns:
            Dict[str, Any]: Dictionary containing list of products in the price range.
        """
        if not isinstance(min_price, (int, float)) or not isinstance(max_price, (int, float)):
            return {"error": "Prices must be numbers"}
            
        if min_price < 0 or max_price < 0:
            return {"error": "Prices must be non-negative"}
            
        if min_price > max_price:
            return {"error": "Minimum price cannot be greater than maximum price"}
            
        results = [
            deepcopy(p) for p in self.products.values()
            if min_price <= p["price"] <= max_price
        ]
        
        return {
            "products": results,
            "count": len(results)
        }
    
    def search_products(
        self,
        name: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Search products by name, category, price range, or stock availability.
        
        Args:
            name: Optional product name to search for (case-insensitive partial match).
            category: Optional category to filter by.
            min_price: Optional minimum price filter.
            max_price: Optional maximum price filter.
            in_stock: Optional boolean to filter by stock availability.
            
        Returns:
            Dict[str, Any]: Dictionary containing list of matching products.
        """
        results = list(self.products.values())
        
        # Filter by name
        if name is not None:
            if not isinstance(name, str):
                return {"error": "Name filter must be a string"}
            results = [p for p in results if name.lower() in p["name"].lower()]
        
        # Filter by category
        if category is not None:
            if not isinstance(category, str):
                return {"error": "Category filter must be a string"}
            results = [
                p for p in results
                if p["category"] == category or p["category"].startswith(category + " > ")
            ]
        
        # Filter by min price
        if min_price is not None:
            if not isinstance(min_price, (int, float)):
                return {"error": "Min price must be a number"}
            results = [p for p in results if p["price"] >= min_price]
        
        # Filter by max price
        if max_price is not None:
            if not isinstance(max_price, (int, float)):
                return {"error": "Max price must be a number"}
            results = [p for p in results if p["price"] <= max_price]
            
        # Filter by in_stock
        if in_stock is not None:
            if not isinstance(in_stock, bool):
                return {"error": "in_stock filter must be a boolean"}
            if in_stock:
                results = [p for p in results if p.get("stock_quantity", 0) > 0]
            else:
                results = [p for p in results if p.get("stock_quantity", 0) <= 0]
        
        return {
            "filters": {
                "name": name,
                "category": category,
                "min_price": min_price,
                "max_price": max_price,
                "in_stock": in_stock
            },
            "products": [deepcopy(p) for p in results],
            "count": len(results)
        }
    
    # ==================== State Change Operations ====================
    
    def add_product_to_collection(
        self,
        product_id: str,
        collection_name: str
    ) -> Dict[str, Any]:
        """
        Assign a product to a collection, ensuring it belongs to at most one collection.
        
        Args:
            product_id: The unique identifier of the product.
            collection_name: The name of the collection to add the product to.
            
        Returns:
            Dict[str, Any]: Success status or error dictionary.
        """
        # Validate inputs
        if not isinstance(product_id, str) or not product_id:
            return {"error": "Product ID must be a non-empty string"}
        
        if not isinstance(collection_name, str) or not collection_name:
            return {"error": "Collection name must be a non-empty string"}
        
        # Validate product exists
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
        
        # Validate collection exists
        if collection_name not in self.collections:
            return {"error": f"Collection '{collection_name}' not found"}
        
        product = self.products[product_id]
        old_collection = product.get("collection_name")
        
        # Check if already in the same collection
        if old_collection == collection_name:
            return {"error": f"Product is already in collection '{collection_name}'"}
        
        # Remove from old collection if applicable
        if old_collection and old_collection in self.collections:
            self.collections[old_collection]["product_count"] -= 1
        
        # Add to new collection
        product["collection_name"] = collection_name
        self.collections[collection_name]["product_count"] += 1
        self.last_updated = self._timestamp()
        
        return {
            "success": True,
            "product_id": product_id,
            "collection_name": collection_name,
            "message": f"Product '{product['name']}' added to collection '{collection_name}'"
        }
    
    def remove_product_from_collection(self, product_id: str) -> Dict[str, Any]:
        """
        Remove a product's association with its current collection.
        
        Args:
            product_id: The unique identifier of the product.
            
        Returns:
            Dict[str, Any]: Success status or error dictionary.
        """
        if not isinstance(product_id, str) or not product_id:
            return {"error": "Product ID must be a non-empty string"}
        
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
        
        product = self.products[product_id]
        collection_name = product.get("collection_name")
        
        if not collection_name:
            return {"error": "Product is not in any collection"}
        
        # Update collection count
        if collection_name in self.collections:
            self.collections[collection_name]["product_count"] -= 1
        
        product["collection_name"] = None
        self.last_updated = self._timestamp()
        
        return {
            "success": True,
            "product_id": product_id,
            "removed_from": collection_name,
            "message": f"Product '{product['name']}' removed from collection '{collection_name}'"
        }
    
    def update_product_price(
        self,
        product_id: str,
        new_price: float
    ) -> Dict[str, Any]:
        """
        Modify the price of a product, ensuring the new price is non-negative.
        
        Args:
            product_id: The unique identifier of the product.
            new_price: The new price to set (must be non-negative).
            
        Returns:
            Dict[str, Any]: Success status with old and new prices, or error dictionary.
        """
        if not isinstance(product_id, str) or not product_id:
            return {"error": "Product ID must be a non-empty string"}
        
        if not isinstance(new_price, (int, float)):
            return {"error": "New price must be a number"}
        
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
        
        # Validate non-negative price
        if new_price < 0:
            return {"error": "Product price must be non-negative"}
        
        product = self.products[product_id]
        old_price = product["price"]
        product["price"] = float(new_price)
        self.last_updated = self._timestamp()
        
        return {
            "success": True,
            "product_id": product_id,
            "name": product["name"],
            "old_price": old_price,
            "new_price": product["price"]
        }
    
    def update_product_stock(self, product_id: str, quantity: int) -> Dict[str, Any]:
        """
        Update the stock quantity of a product.
        
        Args:
            product_id: The unique identifier of the product.
            quantity: The new stock quantity (must be non-negative).
            
        Returns:
            Dict[str, Any]: Success status or error dictionary.
        """
        if not isinstance(product_id, str) or not product_id:
            return {"error": "Product ID must be a non-empty string"}
            
        if not isinstance(quantity, int) or quantity < 0:
            return {"error": "Stock quantity must be a non-negative integer"}
            
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
            
        self.products[product_id]["stock_quantity"] = quantity
        self.last_updated = self._timestamp()
        
        return {
            "success": True,
            "product_id": product_id,
            "stock_quantity": quantity,
            "message": f"Stock updated successfully for product '{product_id}'"
        }
    
    def update_product_category(
        self,
        product_id: str,
        new_category: str
    ) -> Dict[str, Any]:
        """
        Change the category of a product, validating it against existing categories.
        
        Args:
            product_id: The unique identifier of the product.
            new_category: The new category to assign (must exist in categories).
            
        Returns:
            Dict[str, Any]: Success status with old and new categories, or error dictionary.
        """
        if not isinstance(product_id, str) or not product_id:
            return {"error": "Product ID must be a non-empty string"}
        
        if not isinstance(new_category, str) or not new_category:
            return {"error": "New category must be a non-empty string"}
        
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
        
        if new_category not in self.categories:
            return {"error": f"Category '{new_category}' does not exist"}
        
        product = self.products[product_id]
        old_category = product["category"]
        product["category"] = new_category
        self.last_updated = self._timestamp()
        
        return {
            "success": True,
            "product_id": product_id,
            "name": product["name"],
            "old_category": old_category,
            "new_category": new_category
        }
    
    def create_subcategory(
        self,
        category_name: str,
        parent_category: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Add a new subcategory under an existing parent category.
        
        Args:
            category_name: The name for the new subcategory.
            parent_category: The existing parent category name.
            description: Description of the new subcategory.
            
        Returns:
            Dict[str, Any]: Success status or error dictionary.
        """
        if not isinstance(category_name, str) or not category_name:
            return {"error": "Category name must be a non-empty string"}
        
        if not isinstance(parent_category, str) or not parent_category:
            return {"error": "Parent category must be a non-empty string"}
        
        if not isinstance(description, str):
            return {"error": "Description must be a string"}
        
        if parent_category not in self.categories:
            return {"error": f"Parent category '{parent_category}' does not exist"}
        
        # Build full category name (hierarchical)
        full_name = f"{parent_category} > {category_name}"
        
        if full_name in self.categories:
            return {"error": f"Subcategory '{full_name}' already exists"}
        
        self.categories[full_name] = {
            "category_name": full_name,
            "parent_category": parent_category,
            "description": description
        }
        self.last_updated = self._timestamp()
        
        return {
            "success": True,
            "category_name": full_name,
            "parent_category": parent_category,
            "description": description
        }
    
    def bulk_update_prices(
        self,
        category: str,
        percentage_change: float
    ) -> Dict[str, Any]:
        """
        Bulk update prices for all products in a category and its subcategories.
        
        Args:
            category: The category name to filter products by.
            percentage_change: Percentage to change prices (positive for increase, negative for decrease).
            
        Returns:
            Dict[str, Any]: Summary of updated products.
        """
        if not isinstance(category, str) or not category:
            return {"error": "Category must be a non-empty string"}
            
        if not isinstance(percentage_change, (int, float)):
            return {"error": "Percentage change must be a number"}
            
        if category not in self.categories:
            return {"error": f"Category '{category}' not found"}
            
        updated_count = 0
        updated_products = []
        
        for product_id, product in self.products.items():
            if product["category"] == category or product["category"].startswith(category + " > "):
                old_price = product["price"]
                new_price = old_price * (1 + percentage_change / 100.0)
                new_price = max(0.0, round(new_price, 2))
                
                product["price"] = new_price
                updated_products.append({
                    "product_id": product_id,
                    "old_price": old_price,
                    "new_price": new_price
                })
                updated_count += 1
                
        if updated_count > 0:
            self.last_updated = self._timestamp()
            
        return {
            "success": True,
            "category": category,
            "updated_count": updated_count,
            "updated_products": updated_products
        }
    
    def bulk_add_products_to_collection(
        self,
        product_ids: List[str],
        collection_name: str
    ) -> Dict[str, Any]:
        """
        Add multiple products to a collection, with validation for each.
        
        Args:
            product_ids: List of product IDs to add to the collection.
            collection_name: The name of the collection to add products to.
            
        Returns:
            Dict[str, Any]: Summary of successful and failed additions.
        """
        if not isinstance(collection_name, str) or not collection_name:
            return {"error": "Collection name must be a non-empty string"}
        
        if not isinstance(product_ids, list):
            return {"error": "Product IDs must be a list"}
        
        if collection_name not in self.collections:
            return {"error": f"Collection '{collection_name}' not found"}
        
        if not product_ids:
            return {"error": "No product IDs provided"}
        
        successful = []
        failed = []
        
        for product_id in product_ids:
            result = self.add_product_to_collection(product_id, collection_name)
            if "error" in result:
                failed.append({"product_id": product_id, "reason": result["error"]})
            else:
                successful.append(product_id)
        
        return {
            "success": len(failed) == 0,
            "collection_name": collection_name,
            "successful_count": len(successful),
            "successful": successful,
            "failed_count": len(failed),
            "failed": failed
        }
    
    def delete_product(self, product_id: str) -> Dict[str, Any]:
        """
        Remove a product from the catalog (admin-level operation).
        
        Args:
            product_id: The unique identifier of the product to delete.
            
        Returns:
            Dict[str, Any]: Success status or error dictionary.
        """
        if not isinstance(product_id, str) or not product_id:
            return {"error": "Product ID must be a non-empty string"}
        
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
        
        product = self.products[product_id]
        collection_name = product.get("collection_name")
        
        # Update collection count if product was in a collection
        if collection_name and collection_name in self.collections:
            self.collections[collection_name]["product_count"] -= 1
        
        deleted_product = deepcopy(product)
        del self.products[product_id]
        self.last_updated = self._timestamp()
        
        return {
            "success": True,
            "deleted_product": deleted_product,
            "message": f"Product '{deleted_product['name']}' has been deleted"
        }
    
    def create_category(
        self,
        category_name: str,
        description: str,
        parent_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new top-level or nested category to the hierarchy.
        
        Args:
            category_name: The name for the new category.
            description: Description of the new category.
            parent_category: Optional parent category for nested categories.
            
        Returns:
            Dict[str, Any]: Success status or error dictionary.
        """
        if not isinstance(category_name, str) or not category_name:
            return {"error": "Category name must be a non-empty string"}
        
        if not isinstance(description, str):
            return {"error": "Description must be a string"}
        
        # If parent is provided, validate it exists and build full name
        if parent_category is not None:
            if not isinstance(parent_category, str) or not parent_category:
                return {"error": "Parent category must be a non-empty string"}
            if parent_category not in self.categories:
                return {"error": f"Parent category '{parent_category}' does not exist"}
            full_name = f"{parent_category} > {category_name}"
        else:
            full_name = category_name
        
        if full_name in self.categories:
            return {"error": f"Category '{full_name}' already exists"}
        
        self.categories[full_name] = {
            "category_name": full_name,
            "parent_category": parent_category,
            "description": description
        }
        self.last_updated = self._timestamp()
        
        return {
            "success": True,
            "category_name": full_name,
            "parent_category": parent_category,
            "description": description
        }


__TEST_CASES__ = [
    {
        "name": "Search and update product price flow",
        "steps": [
            {"tool_call": "get_product_by_id(product_id='prod_001')", "expect_success": True},
            {"tool_call": "get_product_price(product_id='prod_001')", "expect_success": True},
            {"tool_call": "update_product_price(product_id='prod_001', new_price=34.99)", "expect_success": True},
            {"tool_call": "get_product_price(product_id='prod_001')", "expect_success": True}
        ]
    },
    {
        "name": "Error handling - invalid operations",
        "steps": [
            {"tool_call": "get_product_by_id(product_id='invalid_id')", "expect_success": False},
            {"tool_call": "update_product_price(product_id='prod_001', new_price=-10.00)", "expect_success": False},
            {"tool_call": "add_product_to_collection(product_id='prod_001', collection_name='NonExistent')", "expect_success": False},
            {"tool_call": "update_product_category(product_id='prod_001', new_category='Invalid Category')", "expect_success": False},
            {"tool_call": "remove_product_from_collection(product_id='prod_004')", "expect_success": False}
        ]
    },
    {
        "name": "Product search and filtering",
        "steps": [
            {"tool_call": "search_products(name='Puzzle')", "expect_success": True},
            {"tool_call": "search_products(category='Electronics')", "expect_success": True},
            {"tool_call": "search_products(min_price=50.00, max_price=200.00)", "expect_success": True},
            {"tool_call": "search_products(name='Smart', category='Electronics', in_stock=True)", "expect_success": True},
            {"tool_call": "get_products_by_price_range(min_price=0, max_price=50)", "expect_success": True}
        ]
    },
    {
        "name": "Inventory management",
        "steps": [
            {"tool_call": "get_product_by_id(product_id='prod_002')", "expect_success": True},
            {"tool_call": "update_product_stock(product_id='prod_002', quantity=100)", "expect_success": True},
            {"tool_call": "get_product_by_id(product_id='prod_002')", "expect_success": True},
            {"tool_call": "update_product_stock(product_id='prod_002', quantity=0)", "expect_success": True},
            {"tool_call": "search_products(in_stock=False)", "expect_success": True}
        ]
    },
    {
        "name": "Bulk operations",
        "steps": [
            {"tool_call": "list_all_products()", "expect_success": True},
            {"tool_call": "bulk_update_prices(category='Electronics', percentage_change=10.0)", "expect_success": True},
            {"tool_call": "list_all_products()", "expect_success": True},
            {"tool_call": "bulk_update_prices(category='Toys', percentage_change=-5.0)", "expect_success": True}
        ]
    }
]