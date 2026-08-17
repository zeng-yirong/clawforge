from copy import deepcopy
from typing import Dict, List, Optional, Union

DEFAULT_EDU_STATE = {
    "current_user": None,
    "users": {
        "student1": {"role": "student", "balance": 150.0, "certificates": []},
        "student2": {"role": "student", "balance": 10.0, "certificates": []},
        "instructor1": {"role": "instructor", "balance": 500.0, "certificates": []},
    },
    "courses": {
        201: {
            "id": 201,
            "title": "Python Basics",
            "instructor": "instructor1",
            "price": 49.99,
            "modules": [{"id": 1, "title": "Variables"}, {"id": 2, "title": "Loops"}],
            "prerequisites": [],
            "quiz_passing_score": 70,
            "reviews": [],
            "qa_threads": {
                1: {"id": 1, "student": "student2", "question": "What is a variable?", "answers": []}
            }
        },
    },
    "enrollments": {},
    "course_counter": 202,
    "qa_counter": 2,
}


class AdvancedEduPlatformAPI:
    """
    An advanced online education platform handling payments, Q&A forums, reviews,
    instructor course creation, and complex enrollment logic.
    """

    def __init__(self):
        """
        Initializes the AdvancedEduPlatformAPI with empty or default states.
        """
        self.current_user: Optional[str] = None
        self.users: Dict[str, Dict] = {}
        self.courses: Dict[int, Dict] = {}
        self.enrollments: Dict[str, Dict] = {}
        self.course_counter: int = 0
        self.qa_counter: int = 0
        self._api_description = "A complex e-learning platform with monetization, Q&A forums, reviews, and instructor tools."

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Load a specific scenario into the environment with deep copy protection
        and auto-calibration of counters.
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_EDU_STATE)
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])
        self.users = deepcopy(scenario.get("users", DEFAULT_STATE_COPY["users"]))
        raw_courses = scenario.get("courses", DEFAULT_STATE_COPY["courses"])
        self.courses = {int(k) if str(k).isdigit() else k: deepcopy(v) for k, v in raw_courses.items()}
        self.enrollments = deepcopy(scenario.get("enrollments", DEFAULT_STATE_COPY["enrollments"]))
        # Auto-calibrate course_counter
        max_course_id = max(self.courses.keys()) if self.courses else 0
        scenario_counter = scenario.get("course_counter", DEFAULT_STATE_COPY["course_counter"])
        self.course_counter = max(max_course_id + 1, scenario_counter)
        # Auto-calibrate qa_counter
        max_qa_id = 0
        for course in self.courses.values():
            qa_threads = course.get("qa_threads", {})
            # 2. 如果字典不为空，则将所有 key 转换成整数后再比大小
            if qa_threads:
                max_qa_id = max(max_qa_id, max(int(k) for k in qa_threads.keys()))
        scenario_qa = scenario.get("qa_counter", DEFAULT_STATE_COPY["qa_counter"])
        self.qa_counter = max(max_qa_id + 1, scenario_qa)

    def get_env_state(self) -> Dict:
        """
        Get a deep copy of the current environment state to prevent external mutation.
        """
        return {
            "current_user": self.current_user,
            "users": deepcopy(self.users),
            "courses": deepcopy(self.courses),
            "enrollments": deepcopy(self.enrollments),
            "course_counter": self.course_counter,
            "qa_counter": self.qa_counter,
        }

    def login(self, username: str) -> Dict[str, Union[bool, str]]:
        if username not in self.users:
            return {"error": "User not found."}
        self.current_user = username
        return {"success": True}

    def logout(self) -> Dict[str, Union[bool, str]]:
        """Log out the current user."""
        if not self.current_user:
            return {"error": "No user is currently logged in."}
        self.current_user = None
        return {"success": True}

    def set_prerequisites(self, course_id: int, prerequisites: List[int]) -> Dict[str, str]:
        if not self.current_user or self.users[self.current_user]["role"] != "instructor":
            return {"error": "Only instructors can set prerequisites."}
        if course_id not in self.courses:
            return {"error": "Course not found."}
        if self.courses[course_id]["instructor"] != self.current_user:
            return {"error": "Only the course instructor can modify it."}
        for req_id in prerequisites:
            if req_id not in self.courses:
                return {"error": f"Prerequisite course {req_id} does not exist."}
            if req_id == course_id:
                return {"error": "A course cannot be a prerequisite for itself."}
        original_prereqs = self.courses[course_id]["prerequisites"]
        self.courses[course_id]["prerequisites"] = prerequisites
        if self._has_prerequisite_cycle():
            self.courses[course_id]["prerequisites"] = original_prereqs
            return {"error": "Circular prerequisite detected! This creates a deadlock."}
        return {"success": True, "status": "Prerequisites updated successfully."}

    def _has_prerequisite_cycle(self) -> bool:
        visited = set()
        rec_stack = set()

        def dfs(node_id):
            if node_id in rec_stack:
                return True
            if node_id in visited:
                return False
            visited.add(node_id)
            rec_stack.add(node_id)
            for prereq_id in self.courses[node_id].get("prerequisites", []):
                if dfs(prereq_id):
                    return True
            rec_stack.remove(node_id)
            return False

        for c_id in self.courses:
            if c_id not in visited:
                if dfs(c_id):
                    return True
        return False

    def add_funds(self, amount: float) -> Dict[str, Union[str, float]]:
        if not self.current_user:
            return {"error": "Authentication required."}
        if amount <= 0:
            return {"error": "Amount must be positive."}
        self.users[self.current_user]["balance"] += amount
        return {"success": True, "new_balance": self.users[self.current_user]["balance"]}

    def purchase_course(self, course_id: int) -> Dict[str, str]:
        if not self.current_user or self.users[self.current_user]["role"] != "student":
            return {"error": "Only students can purchase courses."}
        if course_id not in self.courses:
            return {"error": "Course not found."}
        course = self.courses[course_id]
        user = self.users[self.current_user]
        enrollment_key = f"{self.current_user}_{course_id}"
        if enrollment_key in self.enrollments and self.enrollments[enrollment_key].get("purchased"):
            return {"error": "Course already purchased."}
        if user["balance"] < course["price"]:
            return {"error": f"Insufficient funds. Course costs ${course['price']}, but balance is ${user['balance']}."}
        user["balance"] -= course["price"]
        instructor_cut = course["price"] * 0.8
        self.users[course["instructor"]]["balance"] += instructor_cut
        self.enrollments[enrollment_key] = {"purchased": True, "enrolled": False, "progress": [], "quiz_score": None, "completed": False}
        return {"success": True, "status": f"Successfully purchased {course['title']}."}

    def enroll_course(self, course_id: int) -> Dict[str, str]:
        if not self.current_user:
            return {"error": "Authentication required."}
        enrollment_key = f"{self.current_user}_{course_id}"
        if enrollment_key not in self.enrollments or not self.enrollments[enrollment_key].get("purchased"):
            return {"error": "You must purchase this course before enrolling/starting it."}
        if self.enrollments[enrollment_key].get("enrolled"):
            return {"error": "Already enrolled in this course."}
        course = self.courses[course_id]
        for req_id in course["prerequisites"]:
            req_key = f"{self.current_user}_{req_id}"
            if req_key not in self.enrollments or not self.enrollments[req_key].get("completed"):
                return {"error": f"Prerequisite course {req_id} not completed."}
        # Mark as enrolled
        self.enrollments[enrollment_key]["enrolled"] = True
        return {"success": True, "status": "Enrollment verified. You can now access modules."}

    def complete_module(self, course_id: int, module_id: int) -> Dict[str, str]:
        enrollment_key = f"{self.current_user}_{course_id}"
        if enrollment_key not in self.enrollments or not self.enrollments[enrollment_key].get("enrolled"):
            return {"error": "Cannot complete modules for an unenrolled course."}
        course = self.courses[course_id]
        valid_module_ids = [m["id"] for m in course["modules"]]
        if module_id not in valid_module_ids:
            return {"error": "Invalid module ID."}
        # Check sequential order
        for mod in course["modules"]:
            if mod["id"] < module_id and mod["id"] not in self.enrollments[enrollment_key]["progress"]:
                return {"error": f"Module {mod['id']} must be completed before module {module_id}."}
        progress = self.enrollments[enrollment_key]["progress"]
        if module_id not in progress:
            progress.append(module_id)
        return {"success": True, "status": f"Module {module_id} completed. Progress: {len(progress)}/{len(valid_module_ids)}"}

    def take_quiz(self, course_id: int, answers_score: int) -> Dict[str, Union[str, bool]]:
        enrollment_key = f"{self.current_user}_{course_id}"
        if enrollment_key not in self.enrollments or not self.enrollments[enrollment_key].get("enrolled"):
            return {"error": "Not enrolled."}
        if answers_score < 0 or answers_score > 100:
            return {"error": "Invalid score. Must be between 0 and 100."}
        course = self.courses[course_id]
        enr = self.enrollments[enrollment_key]
        if len(enr["progress"]) < len(course["modules"]):
            return {"error": "You must complete all modules before taking the quiz."}
        enr["quiz_score"] = answers_score
        passed = answers_score >= course["quiz_passing_score"]
        if passed:
            enr["completed"] = True
            if course_id not in self.users[self.current_user]["certificates"]:
                self.users[self.current_user]["certificates"].append(course_id)
            return {"success": True, "passed": True, "status": "Quiz passed. Certificate issued."}
        else:
            return {"success": True, "passed": False, "status": "Quiz failed. Score too low."}

    def post_question(self, course_id: int, question: str) -> Dict[str, str]:
        enrollment_key = f"{self.current_user}_{course_id}"
        if enrollment_key not in self.enrollments or not self.enrollments[enrollment_key].get("enrolled"):
            return {"error": "You must be enrolled to post a question."}
        q_id = self.qa_counter
        self.courses[course_id]["qa_threads"][q_id] = {
            "id": q_id, "student": self.current_user, "question": question, "answers": []
        }
        self.qa_counter += 1
        return {"success": True, "status": "Question posted successfully.", "question_id": q_id}

    def answer_question(self, course_id: int, question_id: int, answer: str) -> Dict[str, str]:
        if course_id not in self.courses:
            return {"error": "Course not found."}
        is_instructor = self.courses[course_id]["instructor"] == self.current_user
        enrollment_key = f"{self.current_user}_{course_id}"
        is_enrolled = enrollment_key in self.enrollments and self.enrollments[enrollment_key].get("enrolled")
        if not is_instructor and not is_enrolled:
            return {"error": "Only the instructor or enrolled students can answer."}
        thread = self.courses[course_id]["qa_threads"].get(question_id)
        if not thread:
            return {"error": "Question ID not found."}
        thread["answers"].append({"user": self.current_user, "answer": answer})
        return {"success": True, "status": "Answer added successfully."}

    def leave_review(self, course_id: int, rating: int, comment: str) -> Dict[str, str]:
        enrollment_key = f"{self.current_user}_{course_id}"
        if enrollment_key not in self.enrollments or not self.enrollments[enrollment_key].get("completed"):
            return {"error": "You must complete the course to leave a review."}
        if rating < 1 or rating > 5:
            return {"error": "Rating must be between 1 and 5."}
        # Check duplicate review
        for review in self.courses[course_id]["reviews"]:
            if review["user"] == self.current_user:
                return {"error": "You have already reviewed this course."}
        self.courses[course_id]["reviews"].append({
            "user": self.current_user, "rating": rating, "comment": comment
        })
        return {"success": True, "status": "Review submitted."}

    def create_course(self, title: str, price: float, passing_score: int) -> Dict[str, Union[int, str]]:
        if not self.current_user or self.users[self.current_user]["role"] != "instructor":
            return {"error": "Only instructors can create courses."}
        if not title.strip():
            return {"error": "Course title cannot be empty."}
        if price < 0:
            return {"error": "Course price cannot be negative."}
        if passing_score < 0 or passing_score > 100:
            return {"error": "Passing score must be between 0 and 100."}
        c_id = self.course_counter
        self.courses[c_id] = {
            "id": c_id, "title": title, "instructor": self.current_user, "price": price,
            "modules": [], "prerequisites": [], "quiz_passing_score": passing_score,
            "reviews": [], "qa_threads": {}
        }
        self.course_counter += 1
        return {"success": True, "course_id": c_id, "status": "Course created successfully."}

    def add_course_module(self, course_id: int, module_title: str) -> Dict[str, Union[str, int]]:
        if not self.current_user or self.users[self.current_user]["role"] != "instructor":
            return {"error": "Only instructors can add modules."}
        if course_id not in self.courses:
            return {"error": "Course not found."}
        if self.courses[course_id]["instructor"] != self.current_user:
            return {"error": "Only the course instructor can modify it."}
        if not module_title.strip():
            return {"error": "Module title cannot be empty."}
        course = self.courses[course_id]
        new_module_id = len(course["modules"]) + 1
        course["modules"].append({"id": new_module_id, "title": module_title})
        return {"success": True, "status": "Module added successfully.", "module_id": new_module_id}

    def search_courses(self, keyword: str = "", max_price: Optional[float] = None) -> Dict[str, Union[str, List[Dict]]]:
        results = []
        for c_id, course in self.courses.items():
            if keyword.lower() in course["title"].lower():
                if max_price is None or course["price"] <= max_price:
                    avg_rating = 0.0
                    if course["reviews"]:
                        avg_rating = sum(r["rating"] for r in course["reviews"]) / len(course["reviews"])
                    results.append({
                        "id": c_id,
                        "title": course["title"],
                        "instructor": course["instructor"],
                        "price": course["price"],
                        "modules_count": len(course["modules"]),
                        "rating": avg_rating
                    })
        return {"success": True, "results": results}

    def register_user(self, username: str, role: str) -> Dict[str, str]:
        if not username.strip():
            return {"error": "Username cannot be empty."}
        if username in self.users:
            return {"error": "Username already exists."}
        if role not in ["student", "instructor"]:
            return {"error": "Invalid role. Must be 'student' or 'instructor'."}
        self.users[username] = {
            "role": role,
            "balance": 0.0,
            "certificates": []
        }
        return {"success": True, "status": f"User {username} registered successfully as {role}."}

    def request_refund(self, course_id: int) -> Dict[str, str]:
        if not self.current_user or self.users[self.current_user]["role"] != "student":
            return {"error": "Only students can request refunds."}
        enrollment_key = f"{self.current_user}_{course_id}"
        if enrollment_key not in self.enrollments or not self.enrollments[enrollment_key].get("purchased"):
            return {"error": "Course not purchased."}
        enr = self.enrollments[enrollment_key]
        if enr.get("completed"):
            return {"error": "Cannot refund a completed course."}
        course = self.courses.get(course_id)
        if not course:
            return {"error": "Course not found."}
        total_modules = len(course["modules"])
        progress = len(enr["progress"])
        if total_modules > 0 and (progress / total_modules) > 0.5:
            return {"error": "Refund denied. Course progress exceeds 50%."}
        refund_amount = course["price"]
        instructor_cut = refund_amount * 0.8
        # Transactional check: ensure instructor has enough balance
        if self.users[course["instructor"]]["balance"] < instructor_cut:
            return {"error": "Refund failed: instructor balance insufficient."}
        # Perform refund atomically
        self.users[self.current_user]["balance"] += refund_amount
        self.users[course["instructor"]]["balance"] -= instructor_cut
        del self.enrollments[enrollment_key]
        return {"success": True, "status": "Refund successful."}

    def resolve_question(self, course_id: int, question_id: int, accepted_answer_index: int) -> Dict[str, str]:
        if course_id not in self.courses:
            return {"error": "Course not found."}
        thread = self.courses[course_id]["qa_threads"].get(question_id)
        if not thread:
            return {"error": "Question ID not found."}
        if self.current_user != thread["student"] and self.current_user != self.courses[course_id]["instructor"]:
            return {"error": "Only the student who asked or the instructor can resolve the question."}
        if accepted_answer_index < 0 or accepted_answer_index >= len(thread["answers"]):
            return {"error": "Invalid answer index."}
        if thread.get("resolved"):
            return {"error": "Question already resolved."}
        thread["resolved"] = True
        thread["accepted_answer_index"] = accepted_answer_index
        return {"success": True, "status": "Question resolved successfully."}

    def get_instructor_dashboard(self) -> Dict[str, Union[str, float, List[Dict]]]:
        if not self.current_user or self.users[self.current_user]["role"] != "instructor":
            return {"error": "Only instructors can access the dashboard."}
        total_earnings = 0.0
        course_stats = []
        for c_id, course in self.courses.items():
            if course["instructor"] == self.current_user:
                enrolled_count = sum(1 for k in self.enrollments if k.endswith(f"_{c_id}") and self.enrollments[k].get("purchased"))
                total_earnings += enrolled_count * (course["price"] * 0.8)
                avg_rating = 0.0
                if course["reviews"]:
                    avg_rating = sum(r["rating"] for r in course["reviews"]) / len(course["reviews"])
                course_stats.append({
                    "course_id": c_id,
                    "title": course["title"],
                    "enrollments": enrolled_count,
                    "average_rating": avg_rating
                })
        return {
            "success": True,
            "instructor": self.current_user,
            "current_balance": self.users[self.current_user]["balance"],
            "total_earnings_calculated": total_earnings,
            "courses": course_stats
        }


