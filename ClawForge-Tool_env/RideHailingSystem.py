import math
from copy import deepcopy
from typing import Dict, List, Optional, Union

DEFAULT_RIDE_STATE = {
    "current_user": None,
    "users": {
        "rider_john": {"role": "rider", "location": (0, 0), "balance": 150.0, "rating": 4.8, "rating_count": 10},
        "driver_smith": {"role": "driver", "location": (2, 2), "balance": 500.0, "is_available": True,
                         "car_type": "Premium", "rating": 4.9, "rating_count": 150},
        "driver_doe": {"role": "driver", "location": (10, 10), "balance": 300.0, "is_available": True,
                       "car_type": "Economy", "rating": 4.5, "rating_count": 80},
    },
    "rides": {},
    "car_type_multipliers": {
        "Economy": 1.0,
        "Premium": 1.5,
        "SUV": 2.0
    },
    "ride_counter": 301,
    "surge_multiplier": 1.2,  # Network-wide surge based on demand
    "base_rate_per_unit": 2.5
}


class AdvancedRideHailingAPI:
    """
    Advanced Ride Hailing API. Features include specific car types, intermediate stops,
    radar searching for nearby drivers, dynamic fare updates, tipping, and bi-directional rating.
    """

    VALID_STATUSES = ["Requested", "Accepted", "Arrived", "In Progress", "Completed", "Cancelled"]

    def __init__(self):
        self.current_user: Optional[str] = None
        self.users: Dict[str, Dict] = {}
        self.rides: Dict[int, Dict] = {}
        self.car_type_multipliers: Dict[str, float] = {}
        self.ride_counter: int = 0
        self.surge_multiplier: float = 1.0
        self.base_rate_per_unit: float = 1.0
        self._api_description = "A sophisticated ride-sharing system with dynamic routing, tipping, ratings, and vehicle classes."

    def _load_scenario(self, scenario: dict, long_context=False) -> None:
        """
        Load a specific scenario into the environment.

        Args:
            scenario (dict): The scenario data containing states.
            long_context (bool, optional): Whether to format for long context. Defaults to False.

        Returns:
            None
        """
        DEFAULT_STATE_COPY = deepcopy(DEFAULT_RIDE_STATE)
        self.current_user = scenario.get("current_user", DEFAULT_STATE_COPY["current_user"])
        self.users = deepcopy(scenario.get("users", DEFAULT_STATE_COPY["users"]))
        raw_rides = scenario.get("rides", DEFAULT_STATE_COPY["rides"])
        self.rides = {int(k) if str(k).isdigit() else k: deepcopy(v) for k, v in raw_rides.items()}
        self.car_type_multipliers = deepcopy(scenario.get("car_type_multipliers", DEFAULT_STATE_COPY["car_type_multipliers"]))

        # Auto-calibrate ride_counter to avoid ID collision
        if self.rides:
            max_ride_id = max(self.rides.keys())
            self.ride_counter = max_ride_id + 1
        else:
            self.ride_counter = scenario.get("ride_counter", DEFAULT_STATE_COPY["ride_counter"])

        self.surge_multiplier = scenario.get("surge_multiplier", DEFAULT_STATE_COPY["surge_multiplier"])
        self.base_rate_per_unit = scenario.get("base_rate_per_unit", DEFAULT_STATE_COPY["base_rate_per_unit"])

    def get_env_state(self) -> Dict:
        """
        Get the current environment state.

        Returns:
            Dict: The environment state representation.
        """
        return deepcopy({
            "current_user": self.current_user,
            "users": self.users,
            "rides": self.rides,
            "car_type_multipliers": self.car_type_multipliers,
            "ride_counter": self.ride_counter,
            "surge_multiplier": self.surge_multiplier,
            "base_rate_per_unit": self.base_rate_per_unit
        })

    def login(self, username: str) -> Dict[str, Union[bool, str]]:
        """
        Login a user to the system.

        Args:
            username (str): The username of the user.

        Returns:
            Dict[str, Union[bool, str]]: Success status or error message.
        """
        if username not in self.users:
            return {"success": False, "error": "User not found."}
        self.current_user = username
        return {"success": True, "data": {"message": f"User {username} logged in."}}

    def _calculate_distance(self, loc1: tuple, loc2: tuple) -> float:
        """
        Calculate Euclidean distance between two locations.

        Args:
            loc1 (tuple): The first location coordinates.
            loc2 (tuple): The second location coordinates.

        Returns:
            float: The calculated distance.
        """
        return math.sqrt((loc1[0] - loc2[0]) ** 2 + (loc1[1] - loc2[1]) ** 2)

    def _calculate_route_distance(self, route: List[tuple]) -> float:
        """
        Calculate total distance of a route.

        Args:
            route (List[tuple]): A list of coordinates forming a route.

        Returns:
            float: Total route distance.
        """
        total_dist = 0.0
        for i in range(len(route) - 1):
            total_dist += self._calculate_distance(route[i], route[i + 1])
        return total_dist

    def find_nearby_drivers(self, radius: float, required_car_type: str = "Economy") -> Dict:
        """
        Riders can scan for available drivers within a certain radius.

        Args:
            radius (float): The scan radius.
            required_car_type (str, optional): The desired car type. Defaults to "Economy".

        Returns:
            Dict: A dictionary with a list of nearby drivers or an error.
        """
        if radius < 0:
            return {"success": False, "error": "Radius cannot be negative."}

        if not self.current_user or self.users[self.current_user]["role"] != "rider":
            return {"success": False, "error": "Only riders can search for drivers."}

        rider_loc = self.users[self.current_user]["location"]
        available = []

        for username, user_data in self.users.items():
            if user_data["role"] == "driver" and user_data["is_available"]:
                if user_data["car_type"] == required_car_type:
                    dist = self._calculate_distance(rider_loc, user_data["location"])
                    if dist <= radius:
                        available.append(
                            {"driver": username, "distance": round(dist, 2), "rating": user_data["rating"]})

        return {"success": True, "data": {"nearby_drivers": sorted(available, key=lambda x: x["distance"])}}

    def estimate_fare(self, dropoff_x: int, dropoff_y: int, car_type: str = "Economy") -> Dict:
        """
        Get a fare estimate before requesting.

        Args:
            dropoff_x (int): The X coordinate of the dropoff.
            dropoff_y (int): The Y coordinate of the dropoff.
            car_type (str, optional): The car type. Defaults to "Economy".

        Returns:
            Dict: Estimated fare details or error message.
        """
        if not self.current_user:
            return {"success": False, "error": "Authentication required."}
        if car_type not in self.car_type_multipliers:
            return {"success": False, "error": "Invalid car type."}

        pickup_loc = self.users[self.current_user]["location"]
        dist = self._calculate_distance(pickup_loc, (dropoff_x, dropoff_y))

        multiplier = self.car_type_multipliers[car_type]
        fare = dist * self.base_rate_per_unit * multiplier * self.surge_multiplier
        return {"success": True, "data": {"estimated_fare": round(fare, 2), "distance": round(dist, 2)}}

    def request_ride(self, dropoff_x: int, dropoff_y: int, car_type: str = "Economy") -> Dict:
        """
        Request a ride to a specific dropoff location.

        Args:
            dropoff_x (int): The X coordinate of the dropoff.
            dropoff_y (int): The Y coordinate of the dropoff.
            car_type (str, optional): The requested car type. Defaults to "Economy".

        Returns:
            Dict: Information about the requested ride or error message.
        """
        if not self.current_user or self.users[self.current_user]["role"] != "rider":
            return {"success": False, "error": "Only riders can request rides."}

        estimate = self.estimate_fare(dropoff_x, dropoff_y, car_type)
        if not estimate.get("success", False):
            return estimate

        est_fare = estimate["data"]["estimated_fare"]
        if self.users[self.current_user]["balance"] < est_fare:
            return {"success": False, "error": "Insufficient balance."}

        r_id = self.ride_counter
        self.rides[r_id] = {
            "id": r_id,
            "rider": self.current_user,
            "driver": None,
            "car_type": car_type,
            "route": [self.users[self.current_user]["location"], (dropoff_x, dropoff_y)],
            "status": "Requested",
            "fare": est_fare,
            "tip": 0.0,
            "rider_rated": False,
            "driver_rated": False
        }
        self.ride_counter += 1
        return {"success": True, "data": {"ride_id": r_id, "status": "Requested", "estimated_fare": est_fare}}

    def accept_ride(self, ride_id: int) -> Dict:
        """
        Accept a requested ride.

        Args:
            ride_id (int): The ID of the ride to accept.

        Returns:
            Dict: Status message or error.
        """
        if not self.current_user or self.users[self.current_user]["role"] != "driver":
            return {"success": False, "error": "Only drivers can accept rides."}

        driver = self.users[self.current_user]
        if not driver["is_available"]:
            return {"success": False, "error": "You are currently marked as unavailable."}

        ride = self.rides.get(ride_id)
        if not ride:
            return {"success": False, "error": "Ride not found."}

        if ride["status"] != "Requested":
            return {"success": False, "error": f"Ride unavailable. Status: {ride['status']}"}

        if driver["car_type"] != ride["car_type"]:
            return {"success": False, "error": f"Car type mismatch. Rider requested {ride['car_type']}."}

        ride["driver"] = self.current_user
        ride["status"] = "Accepted"
        driver["is_available"] = False
        return {"success": True, "data": {"status": f"Ride {ride_id} accepted. Proceed to pickup."}}

    def add_stop(self, ride_id: int, stop_x: int, stop_y: int) -> Dict:
        """
        Rider adds an intermediate stop, recalculating the fare dynamically.

        Args:
            ride_id (int): The ID of the ride.
            stop_x (int): The X coordinate of the stop.
            stop_y (int): The Y coordinate of the stop.

        Returns:
            Dict: Status, new fare, and updated route.
        """
        if ride_id not in self.rides:
            return {"success": False, "error": "Ride not found."}
        ride = self.rides[ride_id]

        if self.current_user != ride["rider"]:
            return {"success": False, "error": "Only the rider can modify the route."}
        if ride["status"] in ["Completed", "Cancelled"]:
            return {"success": False, "error": "Cannot modify completed or cancelled rides."}

        temp_route = ride["route"][:]
        final_dropoff = temp_route.pop()
        temp_route.append((stop_x, stop_y))
        temp_route.append(final_dropoff)

        new_dist = self._calculate_route_distance(temp_route)
        multiplier = self.car_type_multipliers[ride["car_type"]]
        new_fare = new_dist * self.base_rate_per_unit * multiplier * self.surge_multiplier
        new_fare = round(new_fare, 2)

        if self.users[self.current_user]["balance"] < new_fare:
            return {"success": False, "error": f"Insufficient balance for new route. Estimated fare: {new_fare}"}

        ride["route"] = temp_route
        ride["fare"] = new_fare

        return {"success": True, "data": {"status": "Stop added.", "new_fare": ride["fare"], "route": deepcopy(ride["route"])}}

    def update_ride_status(self, ride_id: int, new_status: str) -> Dict:
        """
        Update the status of a ride.

        Args:
            ride_id (int): The ID of the ride.
            new_status (str): The new status to set.

        Returns:
            Dict: Status update message or error.
        """
        if ride_id not in self.rides:
            return {"success": False, "error": "Ride not found."}
        if new_status not in self.VALID_STATUSES:
            return {"success": False, "error": "Invalid status."}

        ride = self.rides[ride_id]
        current_status = ride["status"]

        VALID_TRANSITIONS = {
            "Requested": ["Accepted", "Cancelled"],
            "Accepted": ["Arrived", "Cancelled"],
            "Arrived": ["In Progress", "Cancelled"],
            "In Progress": ["Completed", "Cancelled"],
            "Completed": [],
            "Cancelled": []
        }

        if new_status not in VALID_TRANSITIONS.get(current_status, []):
            return {"success": False, "error": f"Invalid state transition from {current_status} to {new_status}."}

        is_driver = self.current_user == ride["driver"]
        is_rider = self.current_user == ride["rider"]

        if new_status == "Cancelled":
            # Passenger cancellation during accepted/arrived: penalty and restore driver
            if is_rider and current_status in ["Accepted", "Arrived"]:
                self.users[self.current_user]["balance"] -= 5.0
                if ride["driver"]:
                    self.users[ride["driver"]]["balance"] += 5.0
                    self.users[ride["driver"]]["is_available"] = True
            # Driver cancellation always restores driver availability
            elif is_driver and ride["driver"]:
                self.users[ride["driver"]]["is_available"] = True

            ride["status"] = "Cancelled"
            return {"success": True, "data": {"status": "Ride cancelled."}}

        if not is_driver:
            return {"success": False, "error": "Only the assigned driver can progress the ride status."}

        ride["status"] = new_status

        if new_status == "Completed":
            fare = ride["fare"]
            rider_name = ride["rider"]
            # Double-check rider's balance before final charge
            if self.users[rider_name]["balance"] < fare:
                return {"success": False, "error": "Rider has insufficient balance to complete the ride."}

            self.users[rider_name]["balance"] -= fare
            self.users[self.current_user]["balance"] += round(fare * 0.75, 2)
            self.users[self.current_user]["is_available"] = True
            self.users[rider_name]["location"] = ride["route"][-1]
            self.users[self.current_user]["location"] = ride["route"][-1]

        return {"success": True, "data": {"status": f"Ride {ride_id} status updated to {new_status}."}}

    def rate_and_tip(self, ride_id: int, target_user: str, rating: int, tip: float = 0.0) -> Dict:
        """
        Allows rider to rate/tip driver, or driver to rate rider.

        Args:
            ride_id (int): The ID of the ride.
            target_user (str): The username of the user being rated/tipped.
            rating (int): Rating value between 1 and 5.
            tip (float, optional): Tip amount. Defaults to 0.0.

        Returns:
            Dict: Status message or error.
        """
        if ride_id not in self.rides:
            return {"success": False, "error": "Ride not found."}
        ride = self.rides[ride_id]
        if ride["status"] != "Completed":
            return {"success": False, "error": "Ride must be completed to rate."}
        if rating < 1 or rating > 5:
            return {"success": False, "error": "Rating must be between 1 and 5."}
        if tip < 0:
            return {"success": False, "error": "Tip cannot be negative."}

        is_rider = self.current_user == ride["rider"]
        is_driver = self.current_user == ride["driver"]

        if is_rider and target_user != ride["driver"]:
            return {"success": False, "error": "Riders can only rate the driver of this specific ride."}
        elif is_driver and target_user != ride["rider"]:
            return {"success": False, "error": "Drivers can only rate the rider of this specific ride."}
        elif not is_rider and not is_driver:
            return {"success": False, "error": "You are not a participant in this ride."}

        # Prevent duplicate ratings per user per ride
        if is_rider and ride.get("rider_rated", False):
            return {"success": False, "error": "You have already rated this ride."}
        if is_driver and ride.get("driver_rated", False):
            return {"success": False, "error": "You have already rated this ride."}

        if target_user not in self.users:
            return {"success": False, "error": "Target user not found."}

        target = self.users[target_user]
        old_rating = target["rating"]
        count = target["rating_count"]
        target["rating"] = round(((old_rating * count) + rating) / (count + 1), 2)
        target["rating_count"] += 1

        # Mark that this participant has rated
        if is_rider:
            ride["rider_rated"] = True
        if is_driver:
            ride["driver_rated"] = True

        if is_rider and tip > 0:
            if self.users[self.current_user]["balance"] < tip:
                return {"success": False, "error": "Insufficient balance for tip."}

            self.users[self.current_user]["balance"] -= tip
            self.users[target_user]["balance"] += tip
            ride["tip"] += tip

        return {"success": True, "data": {"status": f"Successfully rated {target_user}."}}

    def add_funds(self, amount: float) -> Dict:
        """
        Add funds to the current logged-in user's account balance.

        Args:
            amount (float): The amount to recharge.

        Returns:
            Dict: Status message and the new balance, or error message.
        """
        if not self.current_user:
            return {"success": False, "error": "Authentication required."}
        if amount <= 0:
            return {"success": False, "error": "Amount must be strictly positive."}

        self.users[self.current_user]["balance"] += amount
        return {"success": True, "data": {"status": "Funds added successfully.", "new_balance": round(self.users[self.current_user]["balance"], 2)}}

    def set_driver_status(self, is_available: bool) -> Dict:
        """
        Allows a logged-in driver to toggle their availability status (online/offline).

        Args:
            is_available (bool): The desired availability status.

        Returns:
            Dict: Status message and current availability, or error message.
        """
        if not self.current_user:
            return {"success": False, "error": "Authentication required."}

        user = self.users[self.current_user]
        if user["role"] != "driver":
            return {"success": False, "error": "Only drivers can change their availability."}

        user["is_available"] = is_available
        status_str = "online" if is_available else "offline"
        return {"success": True, "data": {"status": f"Driver is now {status_str}.", "is_available": is_available}}

    def get_user_profile(self, target_user: Optional[str] = None) -> Dict:
        """
        Retrieve the detailed profile of a specific user. If no user is specified,
        retrieves the profile of the currently logged-in user.

        Args:
            target_user (Optional[str], optional): The username to query. Defaults to None.

        Returns:
            Dict: The user's detailed profile data or error message.
        """
        if target_user is None:
            if not self.current_user:
                return {"success": False, "error": "Authentication required."}
            target_user = self.current_user

        if target_user not in self.users:
            return {"success": False, "error": "User not found."}

        profile = deepcopy(self.users[target_user])
        return {"success": True, "data": {"profile": profile}}

    def change_destination(self, ride_id: int, new_x: int, new_y: int) -> Dict:
        """
        Allows a rider to change the final destination of an ongoing ride, dynamically recalculating the fare.

        Args:
            ride_id (int): The ID of the ride.
            new_x (int): The new X coordinate of the destination.
            new_y (int): The new Y coordinate of the destination.

        Returns:
            Dict: Status, updated fare, and updated route.
        """
        if not self.current_user:
            return {"success": False, "error": "Authentication required."}

        if ride_id not in self.rides:
            return {"success": False, "error": "Ride not found."}

        ride = self.rides[ride_id]
        if self.current_user != ride["rider"]:
            return {"success": False, "error": "Only the rider can modify the destination."}

        if ride["status"] in ["Completed", "Cancelled"]:
            return {"success": False, "error": "Cannot modify completed or cancelled rides."}

        temp_route = ride["route"][:]
        temp_route[-1] = (new_x, new_y)

        new_dist = self._calculate_route_distance(temp_route)
        multiplier = self.car_type_multipliers[ride["car_type"]]
        new_fare = new_dist * self.base_rate_per_unit * multiplier * self.surge_multiplier
        new_fare = round(new_fare, 2)

        if self.users[self.current_user]["balance"] < new_fare:
            return {"success": False, "error": f"Insufficient balance for new destination. Estimated fare: {new_fare}"}

        ride["route"] = temp_route
        ride["fare"] = new_fare

        return {"success": True, "data": {"status": "Destination changed.", "new_fare": ride["fare"], "route": deepcopy(ride["route"])}}


