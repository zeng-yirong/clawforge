"""
E-commerce Product Inventory System Environment API

An e-commerce product inventory system that organizes information about merchandise
available for sale on a website. It tracks essential product attributes such as
descriptions, quantities, categories, prices, and stock status.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime


DEFAULT_STATE: Dict[str, Any] = {
    "products": {
        "prod_001": {
            "product_id": "prod_001",
            "name": "Wireless Bluetooth Headphones",
            "description": "High-quality wireless headphones with noise cancellation",
            "category": "Electronics",
            "price": 79.99,
            "stock_status": "in stock",
            "quantity_in_stock": 150
        },
        "prod_002": {
            "product_id": "prod_002",
            "name": "Yoga Mat Premium",
            "description": "Non-slip yoga mat with carrying strap, 6mm thick",
            "category": "Fitness Equipment",
            "price": 34.99,
            "stock_status": "in stock",
            "quantity_in_stock": 75
        },
        "prod_003": {
            "product_id": "prod_003",
            "name": "Stainless Steel Water Bottle",
            "description": "Insulated water bottle, keeps drinks cold for 24 hours",
            "category": "Kitchen",
            "price": 24.99,
            "stock_status": "in stock",
            "quantity_in_stock": 200
        },
        "prod_004": {
            "product_id": "prod_004",
            "name": "Running Shoes Pro",
            "description": "Lightweight running shoes with cushioned sole",
            "category": "Fitness Equipment",
            "price": 129.99,
            "stock_status": "out of stock",
            "quantity_in_stock": 0
        },
        "prod_005": {
            "product_id": "prod_005",
            "name": "Organic Green Tea",
            "description": "Premium organic green tea, 100 tea bags",
            "category": "Food & Beverages",
            "price": 18.50,
            "stock_status": "in stock",
            "quantity_in_stock": 500
        }
    },
    "categories": {
        "cat_001": {
            "category_id": "cat_001",
            "name": "Electronics",
            "parent_category": None,
            "is_active": True
        },
        "cat_002": {
            "category_id": "cat_002",
            "name": "Fitness Equipment",
            "parent_category": None,
            "is_active": True
        },
        "cat_003": {
            "category_id": "cat_003",
            "name": "Kitchen",
            "parent_category": None,
            "is_active": True
        },
        "cat_004": {
            "category_id": "cat_004",
            "name": "Food & Beverages",
            "parent_category": None,
            "is_active": True
        },
        "cat_005": {
            "category_id": "cat_005",
            "name": "Audio Devices",
            "parent_category": "Electronics",
            "is_active": True
        }
    },
    "next_product_id": 6,
    "next_category_id": 6
}


class EcommerceProductInventorySystem:
    """
    E-commerce Product Inventory System API.
    
    This class provides methods to manage product inventory for an e-commerce platform,
    including operations for searching, filtering, updating inventory, and managing
    product categories.
    """
    
    def __init__(self) -> None:
        """
        Initialize the E-commerce Product Inventory System.
        
        Declares all state attributes with type hints and sets up the API description.
        
        Args:
            None
            
        Returns:
            None
        """
        self.products: Dict[str, Dict[str, Any]] = {}
        self.categories: Dict[str, Dict[str, Any]] = {}
        self.next_product_id: int = 1
        self.next_category_id: int = 1
        
        self._api_description: str = (
            "E-commerce product inventory management system for tracking merchandise, "
            "managing stock levels, and organizing products by categories."
        )
    
    def _timestamp(self) -> str:
        """
        Generate a unified timestamp string.
        
        Args:
            None
        
        Returns:
            str: ISO format timestamp string.
        """
        return datetime.now().isoformat()
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing initial state values.
            long_context: Flag for long context scenarios (unused in base implementation).
        
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
        Get the current state of the environment.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing all current environment state variables:
                - products: Dict of all products keyed by product_id
                - categories: Dict of all categories keyed by category_id
                - next_product_id: Counter for generating new product IDs
                - next_category_id: Counter for generating new category IDs
        """
        return {
            "products": deepcopy(self.products),
            "categories": deepcopy(self.categories),
            "next_product_id": self.next_product_id,
            "next_category_id": self.next_category_id
        }
    
    def _get_valid_category_names(self) -> List[str]:
        """
        Get list of valid active category names.
        
        Args:
            None
        
        Returns:
            List[str]: List of active category names.
        """
        return [
            cat["name"] for cat in self.categories.values()
            if cat.get("is_active", True)
        ]
    
    def _is_valid_category(self, category_name: str) -> bool:
        """
        Check if a category name is valid and active.
        
        Args:
            category_name: The category name to validate.
            
        Returns:
            bool: True if the category exists and is active.
        """
        return category_name in self._get_valid_category_names()
    
    # ==================== Query Operations ====================
    
    def get_product_by_id(self, product_id: str) -> Dict[str, Any]:
        """
        Retrieve full details of a product using its unique product_id.
        
        Args:
            product_id: The unique identifier of the product.
            
        Returns:
            Dict[str, Any]: Product details if found, or error dictionary if not found.
        """
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
        
        return {"product": deepcopy(self.products[product_id])}
    
    def list_all_products(self) -> Dict[str, Any]:
        """
        Return a list of all products in the inventory regardless of status.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing list of all products and total count.
        """
        products_list = list(deepcopy(self.products).values())
        return {
            "products": products_list,
            "total_count": len(products_list)
        }
    
    def search_products_by_name(self, keyword: str) -> Dict[str, Any]:
        """
        Find products whose names match a given keyword or substring.
        
        Args:
            keyword: The search keyword to match against product names (case-insensitive).
            
        Returns:
            Dict[str, Any]: Dictionary containing matching products and count.
        """
        if not keyword or not keyword.strip():
            return {"error": "Search keyword cannot be empty"}
        
        keyword_lower = keyword.lower().strip()
        matching_products = [
            deepcopy(product)
            for product in self.products.values()
            if keyword_lower in product["name"].lower()
        ]
        
        return {
            "products": matching_products,
            "match_count": len(matching_products),
            "search_keyword": keyword
        }
    
    def filter_products_by_category(self, category: str) -> Dict[str, Any]:
        """
        Retrieve all products belonging to a specified category.
        
        Args:
            category: The category name to filter by.
            
        Returns:
            Dict[str, Any]: Dictionary containing products in the category and count.
        """
        if not category or not category.strip():
            return {"error": "Category name cannot be empty"}
        
        filtered_products = [
            deepcopy(product)
            for product in self.products.values()
            if product["category"] == category
        ]
        
        return {
            "products": filtered_products,
            "category": category,
            "count": len(filtered_products)
        }
    
    def get_available_products(self) -> Dict[str, Any]:
        """
        List products that are available for purchase.
        
        Products are available if stock_status = "in stock" and quantity_in_stock > 0.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing available products and count.
        """
        available_products = [
            deepcopy(product)
            for product in self.products.values()
            if product["stock_status"] == "in stock" and product["quantity_in_stock"] > 0
        ]
        
        return {
            "products": available_products,
            "available_count": len(available_products)
        }
    
    def filter_products_by_price_range(
        self, 
        min_price: float, 
        max_price: float
    ) -> Dict[str, Any]:
        """
        Retrieve products with prices within a specified range.
        
        Args:
            min_price: Minimum price (inclusive).
            max_price: Maximum price (inclusive).
            
        Returns:
            Dict[str, Any]: Dictionary containing filtered products and count.
        """
        if min_price < 0:
            return {"error": "Minimum price cannot be negative"}
        if max_price < 0:
            return {"error": "Maximum price cannot be negative"}
        if min_price > max_price:
            return {"error": "Minimum price cannot be greater than maximum price"}
        
        filtered_products = [
            deepcopy(product)
            for product in self.products.values()
            if min_price <= product["price"] <= max_price
        ]
        
        return {
            "products": filtered_products,
            "price_range": {"min": min_price, "max": max_price},
            "count": len(filtered_products)
        }
    
    def get_product_availability_status(self, product_id: str) -> Dict[str, Any]:
        """
        Check whether a specific product is currently available for purchase.
        
        Args:
            product_id: The unique identifier of the product.
            
        Returns:
            Dict[str, Any]: Availability status information or error if not found.
        """
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
        
        product = self.products[product_id]
        is_available = (
            product["stock_status"] == "in stock" and 
            product["quantity_in_stock"] > 0
        )
        
        return {
            "product_id": product_id,
            "product_name": product["name"],
            "is_available": is_available,
            "stock_status": product["stock_status"],
            "quantity_in_stock": product["quantity_in_stock"]
        }
    
    def list_all_categories(self) -> Dict[str, Any]:
        """
        Retrieve all predefined categories in the system.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: Dictionary containing all categories and total count.
        """
        categories_list = list(deepcopy(self.categories).values())
        return {
            "categories": categories_list,
            "total_count": len(categories_list)
        }
    
    def get_category_info(
        self, 
        category_id: Optional[str] = None, 
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve information about a specific category by category_id or name.
        
        Args:
            category_id: The unique identifier of the category (optional).
            name: The name of the category (optional).
            
        Returns:
            Dict[str, Any]: Category information or error if not found.
        """
        if not category_id and not name:
            return {"error": "Either category_id or name must be provided"}
        
        if category_id:
            if category_id in self.categories:
                return {"category": deepcopy(self.categories[category_id])}
            return {"error": f"Category with ID '{category_id}' not found"}
        
        for cat in self.categories.values():
            if cat["name"] == name:
                return {"category": deepcopy(cat)}
        
        return {"error": f"Category with name '{name}' not found"}
    
    def count_products_in_category(self, category: str) -> Dict[str, Any]:
        """
        Return the number of products in a given category.
        
        Args:
            category: The category name to count products for.
            
        Returns:
            Dict[str, Any]: Dictionary containing category name and product count.
        """
        if not category or not category.strip():
            return {"error": "Category name cannot be empty"}
        
        count = sum(
            1 for product in self.products.values()
            if product["category"] == category
        )
        
        return {
            "category": category,
            "product_count": count
        }
    
    # ==================== State Change Operations ====================
    
    def add_new_product(
        self,
        name: str,
        category: str,
        price: float,
        description: str = "",
        quantity_in_stock: int = 0,
        stock_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new product to inventory after validating required fields.
        
        Validates that name and category are provided, price >= 0, and category is valid.
        
        Args:
            name: Product name (required).
            category: Product category (required, must be predefined).
            price: Product price (must be non-negative).
            description: Product description (optional).
            quantity_in_stock: Initial stock quantity (default 0).
            stock_status: Stock status (auto-determined if not provided).
            
        Returns:
            Dict[str, Any]: Success status with new product details or error.
        """
        # Validate required fields
        if not name or not name.strip():
            return {"error": "Product name is required"}
        if not category or not category.strip():
            return {"error": "Product category is required"}
        
        # Validate price
        if price < 0:
            return {"error": "Price must be a non-negative value"}
        
        # Validate category
        if not self._is_valid_category(category):
            return {"error": f"Category '{category}' is not a valid predefined category"}
        
        # Validate quantity
        if quantity_in_stock < 0:
            return {"error": "Quantity in stock cannot be negative"}
        
        # Auto-determine stock status if not provided
        if stock_status is None:
            stock_status = "in stock" if quantity_in_stock > 0 else "out of stock"
        elif stock_status not in ["in stock", "out of stock"]:
            return {"error": "Stock status must be 'in stock' or 'out of stock'"}
        
        # Generate new product ID
        product_id = f"prod_{self.next_product_id:03d}"
        self.next_product_id += 1
        
        # Create new product
        new_product = {
            "product_id": product_id,
            "name": name.strip(),
            "description": description,
            "category": category,
            "price": price,
            "stock_status": stock_status,
            "quantity_in_stock": quantity_in_stock
        }
        
        self.products[product_id] = new_product
        
        return {
            "success": True,
            "message": "Product added successfully",
            "product": deepcopy(new_product)
        }
    
    def update_product_price(
        self, 
        product_id: str, 
        new_price: float
    ) -> Dict[str, Any]:
        """
        Modify the price of an existing product.
        
        Args:
            product_id: The unique identifier of the product.
            new_price: The new price (must be non-negative).
            
        Returns:
            Dict[str, Any]: Success status with updated product or error.
        """
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
        
        if new_price < 0:
            return {"error": "Price must be a non-negative value"}
        
        old_price = self.products[product_id]["price"]
        self.products[product_id]["price"] = new_price
        
        return {
            "success": True,
            "message": "Product price updated successfully",
            "product_id": product_id,
            "old_price": old_price,
            "new_price": new_price
        }
    
    def update_product_stock(
        self,
        product_id: str,
        quantity_in_stock: Optional[int] = None,
        stock_status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the quantity_in_stock and/or stock_status of a product.
        
        Args:
            product_id: The unique identifier of the product.
            quantity_in_stock: New stock quantity (optional).
            stock_status: New stock status (optional).
            
        Returns:
            Dict[str, Any]: Success status with updated product or error.
        """
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
        
        if quantity_in_stock is None and stock_status is None:
            return {"error": "At least one of quantity_in_stock or stock_status must be provided"}
        
        if quantity_in_stock is not None and quantity_in_stock < 0:
            return {"error": "Quantity in stock cannot be negative"}
        
        if stock_status is not None and stock_status not in ["in stock", "out of stock"]:
            return {"error": "Stock status must be 'in stock' or 'out of stock'"}
        
        product = self.products[product_id]
        updates = {}
        
        if quantity_in_stock is not None:
            updates["old_quantity"] = product["quantity_in_stock"]
            product["quantity_in_stock"] = quantity_in_stock
            updates["new_quantity"] = quantity_in_stock
        
        if stock_status is not None:
            updates["old_status"] = product["stock_status"]
            product["stock_status"] = stock_status
            updates["new_status"] = stock_status
        
        return {
            "success": True,
            "message": "Product stock updated successfully",
            "product_id": product_id,
            **updates
        }
    
    def set_product_availability(
        self, 
        product_id: str, 
        available: bool
    ) -> Dict[str, Any]:
        """
        Explicitly set the availability of a product based on business logic.
        
        Args:
            product_id: The unique identifier of the product.
            available: True for "in stock", False for "out of stock".
            
        Returns:
            Dict[str, Any]: Success status with updated availability or error.
        """
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
        
        product = self.products[product_id]
        old_status = product["stock_status"]
        new_status = "in stock" if available else "out of stock"
        
        product["stock_status"] = new_status
        
        # If setting to unavailable, also set quantity to 0
        if not available:
            product["quantity_in_stock"] = 0
        
        return {
            "success": True,
            "message": "Product availability updated successfully",
            "product_id": product_id,
            "old_status": old_status,
            "new_status": new_status,
            "is_available": available
        }
    
    def edit_product_details(
        self,
        product_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Modify non-ID attributes of a product.
        
        Args:
            product_id: The unique identifier of the product.
            name: New product name (optional, cannot be empty if provided).
            description: New product description (optional).
            category: New product category (optional, must be valid if provided).
            
        Returns:
            Dict[str, Any]: Success status with updated product or error.
        """
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
        
        if name is not None and not name.strip():
            return {"error": "Product name cannot be empty"}
        
        if category is not None:
            if not category.strip():
                return {"error": "Product category cannot be empty"}
            if not self._is_valid_category(category):
                return {"error": f"Category '{category}' is not a valid predefined category"}
        
        product = self.products[product_id]
        updates = {}
        
        if name is not None:
            updates["name"] = {"old": product["name"], "new": name.strip()}
            product["name"] = name.strip()
        
        if description is not None:
            updates["description"] = {"old": product["description"], "new": description}
            product["description"] = description
        
        if category is not None:
            updates["category"] = {"old": product["category"], "new": category}
            product["category"] = category
        
        if not updates:
            return {"error": "No fields provided for update"}
        
        return {
            "success": True,
            "message": "Product details updated successfully",
            "product_id": product_id,
            "updates": updates
        }
    
    def remove_product(self, product_id: str) -> Dict[str, Any]:
        """
        Delete a product from the inventory by product_id.
        
        Args:
            product_id: The unique identifier of the product to remove.
            
        Returns:
            Dict[str, Any]: Success status with removed product info or error.
        """
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
        
        removed_product = deepcopy(self.products[product_id])
        del self.products[product_id]
        
        return {
            "success": True,
            "message": "Product removed successfully",
            "removed_product": removed_product
        }
    
    def add_new_category(
        self,
        name: str,
        parent_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Introduce a new product category into the system.
        
        Args:
            name: The name of the new category (required).
            parent_category: Name of the parent category (optional).
            
        Returns:
            Dict[str, Any]: Success status with new category details or error.
        """
        if not name or not name.strip():
            return {"error": "Category name is required"}
        
        # Check if category already exists
        for cat in self.categories.values():
            if cat["name"] == name:
                return {"error": f"Category '{name}' already exists"}
        
        # Validate parent category if provided
        if parent_category is not None:
            parent_exists = any(
                cat["name"] == parent_category 
                for cat in self.categories.values()
            )
            if not parent_exists:
                return {"error": f"Parent category '{parent_category}' not found"}
        
        # Generate new category ID
        category_id = f"cat_{self.next_category_id:03d}"
        self.next_category_id += 1
        
        # Create new category
        new_category = {
            "category_id": category_id,
            "name": name.strip(),
            "parent_category": parent_category,
            "is_active": True
        }
        
        self.categories[category_id] = new_category
        
        return {
            "success": True,
            "message": "Category added successfully",
            "category": deepcopy(new_category)
        }
    
    def update_category_assignment(
        self, 
        product_id: str, 
        new_category: str
    ) -> Dict[str, Any]:
        """
        Change the category of an existing product.
        
        Args:
            product_id: The unique identifier of the product.
            new_category: The new category name (must be valid and predefined).
            
        Returns:
            Dict[str, Any]: Success status with updated category info or error.
        """
        if product_id not in self.products:
            return {"error": f"Product with ID '{product_id}' not found"}
        
        if not new_category or not new_category.strip():
            return {"error": "Category name cannot be empty"}
        
        if not self._is_valid_category(new_category):
            return {"error": f"Category '{new_category}' is not a valid predefined category"}
        
        product = self.products[product_id]
        old_category = product["category"]
        product["category"] = new_category
        
        return {
            "success": True,
            "message": "Product category updated successfully",
            "product_id": product_id,
            "old_category": old_category,
            "new_category": new_category
        }
    
    def deactivate_category(self, category_id: str) -> Dict[str, Any]:
        """
        Mark a category as inactive.
        
        Inactive categories cannot have new products assigned to them,
        but existing products retain their category assignment.
        
        Args:
            category_id: The unique identifier of the category to deactivate.
            
        Returns:
            Dict[str, Any]: Success status with deactivated category info or error.
        """
        if category_id not in self.categories:
            return {"error": f"Category with ID '{category_id}' not found"}
        
        category = self.categories[category_id]
        
        if not category.get("is_active", True):
            return {"error": f"Category '{category['name']}' is already inactive"}
        
        category["is_active"] = False
        
        return {
            "success": True,
            "message": "Category deactivated successfully",
            "category_id": category_id,
            "category_name": category["name"]
        }
    
    def bulk_update_stock_status(
        self,
        product_ids: List[str],
        new_status: str
    ) -> Dict[str, Any]:
        """
        Update stock status for multiple products at once.
        
        Args:
            product_ids: List of product IDs to update.
            new_status: The new stock status ("in stock" or "out of stock").
            
        Returns:
            Dict[str, Any]: Success status with update results or error.
        """
        if not product_ids:
            return {"error": "Product IDs list cannot be empty"}
        
        if new_status not in ["in stock", "out of stock"]:
            return {"error": "Stock status must be 'in stock' or 'out of stock'"}
        
        updated = []
        not_found = []
        
        for product_id in product_ids:
            if product_id not in self.products:
                not_found.append(product_id)
            else:
                old_status = self.products[product_id]["stock_status"]
                self.products[product_id]["stock_status"] = new_status
                
                # If setting to out of stock, also set quantity to 0
                if new_status == "out of stock":
                    self.products[product_id]["quantity_in_stock"] = 0
                
                updated.append({
                    "product_id": product_id,
                    "old_status": old_status,
                    "new_status": new_status
                })
        
        result = {
            "success": len(updated) > 0,
            "message": f"Updated {len(updated)} product(s)",
            "updated_products": updated,
            "updated_count": len(updated)
        }
        
        if not_found:
            result["not_found"] = not_found
            result["not_found_count"] = len(not_found)
        
        return result


__TEST_CASES__ = [
    {
        "name": "Product search and availability check workflow",
        "steps": [
            {"tool_call": "search_products_by_name(keyword='Yoga')", "expect_success": True},
            {"tool_call": "get_product_availability_status(product_id='prod_002')", "expect_success": True},
            {"tool_call": "filter_products_by_category(category='Fitness Equipment')", "expect_success": True},
            {"tool_call": "get_available_products()", "expect_success": True}
        ]
    },
    {
        "name": "Add new product and update inventory workflow",
        "steps": [
            {"tool_call": "add_new_product(name='Resistance Bands Set', category='Fitness Equipment', price=29.99, description='Set of 5 resistance bands', quantity_in_stock=100)", "expect_success": True},
            {"tool_call": "update_product_price(product_id='prod_006', new_price=24.99)", "expect_success": True},
            {"tool_call": "update_product_stock(product_id='prod_006', quantity_in_stock=150, stock_status='in stock')", "expect_success": True},
            {"tool_call": "get_product_by_id(product_id='prod_006')", "expect_success": True}
        ]
    },
    {
        "name": "Category management workflow",
        "steps": [
            {"tool_call": "list_all_categories()", "expect_success": True},
            {"tool_call": "add_new_category(name='Sports', parent_category=None)", "expect_success": True},
            {"tool_call": "get_category_info(name='Sports')", "expect_success": True},
            {"tool_call": "count_products_in_category(category='Electronics')", "expect_success": True}
        ]
    },
    {
        "name": "Error handling - invalid operations",
        "steps": [
            {"tool_call": "get_product_by_id(product_id='invalid_id')", "expect_success": False},
            {"tool_call": "add_new_product(name='Test Product', category='Invalid Category', price=10.00)", "expect_success": False},
            {"tool_call": "update_product_price(product_id='prod_001', new_price=-5.00)", "expect_success": False},
            {"tool_call": "search_products_by_name(keyword='')", "expect_success": False}
        ]
    },
    {
        "name": "Bulk operations workflow",
        "steps": [
            {"tool_call": "bulk_update_stock(updates=[{'product_id': 'prod_001', 'quantity': 50}, {'product_id': 'prod_002', 'quantity': 75}])", "expect_success": True},
            {"tool_call": "bulk_update_prices(updates=[{'product_id': 'prod_001', 'new_price': 899.99}, {'product_id': 'prod_002', 'new_price': 1099.99}])", "expect_success": True},
            {"tool_call": "get_low_stock_products(threshold=20)", "expect_success": True},
            {"tool_call": "get_inventory_summary()", "expect_success": True}
        ]
    },
    {
        "name": "Product deletion workflow",
        "steps": [
            {"tool_call": "add_new_product(name='Temporary Product', category='Electronics', price=9.99, quantity_in_stock=5)", "expect_success": True},
            {"tool_call": "delete_product(product_id='prod_007')", "expect_success": True},
            {"tool_call": "get_product_by_id(product_id='prod_007')", "expect_success": False},
            {"tool_call": "delete_product(product_id='nonexistent')", "expect_success": False}
        ]
    }
]

def get_product_by_id(product_id: str) -> dict:
    """Retrieve product details by product ID."""
    if not product_id or not isinstance(product_id, str):
        return {"error": "Invalid product_id: must be a non-empty string"}
    
    if product_id not in products_db:
        return {"error": f"Product with id '{product_id}' not found"}
    
    return {"result": products_db[product_id].copy()}

def search_products_by_name(keyword: str) -> dict:
    """Search products by name keyword."""
    if not keyword or not isinstance(keyword, str):
        return {"error": "Invalid keyword: must be a non-empty string"}
    
    keyword_lower = keyword.lower()
    matching_products = [
        product.copy() for product in products_db.values()
        if keyword_lower in product["name"].lower()
    ]
    
    return {"result": matching_products}

def get_product_availability_status(product_id: str) -> dict:
    """Get the availability status of a product."""
    if not product_id or not isinstance(product_id, str):
        return {"error": "Invalid product_id: must be a non-empty string"}
    
    if product_id not in products_db:
        return {"error": f"Product with id '{product_id}' not found"}
    
    product = products_db[product_id]
    return {"result": {
        "product_id": product_id,
        "name": product["name"],
        "stock_status": product["stock_status"],
        "quantity_in_stock": product["quantity_in_stock"]
    }}

def filter_products_by_category(category: str) -> dict:
    """Filter products by category name."""
    if not category or not isinstance(category, str):
        return {"error": "Invalid category: must be a non-empty string"}
    
    if category not in categories_db:
        return {"error": f"Category '{category}' not found"}
    
    filtered_products = [
        product.copy() for product in products_db.values()
        if product["category"] == category
    ]
    
    return {"result": filtered_products}

def get_available_products() -> dict:
    """Get all products that are currently in stock."""
    available_products = [
        product.copy() for product in products_db.values()
        if product["stock_status"] == "in stock" and product["quantity_in_stock"] > 0
    ]
    
    return {"result": available_products}

def add_new_product(name: str, category: str, price: float, description: str = "", quantity_in_stock: int = 0) -> dict:
    """Add a new product to the inventory."""
    if not name or not isinstance(name, str):
        return {"error": "Invalid name: must be a non-empty string"}
    
    if not category or not isinstance(category, str):
        return {"error": "Invalid category: must be a non-empty string"}
    
    if category not in categories_db:
        return {"error": f"Category '{category}' not found"}
    
    if not isinstance(price, (int, float)) or price < 0:
        return {"error": "Invalid price: must be a non-negative number"}
    
    if not isinstance(quantity_in_stock, int) or quantity_in_stock < 0:
        return {"error": "Invalid quantity_in_stock: must be a non-negative integer"}
    
    # Generate new product ID
    product_ids = [int(pid.split('_')[1]) for pid in products_db.keys()]
    new_id = f"prod_{max(product_ids) + 1:03d}" if product_ids else "prod_001"
    
    # Determine stock status
    if quantity_in_stock == 0:
        stock_status = "out of stock"
    elif quantity_in_stock < 10:
        stock_status = "low stock"
    else:
        stock_status = "in stock"
    
    new_product = {
        "product_id": new_id,
        "name": name,
        "category": category,
        "price": float(price),
        "description": description,
        "quantity_in_stock": quantity_in_stock,
        "stock_status": stock_status
    }
    
    products_db[new_id] = new_product
    
    return {"result": new_product}

def update_product_price(product_id: str, new_price: float) -> dict:
    """Update the price of a product."""
    if not product_id or not isinstance(product_id, str):
        return {"error": "Invalid product_id: must be a non-empty string"}
    
    if product_id not in products_db:
        return {"error": f"Product with id '{product_id}' not found"}
    
    if not isinstance(new_price, (int, float)) or new_price < 0:
        return {"error": "Invalid new_price: must be a non-negative number"}
    
    products_db[product_id]["price"] = float(new_price)
    
    return {"result": products_db[product_id].copy()}

def update_product_stock(product_id: str, quantity_in_stock: int, stock_status: str = None) -> dict:
    """Update the stock quantity and status of a product."""
    if not product_id or not isinstance(product_id, str):
        return {"error": "Invalid product_id: must be a non-empty string"}
    
    if product_id not in products_db:
        return {"error": f"Product with id '{product_id}' not found"}
    
    if not isinstance(quantity_in_stock, int) or quantity_in_stock < 0:
        return {"error": "Invalid quantity_in_stock: must be a non-negative integer"}
    
    valid_statuses = ["in stock", "out of stock", "low stock"]
    
    if stock_status is None:
        if quantity_in_stock == 0:
            stock_status = "out of stock"
        elif quantity_in_stock < 10:
            stock_status = "low stock"
        else:
            stock_status = "in stock"
    elif stock_status not in valid_statuses:
        return {"error": f"Invalid stock_status: must be one of {valid_statuses}"}
    
    products_db[product_id]["quantity_in_stock"] = quantity_in_stock
    products_db[product_id]["stock_status"] = stock_status
    
    return {"result": products_db[product_id].copy()}

def list_all_categories() -> dict:
    """List all product categories."""
    categories_list = [
        {"name": name, **info} for name, info in categories_db.items()
    ]
    return {"result": categories_list}

def add_new_category(name: str, parent_category: str = None) -> dict:
    """Add a new category to the system."""
    if not name or not isinstance(name, str):
        return {"error": "Invalid name: must be a non-empty string"}
    
    if name in categories_db:
        return {"error": f"Category '{name}' already exists"}
    
    if parent_category is not None and parent_category not in categories_db:
        return {"error": f"Parent category '{parent_category}' not found"}
    
    categories_db[name] = {
        "parent_category": parent_category,
        "description": ""
    }
    
    return {"result": {"name": name, **categories_db[name]}}

def get_category_info(name: str) -> dict:
    """Get information about a category."""
    if not name or not isinstance(name, str):
        return {"error": "Invalid name: must be a non-empty string"}
    
    if name not in categories_db:
        return {"error": f"Category '{name}' not found"}
    
    return {"result": {"name": name, **categories_db[name]}}

def count_products_in_category(category: str) -> dict:
    """Count the number of products in a category."""
    if not category or not isinstance(category, str):
        return {"error": "Invalid category: must be a non-empty string"}
    
    if category not in categories_db:
        return {"error": f"Category '{category}' not found"}
    
    count = sum(1 for product in products_db.values() if product["category"] == category)
    
    return {"result": {"category": category, "product_count": count}}

def bulk_update_stock(updates: list) -> dict:
    """Bulk update stock quantities for multiple products."""
    if not updates or not isinstance(updates, list):
        return {"error": "Invalid updates: must be a non-empty list"}
    
    results = []
    errors = []
    
    for update in updates:
        if not isinstance(update, dict):
            errors.append({"error": "Each update must be a dictionary"})
            continue
        
        product_id = update.get("product_id")
        quantity = update.get("quantity")
        
        if not product_id or product_id not in products_db:
            errors.append({"product_id": product_id, "error": "Product not found"})
            continue
        
        if not isinstance(quantity, int) or quantity < 0:
            errors.append({"product_id": product_id, "error": "Invalid quantity"})
            continue
        
        # Update stock
        if quantity == 0:
            stock_status = "out of stock"
        elif quantity < 10:
            stock_status = "low stock"
        else:
            stock_status = "in stock"
        
        products_db[product_id]["quantity_in_stock"] = quantity
        products_db[product_id]["stock_status"] = stock_status
        results.append({"product_id": product_id, "new_quantity": quantity, "stock_status": stock_status})
    
    return {"result": {"updated": results, "errors": errors}}

def bulk_update_prices(updates: list) -> dict:
    """Bulk update prices for multiple products."""
    if not updates or not isinstance(updates, list):
        return {"error": "Invalid updates: must be a non-empty list"}
    
    results = []
    errors = []
    
    for update in updates:
        if not isinstance(update, dict):
            errors.append({"error": "Each update must be a dictionary"})
            continue
        
        product_id = update.get("product_id")
        new_price = update.get("new_price")
        
        if not product_id or product_id not in products_db:
            errors.append({"product_id": product_id, "error": "Product not found"})
            continue
        
        if not isinstance(new_price, (int, float)) or new_price < 0:
            errors.append({"product_id": product_id, "error": "Invalid price"})
            continue
        
        products_db[product_id]["price"] = float(new_price)
        results.append({"product_id": product_id, "new_price": float(new_price)})
    
    return {"result": {"updated": results, "errors": errors}}

def get_low_stock_products(threshold: int = 10) -> dict:
    """Get all products with stock below a threshold."""
    if not isinstance(threshold, int) or threshold < 0:
        return {"error": "Invalid threshold: must be a non-negative integer"}
    
    low_stock = [
        product.copy() for product in products_db.values()
        if product["quantity_in_stock"] < threshold
    ]
    
    return {"result": low_stock}

def get_inventory_summary() -> dict:
    """Get a summary of the entire inventory."""
    total_products = len(products_db)
    total_value = sum(p["price"] * p["quantity_in_stock"] for p in products_db.values())
    total_items = sum(p["quantity_in_stock"] for p in products_db.values())
    
    status_counts = {"in stock": 0, "out of stock": 0, "low stock": 0}
    for product in products_db.values():
        status_counts[product["stock_status"]] = status_counts.get(product["stock_status"], 0) + 1
    
    category_counts = {}
    for product in products_db.values():
        cat = product["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    return {"result": {
        "total_products": total_products,
        "total_items_in_stock": total_items,
        "total_inventory_value": round(total_value, 2),
        "status_breakdown": status_counts,
        "category_breakdown": category_counts
    }}

def delete_product(product_id: str) -> dict:
    """Delete a product from the inventory."""
    if not product_id or not isinstance(product_id, str):
        return {"error": "Invalid product_id: must be a non-empty string"}
    
    if product_id not in products_db:
        return {"error": f"Product with id '{product_id}' not found"}
    
    deleted_product = products_db.pop(product_id)
    
    return {"result": {"message": f"Product '{deleted_product['name']}' deleted successfully", "deleted_product": deleted_product}}

__TEST_CASES__ = [
    # Test get_product_by_id
    {"tool_call": "get_product_by_id(product_id='prod_001')", "expect_success": True},
    {"tool_call": "get_product_by_id(product_id='invalid_id')", "expect_success": False},
    {"tool_call": "get_product_by_id(product_id='')", "expect_success": False},
    
    # Test search_products_by_name
    {"tool_call": "search_products_by_name(keyword='Laptop')", "expect_success": True},
    {"tool_call": "search_products_by_name(keyword='nonexistent')", "expect_success": True},
    {"tool_call": "search_products_by_name(keyword='')", "expect_success": False},
    
    # Test get_product_availability_status
    {"tool_call": "get_product_availability_status(product_id='prod_001')", "expect_success": True},
    {"tool_call": "get_product_availability_status(product_id='invalid')", "expect_success": False},
    
    # Test filter_products_by_category
    {"tool_call": "filter_products_by_category(category='Electronics')", "expect_success": True},
    {"tool_call": "filter_products_by_category(category='Invalid Category')", "expect_success": False},
    
    # Test get_available_products
    {"tool_call": "get_available_products()", "expect_success": True},
    
    # Test add_new_product
    {"tool_call": "add_new_product(name='Test Product', category='Electronics', price=99.99, quantity_in_stock=50)", "expect_success": True},
    {"tool_call": "add_new_product(name='', category='Electronics', price=99.99)", "expect_success": False},
    {"tool_call": "add_new_product(name='Test', category='Invalid', price=99.99)", "expect_success": False},
    {"tool_call": "add_new_product(name='Test', category='Electronics', price=-10.00)", "expect_success": False},
    
    # Test update_product_price
    {"tool_call": "update_product_price(product_id='prod_001', new_price=999.99)", "expect_success": True},
    {"tool_call": "update_product_price(product_id='invalid', new_price=100.00)", "expect_success": False},
    {"tool_call": "update_product_price(product_id='prod_001', new_price=-5.00)", "expect_success": False},
    
    # Test update_product_stock
    {"tool_call": "update_product_stock(product_id='prod_001', quantity_in_stock=100)", "expect_success": True},
    {"tool_call": "update_product_stock(product_id='prod_001', quantity_in_stock=5, stock_status='low stock')", "expect_success": True},
    {"tool_call": "update_product_stock(product_id='invalid', quantity_in_stock=50)", "expect_success": False},
    
    # Test list_all_categories
    {"tool_call": "list_all_categories()", "expect_success": True},
    
    # Test add_new_category
    {"tool_call": "add_new_category(name='New Category')", "expect_success": True},
    {"tool_call": "add_new_category(name='Electronics')", "expect_success": False},
    {"tool_call": "add_new_category(name='')", "expect_success": False},
    
    # Test get_category_info
    {"tool_call": "get_category_info(name='Electronics')", "expect_success": True},
    {"tool_call": "get_category_info(name='Invalid')", "expect_success": False},
    
    # Test count_products_in_category
    {"tool_call": "count_products_in_category(category='Electronics')", "expect_success": True},
    {"tool_call": "count_products_in_category(category='Invalid')", "expect_success": False},
    
    # Test bulk_update_stock
    {"tool_call": "bulk_update_stock(updates=[{'product_id': 'prod_001', 'quantity': 100}])", "expect_success": True},
    {"tool_call": "bulk_update_stock(updates=[])", "expect_success": False},
    
    # Test bulk_update_prices
    {"tool_call": "bulk_update_prices(updates=[{'product_id': 'prod_001', 'new_price': 899.99}])", "expect_success": True},
    {"tool_call": "bulk_update_prices(updates=[])", "expect_success": False},
    
    # Test get_low_stock_products
    {"tool_call": "get_low_stock_products(threshold=20)", "expect_success": True},
    {"tool_call": "get_low_stock_products(threshold=-1)", "expect_success": False},
    
    # Test get_inventory_summary
    {"tool_call": "get_inventory_summary()", "expect_success": True},
    
    # Test delete_product
    {"tool_call": "delete_product(product_id='prod_005')", "expect_success": True},
    {"tool_call": "delete_product(product_id='nonexistent')", "expect_success": False},
    {"tool_call": "delete_product(product_id='')", "expect_success": False},
]