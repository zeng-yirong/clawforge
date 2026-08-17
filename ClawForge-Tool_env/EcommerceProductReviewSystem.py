"""
E-commerce Product Review System Environment API

An e-commerce product review system that manages products, user reviews, and ratings.
Supports browsing, searching, and managing product reviews for consumer decision-making.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime
import re

DEFAULT_STATE: Dict[str, Any] = {
    # Products in the catalog
    "products": {
        "prod_001": {
            "product_id": "prod_001",
            "name": "ProForm Treadmill Pro 2000",
            "brand": "ProForm",
            "category": "fitness equipment",
            "description": "Professional grade treadmill with incline support and heart rate monitor"
        },
        "prod_002": {
            "product_id": "prod_002",
            "name": "Sony WH-1000XM5 Headphones",
            "brand": "Sony",
            "category": "electronics",
            "description": "Premium noise-cancelling wireless headphones with 30-hour battery life"
        },
        "prod_003": {
            "product_id": "prod_003",
            "name": "Instant Pot Duo 7-in-1",
            "brand": "Instant Pot",
            "category": "kitchen appliances",
            "description": "Multi-functional pressure cooker with 7 cooking modes"
        },
        "prod_004": {
            "product_id": "prod_004",
            "name": "Nike Air Max 270",
            "brand": "Nike",
            "category": "footwear",
            "description": "Comfortable running shoes with Max Air unit for cushioning"
        }
    },

    # User reviews
    "reviews": {
        "rev_001": {
            "review_id": "rev_001",
            "product_id": "prod_001",
            "user_id": "user_001",
            "rating": 5,
            "title": "Excellent!",
            "comment": "Excellent treadmill! Very sturdy and quiet operation.",
            "timestamp": "2024-01-15T10:30:00",
            "helpful_votes": 12,
            "unhelpful_votes": 0,
            "is_verified_purchase": True,
            "status": "approved",
            "moderated_by": None,
            "moderated_at": None,
            "moderation_reason": None,
            "seller_response": None
        },
        "rev_002": {
            "review_id": "rev_002",
            "product_id": "prod_001",
            "user_id": "user_002",
            "rating": 4,
            "title": "Good but assembly",
            "comment": "Good quality but assembly took a while.",
            "timestamp": "2024-01-20T14:45:00",
            "helpful_votes": 8,
            "unhelpful_votes": 1,
            "is_verified_purchase": True,
            "status": "approved",
            "moderated_by": None,
            "moderated_at": None,
            "moderation_reason": None,
            "seller_response": None
        },
        "rev_003": {
            "review_id": "rev_003",
            "product_id": "prod_002",
            "user_id": "user_001",
            "rating": 5,
            "title": "Best headphones",
            "comment": "Best headphones I've ever owned. Amazing noise cancellation!",
            "timestamp": "2024-02-01T09:15:00",
            "helpful_votes": 25,
            "unhelpful_votes": 0,
            "is_verified_purchase": True,
            "status": "approved",
            "moderated_by": None,
            "moderated_at": None,
            "moderation_reason": None,
            "seller_response": None
        },
        "rev_004": {
            "review_id": "rev_004",
            "product_id": "prod_003",
            "user_id": "user_003",
            "rating": 3,
            "title": "Steep learning curve",
            "comment": "Works well but the learning curve is steep.",
            "timestamp": "2024-02-10T16:20:00",
            "helpful_votes": 5,
            "unhelpful_votes": 2,
            "is_verified_purchase": True,
            "status": "approved",
            "moderated_by": None,
            "moderated_at": None,
            "moderation_reason": None,
            "seller_response": None
        }
    },

    # Users
    "users": {
        "user_001": {
            "user_id": "user_001",
            "username": "john_fitness",
            "email": "john@example.com",
            "account_status": "active",
            "purchase_history": ["prod_001", "prod_002", "prod_004"],
            "is_admin": False,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "user_002": {
            "user_id": "user_002",
            "username": "sarah_runner",
            "email": "sarah@example.com",
            "account_status": "active",
            "purchase_history": ["prod_001", "prod_003"],
            "is_admin": False,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "user_003": {
            "user_id": "user_003",
            "username": "mike_chef",
            "email": "mike@example.com",
            "account_status": "active",
            "purchase_history": ["prod_003", "prod_004"],
            "is_admin": False,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "user_004": {
            "user_id": "user_004",
            "username": "admin_user",
            "email": "admin@example.com",
            "account_status": "active",
            "purchase_history": [],
            "is_admin": True,
            "created_at": "2024-01-01T00:00:00Z"
        }
    },

    # Current authenticated user
    "current_user_id": "user_001",

    # Review ID counter for generating new IDs
    "next_review_id": 5,

    # Product ID counter for generating new IDs
    "next_product_id": 5,

    # User ID counter for generating new IDs
    "next_user_id": 5
}


class EcommerceProductReviewSystem:
    """
    E-commerce Product Review System API.

    Manages products, user reviews, and ratings for an e-commerce platform.
    Supports browsing, searching, and managing product reviews to facilitate
    consumer decision-making and seller reputation tracking.
    """

    def __init__(self) -> None:
        self.products: Dict[str, Dict[str, Any]] = {}
        self.reviews: Dict[str, Dict[str, Any]] = {}
        self.users: Dict[str, Dict[str, Any]] = {}
        self.current_user_id: Optional[str] = None
        self.next_review_id: int = 1
        self.next_product_id: int = 1
        self.next_user_id: int = 1
        self.review_votes: Dict[str, Dict[str, str]] = {}  # review_id -> {user_id: vote_type}
        self.review_reports: Dict[str, List[Dict]] = {}     # review_id -> list of reports

        self._api_description: str = (
            "E-commerce product review system for managing products, reviews, "
            "and ratings to support consumer decisions and seller reputation tracking."
        )

    def _timestamp(self) -> str:
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        if not scenario:
            scenario = {}
        for key in DEFAULT_STATE:
            if key in scenario:
                setattr(self, key, deepcopy(scenario[key]))
            else:
                setattr(self, key, deepcopy(DEFAULT_STATE[key]))
        # 确保review_votes和review_reports存在（如果scenario没有提供则初始化空）
        if "review_votes" not in scenario:
            self.review_votes = {rid: {} for rid in self.reviews}
        else:
            self.review_votes = deepcopy(scenario["review_votes"])
        if "review_reports" not in scenario:
            self.review_reports = {rid: [] for rid in self.reviews}
        else:
            self.review_reports = deepcopy(scenario["review_reports"])

    def get_env_state(self) -> Dict[str, Any]:
        return {
            "products": deepcopy(self.products),
            "reviews": deepcopy(self.reviews),
            "users": deepcopy(self.users),
            "current_user_id": self.current_user_id,
            "next_review_id": self.next_review_id,
            "next_product_id": self.next_product_id,
            "next_user_id": self.next_user_id,
            "review_votes": deepcopy(self.review_votes),
            "review_reports": deepcopy(self.review_reports)
        }

    def _is_admin(self, user_id: str) -> bool:
        user = self.users.get(user_id)
        return user is not None and user.get("is_admin", False)

    def _validate_email(self, email: str) -> bool:
        if not email or not isinstance(email, str):
            return False
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    # ==================== QUERY OPERATIONS ====================

    def get_product_by_name(self, name: str, exact_match: bool = False) -> Dict[str, Any]:
        if not name:
            return {"error": "Product name cannot be empty"}
        matches = []
        name_lower = name.lower()
        for product in self.products.values():
            product_name_lower = product["name"].lower()
            if exact_match:
                if product_name_lower == name_lower:
                    return {"product": deepcopy(product)}
            else:
                if name_lower in product_name_lower:
                    matches.append(deepcopy(product))
        if exact_match:
            return {"error": f"No product found with exact name: {name}"}
        if not matches:
            return {"error": f"No products found matching: {name}"}
        if len(matches) == 1:
            return {"product": matches[0]}
        return {"products": matches, "count": len(matches)}

    def get_product_by_id(self, product_id: str) -> Dict[str, Any]:
        if not product_id:
            return {"error": "Product ID cannot be empty"}
        product = self.products.get(product_id)
        if not product:
            return {"error": f"Product not found with ID: {product_id}"}
        return {"product": deepcopy(product)}

    def search_products_by_category(self, category: str) -> Dict[str, Any]:
        if not category:
            return {"error": "Category cannot be empty"}
        category_lower = category.lower()
        matches = [
            deepcopy(product)
            for product in self.products.values()
            if product["category"].lower() == category_lower
        ]
        if not matches:
            return {"error": f"No products found in category: {category}"}
        return {"products": matches, "count": len(matches)}

    def list_all_products(self) -> Dict[str, Any]:
        products = [deepcopy(product) for product in self.products.values()]
        return {"products": products, "count": len(products)}

    def get_reviews_by_product_id(self, product_id: str) -> Dict[str, Any]:
        if not product_id:
            return {"error": "Product ID cannot be empty"}
        if product_id not in self.products:
            return {"error": f"Product not found with ID: {product_id}"}
        reviews = [
            deepcopy(review)
            for review in self.reviews.values()
            if review["product_id"] == product_id
        ]
        return {"reviews": reviews, "count": len(reviews)}

    def get_reviews_by_product_name(self, product_name: str) -> Dict[str, Any]:
        if not product_name:
            return {"error": "Product name cannot be empty"}
        product_result = self.get_product_by_name(product_name, exact_match=True)
        if "error" in product_result:
            product_result = self.get_product_by_name(product_name, exact_match=False)
        if "error" in product_result:
            return product_result
        if "product" in product_result:
            product_id = product_result["product"]["product_id"]
        elif "products" in product_result:
            product_id = product_result["products"][0]["product_id"]
        else:
            return {"error": f"Could not resolve product name: {product_name}"}
        return self.get_reviews_by_product_id(product_id)

    def get_review_by_id(self, review_id: str) -> Dict[str, Any]:
        if not review_id:
            return {"error": "Review ID cannot be empty"}
        review = self.reviews.get(review_id)
        if not review:
            return {"error": f"Review not found with ID: {review_id}"}
        return {"review": deepcopy(review)}

    def get_user_by_id(self, user_id: str) -> Dict[str, Any]:
        if not user_id:
            return {"error": "User ID cannot be empty"}
        user = self.users.get(user_id)
        if not user:
            return {"error": f"User not found with ID: {user_id}"}
        return {"user": deepcopy(user)}

    def check_user_purchase_history(self, user_id: str, product_id: str) -> Dict[str, Any]:
        if not user_id:
            return {"error": "User ID cannot be empty"}
        if not product_id:
            return {"error": "Product ID cannot be empty"}
        user = self.users.get(user_id)
        if not user:
            return {"error": f"User not found with ID: {user_id}"}
        if product_id not in self.products:
            return {"error": f"Product not found with ID: {product_id}"}
        has_purchased = product_id in user.get("purchase_history", [])
        return {"user_id": user_id, "product_id": product_id, "has_purchased": has_purchased}

    def get_average_rating_for_product(self, product_id: str) -> Dict[str, Any]:
        if not product_id:
            return {"error": "Product ID cannot be empty"}
        if product_id not in self.products:
            return {"error": f"Product not found with ID: {product_id}"}
        ratings = [
            review["rating"]
            for review in self.reviews.values()
            if review["product_id"] == product_id and review.get("status") == "approved"
        ]
        if not ratings:
            return {"product_id": product_id, "average_rating": None, "review_count": 0, "message": "No approved reviews yet for this product"}
        average = sum(ratings) / len(ratings)
        return {"product_id": product_id, "average_rating": round(average, 2), "review_count": len(ratings)}

    def get_most_helpful_reviews(self, product_id: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        if limit < 1:
            return {"error": "Limit must be at least 1"}
        if product_id and product_id not in self.products:
            return {"error": f"Product not found with ID: {product_id}"}
        if product_id:
            reviews = [deepcopy(review) for review in self.reviews.values() if review["product_id"] == product_id]
        else:
            reviews = [deepcopy(review) for review in self.reviews.values()]
        sorted_reviews = sorted(reviews, key=lambda r: r.get("helpful_votes", 0), reverse=True)[:limit]
        return {"reviews": sorted_reviews, "count": len(sorted_reviews)}

    # ==================== USER MANAGEMENT ====================

    def register_user(self, username: str, email: str, is_admin: bool = False) -> Dict[str, Any]:
        if not username or not username.strip():
            return {"error": "Username cannot be empty"}
        username = username.strip()
        for user in self.users.values():
            if user["username"].lower() == username.lower():
                return {"error": f"Username already exists: {username}"}
        if not self._validate_email(email):
            return {"error": "Invalid email format"}
        for user in self.users.values():
            if user.get("email", "").lower() == email.lower():
                return {"error": f"Email already registered: {email}"}
        user_id = f"user_{self.next_user_id:03d}"
        self.next_user_id += 1
        new_user = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "account_status": "active",
            "purchase_history": [],
            "is_admin": is_admin,
            "created_at": self._timestamp()
        }
        self.users[user_id] = new_user
        return {"success": True, "user": deepcopy(new_user)}

    # ==================== REVIEW OPERATIONS ====================

    def submit_review(self, product_id: str, user_id: str, rating: int, title: str, content: str) -> Dict[str, Any]:
        if not product_id:
            return {"error": "Product ID cannot be empty"}
        if not user_id:
            return {"error": "User ID cannot be empty"}
        if not content:
            return {"error": "Review content cannot be empty"}
        if product_id not in self.products:
            return {"error": f"Product not found with ID: {product_id}"}
        user = self.users.get(user_id)
        if not user:
            return {"error": f"User not found with ID: {user_id}"}
        if user.get("account_status") != "active":
            return {"error": "User account is not active"}
        if product_id not in user.get("purchase_history", []):
            return {"error": "User has not purchased this product and cannot submit a review"}
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return {"error": "Rating must be an integer between 1 and 5"}
        if not title or not title.strip():
            return {"error": "Review title cannot be empty"}
        # check duplicate
        for review in self.reviews.values():
            if review["user_id"] == user_id and review["product_id"] == product_id:
                return {"error": "User has already reviewed this product"}
        review_id = f"rev_{self.next_review_id:03d}"
        self.next_review_id += 1
        is_verified = self.check_user_purchase_history(user_id, product_id).get("has_purchased", False)
        new_review = {
            "review_id": review_id,
            "product_id": product_id,
            "user_id": user_id,
            "rating": rating,
            "title": title.strip(),
            "comment": content.strip(),
            "timestamp": self._timestamp(),
            "helpful_votes": 0,
            "unhelpful_votes": 0,
            "is_verified_purchase": is_verified,
            "status": "pending",
            "moderated_by": None,
            "moderated_at": None,
            "moderation_reason": None,
            "seller_response": None
        }
        self.reviews[review_id] = new_review
        self.review_votes[review_id] = {}
        self.review_reports[review_id] = []
        return {"success": True, "review": deepcopy(new_review)}

    def edit_review(self, review_id: str, user_id: str, rating: Optional[int] = None,
                    title: Optional[str] = None, content: Optional[str] = None) -> Dict[str, Any]:
        if not review_id:
            return {"error": "Review ID cannot be empty"}
        if not user_id:
            return {"error": "User ID cannot be empty"}
        review = self.reviews.get(review_id)
        if not review:
            return {"error": f"Review not found with ID: {review_id}"}
        if user_id not in self.users:
            return {"error": f"User not found with ID: {user_id}"}
        is_owner = review["user_id"] == user_id
        is_admin = self._is_admin(user_id)
        if not is_owner and not is_admin:
            return {"error": "Only the review owner or admin can edit this review"}
        if rating is None and title is None and content is None:
            return {"error": "No changes provided. Specify rating, title, or content to update"}
        if rating is not None:
            if not isinstance(rating, int) or rating < 1 or rating > 5:
                return {"error": "Rating must be an integer between 1 and 5"}
            review["rating"] = rating
        if title is not None:
            if not title.strip():
                return {"error": "Title cannot be empty"}
            review["title"] = title.strip()
        if content is not None:
            if not content.strip():
                return {"error": "Content cannot be empty"}
            review["comment"] = content.strip()
        return {"success": True, "review": deepcopy(review)}

    def update_review(self, user_id: str, review_id: str, rating: Optional[int] = None,
                      title: Optional[str] = None, content: Optional[str] = None) -> Dict[str, Any]:
        # Alias to edit_review for compatibility
        return self.edit_review(review_id, user_id, rating, title, content)

    def delete_review(self, review_id: str, user_id: str) -> Dict[str, Any]:
        if not review_id:
            return {"error": "Review ID cannot be empty"}
        if not user_id:
            return {"error": "User ID cannot be empty"}
        review = self.reviews.get(review_id)
        if not review:
            return {"error": f"Review not found with ID: {review_id}"}
        if user_id not in self.users:
            return {"error": f"User not found with ID: {user_id}"}
        is_owner = review["user_id"] == user_id
        is_admin = self._is_admin(user_id)
        if not is_owner and not is_admin:
            return {"error": "Only the review owner or admin can delete this review"}
        del self.reviews[review_id]
        self.review_votes.pop(review_id, None)
        self.review_reports.pop(review_id, None)
        return {"success": True, "message": f"Review {review_id} has been deleted"}

    def increment_helpful_vote(self, review_id: str, user_id: str) -> Dict[str, Any]:
        if not review_id:
            return {"error": "Review ID cannot be empty"}
        if not user_id:
            return {"error": "User ID cannot be empty"}
        if user_id not in self.users:
            return {"error": f"User not found with ID: {user_id}"}
        review = self.reviews.get(review_id)
        if not review:
            return {"error": f"Review not found with ID: {review_id}"}
        review["helpful_votes"] = review.get("helpful_votes", 0) + 1
        return {"success": True, "review_id": review_id, "helpful_votes": review["helpful_votes"]}

    def vote_review(self, user_id: str, review_id: str, vote_type: str) -> Dict[str, Any]:
        if not user_id:
            return {"error": "User ID cannot be empty"}
        if user_id not in self.users:
            return {"error": f"User not found with ID: {user_id}"}
        if not review_id:
            return {"error": "Review ID cannot be empty"}
        if review_id not in self.reviews:
            return {"error": f"Review not found with ID: {review_id}"}
        if vote_type not in ["helpful", "unhelpful"]:
            return {"error": "vote_type must be 'helpful' or 'unhelpful'"}
        review = self.reviews[review_id]
        if review["user_id"] == user_id:
            return {"error": "Users cannot vote on their own reviews"}
        # Check and update vote
        user_votes = self.review_votes.setdefault(review_id, {})
        if user_id in user_votes:
            old_vote = user_votes[user_id]
            if old_vote == vote_type:
                return {"error": "User has already cast this vote"}
            # Change vote
            if old_vote == "helpful":
                review["helpful_votes"] -= 1
            else:
                review["unhelpful_votes"] -= 1
            user_votes[user_id] = vote_type
            if vote_type == "helpful":
                review["helpful_votes"] += 1
            else:
                review["unhelpful_votes"] += 1
            return {"success": True, "message": "Vote updated", "helpful_votes": review["helpful_votes"], "unhelpful_votes": review["unhelpful_votes"]}
        else:
            user_votes[user_id] = vote_type
            if vote_type == "helpful":
                review["helpful_votes"] += 1
            else:
                review["unhelpful_votes"] += 1
            return {"success": True, "message": "Vote recorded", "helpful_votes": review["helpful_votes"], "unhelpful_votes": review["unhelpful_votes"]}

    def report_review(self, user_id: str, review_id: str, reason: str, description: str = "") -> Dict[str, Any]:
        if not user_id:
            return {"error": "User ID cannot be empty"}
        if user_id not in self.users:
            return {"error": f"User not found with ID: {user_id}"}
        if not review_id:
            return {"error": "Review ID cannot be empty"}
        if review_id not in self.reviews:
            return {"error": f"Review not found with ID: {review_id}"}
        if not reason:
            return {"error": "Report reason cannot be empty"}
        valid_reasons = ["spam", "inappropriate", "fake", "offensive", "other"]
        if reason not in valid_reasons:
            return {"error": f"Invalid reason. Must be one of: {', '.join(valid_reasons)}"}
        review = self.reviews[review_id]
        if review["user_id"] == user_id:
            return {"error": "Users cannot report their own reviews"}
        reports = self.review_reports.setdefault(review_id, [])
        for report in reports:
            if report["user_id"] == user_id:
                return {"error": "You have already reported this review"}
        report_id = f"report_{len(reports)+1}_{review_id}"
        report = {
            "report_id": report_id,
            "user_id": user_id,
            "reason": reason,
            "description": description,
            "status": "pending",
            "created_at": self._timestamp()
        }
        reports.append(report)
        return {"success": True, "message": "Review reported successfully", "report_id": report_id}

    def moderate_review(self, admin_user_id: str, review_id: str, action: str, reason: str = "") -> Dict[str, Any]:
        if not admin_user_id:
            return {"error": "Admin user ID cannot be empty"}
        if admin_user_id not in self.users:
            return {"error": f"User not found with ID: {admin_user_id}"}
        if not self._is_admin(admin_user_id):
            return {"error": "Only admin users can moderate reviews"}
        if not review_id:
            return {"error": "Review ID cannot be empty"}
        if review_id not in self.reviews:
            return {"error": f"Review not found with ID: {review_id}"}
        valid_actions = ["approve", "reject", "flag"]
        if action not in valid_actions:
            return {"error": f"Action must be one of: {', '.join(valid_actions)}"}
        review = self.reviews[review_id]
        if action == "approve":
            review["status"] = "approved"
        elif action == "reject":
            review["status"] = "rejected"
        else:
            review["status"] = "flagged"
        review["moderated_by"] = admin_user_id
        review["moderated_at"] = self._timestamp()
        review["moderation_reason"] = reason if reason else None
        # Resolve pending reports
        for report in self.review_reports.get(review_id, []):
            if report["status"] == "pending":
                report["status"] = "resolved"
                report["resolved_by"] = admin_user_id
                report["resolved_at"] = self._timestamp()
        return {"success": True, "message": f"Review {action}d successfully", "review_id": review_id, "new_status": review["status"]}

    def get_user_reviews(self, user_id: str, include_pending: bool = False) -> Dict[str, Any]:
        if not user_id:
            return {"error": "User ID cannot be empty"}
        if user_id not in self.users:
            return {"error": f"User not found with ID: {user_id}"}
        user_reviews = []
        for review in self.reviews.values():
            if review["user_id"] == user_id:
                if include_pending or review.get("status") == "approved":
                    user_reviews.append(deepcopy(review))
        user_reviews.sort(key=lambda x: x["timestamp"], reverse=True)
        return {"success": True, "user_id": user_id, "total_reviews": len(user_reviews), "reviews": user_reviews}

    def get_product_reviews(self, product_id: str, min_rating: int = None, max_rating: int = None,
                            verified_only: bool = False, sort_by: str = "created_at",
                            sort_order: str = "desc") -> Dict[str, Any]:
        if not product_id:
            return {"error": "Product ID cannot be empty"}
        if product_id not in self.products:
            return {"error": f"Product not found with ID: {product_id}"}
        reviews = [r for r in self.reviews.values()
                   if r["product_id"] == product_id and r.get("status") == "approved"]
        if min_rating is not None:
            if not isinstance(min_rating, int) or min_rating < 1 or min_rating > 5:
                return {"error": "min_rating must be integer 1-5"}
            reviews = [r for r in reviews if r["rating"] >= min_rating]
        if max_rating is not None:
            if not isinstance(max_rating, int) or max_rating < 1 or max_rating > 5:
                return {"error": "max_rating must be integer 1-5"}
            reviews = [r for r in reviews if r["rating"] <= max_rating]
        if verified_only:
            reviews = [r for r in reviews if r.get("is_verified_purchase", False)]
        valid_sort_fields = ["created_at", "rating", "helpful_votes"]
        if sort_by not in valid_sort_fields:
            return {"error": f"Invalid sort_by field. Must be one of: {valid_sort_fields}"}
        if sort_order not in ["asc", "desc"]:
            return {"error": "sort_order must be 'asc' or 'desc'"}
        reverse = sort_order == "desc"
        reviews.sort(key=lambda x: x.get(sort_by, 0) if sort_by != "created_at" else x.get("timestamp", ""), reverse=reverse)
        return {"success": True, "reviews": deepcopy(reviews)}

    def search_reviews(self, product_id: str = None, keyword: str = None, min_rating: int = None,
                       max_rating: int = None, verified_only: bool = False, sort_by: str = "recent",
                       limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        if limit < 1 or limit > 100:
            return {"error": "Limit must be between 1 and 100"}
        if offset < 0:
            return {"error": "Offset cannot be negative"}
        if min_rating is not None and (min_rating < 1 or min_rating > 5):
            return {"error": "Minimum rating must be between 1 and 5"}
        if max_rating is not None and (max_rating < 1 or max_rating > 5):
            return {"error": "Maximum rating must be between 1 and 5"}
        if min_rating is not None and max_rating is not None and min_rating > max_rating:
            return {"error": "Minimum rating cannot be greater than maximum rating"}
        valid_sort = ["recent", "helpful", "rating_high", "rating_low"]
        if sort_by not in valid_sort:
            return {"error": f"Invalid sort option. Must be one of: {', '.join(valid_sort)}"}
        filtered = []
        for review in self.reviews.values():
            if review.get("status") != "approved":
                continue
            if product_id and review["product_id"] != product_id:
                continue
            if keyword:
                kw = keyword.lower()
                if kw not in review.get("title", "").lower() and kw not in review.get("comment", "").lower():
                    continue
            if min_rating is not None and review["rating"] < min_rating:
                continue
            if max_rating is not None and review["rating"] > max_rating:
                continue
            if verified_only and not review.get("is_verified_purchase", False):
                continue
            filtered.append(deepcopy(review))
        # Sort
        if sort_by == "recent":
            filtered.sort(key=lambda x: x["timestamp"], reverse=True)
        elif sort_by == "helpful":
            filtered.sort(key=lambda x: x.get("helpful_votes", 0), reverse=True)
        elif sort_by == "rating_high":
            filtered.sort(key=lambda x: x["rating"], reverse=True)
        else:
            filtered.sort(key=lambda x: x["rating"])
        total = len(filtered)
        paginated = filtered[offset:offset+limit]
        return {"success": True, "total_results": total, "limit": limit, "offset": offset, "reviews": paginated}

    def get_product_rating_summary(self, product_id: str) -> Dict[str, Any]:
        if not product_id:
            return {"error": "Product ID cannot be empty"}
        if product_id not in self.products:
            return {"error": f"Product not found with ID: {product_id}"}
        approved_reviews = [r for r in self.reviews.values()
                           if r["product_id"] == product_id and r.get("status") == "approved"]
        if not approved_reviews:
            return {"success": True, "product_id": product_id, "total_reviews": 0, "average_rating": 0,
                    "rating_distribution": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}}
        total_rating = sum(r["rating"] for r in approved_reviews)
        avg = round(total_rating / len(approved_reviews), 2)
        dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for r in approved_reviews:
            dist[r["rating"]] += 1
        return {"success": True, "product_id": product_id, "total_reviews": len(approved_reviews),
                "average_rating": avg, "rating_distribution": dist}

    def get_review_statistics(self, product_id: str = None) -> Dict[str, Any]:
        if product_id:
            if product_id not in self.products:
                return {"error": f"Product not found with ID: {product_id}"}
            reviews = [r for r in self.reviews.values() if r["product_id"] == product_id]
        else:
            reviews = list(self.reviews.values())
        if not reviews:
            return {"success": True, "total_reviews": 0, "approved_reviews": 0, "pending_reviews": 0,
                    "rejected_reviews": 0, "average_rating": 0, "verified_purchase_percentage": 0,
                    "total_helpful_votes": 0}
        total = len(reviews)
        approved = len([r for r in reviews if r.get("status") == "approved"])
        pending = len([r for r in reviews if r.get("status") == "pending"])
        rejected = len([r for r in reviews if r.get("status") == "rejected"])
        approved_list = [r for r in reviews if r.get("status") == "approved"]
        avg = round(sum(r["rating"] for r in approved_list) / len(approved_list), 2) if approved_list else 0
        verified = len([r for r in reviews if r.get("is_verified_purchase", False)])
        verified_pct = round((verified / total) * 100, 2) if total else 0
        total_helpful = sum(r.get("helpful_votes", 0) for r in reviews)
        return {"success": True, "total_reviews": total, "approved_reviews": approved, "pending_reviews": pending,
                "rejected_reviews": rejected, "average_rating": avg, "verified_purchase_percentage": verified_pct,
                "total_helpful_votes": total_helpful}

    def add_review_response(self, seller_id: str, review_id: str, response_text: str) -> Dict[str, Any]:
        if not seller_id:
            return {"error": "Seller ID cannot be empty"}
        if seller_id not in self.users:
            return {"error": f"User not found with ID: {seller_id}"}
        if not review_id:
            return {"error": "Review ID cannot be empty"}
        if review_id not in self.reviews:
            return {"error": f"Review not found with ID: {review_id}"}
        if not response_text or not response_text.strip():
            return {"error": "Response text cannot be empty"}
        if len(response_text) > 2000:
            return {"error": "Response text cannot exceed 2000 characters"}
        review = self.reviews[review_id]
        product = self.products.get(review["product_id"])
        if not product:
            return {"error": "Product not found"}
        # Check if seller is admin or product seller (not implemented yet, use is_admin for simplicity)
        if not self._is_admin(seller_id):
            return {"error": "Only admins can respond to reviews (seller validation not implemented)"}
        if review.get("seller_response"):
            return {"error": "A response has already been added to this review"}
        review["seller_response"] = {
            "seller_id": seller_id,
            "text": response_text.strip(),
            "created_at": self._timestamp()
        }
        return {"success": True, "message": "Response added successfully", "review_id": review_id}

    def bulk_delete_reviews_by_product(self, product_id: str, admin_user_id: str) -> Dict[str, Any]:
        if not product_id:
            return {"error": "Product ID cannot be empty"}
        if not admin_user_id:
            return {"error": "Admin user ID cannot be empty"}
        if admin_user_id not in self.users:
            return {"error": f"User not found with ID: {admin_user_id}"}
        if not self._is_admin(admin_user_id):
            return {"error": "Only admin users can perform bulk delete operations"}
        if product_id not in self.products:
            return {"error": f"Product not found with ID: {product_id}"}
        reviews_to_delete = [rid for rid, rev in self.reviews.items() if rev["product_id"] == product_id]
        for rid in reviews_to_delete:
            del self.reviews[rid]
            self.review_votes.pop(rid, None)
            self.review_reports.pop(rid, None)
        return {"success": True, "product_id": product_id, "deleted_count": len(reviews_to_delete),
                "message": f"Deleted {len(reviews_to_delete)} reviews for product {product_id}"}

    def update_product_info(self, product_id: str, admin_user_id: str, name: Optional[str] = None,
                            brand: Optional[str] = None, category: Optional[str] = None,
                            description: Optional[str] = None) -> Dict[str, Any]:
        if not product_id:
            return {"error": "Product ID cannot be empty"}
        if not admin_user_id:
            return {"error": "Admin user ID cannot be empty"}
        if admin_user_id not in self.users:
            return {"error": f"User not found with ID: {admin_user_id}"}
        if not self._is_admin(admin_user_id):
            return {"error": "Only admin users can update product information"}
        product = self.products.get(product_id)
        if not product:
            return {"error": f"Product not found with ID: {product_id}"}
        if all(v is None for v in [name, brand, category, description]):
            return {"error": "No changes provided. Specify at least one field to update"}
        if name is not None:
            if not name.strip():
                return {"error": "Product name cannot be empty"}
            product["name"] = name.strip()
        if brand is not None:
            if not brand.strip():
                return {"error": "Brand cannot be empty"}
            product["brand"] = brand.strip()
        if category is not None:
            if not category.strip():
                return {"error": "Category cannot be empty"}
            product["category"] = category.strip()
        if description is not None:
            product["description"] = description
        return {"success": True, "product": deepcopy(product)}

    def add_product(self, admin_user_id: str, name: str, brand: str, category: str, description: str) -> Dict[str, Any]:
        if not admin_user_id:
            return {"error": "Admin user ID cannot be empty"}
        if admin_user_id not in self.users:
            return {"error": f"User not found with ID: {admin_user_id}"}
        if not self._is_admin(admin_user_id):
            return {"error": "Only admin users can add products"}
        if not name or not name.strip():
            return {"error": "Product name cannot be empty"}
        if not brand or not brand.strip():
            return {"error": "Brand cannot be empty"}
        if not category or not category.strip():
            return {"error": "Category cannot be empty"}
        if not description:
            return {"error": "Description cannot be empty"}
        product_id = f"prod_{self.next_product_id:03d}"
        self.next_product_id += 1
        new_product = {
            "product_id": product_id,
            "name": name.strip(),
            "brand": brand.strip(),
            "category": category.strip(),
            "description": description
        }
        self.products[product_id] = new_product
        return {"success": True, "product": deepcopy(new_product)}


# Test cases for the E-commerce Product Review System
__TEST_CASES__ = [
    {
        "name": "register_user_success",
        "input": {
            "action": "register_user",
            "params": {
                "username": "john_doe",
                "email": "john@example.com"
            }
        },
        "expected_code": 0,
        "expected_behavior": "Should successfully register a new user and return user info with user_id"
    },
    {
        "name": "register_user_empty_username",
        "input": {
            "action": "register_user",
            "params": {
                "username": "",
                "email": "john@example.com"
            }
        },
        "expected_code": 1,
        "expected_behavior": "Should return error for empty username"
    },
    {
        "name": "register_user_duplicate_username",
        "input": {
            "action": "register_user",
            "params": {
                "username": "john_fitness",
                "email": "new@example.com"
            }
        },
        "expected_code": 1,
        "expected_behavior": "Should return error if username already exists"
    },
    {
        "name": "submit_review_success",
        "input": {
            "action": "submit_review",
            "params": {
                "user_id": "user_001",
                "product_id": "prod_001",
                "rating": 5,
                "title": "Great product!",
                "content": "I love this product, highly recommend it."
            }
        },
        "expected_code": 0,
        "expected_behavior": "Should successfully submit review and return review info"
    },
    {
        "name": "submit_review_invalid_rating",
        "input": {
            "action": "submit_review",
            "params": {
                "user_id": "user_001",
                "product_id": "prod_001",
                "rating": 6,
                "title": "Great product!",
                "content": "I love this product."
            }
        },
        "expected_code": 1,
        "expected_behavior": "Should return error for rating outside 1-5 range"
    },
    {
        "name": "submit_review_product_not_found",
        "input": {
            "action": "submit_review",
            "params": {
                "user_id": "user_001",
                "product_id": "nonexistent_prod",
                "rating": 4,
                "title": "Good",
                "content": "Nice product"
            }
        },
        "expected_code": 1,
        "expected_behavior": "Should return error if product does not exist"
    },
    {
        "name": "vote_review_helpful",
        "input": {
            "action": "vote_review",
            "params": {
                "user_id": "user_002",
                "review_id": "rev_001",
                "vote_type": "helpful"
            }
        },
        "expected_code": 0,
        "expected_behavior": "Should successfully record helpful vote"
    },
    {
        "name": "vote_review_own_review",
        "input": {
            "action": "vote_review",
            "params": {
                "user_id": "user_001",
                "review_id": "rev_001",
                "vote_type": "helpful"
            }
        },
        "expected_code": 1,
        "expected_behavior": "Should return error when voting on own review"
    },
    {
        "name": "moderate_review_approve",
        "input": {
            "action": "moderate_review",
            "params": {
                "admin_user_id": "user_004",
                "review_id": "rev_001",
                "action": "approve"
            }
        },
        "expected_code": 0,
        "expected_behavior": "Should approve the review and update status"
    },
    {
        "name": "moderate_review_non_admin",
        "input": {
            "action": "moderate_review",
            "params": {
                "admin_user_id": "user_001",
                "review_id": "rev_001",
                "action": "approve"
            }
        },
        "expected_code": 1,
        "expected_behavior": "Should return error when non-admin tries to moderate"
    },
    {
        "name": "get_product_rating_summary",
        "input": {
            "action": "get_product_rating_summary",
            "params": {
                "product_id": "prod_001"
            }
        },
        "expected_code": 0,
        "expected_behavior": "Should return average rating and rating distribution"
    },
    {
        "name": "search_reviews_keyword",
        "input": {
            "action": "search_reviews",
            "params": {
                "keyword": "treadmill",
                "sort_by": "recent",
                "limit": 10
            }
        },
        "expected_code": 0,
        "expected_behavior": "Should return reviews matching keyword"
    },
    {
        "name": "delete_review_by_owner",
        "input": {
            "action": "delete_review",
            "params": {
                "user_id": "user_001",
                "review_id": "rev_003"
            }
        },
        "expected_code": 0,
        "expected_behavior": "Should successfully delete the review"
    },
    {
        "name": "add_product_success",
        "input": {
            "action": "add_product",
            "params": {
                "admin_user_id": "user_004",
                "name": "Wireless Mouse",
                "brand": "TechBrand",
                "category": "Electronics",
                "description": "A high-quality wireless mouse"
            }
        },
        "expected_code": 0,
        "expected_behavior": "Should successfully add product and return product info"
    }
]