__TEST_CASES__ = [
    {
        'name': 'Normal path - Rider requests ride',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].find_nearby_drivers(radius=5.0, required_car_type='Premium')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].estimate_fare(dropoff_x=5, dropoff_y=5, car_type='Premium')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].request_ride(dropoff_x=5, dropoff_y=5, car_type='Premium')"}
        ]
    },
    {
        'name': 'Normal path - Driver accepts and completes ride',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].request_ride(dropoff_x=10, dropoff_y=10, car_type='Premium')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='driver_smith')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].accept_ride(ride_id=301)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='Arrived')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='In Progress')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='Completed')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].rate_and_tip(ride_id=301, target_user='rider_john', rating=5, tip=0.0)"}
        ]
    },
    {
        'name': 'Cross-method workflow - Rider adds stop during ride',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].request_ride(dropoff_x=10, dropoff_y=10, car_type='Economy')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='driver_doe')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].accept_ride(ride_id=301)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].add_stop(ride_id=301, stop_x=5, stop_y=5)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='driver_doe')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='Arrived')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='In Progress')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='Completed')"}
        ]
    },
    {
        'name': 'Error path - Invalid login and unauthorized actions',
        'steps': [
            {'expect_success': False, 'tool_call': "env['ridehailing'].login(username='non_existent_user')"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].request_ride(dropoff_x=1, dropoff_y=1, car_type='Premium')"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].accept_ride(ride_id=301)"}
        ]
    },
    {
        'name': 'Boundary values - Find drivers & estimate fare',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].find_nearby_drivers(radius=0.0, required_car_type='Economy')"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].find_nearby_drivers(radius=-10.0, required_car_type='Premium')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].estimate_fare(dropoff_x=0, dropoff_y=0, car_type='Premium')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].estimate_fare(dropoff_x=999999, dropoff_y=-999999, car_type='Economy')"}
        ]
    },
    {
        'name': 'Error path - Invalid ride operations',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='driver_smith')"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].accept_ride(ride_id=999)"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].add_stop(ride_id=999, stop_x=1, stop_y=1)"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=999, new_status='Completed')"}
        ]
    },
    {
        'name': 'State-change verification - Check driver availability',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].request_ride(dropoff_x=3, dropoff_y=3, car_type='Premium')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='driver_smith')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].accept_ride(ride_id=301)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].get_env_state()"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='Arrived')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='In Progress')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='Completed')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].get_env_state()"}
        ]
    },
    {
        'name': 'Error path - Invalid status and ratings',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].request_ride(dropoff_x=4, dropoff_y=4, car_type='Economy')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='driver_doe')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].accept_ride(ride_id=301)"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='invalid_status')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='Arrived')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='In Progress')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='Completed')"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].rate_and_tip(ride_id=301, target_user='rider_john', rating=6, tip=5.0)"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].rate_and_tip(ride_id=301, target_user='rider_john', rating=-1, tip=5.0)"}
        ]
    },
    {
        'name': 'Boundary values - Tipping and Rating',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].request_ride(dropoff_x=4, dropoff_y=4, car_type='Economy')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='driver_doe')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].accept_ride(ride_id=301)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='Arrived')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='In Progress')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='Completed')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].rate_and_tip(ride_id=301, target_user='driver_doe', rating=5, tip=-10.0)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].rate_and_tip(ride_id=301, target_user='driver_doe', rating=5, tip=0.0)"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].rate_and_tip(ride_id=301, target_user='driver_doe', rating=1, tip=999999.0)"}
        ]
    },
    {
        'name': 'Cross-method workflow - Full lifecycle with multiple stops and tips',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].request_ride(dropoff_x=20, dropoff_y=20, car_type='Premium')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='driver_smith')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].accept_ride(ride_id=301)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='Arrived')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='In Progress')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].add_stop(ride_id=301, stop_x=10, stop_y=10)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].add_stop(ride_id=301, stop_x=15, stop_y=15)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='driver_smith')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='Completed')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].rate_and_tip(ride_id=301, target_user='rider_john', rating=4, tip=0.0)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].rate_and_tip(ride_id=301, target_user='driver_smith', rating=5, tip=10.0)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].get_env_state()"}
        ]
    },
    {
        'name': 'New Methods - Add funds and Profile Query',
        'steps': [
            {'expect_success': False, 'tool_call': "env['ridehailing'].add_funds(amount=50.0)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].add_funds(amount=-10.0)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].add_funds(amount=50.0)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].get_user_profile()"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].get_user_profile(target_user='driver_smith')"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].get_user_profile(target_user='ghost_user')"}
        ]
    },
    {
        'name': 'New Methods - Driver Status and Change Destination',
        'steps': [
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='driver_doe')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].set_driver_status(is_available=False)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].set_driver_status(is_available=True)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].request_ride(dropoff_x=10, dropoff_y=10, car_type='Economy')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='driver_doe')"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].accept_ride(ride_id=301)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].set_driver_status(is_available=True)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].accept_ride(ride_id=301)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].change_destination(ride_id=301, new_x=15, new_y=15)"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='driver_doe')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='Arrived')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='In Progress')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].update_ride_status(ride_id=301, new_status='Completed')"},
            {'expect_success': True, 'tool_call': "env['ridehailing'].login(username='rider_john')"},
            {'expect_success': False, 'tool_call': "env['ridehailing'].change_destination(ride_id=301, new_x=20, new_y=20)"}
        ]
    }
]