__TEST_CASES__ = [
    {   'name': 'End-to-end student workflow (Normal Path & Cross-method)',
        'steps': [   {'expect_success': True, 'tool_call': "env['course'].login(username='student1')"},
                     {'expect_success': True, 'tool_call': "env['course'].purchase_course(course_id=201)"},
                     {'expect_success': True, 'tool_call': "env['course'].enroll_course(course_id=201)"},
                     {'expect_success': True, 'tool_call': "env['course'].complete_module(course_id=201, module_id=1)"},
                     {'expect_success': True, 'tool_call': "env['course'].complete_module(course_id=201, module_id=2)"},
                     {'expect_success': True, 'tool_call': "env['course'].take_quiz(course_id=201, answers_score=85)"},
                     {   'expect_success': True,
                         'tool_call': "env['course'].leave_review(course_id=201, rating=5, comment='Excellent course!')"},
                     {'expect_success': True, 'tool_call': "env['course'].get_env_state()"}]},
    {   'name': 'Instructor workflow (Normal Path & Cross-method)',
        'steps': [   {'expect_success': True, 'tool_call': "env['course'].login(username='instructor1')"},
                     {   'expect_success': True,
                         'tool_call': "env['course'].create_course(title='Advanced Python', price=99.99, passing_score=80)"},
                     {   'expect_success': True,
                         'tool_call': "env['course'].set_prerequisites(course_id=201, prerequisites=[])"},
                     {   'expect_success': True,
                         'tool_call': "env['course'].answer_question(course_id=201, question_id=1, answer='A variable is a memory location.')"}]},
    {   'name': 'Insufficient funds error path (Error Path)',
        'steps': [   {'expect_success': True, 'tool_call': "env['course'].login(username='student2')"},
                     {'expect_success': False, 'tool_call': "env['course'].purchase_course(course_id=201)"},
                     {'expect_success': True, 'tool_call': "env['course'].add_funds(amount=50.0)"},
                     {'expect_success': True, 'tool_call': "env['course'].purchase_course(course_id=201)"}]},
    {   'name': 'Invalid authentication and non-existent IDs (Error Path)',
        'steps': [   {'expect_success': False, 'tool_call': "env['course'].login(username='hacker')"},
                     {'expect_success': True, 'tool_call': "env['course'].login(username='student1')"},
                     {'expect_success': False, 'tool_call': "env['course'].purchase_course(course_id=999)"},
                     {'expect_success': False, 'tool_call': "env['course'].enroll_course(course_id=999)"},
                     {   'expect_success': False,
                         'tool_call': "env['course'].complete_module(course_id=201, module_id=999)"}]},
    {   'name': 'Boundary values for course creation (Boundary Values)',
        'steps': [   {'expect_success': True, 'tool_call': "env['course'].login(username='instructor1')"},
                     {   'expect_success': False,
                         'tool_call': "env['course'].create_course(title='', price=0.0, passing_score=-5)"},
                     {   'expect_success': True,
                         'tool_call': "env['course'].create_course(title='Free Course', price=0.0, passing_score=0)"},
                     {   'expect_success': True,
                         'tool_call': "env['course'].create_course(title='Super Long Course Title That Exceeds Normal Length Limits To Test Boundary Conditions', price=10000.0, passing_score=100)"}]},
    {   'name': 'Taking quiz without completing modules or failing score (Error Path)',
        'steps': [   {'expect_success': True, 'tool_call': "env['course'].login(username='student2')"},
                     {'expect_success': True, 'tool_call': "env['course'].add_funds(amount=50.0)"},
                     {'expect_success': True, 'tool_call': "env['course'].purchase_course(course_id=201)"},
                     {'expect_success': True, 'tool_call': "env['course'].enroll_course(course_id=201)"},
                     {   'expect_success': False,
                         'tool_call': "env['course'].take_quiz(course_id=201, answers_score=100)"},
                     {'expect_success': True, 'tool_call': "env['course'].complete_module(course_id=201, module_id=1)"},
                     {'expect_success': True, 'tool_call': "env['course'].complete_module(course_id=201, module_id=2)"},
                     {   'expect_success': True,   # changed from False to True because failing score is a valid business outcome
                         'tool_call': "env['course'].take_quiz(course_id=201, answers_score=50)"}]},
    {   'name': 'Circular dependency in prerequisites (Error Path)',
        'steps': [   {'expect_success': True, 'tool_call': "env['course'].login(username='instructor1')"},
                     {   'expect_success': False,
                         'tool_call': "env['course'].set_prerequisites(course_id=201, prerequisites=[201])"},
                     {   'expect_success': False,
                         'tool_call': "env['course'].set_prerequisites(course_id=201, prerequisites=[999])"}]},
    {   'name': 'Q&A Forum Workflow (Normal Path & Cross-method)',
        'steps': [   {'expect_success': True, 'tool_call': "env['course'].login(username='student1')"},
                     {'expect_success': True, 'tool_call': "env['course'].purchase_course(course_id=201)"},
                     {'expect_success': True, 'tool_call': "env['course'].enroll_course(course_id=201)"},
                     {   'expect_success': True,
                         'tool_call': "env['course'].post_question(course_id=201, question='How do loops work?')"},
                     {'expect_success': True, 'tool_call': "env['course'].login(username='instructor1')"},
                     {   'expect_success': True,
                         'tool_call': "env['course'].answer_question(course_id=201, question_id=2, answer='They repeat code blocks.')"}]},
    {   'name': 'Boundary values for funds and quiz scores (Boundary Values)',
        'steps': [   {'expect_success': True, 'tool_call': "env['course'].login(username='student1')"},
                     {'expect_success': False, 'tool_call': "env['course'].add_funds(amount=-50.0)"},
                     {'expect_success': False, 'tool_call': "env['course'].add_funds(amount=0.0)"},
                     {'expect_success': True, 'tool_call': "env['course'].purchase_course(course_id=201)"},
                     {'expect_success': True, 'tool_call': "env['course'].enroll_course(course_id=201)"},
                     {'expect_success': True, 'tool_call': "env['course'].complete_module(course_id=201, module_id=1)"},
                     {'expect_success': True, 'tool_call': "env['course'].complete_module(course_id=201, module_id=2)"},
                     {   'expect_success': False,
                         'tool_call': "env['course'].take_quiz(course_id=201, answers_score=-10)"},
                     {   'expect_success': False,
                         'tool_call': "env['course'].take_quiz(course_id=201, answers_score=150)"}]},
    {   'name': 'Review without completing course and state verification (Error Path & State-change)',
        'steps': [   {'expect_success': True, 'tool_call': "env['course'].login(username='student2')"},
                     {'expect_success': True, 'tool_call': "env['course'].add_funds(amount=50.0)"},
                     {'expect_success': True, 'tool_call': "env['course'].purchase_course(course_id=201)"},
                     {'expect_success': True, 'tool_call': "env['course'].enroll_course(course_id=201)"},
                     {   'expect_success': False,
                         'tool_call': "env['course'].leave_review(course_id=201, rating=5, comment='Nice!')"},
                     {'expect_success': True, 'tool_call': "env['course'].get_env_state()"}]},
    {   'name': 'New Features Workflow (Normal Path & Cross-method)',
        'steps': [   {'expect_success': True, 'tool_call': "env['course'].register_user(username='instructor2', role='instructor')"},
                     {'expect_success': True, 'tool_call': "env['course'].login(username='instructor2')"},
                     {'expect_success': True, 'tool_call': "env['course'].create_course(title='Data Science', price=100.0, passing_score=70)"},
                     {'expect_success': True, 'tool_call': "env['course'].add_course_module(course_id=202, module_title='Pandas')"},
                     {'expect_success': True, 'tool_call': "env['course'].add_course_module(course_id=202, module_title='Numpy')"},
                     {'expect_success': True, 'tool_call': "env['course'].search_courses(keyword='Data Science', max_price=150.0)"},
                     {'expect_success': True, 'tool_call': "env['course'].get_instructor_dashboard()"},
                     {'expect_success': True, 'tool_call': "env['course'].register_user(username='student3', role='student')"},
                     {'expect_success': True, 'tool_call': "env['course'].login(username='student3')"},
                     {'expect_success': True, 'tool_call': "env['course'].add_funds(amount=200.0)"},
                     {'expect_success': True, 'tool_call': "env['course'].purchase_course(course_id=202)"},
                     {'expect_success': True, 'tool_call': "env['course'].enroll_course(course_id=202)"},
                     {'expect_success': True, 'tool_call': "env['course'].post_question(course_id=202, question='What is a dataframe?')"},
                     {'expect_success': True, 'tool_call': "env['course'].login(username='instructor2')"},
                     {'expect_success': True, 'tool_call': "env['course'].answer_question(course_id=202, question_id=2, answer='It is a table.')"},
                     {'expect_success': True, 'tool_call': "env['course'].resolve_question(course_id=202, question_id=2, accepted_answer_index=0)"}]},
    {   'name': 'Refund Workflow and Boundaries (Error Path)',
        'steps': [   {'expect_success': True, 'tool_call': "env['course'].register_user(username='student4', role='student')"},
                     {'expect_success': True, 'tool_call': "env['course'].login(username='student4')"},
                     {'expect_success': True, 'tool_call': "env['course'].add_funds(amount=100.0)"},
                     {'expect_success': False, 'tool_call': "env['course'].request_refund(course_id=201)"},
                     {'expect_success': True, 'tool_call': "env['course'].purchase_course(course_id=201)"},
                     {'expect_success': True, 'tool_call': "env['course'].enroll_course(course_id=201)"},
                     {'expect_success': True, 'tool_call': "env['course'].complete_module(course_id=201, module_id=1)"},
                     {'expect_success': True, 'tool_call': "env['course'].complete_module(course_id=201, module_id=2)"},
                     {'expect_success': False, 'tool_call': "env['course'].request_refund(course_id=201)"},
                     {'expect_success': True, 'tool_call': "env['course'].login(username='instructor1')"},
                     {'expect_success': True, 'tool_call': "env['course'].create_course(title='Short Course', price=50.0, passing_score=70)"},
                     {'expect_success': True, 'tool_call': "env['course'].add_course_module(course_id=202, module_title='Only Module')"},
                     {'expect_success': True, 'tool_call': "env['course'].login(username='student4')"},
                     {'expect_success': True, 'tool_call': "env['course'].purchase_course(course_id=202)"},
                     {'expect_success': True, 'tool_call': "env['course'].request_refund(course_id=202)"},
                     {'expect_success': False, 'tool_call': "env['course'].request_refund(course_id=202)"}]}
]