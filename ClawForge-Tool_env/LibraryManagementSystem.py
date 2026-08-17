from copy import deepcopy
from typing import Dict, List, Optional, Union, Any
from datetime import datetime, timedelta

DEFAULT_STATE = {
    "books": {
        "B001": {"title": "Design Patterns", "author": "Erich Gamma", "total_copies": 2, "available": 0,
                 "waitlist": ["bob"]},
        "B002": {"title": "Clean Code", "author": "Robert C. Martin", "total_copies": 5, "available": 4,
                 "waitlist": []},
        "B003": {"title": "Deep Learning", "author": "Ian Goodfellow", "total_copies": 1, "available": 1,
                 "waitlist": []}
    },
    "user_accounts": {
        "alice": {
            "borrowed": [{"book_id": "B001", "due_date": "2026-03-01", "renewals": 0}],
            "fines": 0.0
        },
        "bob": {
            "borrowed": [{"book_id": "B001", "due_date": "2026-03-15", "renewals": 1}],
            "fines": 2.50
        }
    },
    "current_user": None,
    "system_date": "2026-03-05"  # Mock date for fine calculations
}


class LibraryAPI:
    """
    Advanced Library Management API supporting waitlists, fines, renewals, and due-date tracking.

    Attributes:
        books (Dict): Book catalog with availability and waitlist queues.
        user_accounts (Dict): User records including borrowed items and accumulated fines.
        current_user (Optional[str]): Authenticated session user.
        system_date (str): Simulated current date for logical calculations.
    """

    def __init__(self):
        self.books: Dict[str, Dict[str, Union[str, int, List[str]]]] = {}
        self.user_accounts: Dict[str, Dict[str, Union[List[dict], float]]] = {}
        self.current_user: Optional[str] = None
        self.system_date: str = "2026-03-05"
        self.max_renewals = 2
        self.fine_per_day = 0.50
        self._api_description = "Advanced library tool handling borrowing, waitlists, fines, and renewals."
        self._load_scenario(deepcopy(DEFAULT_STATE))

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load a specific scenario into the environment state.

        Args:
            scenario (dict): Dictionary containing the state to load.
            long_context (bool, optional): Unused parameter for long context mode. Defaults to False.

        Returns:
            None
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_STATE)
        self.books = scenario.get("books", DEFAULT_STATE_COPY["books"])
        self.user_accounts = scenario.get("user_accounts", DEFAULT_STATE_COPY["user_accounts"])
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])
        self.system_date = scenario.get("system_date", DEFAULT_STATE_COPY["system_date"])

    def get_env_state(self) -> Dict[str, Any]:
        """
        Get the current environment state.

        Returns:
            Dict[str, Any]: Dictionary representing the current state of books, user accounts, current user, and system date.
        """
        return {
            "books": self.books,
            "user_accounts": self.user_accounts,
            "current_user": self.current_user,
            "system_date": self.system_date
        }

    def lib_login(self, username: str) -> Dict[str, str]:
        """
        Log in a user, initializing their account if it does not exist.

        Args:
            username (str): The username to log in.

        Returns:
            Dict[str, str]: Status message or error dictionary.
        """
        if not username:
            return {"error": "Username required."}
        self.current_user = username
        if username not in self.user_accounts:
            self.user_accounts[username] = {"borrowed": [], "fines": 0.0}
        return {"status": f"Logged in as {username}."}

    def _timestamp(self) -> datetime:
        """
        Get the current system date as a datetime object.

        Returns:
            datetime: The simulated current date.
        """
        return datetime.strptime(self.system_date, "%Y-%m-%d")

    def reserve_book(self, book_id: str) -> Dict[str, str]:
        """
        Add the current user to the waitlist for a specific book.

        Args:
            book_id (str): The ID of the book to reserve.

        Returns:
            Dict[str, str]: Status message or error dictionary.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if book_id not in self.books:
            return {"error": "Book not found."}

        book_data = self.books[book_id]
        if self.current_user in book_data["waitlist"]:
            return {"error": "You are already on the waitlist."}

        book_data["waitlist"].append(self.current_user)
        position = len(book_data["waitlist"])
        return {"status": f"Added to waitlist. Your position is {position}."}

    def borrow_book(self, book_id: str) -> Dict[str, str]:
        """
        Attempt to borrow a book. Fails if user has outstanding fines.

        Args:
            book_id (str): The ID of the book to borrow.

        Returns:
            Dict[str, str]: Status message or error dictionary.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if book_id not in self.books:
            return {"error": "Book not found."}

        user_data = self.user_accounts[self.current_user]
        if user_data["fines"] > 0:
            return {"error": f"Cannot borrow. You have outstanding fines: ${user_data['fines']:.2f}."}

        book_data = self.books[book_id]
        if book_data["available"] <= 0:
            return {"error": "Book currently unavailable. Please use reserve_book() to join waitlist."}

        # If there's a waitlist, ensure the current user is first
        if book_data["waitlist"] and book_data["waitlist"][0] != self.current_user:
            return {"error": "Book reserved for another user on the waitlist."}

        if book_data["waitlist"] and book_data["waitlist"][0] == self.current_user:
            book_data["waitlist"].pop(0)  # Remove user from waitlist upon borrowing

        book_data["available"] -= 1
        due_date = (self._timestamp() + timedelta(days=14)).strftime("%Y-%m-%d")

        user_data["borrowed"].append({
            "book_id": book_id,
            "due_date": due_date,
            "renewals": 0
        })

        return {"status": f"Successfully borrowed. Due date is {due_date}."}

    def renew_book(self, book_id: str) -> Dict[str, str]:
        """
        Extend the due date if max renewals not reached, no waitlist exists, and no fines/overdue.

        Args:
            book_id (str): The ID of the book to renew.

        Returns:
            Dict[str, str]: Status message or error dictionary.
        """
        if not self.current_user:
            return {"error": "Authentication required."}

        user_data = self.user_accounts[self.current_user]

        # 1. Check for outstanding recorded fines
        if user_data["fines"] > 0:
            return {"error": f"Cannot renew. You have outstanding fines: ${user_data['fines']:.2f}."}

        user_borrowed = user_data["borrowed"]
        book_record = next((b for b in user_borrowed if b["book_id"] == book_id), None)

        if not book_record:
            return {"error": "You have not borrowed this book."}

        # 2. Implicit overdue check
        current_due = datetime.strptime(book_record["due_date"], "%Y-%m-%d")
        sys_date = self._timestamp()
        days_overdue = (sys_date - current_due).days

        if days_overdue > 0:
            pending_fine = days_overdue * self.fine_per_day
            return {
                "error": f"Cannot renew an overdue book. You have a pending fine of ${pending_fine:.2f}. Please return the book."}

        # 3. Check for waitlist
        if self.books[book_id]["waitlist"]:
            return {"error": "Cannot renew. There is a waitlist for this book."}

        # 4. Check for max renewals
        if book_record["renewals"] >= self.max_renewals:
            return {"error": f"Cannot renew. Maximum renewals ({self.max_renewals}) reached."}

        # 5. Renew successfully
        new_due = (current_due + timedelta(days=7)).strftime("%Y-%m-%d")

        book_record["due_date"] = new_due
        book_record["renewals"] += 1

        return {"status": f"Book renewed successfully. New due date is {new_due}."}

    def return_book(self, book_id: str) -> Dict[str, Union[str, float]]:
        """
        Return a book and calculate overdue fines if applicable.

        Args:
            book_id (str): The ID of the book to return.

        Returns:
            Dict[str, Union[str, float]]: Status message and potential warnings, or error dictionary.
        """
        if not self.current_user:
            return {"error": "Authentication required."}

        user_data = self.user_accounts[self.current_user]
        book_record_idx = next((i for i, b in enumerate(user_data["borrowed"]) if b["book_id"] == book_id), -1)

        if book_record_idx == -1:
            return {"error": "You have not borrowed this book."}

        book_record = user_data["borrowed"].pop(book_record_idx)
        self.books[book_id]["available"] += 1

        # Calculate fine
        due_date = datetime.strptime(book_record["due_date"], "%Y-%m-%d")
        sys_date = self._timestamp()
        days_overdue = (sys_date - due_date).days

        fine_incurred = 0.0
        if days_overdue > 0:
            fine_incurred = days_overdue * self.fine_per_day
            user_data["fines"] += fine_incurred

        response = {"status": "Book returned."}
        if fine_incurred > 0:
            response["warning"] = f"Book returned late. Fine incurred: ${fine_incurred:.2f}"

        return response

    def pay_fines(self, amount: float) -> Dict[str, str]:
        """
        Pay down library fines.

        Args:
            amount (float): The amount to pay.

        Returns:
            Dict[str, str]: Status message or error dictionary.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if not isinstance(amount, (int, float)):
            return {"error": "Amount must be a number."}
        if amount <= 0:
            return {"error": "Payment amount must be positive."}

        user_data = self.user_accounts[self.current_user]
        user_data["fines"] = max(0.0, user_data["fines"] - amount)

        return {"status": f"Payment applied. Remaining balance: ${user_data['fines']:.2f}"}

    def search_books(self, query: str) -> List[Dict[str, str]]:
        """
        Search for books by title or author keywords.

        Args:
            query (str): The keyword to search for.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing matching book details and their IDs.
        """
        if not isinstance(query, str) or not query.strip():
            return []
            
        query_lower = query.lower()
        results = []
        for book_id, book_info in self.books.items():
            title = str(book_info.get("title", ""))
            author = str(book_info.get("author", ""))
            if query_lower in title.lower() or query_lower in author.lower():
                results.append({
                    "book_id": book_id,
                    "title": title,
                    "author": author
                })
        return results

    def get_my_account(self) -> Dict[str, Any]:
        """
        Get the local view of the currently logged-in user's account.

        Returns:
            Dict[str, Any]: A dictionary with borrowed books, due dates, fines, and current waitlisted reservations.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
            
        user_data = self.user_accounts[self.current_user]
        
        waitlisted_books = []
        for book_id, book_info in self.books.items():
            waitlist = book_info.get("waitlist", [])
            if isinstance(waitlist, list) and self.current_user in waitlist:
                waitlisted_books.append(book_id)
                
        return {
            "username": self.current_user,
            "borrowed": user_data.get("borrowed", []),
            "fines": user_data.get("fines", 0.0),
            "waitlisted_books": waitlisted_books
        }

    def cancel_reservation(self, book_id: str) -> Dict[str, str]:
        """
        Cancel a waitlist reservation for a specific book.

        Args:
            book_id (str): The ID of the book to cancel the reservation for.

        Returns:
            Dict[str, str]: Status message or error dictionary.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
        if book_id not in self.books:
            return {"error": "Book not found."}
            
        waitlist = self.books[book_id].get("waitlist", [])
        if self.current_user not in waitlist:
            return {"error": "You are not on the waitlist for this book."}
            
        waitlist.remove(self.current_user)
        return {"status": "Reservation cancelled successfully."}

    def advance_time(self, days: int) -> Dict[str, str]:
        """
        Simulate the passage of time by advancing the system date.

        Args:
            days (int): The number of days to advance.

        Returns:
            Dict[str, str]: Status message or error dictionary.
        """
        if not isinstance(days, int):
            return {"error": "Days must be an integer."}
        if days <= 0:
            return {"error": "Days must be a positive integer."}
            
        current_date = self._timestamp()
        new_date = current_date + timedelta(days=days)
        self.system_date = new_date.strftime("%Y-%m-%d")
        
        return {"status": f"System date advanced by {days} days to {self.system_date}."}

    def get_book_details(self, book_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific book, including waitlist length.

        Args:
            book_id (str): The ID of the book.

        Returns:
            Dict[str, Any]: Book details or error dictionary.
        """
        if book_id not in self.books:
            return {"error": "Book not found."}
            
        book_info = self.books[book_id]
        waitlist = book_info.get("waitlist", [])
        return {
            "book_id": book_id,
            "title": book_info.get("title"),
            "author": book_info.get("author"),
            "total_copies": book_info.get("total_copies"),
            "available": book_info.get("available"),
            "waitlist_length": len(waitlist) if isinstance(waitlist, list) else 0
        }

    def lib_logout(self) -> Dict[str, str]:
        """
        Log out the current user, clearing the session.

        Returns:
            Dict[str, str]: Status message or error dictionary.
        """
        if not self.current_user:
            return {"error": "No user currently logged in."}
            
        username = self.current_user
        self.current_user = None
        return {"status": f"User {username} successfully logged out."}

    def report_lost_book(self, book_id: str) -> Dict[str, str]:
        """
        Report a borrowed book as lost. The book will be removed from borrowed items, 
        and a replacement fee will be added to the user's account.

        Args:
            book_id (str): The ID of the lost book.

        Returns:
            Dict[str, str]: Status message or error dictionary.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
            
        user_data = self.user_accounts[self.current_user]
        book_record_idx = next((i for i, b in enumerate(user_data["borrowed"]) if b["book_id"] == book_id), -1)

        if book_record_idx == -1:
            return {"error": "You have not borrowed this book."}

        user_data["borrowed"].pop(book_record_idx)
        
        if book_id in self.books:
            self.books[book_id]["total_copies"] = max(0, int(self.books[book_id]["total_copies"]) - 1)
            
        lost_fee = 20.0
        user_data["fines"] += lost_fee
        
        return {"status": f"Book '{book_id}' reported lost. A replacement fee of ${lost_fee:.2f} has been added to your account."}

    def get_library_policies(self) -> Dict[str, Any]:
        """
        Retrieve the library's system rules and configurations.

        Returns:
            Dict[str, Any]: Dictionary containing policy parameters.
        """
        return {
            "max_renewals": self.max_renewals,
            "fine_per_day": self.fine_per_day,
            "standard_borrow_days": 14,
            "lost_book_fee": 20.0
        }

    def donate_book(self, title: str, author: str, copies: int) -> Dict[str, str]:
        """
        Donate new books or copies to the library.

        Args:
            title (str): Title of the book.
            author (str): Author of the book.
            copies (int): Number of copies to donate.

        Returns:
            Dict[str, str]: Status message or error dictionary.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
            
        if not isinstance(copies, int) or copies <= 0:
            return {"error": "Copies must be a positive integer."}
            
        if not title or not author:
            return {"error": "Title and author are required."}

        # Check for existing book
        for b_id, b_info in self.books.items():
            if str(b_info.get("title", "")).lower() == title.lower() and str(b_info.get("author", "")).lower() == author.lower():
                self.books[b_id]["total_copies"] += copies
                self.books[b_id]["available"] += copies
                return {"status": f"Donated {copies} copies to existing book {b_id}."}
                
        # Create new book ID
        existing_ids = [int(k[1:]) for k in self.books.keys() if k.startswith('B') and k[1:].isdigit()]
        next_id_num = max(existing_ids) + 1 if existing_ids else 1
        new_id = f"B{next_id_num:03d}"
        
        self.books[new_id] = {
            "title": title,
            "author": author,
            "total_copies": copies,
            "available": copies,
            "waitlist": []
        }
        return {"status": f"Donated {copies} copies. New book created with ID {new_id}."}

    def check_waitlist_status(self) -> Union[List[Dict[str, Any]], Dict[str, str]]:
        """
        Check the queue position and availability for all currently waitlisted books.

        Returns:
            Union[List[Dict[str, Any]], Dict[str, str]]: List of waitlist statuses or error dictionary.
        """
        if not self.current_user:
            return {"error": "Authentication required."}
            
        status_list = []
        for book_id, book_info in self.books.items():
            waitlist = book_info.get("waitlist", [])
            if isinstance(waitlist, list) and self.current_user in waitlist:
                position = waitlist.index(self.current_user) + 1
                status_list.append({
                    "book_id": book_id,
                    "title": book_info.get("title", ""),
                    "position": position,
                    "available": book_info.get("available", 0)
                })
                
        return status_list


