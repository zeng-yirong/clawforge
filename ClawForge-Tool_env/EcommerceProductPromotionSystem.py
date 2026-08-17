"""
E-commerce Product and Promotion Management System API

This module provides a complete API for managing products, promotions, and their
associations in an e-commerce platform. It supports dynamic pricing, time-bound
deals, and customer-specific offers.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

DEFAULT_STATE = {
    # Products
    "products": {
        "SKU001": {
            "sku": "SKU001",
            "name": "Wireless Bluetooth Headphones",
            "base_price": 99.99,
            "current_price": 99.99,
            "inventory_level": 150,
            "category": "Electronics"
        },
        "SKU002": {
            "sku": "SKU002",
            "name": "Organic Green Tea - 100 Bags",
            "base_price": 24.99,
            "current_price": 24.99,
            "inventory_level": 500,
            "category": "Food & Beverages"
        },
        "SKU003": {
            "sku": "SKU003",
            "name": "Running Shoes - Men's Size 10",
            "base_price": 129.99,
            "current_price": 129.99,
            "inventory_level": 75,
            "category": "Sportswear"
        },
        "SKU004": {
            "sku": "SKU004",
            "name": "Stainless Steel Water Bottle",
            "base_price": 19.99,
            "current_price": 19.99,
            "inventory_level": 0,
            "category": "Home & Kitchen"
        }
    },
    
    # Promotions
    "promotions": {
        "PROMO001": {
            "promotion_id": "PROMO001",
            "name": "Summer Sale",
            "description": "20% off on all electronics",
            "discount_type": "percentage",
            "discount_value": 20.0,
            "start_time": "2024-06-01T00:00:00",
            "end_time": "2024-08-31T23:59:59",
            "eligibility_criteria": {"membership_level": ["Gold", "Platinum", "Standard"]},
            "active": True
        },
        "PROMO002": {
            "promotion_id": "PROMO002",
            "name": "VIP Member Exclusive",
            "description": "$10 off for Platinum members",
            "discount_type": "fixed",
            "discount_value": 10.0,
            "start_time": "2024-01-01T00:00:00",
            "end_time": "2024-12-31T23:59:59",
            "eligibility_criteria": {"membership_level": ["Platinum"]},
            "active": True
        },
        "PROMO003": {
            "promotion_id": "PROMO003",
            "name": "Flash Deal",
            "description": "15% off sportswear - limited time",
            "discount_type": "percentage",
            "discount_value": 15.0,
            "start_time": "2024-07-01T00:00:00",
            "end_time": "2024-07-07T23:59:59",
            "eligibility_criteria": {"membership_level": ["Gold", "Platinum", "Standard"]},
            "active": True
        },
        "PROMO004": {
            "promotion_id": "PROMO004",
            "name": "Expired Promo",
            "description": "Old promotion that has ended",
            "discount_type": "percentage",
            "discount_value": 50.0,
            "start_time": "2023-01-01T00:00:00",
            "end_time": "2023-12-31T23:59:59",
            "eligibility_criteria": {"membership_level": ["Standard"]},
            "active": False
        }
    },
    
    # Product-Promotion Links
    "product_promotions": [
        {
            "sku": "SKU001",
            "promotion_id": "PROMO001",
            "effective_start": "2024-06-01T00:00:00",
            "effective_end": "2024-08-31T23:59:59"
        },
        {
            "sku": "SKU001",
            "promotion_id": "PROMO002",
            "effective_start": "2024-01-01T00:00:00",
            "effective_end": "2024-12-31T23:59:59"
        },
        {
            "sku": "SKU003",
            "promotion_id": "PROMO003",
            "effective_start": "2024-07-01T00:00:00",
            "effective_end": "2024-07-07T23:59:59"
        }
    ],
    
    # Customers
    "customers": {
        "CUST001": {
            "customer_id": "CUST001",
            "membership_level": "Platinum",
            "location": "New York, USA",
            "purchase_history": ["SKU001", "SKU002"]
        },
        "CUST002": {
            "customer_id": "CUST002",
            "membership_level": "Gold",
            "location": "Los Angeles, USA",
            "purchase_history": ["SKU003"]
        },
        "CUST003": {
            "customer_id": "CUST003",
            "membership_level": "Standard",
            "location": "Chicago, USA",
            "purchase_history": []
        }
    },
    
    # System state
    "current_time": "2024-07-05T12:00:00",
    "current_user": None
}


class EcommerceProductPromotionSystem:
    """
    E-commerce Product and Promotion Management System API.
    
    This class provides a comprehensive API for managing products, promotions,
    and their associations in an e-commerce platform. It supports dynamic pricing
    rules, time-bound deals, and customer-specific offers, enabling real-time
    updates and queries for both customer-facing displays and back-end operations.
    """
    
    def __init__(self):
        """
        Initialize the E-commerce Product and Promotion Management System.
        
        Sets up all state attributes with type hints and initializes the API description.
        """
        self.products: Dict[str, Dict[str, Any]] = {}
        self.promotions: Dict[str, Dict[str, Any]] = {}
        self.product_promotions: List[Dict[str, Any]] = []
        self.customers: Dict[str, Dict[str, Any]] = {}
        self.current_time: str = ""
        self.current_user: Optional[str] = None
        
        self._api_description = "E-commerce product and promotion management system for managing SKUs, pricing, inventory, and marketing offers."
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing the initial state configuration.
            long_context: Flag for extended context loading (reserved for future use).
            
        Returns:
            None
        """
        if not scenario:
            return
        for key in DEFAULT_STATE:
            if key in scenario:
                setattr(self, key, deepcopy(scenario[key]))
            else:
                setattr(self, key, deepcopy(DEFAULT_STATE[key]))
    
    def get_env_state(self) -> dict:
        """
        Get the current state of the environment.
        
        Returns a dictionary containing all internal state variables of the system,
        including products, promotions, product-promotion links, customers, and
        system configuration.
        
        Args:
            None
        
        Returns:
            dict: A dictionary containing:
                - products: Dict of all products keyed by SKU
                - promotions: Dict of all promotions keyed by promotion_id
                - product_promotions: List of product-promotion link records
                - customers: Dict of all customers keyed by customer_id
                - current_time: Current system time as ISO string
                - current_user: Currently active user ID or None
        """
        return {
            "products": deepcopy(self.products),
            "promotions": deepcopy(self.promotions),
            "product_promotions": deepcopy(self.product_promotions),
            "customers": deepcopy(self.customers),
            "current_time": self.current_time,
            "current_user": self.current_user
        }
    
    def _timestamp(self) -> str:
        """
        Generate a consistent timestamp for the system.
        
        Args:
            None
        
        Returns:
            str: ISO format timestamp string based on current_time or system time.
        """
        if self.current_time:
            return self.current_time
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _parse_time(self, time_str: str) -> datetime:
        """
        Parse an ISO format time string to datetime object.
        
        Args:
            time_str: ISO format time string (YYYY-MM-DDTHH:MM:SS).
            
        Returns:
            datetime: Parsed datetime object.
        """
        return datetime.fromisoformat(time_str)
    
    # ==================== PRODUCT OPERATIONS ====================
    
    def add_product(
        self,
        sku: str,
        name: str,
        price: float,
        category: str,
        inventory_level: int = 0
    ) -> Dict[str, Any]:
        """
        Add a new product to the system.
        
        Args:
            sku: Unique Stock Keeping Unit identifier for the product.
            name: Display name of the product.
            price: Base price of the product.
            category: Category the product belongs to.
            inventory_level: Initial inventory level (default 0).
            
        Returns:
            dict: Contains 'success' boolean and product details,
                  or error dict if product already exists.
        """
        if sku in self.products:
            return {"error": f"Product with SKU '{sku}' already exists"}
        
        if price < 0:
            return {"error": "Price cannot be negative"}
        
        if inventory_level < 0:
            return {"error": "Inventory level cannot be negative"}
        
        new_product = {
            "sku": sku,
            "name": name,
            "base_price": price,
            "current_price": price,
            "inventory_level": inventory_level,
            "category": category
        }
        
        self.products[sku] = new_product
        
        return {"success": True, "sku": sku, "product": deepcopy(new_product)}
    
    def get_product(self, sku: str) -> Dict[str, Any]:
        """
        Retrieve full product details using SKU.
        
        Args:
            sku: The Stock Keeping Unit identifier for the product.
            
        Returns:
            dict: Product details including name, base_price, current_price,
                  inventory_level, and category. Returns error dict if not found.
        """
        if sku not in self.products:
            return {"error": f"Product with SKU '{sku}' not found"}
        return deepcopy(self.products[sku])
    
    def update_product(
        self,
        sku: str,
        name: Optional[str] = None,
        price: Optional[float] = None,
        category: Optional[str] = None,
        inventory_level: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Update an existing product's details.
        
        Args:
            sku: The Stock Keeping Unit identifier for the product to update.
            name: Optional new display name.
            price: Optional new base price.
            category: Optional new category.
            inventory_level: Optional new inventory level.
            
        Returns:
            dict: Contains 'success' boolean and updated product details,
                  or error dict if product not found or validation fails.
        """
        if sku not in self.products:
            return {"error": f"Product with SKU '{sku}' not found"}
        
        if price is not None and price < 0:
            return {"error": "Price cannot be negative"}
        
        if inventory_level is not None and inventory_level < 0:
            return {"error": "Inventory level cannot be negative"}
        
        product = self.products[sku]
        
        if name is not None:
            product["name"] = name
        if price is not None:
            product["base_price"] = price
            product["current_price"] = price
        if category is not None:
            product["category"] = category
        if inventory_level is not None:
            product["inventory_level"] = inventory_level
        
        return {"success": True, "product": deepcopy(product)}
    
    def delete_product(self, sku: str) -> Dict[str, Any]:
        """
        Remove a product from the system.
        
        Args:
            sku: The Stock Keeping Unit identifier for the product to delete.
            
        Returns:
            dict: Contains 'success' boolean and deleted product details,
                  or error dict if product not found.
        """
        if sku not in self.products:
            return {"error": f"Product with SKU '{sku}' not found"}
        
        deleted_product = deepcopy(self.products[sku])
        del self.products[sku]
        
        # Remove all product-promotion links for this product
        self.product_promotions = [
            link for link in self.product_promotions
            if link["sku"] != sku
        ]
        
        return {"success": True, "deleted_product": deleted_product}
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_product_by_sku(self, sku: str) -> Dict[str, Any]:
        """
        Retrieve full product details using SKU.
        
        Args:
            sku: The Stock Keeping Unit identifier for the product.
            
        Returns:
            dict: Product details including name, base_price, current_price,
                  inventory_level, and category. Returns error dict if not found.
        """
        if sku not in self.products:
            return {"error": f"Product with SKU '{sku}' not found"}
        return deepcopy(self.products[sku])
    
    def list_promotions_for_product(self, sku: str) -> Dict[str, Any]:
        """
        Get all promotions associated with a given SKU via ProductPromotion links.
        
        Args:
            sku: The Stock Keeping Unit identifier for the product.
            
        Returns:
            dict: Contains 'promotions' list with all linked promotion details,
                  or error dict if product not found.
        """
        if sku not in self.products:
            return {"error": f"Product with SKU '{sku}' not found"}
        
        linked_promotions = []
        for link in self.product_promotions:
            if link["sku"] == sku:
                promo_id = link["promotion_id"]
                if promo_id in self.promotions:
                    promo_data = deepcopy(self.promotions[promo_id])
                    promo_data["effective_start"] = link["effective_start"]
                    promo_data["effective_end"] = link["effective_end"]
                    linked_promotions.append(promo_data)
        
        return {"sku": sku, "promotions": linked_promotions}
    
    def get_promotion_by_id(self, promotion_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific promotion.
        
        Args:
            promotion_id: The unique identifier for the promotion.
            
        Returns:
            dict: Promotion details including discount type, value, time window,
                  and eligibility rules. Returns error dict if not found.
        """
        if promotion_id not in self.promotions:
            return {"error": f"Promotion with ID '{promotion_id}' not found"}
        return deepcopy(self.promotions[promotion_id])
    
    def check_promotion_active(self, promotion_id: str) -> Dict[str, Any]:
        """
        Determine if a promotion is currently active based on time window and active flag.
        
        Args:
            promotion_id: The unique identifier for the promotion.
            
        Returns:
            dict: Contains 'is_active' boolean and promotion details,
                  or error dict if promotion not found.
        """
        if promotion_id not in self.promotions:
            return {"error": f"Promotion with ID '{promotion_id}' not found"}
        
        promo = self.promotions[promotion_id]
        
        # Check active flag first
        if not promo.get("active", True):
            return {
                "promotion_id": promotion_id,
                "is_active": False,
                "start_time": promo["start_time"],
                "end_time": promo["end_time"],
                "current_time": self._timestamp(),
                "reason": "Promotion is deactivated"
            }
        
        current = self._parse_time(self._timestamp())
        start = self._parse_time(promo["start_time"])
        end = self._parse_time(promo["end_time"])
        
        is_active = start <= current <= end
        
        return {
            "promotion_id": promotion_id,
            "is_active": is_active,
            "start_time": promo["start_time"],
            "end_time": promo["end_time"],
            "current_time": self._timestamp()
        }
    
    def get_current_price(self, sku: str, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Compute the effective current_price of a product considering active promotions.
        
        Args:
            sku: The Stock Keeping Unit identifier for the product.
            customer_id: Optional customer ID to consider customer-specific promotions.
            
        Returns:
            dict: Contains 'current_price', 'base_price', and 'applied_promotions' list,
                  or error dict if product not found.
        """
        if sku not in self.products:
            return {"error": f"Product with SKU '{sku}' not found"}
        
        product = self.products[sku]
        base_price = product["base_price"]
        final_price = base_price
        applied_promotions = []
        
        current = self._parse_time(self._timestamp())
        
        for link in self.product_promotions:
            if link["sku"] != sku:
                continue
            
            promo_id = link["promotion_id"]
            if promo_id not in self.promotions:
                continue
            
            promo = self.promotions[promo_id]
            
            # Check if promotion is active
            if not promo.get("active", True):
                continue
            
            # Check promotion time window
            promo_start = self._parse_time(promo["start_time"])
            promo_end = self._parse_time(promo["end_time"])
            if not (promo_start <= current <= promo_end):
                continue
            
            # Check link effective period
            link_start = self._parse_time(link["effective_start"])
            link_end = self._parse_time(link["effective_end"])
            if not (link_start <= current <= link_end):
                continue
            
            # Check customer eligibility if customer_id provided
            if customer_id:
                eligibility_result = self.evaluate_customer_eligibility(customer_id, promo_id)
                if "error" in eligibility_result or not eligibility_result.get("is_eligible", False):
                    continue
            
            # Apply discount
            if promo["discount_type"] == "percentage":
                discount = final_price * (promo["discount_value"] / 100)
                final_price -= discount
            elif promo["discount_type"] == "fixed":
                final_price -= promo["discount_value"]
            
            applied_promotions.append({
                "promotion_id": promo_id,
                "name": promo["name"],
                "discount_type": promo["discount_type"],
                "discount_value": promo["discount_value"]
            })
        
        final_price = max(0, round(final_price, 2))
        
        return {
            "sku": sku,
            "base_price": base_price,
            "current_price": final_price,
            "applied_promotions": applied_promotions
        }
    
    def is_product_available(self, sku: str) -> Dict[str, Any]:
        """
        Check if a product is available for sale (inventory_level > 0).
        
        Args:
            sku: The Stock Keeping Unit identifier for the product.
            
        Returns:
            dict: Contains 'is_available' boolean and 'inventory_level',
                  or error dict if product not found.
        """
        if sku not in self.products:
            return {"error": f"Product with SKU '{sku}' not found"}
        
        product = self.products[sku]
        is_available = product["inventory_level"] > 0
        
        return {
            "sku": sku,
            "is_available": is_available,
            "inventory_level": product["inventory_level"]
        }
    
    def evaluate_customer_eligibility(self, customer_id: str, promotion_id: str) -> Dict[str, Any]:
        """
        Assess whether a customer meets the eligibility_criteria of a promotion.
        
        Args:
            customer_id: The unique identifier for the customer.
            promotion_id: The unique identifier for the promotion.
            
        Returns:
            dict: Contains 'is_eligible' boolean and eligibility details,
                  or error dict if customer or promotion not found.
        """
        if customer_id not in self.customers:
            return {"error": f"Customer with ID '{customer_id}' not found"}
        
        if promotion_id not in self.promotions:
            return {"error": f"Promotion with ID '{promotion_id}' not found"}
        
        customer = self.customers[customer_id]
        promo = self.promotions[promotion_id]
        criteria = promo.get("eligibility_criteria", {})
        
        is_eligible = True
        eligibility_details = []
        
        # Check membership level
        if "membership_level" in criteria:
            allowed_levels = criteria["membership_level"]
            if customer["membership_level"] not in allowed_levels:
                is_eligible = False
                eligibility_details.append(
                    f"Membership level '{customer['membership_level']}' not in allowed levels: {allowed_levels}"
                )
            else:
                eligibility_details.append(f"Membership level '{customer['membership_level']}' is eligible")
        
        # Check location if specified
        if "location" in criteria:
            allowed_locations = criteria["location"]
            if customer["location"] not in allowed_locations:
                is_eligible = False
                eligibility_details.append(
                    f"Location '{customer['location']}' not in allowed locations: {allowed_locations}"
                )
            else:
                eligibility_details.append(f"Location '{customer['location']}' is eligible")
        
        return {
            "customer_id": customer_id,
            "promotion_id": promotion_id,
            "is_eligible": is_eligible,
            "eligibility_details": eligibility_details
        }
    
    def get_applicable_promotions(self, sku: str, customer_id: str) -> Dict[str, Any]:
        """
        Return all promotions that are active, linked to the product, and eligible for the customer.
        
        Args:
            sku: The Stock Keeping Unit identifier for the product.
            customer_id: The unique identifier for the customer.
            
        Returns:
            dict: Contains 'applicable_promotions' list with promotion details,
                  or error dict if product or customer not found.
        """
        if sku not in self.products:
            return {"error": f"Product with SKU '{sku}' not found"}
        
        if customer_id not in self.customers:
            return {"error": f"Customer with ID '{customer_id}' not found"}
        
        applicable = []
        current = self._parse_time(self._timestamp())
        
        for link in self.product_promotions:
            if link["sku"] != sku:
                continue
            
            promo_id = link["promotion_id"]
            if promo_id not in self.promotions:
                continue
            
            promo = self.promotions[promo_id]
            
            # Check if promotion is active
            if not promo.get("active", True):
                continue
            
            # Check promotion time window
            promo_start = self._parse_time(promo["start_time"])
            promo_end = self._parse_time(promo["end_time"])
            if not (promo_start <= current <= promo_end):
                continue
            
            # Check link effective period
            link_start = self._parse_time(link["effective_start"])
            link_end = self._parse_time(link["effective_end"])
            if not (link_start <= current <= link_end):
                continue
            
            # Check customer eligibility
            eligibility_result = self.evaluate_customer_eligibility(customer_id, promo_id)
            if "error" in eligibility_result or not eligibility_result.get("is_eligible", False):
                continue
            
            applicable.append(deepcopy(promo))
        
        return {
            "sku": sku,
            "customer_id": customer_id,
            "applicable_promotions": applicable
        }
    
    def list_all_promotions(self) -> Dict[str, Any]:
        """
        Retrieve all defined promotions in the system.
        
        Args:
            None
        
        Returns:
            dict: Contains 'promotions' list with all promotion details
                  and 'count' of total promotions.
        """
        return {
            "promotions": list(deepcopy(self.promotions).values()),
            "count": len(self.promotions)
        }
    
    def get_product_promotion_link(self, sku: str, promotion_id: str) -> Dict[str, Any]:
        """
        Retrieve the effective_start and effective_end period for a product-promotion association.
        
        Args:
            sku: The Stock Keeping Unit identifier for the product.
            promotion_id: The unique identifier for the promotion.
            
        Returns:
            dict: Contains link details including effective_start and effective_end,
                  or error dict if link not found.
        """
        if sku not in self.products:
            return {"error": f"Product with SKU '{sku}' not found"}
        
        if promotion_id not in self.promotions:
            return {"error": f"Promotion with ID '{promotion_id}' not found"}
        
        for link in self.product_promotions:
            if link["sku"] == sku and link["promotion_id"] == promotion_id:
                return deepcopy(link)
        
        return {"error": f"No link found between SKU '{sku}' and promotion '{promotion_id}'"}
    
    # ==================== STATE CHANGE OPERATIONS ====================
    
    def create_promotion(
        self,
        promotion_id: str,
        name: str,
        description: str = "",
        discount_type: str = "percentage",
        discount_value: Optional[float] = None,
        discount_percent: Optional[float] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        eligibility_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add a new promotion with defined discount, timing, and eligibility criteria.
        
        Args:
            promotion_id: Unique identifier for the new promotion.
            name: Display name of the promotion.
            description: Detailed description of the promotion.
            discount_type: Type of discount ('percentage' or 'fixed').
            discount_value: Numeric value of the discount.
            discount_percent: Alias for discount_value when discount_type is percentage.
            start_time: ISO format start time for the promotion (optional, defaults to now).
            end_time: ISO format end time for the promotion (optional, defaults to 1 year from now).
            eligibility_criteria: Optional dict specifying customer eligibility rules.
            
        Returns:
            dict: Contains 'success' boolean and created promotion details,
                  or error dict if validation fails.
        """
        if promotion_id in self.promotions:
            return {"error": f"Promotion with ID '{promotion_id}' already exists"}
        
        # Handle discount_percent as alias for discount_value
        actual_discount_value = discount_value
        if discount_percent is not None:
            actual_discount_value = discount_percent
            discount_type = "percentage"
        
        if actual_discount_value is None:
            return {"error": "discount_value or discount_percent is required"}
        
        if discount_type not in ["percentage", "fixed"]:
            return {"error": f"Invalid discount_type '{discount_type}'. Must be 'percentage' or 'fixed'"}
        
        if actual_discount_value < 0:
            return {"error": "discount_value cannot be negative"}
        
        if discount_type == "percentage" and actual_discount_value > 100:
            return {"error": "Percentage discount cannot exceed 100"}
        
        # Default time values
        if start_time is None:
            start_time = self._timestamp()
        if end_time is None:
            # Default to 1 year from start
            start_dt = self._parse_time(start_time)
            end_dt = start_dt.replace(year=start_dt.year + 1)
            end_time = end_dt.strftime("%Y-%m-%dT%H:%M:%S")
        
        try:
            start_dt = self._parse_time(start_time)
            end_dt = self._parse_time(end_time)
        except ValueError:
            return {"error": "Invalid time format. Use ISO format: YYYY-MM-DDTHH:MM:SS"}
        
        if end_dt <= start_dt:
            return {"error": "end_time must be after start_time"}
        
        new_promotion = {
            "promotion_id": promotion_id,
            "name": name,
            "description": description,
            "discount_type": discount_type,
            "discount_value": actual_discount_value,
            "start_time": start_time,
            "end_time": end_time,
            "eligibility_criteria": eligibility_criteria or {},
            "active": True
        }
        
        self.promotions[promotion_id] = new_promotion
        
        return {"success": True, "promotion_id": promotion_id, "promotion": deepcopy(new_promotion)}
    
    def update_promotion(
        self,
        promotion_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        discount_type: Optional[str] = None,
        discount_value: Optional[float] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        eligibility_criteria: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Modify an existing promotion's details.
        
        Args:
            promotion_id: The unique identifier for the promotion to update.
            name: Optional new display name.
            description: Optional new description.
            discount_type: Optional new discount type.
            discount_value: Optional new discount value.
            start_time: Optional new start time.
            end_time: Optional new end time.
            eligibility_criteria: Optional new eligibility rules.
            
        Returns:
            dict: Contains 'success' boolean and updated promotion details,
                  or error dict if validation fails.
        """
        if promotion_id not in self.promotions:
            return {"error": f"Promotion with ID '{promotion_id}' not found"}
        promotion = self.promotions[promotion_id]
        
        if name is not None:
            if not isinstance(name, str) or len(name.strip()) == 0:
                return {"error": "Name must be a non-empty string"}
            promotion["name"] = name.strip()
            
        if description is not None:
            promotion["description"] = description
            
        if discount_type is not None:
            valid_types = ["percentage", "fixed", "buy_one_get_one", "free_shipping"]
            if discount_type not in valid_types:
                return {"error": f"Invalid discount type. Must be one of: {valid_types}"}
            promotion["discount_type"] = discount_type
            
        if discount_value is not None:
            if not isinstance(discount_value, (int, float)) or discount_value < 0:
                return {"error": "Discount value must be a non-negative number"}
            if promotion["discount_type"] == "percentage" and discount_value > 100:
                return {"error": "Percentage discount cannot exceed 100"}
            promotion["discount_value"] = discount_value
            
        if start_time is not None:
            promotion["start_time"] = start_time
            
        if end_time is not None:
            if start_time is not None and end_time < start_time:
                return {"error": "End time cannot be before start time"}
            elif start_time is None and end_time < promotion["start_time"]:
                return {"error": "End time cannot be before start time"}
            promotion["end_time"] = end_time
            
        if eligibility_criteria is not None:
            promotion["eligibility_criteria"] = eligibility_criteria
            
        promotion["updated_at"] = datetime.now()
        
        return {"success": True, "promotion": promotion}
    
    def delete_promotion(self, promotion_id: str) -> dict:
        """
        Delete a promotion from the system.
        
        Args:
            promotion_id: The unique identifier for the promotion to delete.
            
        Returns:
            dict: Contains 'success' boolean and confirmation message,
                  or error dict if promotion not found.
        """
        if promotion_id not in self.promotions:
            return {"error": f"Promotion with ID '{promotion_id}' not found"}
            
        deleted_promotion = self.promotions.pop(promotion_id)
        return {"success": True, "message": f"Promotion '{deleted_promotion['name']}' deleted successfully"}
    
    def get_active_promotions(self) -> list:
        """
        Retrieve all currently active promotions.
        
        Returns:
            list: All promotions where current time is between start and end times.
        """
        current_time = datetime.now()
        active = []
        
        for promotion in self.promotions.values():
            if promotion["start_time"] <= current_time <= promotion["end_time"]:
                active.append(promotion)
                
        return active
    
    def apply_promotion(self, promotion_id: str, cart_total: float, user_id: str = None) -> dict:
        """
        Apply a promotion to a cart and calculate the discount.
        
        Args:
            promotion_id: The promotion to apply.
            cart_total: The current cart total before discount.
            user_id: Optional user ID for eligibility checking.
            
        Returns:
            dict: Contains discount amount, final total, and promotion details,
                  or error dict if promotion cannot be applied.
        """
        if promotion_id not in self.promotions:
            return {"error": f"Promotion with ID '{promotion_id}' not found"}
            
        promotion = self.promotions[promotion_id]
        current_time = datetime.now()
        
        if not (promotion["start_time"] <= current_time <= promotion["end_time"]):
            return {"error": "Promotion is not currently active"}
            
        criteria = promotion.get("eligibility_criteria", {})
        min_purchase = criteria.get("min_purchase", 0)
        
        if cart_total < min_purchase:
            return {"error": f"Cart total must be at least ${min_purchase} to use this promotion"}
            
        discount_type = promotion["discount_type"]
        discount_value = promotion["discount_value"]
        
        if discount_type == "percentage":
            discount_amount = cart_total * (discount_value / 100)
        elif discount_type == "fixed":
            discount_amount = min(discount_value, cart_total)
        elif discount_type == "free_shipping":
            discount_amount = criteria.get("shipping_cost", 0)
        else:
            discount_amount = 0
            
        final_total = cart_total - discount_amount
        
        return {
            "success": True,
            "original_total": cart_total,
            "discount_amount": round(discount_amount, 2),
            "final_total": round(final_total, 2),
            "promotion_applied": promotion["name"]
        }


__TEST_CASES__ = [
    {
        "name": "test_create_promotion_success",
        "setup": lambda: PromotionManager(),
        "action": lambda pm: pm.create_promotion(
            name="Summer Sale",
            description="20% off all items",
            discount_type="percentage",
            discount_value=20,
            start_time=datetime(2024, 6, 1),
            end_time=datetime(2024, 8, 31)
        ),
        "expected_check": lambda result: result["success"] == True and result["promotion"]["name"] == "Summer Sale"
    },
    {
        "name": "test_create_promotion_invalid_type",
        "setup": lambda: PromotionManager(),
        "action": lambda pm: pm.create_promotion(
            name="Bad Promo",
            description="Invalid",
            discount_type="invalid_type",
            discount_value=10,
            start_time=datetime(2024, 1, 1),
            end_time=datetime(2024, 12, 31)
        ),
        "expected_check": lambda result: "error" in result and "Invalid discount type" in result["error"]
    },
    {
        "name": "test_create_promotion_percentage_over_100",
        "setup": lambda: PromotionManager(),
        "action": lambda pm: pm.create_promotion(
            name="Too Much",
            description="Over 100%",
            discount_type="percentage",
            discount_value=150,
            start_time=datetime(2024, 1, 1),
            end_time=datetime(2024, 12, 31)
        ),
        "expected_check": lambda result: "error" in result and "cannot exceed 100" in result["error"]
    },
    {
        "name": "test_get_promotion_success",
        "setup": lambda: _create_pm_with_promo(),
        "action": lambda pm: pm.get_promotion("test_promo_1"),
        "expected_check": lambda result: result is not None and result["name"] == "Test Promo"
    },
    {
        "name": "test_get_promotion_not_found",
        "setup": lambda: PromotionManager(),
        "action": lambda pm: pm.get_promotion("nonexistent"),
        "expected_check": lambda result: result is None
    },
    {
        "name": "test_update_promotion_success",
        "setup": lambda: _create_pm_with_promo(),
        "action": lambda pm: pm.update_promotion("test_promo_1", name="Updated Promo", discount_value=30),
        "expected_check": lambda result: result["success"] == True and result["promotion"]["name"] == "Updated Promo"
    },
    {
        "name": "test_update_promotion_not_found",
        "setup": lambda: PromotionManager(),
        "action": lambda pm: pm.update_promotion("nonexistent", name="New Name"),
        "expected_check": lambda result: "error" in result and "not found" in result["error"]
    },
    {
        "name": "test_delete_promotion_success",
        "setup": lambda: _create_pm_with_promo(),
        "action": lambda pm: pm.delete_promotion("test_promo_1"),
        "expected_check": lambda result: result["success"] == True and "deleted successfully" in result["message"]
    },
    {
        "name": "test_delete_promotion_not_found",
        "setup": lambda: PromotionManager(),
        "action": lambda pm: pm.delete_promotion("nonexistent"),
        "expected_check": lambda result: "error" in result and "not found" in result["error"]
    },
    {
        "name": "test_apply_promotion_percentage",
        "setup": lambda: _create_active_pm(),
        "action": lambda pm: pm.apply_promotion("active_promo", 100.0),
        "expected_check": lambda result: result["success"] == True and result["discount_amount"] == 20.0 and result["final_total"] == 80.0
    },
    {
        "name": "test_apply_promotion_not_found",
        "setup": lambda: PromotionManager(),
        "action": lambda pm: pm.apply_promotion("nonexistent", 100.0),
        "expected_check": lambda result: "error" in result and "not found" in result["error"]
    },
    {
        "name": "test_list_all_promotions",
        "setup": lambda: _create_pm_with_multiple_promos(),
        "action": lambda pm: pm.list_promotions(),
        "expected_check": lambda result: len(result) == 3
    }
]


def _create_pm_with_promo():
    pm = PromotionManager()
    pm.promotions["test_promo_1"] = {
        "id": "test_promo_1",
        "name": "Test Promo",
        "description": "Test description",
        "discount_type": "percentage",
        "discount_value": 20,
        "start_time": datetime(2024, 1, 1),
        "end_time": datetime(2024, 12, 31),
        "eligibility_criteria": {},
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    return pm


def _create_active_pm():
    pm = PromotionManager()
    pm.promotions["active_promo"] = {
        "id": "active_promo",
        "name": "Active Promo",
        "description": "Currently active",
        "discount_type": "percentage",
        "discount_value": 20,
        "start_time": datetime.now() - timedelta(days=1),
        "end_time": datetime.now() + timedelta(days=1),
        "eligibility_criteria": {},
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    return pm


def _create_pm_with_multiple_promos():
    pm = PromotionManager()
    for i in range(3):
        pm.promotions[f"promo_{i}"] = {
            "id": f"promo_{i}",
            "name": f"Promo {i}",
            "description": f"Description {i}",
            "discount_type": "percentage",
            "discount_value": 10 * (i + 1),
            "start_time": datetime(2024, 1, 1),
            "end_time": datetime(2024, 12, 31),
            "eligibility_criteria": {},
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
    return pm


def run_tests():
    """Run all test cases and report results."""
    passed = 0
    failed = 0
    
    for test in __TEST_CASES__:
        try:
            pm = test["setup"]()
            result = test["action"](pm)
            if test["expected_check"](result):
                print(f"✓ {test['name']} passed")
                passed += 1
            else:
                print(f"✗ {test['name']} failed - unexpected result: {result}")
                failed += 1
        except Exception as e:
            print(f"✗ {test['name']} failed with exception: {e}")
            failed += 1
    
    print(f"\nResults: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    run_tests()