__TEST_CASES__ = [
    {
        'name': 'Error path: Renew overdue book with waitlist',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='alice')"},
            {'expect_success': False, 'tool_call': "env['library'].renew_book(book_id='B001')"}
        ]
    },
    {
        'name': 'Normal path: Return overdue book, pay fines, verify state',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['library'].return_book(book_id='B001')"},
            {'expect_success': True, 'tool_call': "env['library'].pay_fines(amount=1.0)"},
            {'expect_success': True, 'tool_call': "env['library'].get_env_state()"}
        ]
    },
    {
        'name': 'Error path: Borrow with outstanding fines',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='bob')"},
            {'expect_success': False, 'tool_call': "env['library'].borrow_book(book_id='B002')"}
        ]
    },
    {
        'name': 'Cross-method workflow: Pay fines, borrow, and renew',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='bob')"},
            {'expect_success': True, 'tool_call': "env['library'].pay_fines(amount=2.5)"},
            {'expect_success': True, 'tool_call': "env['library'].borrow_book(book_id='B002')"},
            {'expect_success': True, 'tool_call': "env['library'].renew_book(book_id='B002')"}
        ]
    },
    {
        'name': 'Normal path: Borrow book and verify state',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='charlie')"},
            {'expect_success': True, 'tool_call': "env['library'].borrow_book(book_id='B003')"},
            {'expect_success': True, 'tool_call': "env['library'].get_env_state()"}
        ]
    },
    {
        'name': 'State-change verification: Reserve unavailable book',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='dave')"},
            {'expect_success': False, 'tool_call': "env['library'].borrow_book(book_id='B001')"},
            {'expect_success': True, 'tool_call': "env['library'].reserve_book(book_id='B001')"},
            {'expect_success': True, 'tool_call': "env['library'].get_env_state()"}
        ]
    },
    {
        'name': 'Error path: Non-existent IDs',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='eve')"},
            {'expect_success': False, 'tool_call': "env['library'].borrow_book(book_id='B999')"},
            {'expect_success': False, 'tool_call': "env['library'].reserve_book(book_id='B999')"},
            {'expect_success': False, 'tool_call': "env['library'].renew_book(book_id='B999')"},
            {'expect_success': False, 'tool_call': "env['library'].return_book(book_id='B999')"}
        ]
    },
    {
        'name': 'Boundary and Error: Negative fines, zero, empty strings, missing fields',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='frank')"},
            {'expect_success': False, 'tool_call': "env['library'].pay_fines(amount=-10.0)"},
            {'expect_success': False, 'tool_call': "env['library'].pay_fines(amount=0.0)"},
            {'expect_success': False, 'tool_call': "env['library'].borrow_book(book_id='')"},
            {'expect_success': False, 'tool_call': "env['library'].borrow_book()"}
        ]
    },
    {
        'name': 'Cross-method workflow: Complete lifecycle (borrow, renew, return)',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='grace')"},
            {'expect_success': True, 'tool_call': "env['library'].borrow_book(book_id='B002')"},
            {'expect_success': True, 'tool_call': "env['library'].renew_book(book_id='B002')"},
            {'expect_success': True, 'tool_call': "env['library'].return_book(book_id='B002')"},
            {'expect_success': True, 'tool_call': "env['library'].get_env_state()"}
        ]
    },
    {
        'name': 'Boundary and Error: Excessively long strings and wrong types',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='a_very_long_username_that_exceeds_normal_limits_for_a_system_1234567890')"},
            {'expect_success': True, 'tool_call': "env['library'].borrow_book(book_id='B002')"},
            {'expect_success': False, 'tool_call': "env['library'].pay_fines(amount='not_a_float')"}
        ]
    },
    {
        'name': 'New Methods: Search and Book Details',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].search_books(query='Design')"},
            {'expect_success': True, 'tool_call': "env['library'].get_book_details(book_id='B001')"},
            {'expect_success': False, 'tool_call': "env['library'].get_book_details(book_id='B999')"}
        ]
    },
    {
        'name': 'New Methods: Account info and cancellation',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['library'].get_my_account()"},
            {'expect_success': True, 'tool_call': "env['library'].reserve_book(book_id='B001')"},
            {'expect_success': True, 'tool_call': "env['library'].get_my_account()"},
            {'expect_success': True, 'tool_call': "env['library'].cancel_reservation(book_id='B001')"},
            {'expect_success': False, 'tool_call': "env['library'].cancel_reservation(book_id='B001')"}
        ]
    },
    {
        'name': 'New Methods: Advance time and incur fines',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='charlie')"},
            {'expect_success': True, 'tool_call': "env['library'].borrow_book(book_id='B002')"},
            {'expect_success': True, 'tool_call': "env['library'].advance_time(days=20)"},
            {'expect_success': True, 'tool_call': "env['library'].return_book(book_id='B002')"},
            {'expect_success': True, 'tool_call': "env['library'].get_my_account()"}
        ]
    },
    {
        'name': 'New Methods: Logout',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='dave')"},
            {'expect_success': True, 'tool_call': "env['library'].lib_logout()"},
            {'expect_success': False, 'tool_call': "env['library'].lib_logout()"},
            {'expect_success': False, 'tool_call': "env['library'].get_my_account()"}
        ]
    },
    {
        'name': 'New Methods: Report lost book',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['library'].report_lost_book(book_id='B001')"},
            {'expect_success': False, 'tool_call': "env['library'].report_lost_book(book_id='B002')"},
            {'expect_success': True, 'tool_call': "env['library'].get_my_account()"}
        ]
    },
    {
        'name': 'New Methods: Library policies',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].get_library_policies()"}
        ]
    },
    {
        'name': 'New Methods: Donate book',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['library'].donate_book(title='New Book', author='New Author', copies=3)"},
            {'expect_success': True, 'tool_call': "env['library'].donate_book(title='Clean Code', author='Robert C. Martin', copies=2)"},
            {'expect_success': False, 'tool_call': "env['library'].donate_book(title='', author='', copies=-1)"}
        ]
    },
    {
        'name': 'New Methods: Waitlist status',
        'steps': [
            {'expect_success': True, 'tool_call': "env['library'].lib_login(username='alice')"},
            {'expect_success': True, 'tool_call': "env['library'].reserve_book(book_id='B003')"},
            {'expect_success': True, 'tool_call': "env['library'].check_waitlist_status()"},
            {'expect_success': True, 'tool_call': "env['library'].lib_logout()"},
            {'expect_success': False, 'tool_call': "env['library'].check_waitlist_status()"}
        ]
    }
]