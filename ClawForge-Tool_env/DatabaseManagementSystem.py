"""
Database Management System (DBMS) Environment API

A stateful environment that stores structured data in tables, views, and other schema objects,
maintaining metadata such as column names, data types, and constraints.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

# Default initial state with sample data for all entities
DEFAULT_STATE: Dict[str, Any] = {
    # Schema entities
    "schemas": [
        {
            "schema_id": "schema_001",
            "schema_name": "public",
            "owner": "admin"
        },
        {
            "schema_id": "schema_002",
            "schema_name": "sales",
            "owner": "sales_admin"
        },
        {
            "schema_id": "schema_003",
            "schema_name": "hr",
            "owner": "hr_admin"
        }
    ],
    
    # Table entities
    "tables": [
        {
            "table_id": "table_001",
            "table_name": "users",
            "schema_name": "public",
            "creation_time": "2024-01-15T10:30:00",
            "status": "active"
        },
        {
            "table_id": "table_002",
            "table_name": "orders",
            "schema_name": "sales",
            "creation_time": "2024-01-16T14:20:00",
            "status": "active"
        },
        {
            "table_id": "table_003",
            "table_name": "employees",
            "schema_name": "hr",
            "creation_time": "2024-01-17T09:00:00",
            "status": "active"
        }
    ],
    
    # Column entities
    "columns": [
        {
            "column_id": "col_001",
            "table_id": "table_001",
            "column_name": "user_id",
            "data_type": "INTEGER",
            "is_nullable": False,
            "ordinal_position": 1
        },
        {
            "column_id": "col_002",
            "table_id": "table_001",
            "column_name": "username",
            "data_type": "VARCHAR(255)",
            "is_nullable": False,
            "ordinal_position": 2
        },
        {
            "column_id": "col_003",
            "table_id": "table_001",
            "column_name": "email",
            "data_type": "VARCHAR(255)",
            "is_nullable": True,
            "ordinal_position": 3
        },
        {
            "column_id": "col_004",
            "table_id": "table_002",
            "column_name": "order_id",
            "data_type": "INTEGER",
            "is_nullable": False,
            "ordinal_position": 1
        },
        {
            "column_id": "col_005",
            "table_id": "table_002",
            "column_name": "customer_id",
            "data_type": "INTEGER",
            "is_nullable": False,
            "ordinal_position": 2
        },
        {
            "column_id": "col_006",
            "table_id": "table_002",
            "column_name": "total_amount",
            "data_type": "DECIMAL(10,2)",
            "is_nullable": True,
            "ordinal_position": 3
        },
        {
            "column_id": "col_007",
            "table_id": "table_003",
            "column_name": "employee_id",
            "data_type": "INTEGER",
            "is_nullable": False,
            "ordinal_position": 1
        },
        {
            "column_id": "col_008",
            "table_id": "table_003",
            "column_name": "full_name",
            "data_type": "VARCHAR(255)",
            "is_nullable": False,
            "ordinal_position": 2
        },
        {
            "column_id": "col_009",
            "table_id": "table_003",
            "column_name": "department",
            "data_type": "VARCHAR(100)",
            "is_nullable": True,
            "ordinal_position": 3
        }
    ],
    
    # System catalog
    "system_catalog": {
        "last_refresh_time": "2024-01-20T08:00:00",
        "access_log": [
            {"timestamp": "2024-01-20T08:00:00", "event": "system_startup", "user": "system"},
            {"timestamp": "2024-01-20T08:05:00", "event": "catalog_refresh", "user": "admin"},
            {"timestamp": "2024-01-20T08:10:00", "event": "schema_query", "user": "developer"}
        ]
    },
    
    # Auxiliary state
    "current_user": "admin",
    "session_id": "sess_001",
    
    # ID counters for generating unique IDs
    "next_table_id": 4,
    "next_column_id": 10,
    "next_schema_id": 4
}


class DatabaseManagementSystemAPI:
    """
    Database Management System (DBMS) Environment API.
    
    A stateful environment that stores structured data in tables, views, and other schema objects,
    maintaining metadata such as column names, data types, and constraints. It supports querying
    both data and schema information through standardized interfaces or system catalog tables.
    """
    
    def __init__(self):
        """
        Initialize the DBMS environment API.
        
        Declares all state attributes with type hints and sets up the API description.
        """
        self.schemas: List[Dict[str, Any]] = []
        self.tables: List[Dict[str, Any]] = []
        self.columns: List[Dict[str, Any]] = []
        self.system_catalog: Dict[str, Any] = {}
        self.current_user: str = ""
        self.session_id: str = ""
        self.next_table_id: int = 1
        self.next_column_id: int = 1
        self.next_schema_id: int = 1
        
        self._api_description = "A database management system API for managing tables, columns, schemas, and system catalog metadata."
    
    def _timestamp(self) -> str:
        """
        Generate a consistent ISO format timestamp string.
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        If a key is not present in the scenario, falls back to DEFAULT_STATE using deepcopy.
        
        Args:
            scenario: Dictionary containing the initial state configuration.
            long_context: Flag for long context scenarios (reserved for future use).
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
        Return a dictionary containing all current environment state variables.
        
        Returns:
            Dict[str, Any]: A dictionary with all internal state variables including:
                - schemas: List of schema objects
                - tables: List of table objects
                - columns: List of column objects
                - system_catalog: System catalog state
                - current_user: Current active user
                - session_id: Current session identifier
                - next_table_id: Counter for generating table IDs
                - next_column_id: Counter for generating column IDs
                - next_schema_id: Counter for generating schema IDs
        """
        return {
            "schemas": deepcopy(self.schemas),
            "tables": deepcopy(self.tables),
            "columns": deepcopy(self.columns),
            "system_catalog": deepcopy(self.system_catalog),
            "current_user": self.current_user,
            "session_id": self.session_id,
            "next_table_id": self.next_table_id,
            "next_column_id": self.next_column_id,
            "next_schema_id": self.next_schema_id
        }
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_columns_by_table_id(self, table_id: str) -> Dict[str, Any]:
        """
        Retrieve all columns associated with a given table_id, ordered by ordinal_position.
        
        Args:
            table_id: The unique identifier of the table.
            
        Returns:
            Dict[str, Any]: A dictionary containing either:
                - 'columns': List of column objects ordered by ordinal_position
                - 'error': Error message if table doesn't exist
        """
        # Check if table exists
        table_exists = any(t["table_id"] == table_id for t in self.tables)
        if not table_exists:
            return {"error": f"Table with table_id '{table_id}' does not exist."}
        
        # Get columns for the table
        table_columns = [c for c in self.columns if c["table_id"] == table_id]
        # Sort by ordinal_position
        table_columns.sort(key=lambda x: x["ordinal_position"])
        
        return {"columns": deepcopy(table_columns)}
    
    def get_table_by_id(self, table_id: str) -> Dict[str, Any]:
        """
        Retrieve metadata (name, schema, creation time, status) for a table given its table_id.
        
        Args:
            table_id: The unique identifier of the table.
            
        Returns:
            Dict[str, Any]: A dictionary containing either:
                - 'table': The table metadata object
                - 'error': Error message if table doesn't exist
        """
        for table in self.tables:
            if table["table_id"] == table_id:
                return {"table": deepcopy(table)}
        
        return {"error": f"Table with table_id '{table_id}' does not exist."}
    
    def get_table_by_name(self, table_name: str, schema_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Find a table by its table_name within a schema (optional schema context).
        
        Args:
            table_name: The name of the table to find.
            schema_name: Optional schema name to narrow the search.
            
        Returns:
            Dict[str, Any]: A dictionary containing either:
                - 'table': The table metadata object
                - 'tables': List of matching tables if multiple found (no schema specified)
                - 'error': Error message if table doesn't exist
        """
        matching_tables = []
        for table in self.tables:
            if table["table_name"] == table_name:
                if schema_name is None or table["schema_name"] == schema_name:
                    matching_tables.append(deepcopy(table))
        
        if not matching_tables:
            if schema_name:
                return {"error": f"Table '{table_name}' not found in schema '{schema_name}'."}
            return {"error": f"Table '{table_name}' not found."}
        
        if len(matching_tables) == 1:
            return {"table": matching_tables[0]}
        
        return {"tables": matching_tables}
    
    def list_all_tables(self) -> Dict[str, Any]:
        """
        Return a list of all tables in the system with basic metadata.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - 'tables': List of all table metadata objects
                - 'count': Total number of tables
        """
        return {
            "tables": deepcopy(self.tables),
            "count": len(self.tables)
        }
    
    def list_tables_in_schema(self, schema_name: str) -> Dict[str, Any]:
        """
        Retrieve all tables belonging to a specific schema.
        
        Args:
            schema_name: The name of the schema.
            
        Returns:
            Dict[str, Any]: A dictionary containing either:
                - 'tables': List of tables in the schema
                - 'count': Number of tables found
                - 'error': Error message if schema doesn't exist
        """
        # Check if schema exists
        schema_exists = any(s["schema_name"] == schema_name for s in self.schemas)
        if not schema_exists:
            return {"error": f"Schema '{schema_name}' does not exist."}
        
        schema_tables = [t for t in self.tables if t["schema_name"] == schema_name]
        return {
            "tables": deepcopy(schema_tables),
            "count": len(schema_tables)
        }
    
    def get_schema_by_name(self, schema_name: str) -> Dict[str, Any]:
        """
        Retrieve schema metadata by schema_name.
        
        Args:
            schema_name: The name of the schema.
            
        Returns:
            Dict[str, Any]: A dictionary containing either:
                - 'schema': The schema metadata object
                - 'error': Error message if schema doesn't exist
        """
        for schema in self.schemas:
            if schema["schema_name"] == schema_name:
                return {"schema": deepcopy(schema)}
        
        return {"error": f"Schema '{schema_name}' does not exist."}
    
    def list_all_schemas(self) -> Dict[str, Any]:
        """
        Return all available schemas in the database.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - 'schemas': List of all schema metadata objects
                - 'count': Total number of schemas
        """
        return {
            "schemas": deepcopy(self.schemas),
            "count": len(self.schemas)
        }
    
    def get_system_catalog_state(self) -> Dict[str, Any]:
        """
        Retrieve current system catalog information including last refresh time and access log.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - 'system_catalog': The system catalog state object
        """
        return {"system_catalog": deepcopy(self.system_catalog)}
    
    def check_column_exists(self, table_id: str, column_name: str) -> Dict[str, Any]:
        """
        Verify whether a column with a given name exists in a specified table.
        
        Args:
            table_id: The unique identifier of the table.
            column_name: The name of the column to check.
            
        Returns:
            Dict[str, Any]: A dictionary containing:
                - 'exists': Boolean indicating if the column exists
                - 'column': The column object if found (optional)
                - 'error': Error message if table doesn't exist
        """
        # Check if table exists
        table_exists = any(t["table_id"] == table_id for t in self.tables)
        if not table_exists:
            return {"error": f"Table with table_id '{table_id}' does not exist."}
        
        for column in self.columns:
            if column["table_id"] == table_id and column["column_name"] == column_name:
                return {"exists": True, "column": deepcopy(column)}
        
        return {"exists": False}
    
    def get_column_by_name(self, table_id: str, column_name: str) -> Dict[str, Any]:
        """
        Retrieve column metadata by column name and associated table.
        
        Args:
            table_id: The unique identifier of the table.
            column_name: The name of the column.
            
        Returns:
            Dict[str, Any]: A dictionary containing either:
                - 'column': The column metadata object
                - 'error': Error message if table or column doesn't exist
        """
        # Check if table exists
        table_exists = any(t["table_id"] == table_id for t in self.tables)
        if not table_exists:
            return {"error": f"Table with table_id '{table_id}' does not exist."}
        
        for column in self.columns:
            if column["table_id"] == table_id and column["column_name"] == column_name:
                return {"column": deepcopy(column)}
        
        return {"error": f"Column '{column_name}' not found in table '{table_id}'."}
    
    # ==================== STATE CHANGE OPERATIONS ====================
    
    def create_table(
        self,
        table_name: str,
        schema_name: str,
        status: str = "active"
    ) -> Dict[str, Any]:
        """
        Add a new table to the system with specified metadata and associate it with a schema.
        
        Args:
            table_name: The name for the new table.
            schema_name: The schema to associate the table with.
            status: The initial status of the table (default: 'active').
            
        Returns:
            Dict[str, Any]: A dictionary containing either:
                - 'success': True and 'table': The created table object
                - 'error': Error message if validation fails
        """
        # Validate schema exists
        schema_exists = any(s["schema_name"] == schema_name for s in self.schemas)
        if not schema_exists:
            return {"error": f"Schema '{schema_name}' does not exist. Cannot create table."}
        
        # Check for duplicate table name in schema
        for table in self.tables:
            if table["table_name"] == table_name and table["schema_name"] == schema_name:
                return {"error": f"Table '{table_name}' already exists in schema '{schema_name}'."}
        
        # Create new table
        new_table = {
            "table_id": f"table_{self.next_table_id:03d}",
            "table_name": table_name,
            "schema_name": schema_name,
            "creation_time": self._timestamp(),
            "status": status
        }
        
        self.tables.append(new_table)
        self.next_table_id += 1
        
        return {"success": True, "table": deepcopy(new_table)}
    
    def delete_table(self, table_id: str) -> Dict[str, Any]:
        """
        Remove a table by table_id and invalidate or delete all its associated columns.
        
        Enforces referential integrity by removing all columns belonging to the table.
        
        Args:
            table_id: The unique identifier of the table to delete.
            
        Returns:
            Dict[str, Any]: A dictionary containing either:
                - 'success': True and deletion details
                - 'error': Error message if table doesn't exist
        """
        # Find table
        table_index = None
        for i, table in enumerate(self.tables):
            if table["table_id"] == table_id:
                table_index = i
                break
        
        if table_index is None:
            return {"error": f"Table with table_id '{table_id}' does not exist."}
        
        # Remove associated columns (enforce referential integrity)
        columns_before = len(self.columns)
        self.columns = [c for c in self.columns if c["table_id"] != table_id]
        columns_removed = columns_before - len(self.columns)
        
        # Remove table
        deleted_table = self.tables.pop(table_index)
        
        return {
            "success": True,
            "deleted_table": deepcopy(deleted_table),
            "columns_removed": columns_removed
        }
    
    def create_column(
        self,
        table_id: str,
        column_name: str,
        data_type: str,
        is_nullable: bool = True,
        ordinal_position: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Add a new column to an existing table.
        
        Validates that the table exists and the column metadata is consistent.
        
        Args:
            table_id: The table to add the column to.
            column_name: The name for the new column.
            data_type: The data type of the column.
            is_nullable: Whether the column allows NULL values (default: True).
            ordinal_position: The position of the column (auto-assigned if not provided).
            
        Returns:
            Dict[str, Any]: A dictionary containing either:
                - 'success': True and 'column': The created column object
                - 'error': Error message if validation fails
        """
        # Validate table exists (Constraint: Only existing tables can have columns)
        table_exists = any(t["table_id"] == table_id for t in self.tables)
        if not table_exists:
            return {"error": f"Table with table_id '{table_id}' does not exist. Cannot create column."}
        
        # Check for duplicate column name in table (Constraint: consistent metadata)
        for column in self.columns:
            if column["table_id"] == table_id and column["column_name"] == column_name:
                return {"error": f"Column '{column_name}' already exists in table '{table_id}'."}
        
        # Calculate ordinal position if not provided
        if ordinal_position is None:
            existing_positions = [c["ordinal_position"] for c in self.columns if c["table_id"] == table_id]
            ordinal_position = max(existing_positions, default=0) + 1
        
        # Create new column
        new_column = {
            "column_id": f"col_{self.next_column_id:03d}",
            "table_id": table_id,
            "column_name": column_name,
            "data_type": data_type,
            "is_nullable": is_nullable,
            "ordinal_position": ordinal_position
        }
        
        self.columns.append(new_column)
        self.next_column_id += 1
        
        return {"success": True, "column": deepcopy(new_column)}
    
    def delete_column(self, column_id: str) -> Dict[str, Any]:
        """
        Remove a column by column_id.
        
        Ensures the column belongs to an existing table before deletion.
        
        Args:
            column_id: The unique identifier of the column to delete.
            
        Returns:
            Dict[str, Any]: A dictionary containing either:
                - 'success': True and 'deleted_column': The deleted column object
                - 'error': Error message if column doesn't exist
        """
        # Find column
        column_index = None
        for i, column in enumerate(self.columns):
            if column["column_id"] == column_id:
                column_index = i
                break
        
        if column_index is None:
            return {"error": f"Column with column_id '{column_id}' does not exist."}
        
        # Remove column
        deleted_column = self.columns.pop(column_index)
        
        return {"success": True, "deleted_column": deepcopy(deleted_column)}
    
    def rename_table(self, table_id: str, new_table_name: str) -> Dict[str, Any]:
        """
        Update the table_name of an existing table.
        
        Args:
            table_id: The unique identifier of the table.
            new_table_name: The new name for the table.
            
        Returns:
            Dict[str, Any]: A dictionary containing either:
                - 'success': True and 'table': The updated table object
                - 'error': Error message if validation fails
        """
        # Find table
        target_table = None
        for table in self.tables:
            if table["table_id"] == table_id:
                target_table = table
                break
        
        if target_table is None:
            return {"error": f"Table with table_id '{table_id}' does not exist."}
        
        # Check for name conflict in same schema
        for table in self.tables:
            if (table["table_name"] == new_table_name and 
                table["schema_name"] == target_table["schema_name"] and
                table["table_id"] != table_id):
                return {"error": f"Table '{new_table_name}' already exists in schema '{target_table['schema_name']}'."}
        
        # Update table name
        old_name = target_table["table_name"]
        target_table["table_name"] = new_table_name
        
        return {
            "success": True,
            "table": deepcopy(target_table),
            "old_name": old_name
        }
    
    def rename_column(self, column_id: str, new_column_name: str) -> Dict[str, Any]:
        """
        Update the column_name of an existing column.
        
        Args:
            column_id: The unique identifier of the column.
            new_column_name: The new name for the column.
            
        Returns:
            Dict[str, Any]: A dictionary containing either:
                - 'success': True and 'column': The updated column object
                - 'error': Error message if validation fails
        """
        # Find column
        target_column = None
        for column in self.columns:
            if column["column_id"] == column_id:
                target_column = column
                break
        
        if target_column is None:
            return {"error": f"Column with column_id '{column_id}' does not exist."}
        
        # Check for name conflict in same table
        for column in self.columns:
            if (column["column_name"] == new_column_name and 
                column["table_id"] == target_column["table_id"] and
                column["column_id"] != column_id):
                return {"error": f"Column '{new_column_name}' already exists in table '{target_column['table_id']}'."}
        
        # Update column name
        old_name = target_column["column_name"]
        target_column["column_name"] = new_column_name
        
        return {
            "success": True,
            "column": deepcopy(target_column),
            "old_name": old_name
        }
    
    def update_column_data_type(self, column_id: str, new_data_type: str) -> Dict[str, Any]:
        """
        Modify the data_type of an existing column.
        
        Subject to schema validation.
        
        Args:
            column_id: The unique identifier of the column.
            new_data_type: The new data type for the column.
            
        Returns:
            Dict[str, Any]: A dictionary containing either:
                - 'success': True and 'column': The updated column object
                - 'error': Error message if column doesn't exist or validation fails
        """
        # Find column
        target_column = None
        for column in self.columns:
            if column["column_id"] == column_id:
                target_column = column
                break
        
        if target_column is None:
            return {"error": f"Column with column_id '{column_id}' does not exist."}
        
        # Validate data type is not empty
        if not new_data_type or not new_data_type.strip():
            return {"error": "Data type cannot be empty."}
        
        # Update data type
        old_data_type = target_column["data_type"]
        target_column["data_type"] = new_data_type
        
        return {
            "success": True,
            "column": deepcopy(target_column),
            "old_data_type": old_data_type
        }
    
    def refresh_system_catalog(self) -> Dict[str, Any]:
        """
        Update the system catalog's internal state (e.g., last_refresh_time) and log the event.
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - 'success': True
                - 'last_refresh_time': The new refresh timestamp
        """
        timestamp = self._timestamp()
        self.system_catalog["last_refresh_time"] = timestamp
        
        # Log the refresh event
        if "access_log" not in self.system_catalog:
            self.system_catalog["access_log"] = []
        
        self.system_catalog["access_log"].append({
            "timestamp": timestamp,
            "event": "catalog_refresh",
            "user": self.current_user
        })
        
        return {
            "success": True,
            "last_refresh_time": timestamp
        }
    
    def log_access_event(self, event: str, user: Optional[str] = None) -> Dict[str, Any]:
        """
        Append a new entry to the system catalog access log (e.g., for auditing query operations).
        
        Args:
            event: Description of the access event.
            user: The user performing the action (defaults to current_user).
            
        Returns:
            Dict[str, Any]: A dictionary containing either:
                - 'success': True and 'log_entry': The created log entry
                - 'error': Error message if event description is empty
        """
        if not event or not event.strip():
            return {"error": "Event description cannot be empty."}
        
        # Ensure access_log exists
        if "access_log" not in self.system_catalog:
            self.system_catalog["access_log"] = []
        
        log_entry = {
            "timestamp": self._timestamp(),
            "event": event,
            "user": user if user else self.current_user
        }
        
        self.system_catalog["access_log"].append(log_entry)
        
        return {"success": True, "log_entry": deepcopy(log_entry)}


# Test cases for the DBMS API
__TEST_CASES__ = [
    {
        "name": "Complete table and column lifecycle",
        "steps": [
            {"tool_call": "list_all_schemas()", "expect_success": True},
            {"tool_call": "create_table(table_name='products', schema_name='sales')", "expect_success": True},
            {"tool_call": "get_table_by_name(table_name='products', schema_name='sales')", "expect_success": True},
            {"tool_call": "create_column(table_id='table_004', column_name='product_id', data_type='INTEGER', is_nullable=False)", "expect_success": True},
            {"tool_call": "create_column(table_id='table_004', column_name='product_name', data_type='VARCHAR(255)')", "expect_success": True},
            {"tool_call": "get_columns_by_table_id(table_id='table_004')", "expect_success": True},
            {"tool_call": "delete_table(table_id='table_004')", "expect_success": True}
        ]
    },
    {
        "name": "Query existing data and verify schema structure",
        "steps": [
            {"tool_call": "list_all_tables()", "expect_success": True},
            {"tool_call": "get_table_by_id(table_id='table_001')", "expect_success": True},
            {"tool_call": "get_columns_by_table_id(table_id='table_001')", "expect_success": True},
            {"tool_call": "check_column_exists(table_id='table_001', column_name='username')", "expect_success": True},
            {"tool_call": "get_column_by_name(table_id='table_001', column_name='email')", "expect_success": True},
            {"tool_call": "get_system_catalog_state()", "expect_success": True}
        ]
    },
    {
        "name": "Rename operations and metadata updates",
        "steps": [
            {"tool_call": "rename_table(table_id='table_002', new_table_name='customer_orders')", "expect_success": True},
            {"tool_call": "get_table_by_id(table_id='table_002')", "expect_success": True},
            {"tool_call": "rename_column(column_id='col_005', new_column_name='buyer_id')", "expect_success": True},
            {"tool_call": "get_column_by_id(column_id='col_005')", "expect_success": True},
            {"tool_call": "update_column_type(column_id='col_005', new_data_type='BIGINT')", "expect_success": True}
        ]
    },
    {
        "name": "Error handling for invalid operations",
        "steps": [
            {"tool_call": "get_table_by_id(table_id='nonexistent_table')", "expect_success": False},
            {"tool_call": "delete_column(column_id='nonexistent_col')", "expect_success": False},
            {"tool_call": "create_table(table_name='users', schema_name='public')", "expect_success": False},
            {"tool_call": "create_column(table_id='table_001', column_name='username', data_type='VARCHAR(50)')", "expect_success": False}
        ]
    },
    {
        "name": "Schema management operations",
        "steps": [
            {"tool_call": "create_schema(schema_name='analytics')", "expect_success": True},
            {"tool_call": "get_schema_by_name(schema_name='analytics')", "expect_success": True},
            {"tool_call": "list_tables_in_schema(schema_name='analytics')", "expect_success": True},
            {"tool_call": "rename_schema(schema_name='analytics', new_schema_name='reporting')", "expect_success": True},
            {"tool_call": "delete_schema(schema_name='reporting')", "expect_success": True}
        ]
    }
]


class DatabaseManagementSystem:
    def __init__(self):
        self.schemas = {
            "public": {
                "schema_id": "schema_001",
                "schema_name": "public",
                "created_at": "2024-01-01T00:00:00Z"
            },
            "sales": {
                "schema_id": "schema_002",
                "schema_name": "sales",
                "created_at": "2024-01-15T00:00:00Z"
            }
        }
        
        self.tables = {
            "table_001": {
                "table_id": "table_001",
                "table_name": "users",
                "schema_name": "public",
                "created_at": "2024-01-01T10:00:00Z",
                "updated_at": "2024-01-01T10:00:00Z"
            },
            "table_002": {
                "table_id": "table_002",
                "table_name": "orders",
                "schema_name": "public",
                "created_at": "2024-01-02T10:00:00Z",
                "updated_at": "2024-01-02T10:00:00Z"
            },
            "table_003": {
                "table_id": "table_003",
                "table_name": "customers",
                "schema_name": "sales",
                "created_at": "2024-01-15T12:00:00Z",
                "updated_at": "2024-01-15T12:00:00Z"
            }
        }
        
        self.columns = {
            "col_001": {
                "column_id": "col_001",
                "table_id": "table_001",
                "column_name": "user_id",
                "data_type": "INTEGER",
                "is_nullable": False,
                "is_primary_key": True,
                "default_value": None
            },
            "col_002": {
                "column_id": "col_002",
                "table_id": "table_001",
                "column_name": "username",
                "data_type": "VARCHAR(50)",
                "is_nullable": False,
                "is_primary_key": False,
                "default_value": None
            },
            "col_003": {
                "column_id": "col_003",
                "table_id": "table_001",
                "column_name": "email",
                "data_type": "VARCHAR(255)",
                "is_nullable": True,
                "is_primary_key": False,
                "default_value": None
            },
            "col_004": {
                "column_id": "col_004",
                "table_id": "table_002",
                "column_name": "order_id",
                "data_type": "INTEGER",
                "is_nullable": False,
                "is_primary_key": True,
                "default_value": None
            },
            "col_005": {
                "column_id": "col_005",
                "table_id": "table_002",
                "column_name": "customer_id",
                "data_type": "INTEGER",
                "is_nullable": False,
                "is_primary_key": False,
                "default_value": None
            },
            "col_006": {
                "column_id": "col_006",
                "table_id": "table_003",
                "column_name": "customer_id",
                "data_type": "INTEGER",
                "is_nullable": False,
                "is_primary_key": True,
                "default_value": None
            },
            "col_007": {
                "column_id": "col_007",
                "table_id": "table_003",
                "column_name": "customer_name",
                "data_type": "VARCHAR(100)",
                "is_nullable": False,
                "is_primary_key": False,
                "default_value": None
            }
        }
        
        self.next_table_id = 4
        self.next_column_id = 8
        self.next_schema_id = 3

    def _get_current_timestamp(self):
        from datetime import datetime
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    # Schema operations
    def list_all_schemas(self):
        return {"schemas": list(self.schemas.values())}

    def create_schema(self, schema_name):
        if schema_name in self.schemas:
            return {"error": f"Schema '{schema_name}' already exists"}
        
        schema_id = f"schema_{self.next_schema_id:03d}"
        self.next_schema_id += 1
        
        new_schema = {
            "schema_id": schema_id,
            "schema_name": schema_name,
            "created_at": self._get_current_timestamp()
        }
        self.schemas[schema_name] = new_schema
        return {"schema": new_schema, "message": f"Schema '{schema_name}' created successfully"}

    def get_schema_by_name(self, schema_name):
        if schema_name not in self.schemas:
            return {"error": f"Schema '{schema_name}' not found"}
        return {"schema": self.schemas[schema_name]}

    def rename_schema(self, schema_name, new_schema_name):
        if schema_name not in self.schemas:
            return {"error": f"Schema '{schema_name}' not found"}
        if new_schema_name in self.schemas:
            return {"error": f"Schema '{new_schema_name}' already exists"}
        
        schema = self.schemas.pop(schema_name)
        schema["schema_name"] = new_schema_name
        self.schemas[new_schema_name] = schema
        
        # Update tables referencing this schema
        for table in self.tables.values():
            if table["schema_name"] == schema_name:
                table["schema_name"] = new_schema_name
        
        return {"schema": schema, "message": f"Schema renamed from '{schema_name}' to '{new_schema_name}'"}

    def delete_schema(self, schema_name):
        if schema_name not in self.schemas:
            return {"error": f"Schema '{schema_name}' not found"}
        
        # Check if schema has tables
        tables_in_schema = [t for t in self.tables.values() if t["schema_name"] == schema_name]
        if tables_in_schema:
            return {"error": f"Cannot delete schema '{schema_name}': contains {len(tables_in_schema)} table(s)"}
        
        deleted_schema = self.schemas.pop(schema_name)
        return {"message": f"Schema '{schema_name}' deleted successfully", "deleted_schema": deleted_schema}

    # Table operations
    def list_all_tables(self):
        return {"tables": list(self.tables.values())}

    def list_tables_in_schema(self, schema_name):
        if schema_name not in self.schemas:
            return {"error": f"Schema '{schema_name}' not found"}
        
        tables = [t for t in self.tables.values() if t["schema_name"] == schema_name]
        return {"schema_name": schema_name, "tables": tables}

    def create_table(self, table_name, schema_name="public"):
        if schema_name not in self.schemas:
            return {"error": f"Schema '{schema_name}' not found"}
        
        # Check if table already exists in schema
        for table in self.tables.values():
            if table["table_name"] == table_name and table["schema_name"] == schema_name:
                return {"error": f"Table '{table_name}' already exists in schema '{schema_name}'"}
        
        table_id = f"table_{self.next_table_id:03d}"
        self.next_table_id += 1
        
        current_time = self._get_current_timestamp()
        new_table = {
            "table_id": table_id,
            "table_name": table_name,
            "schema_name": schema_name,
            "created_at": current_time,
            "updated_at": current_time
        }
        self.tables[table_id] = new_table
        return {"table": new_table, "message": f"Table '{table_name}' created successfully in schema '{schema_name}'"}

    def get_table_by_id(self, table_id):
        if table_id not in self.tables:
            return {"error": f"Table with id '{table_id}' not found"}
        return {"table": self.tables[table_id]}

    def get_table_by_name(self, table_name, schema_name="public"):
        for table in self.tables.values():
            if table["table_name"] == table_name and table["schema_name"] == schema_name:
                return {"table": table}
        return {"error": f"Table '{table_name}' not found in schema '{schema_name}'"}

    def rename_table(self, table_id, new_table_name):
        if table_id not in self.tables:
            return {"error": f"Table with id '{table_id}' not found"}
        
        table = self.tables[table_id]
        schema_name = table["schema_name"]
        
        # Check if new name already exists in same schema
        for t in self.tables.values():
            if t["table_name"] == new_table_name and t["schema_name"] == schema_name and t["table_id"] != table_id:
                return {"error": f"Table '{new_table_name}' already exists in schema '{schema_name}'"}
        
        old_name = table["table_name"]
        table["table_name"] = new_table_name
        table["updated_at"] = self._get_current_timestamp()
        
        return {"table": table, "message": f"Table renamed from '{old_name}' to '{new_table_name}'"}

    def delete_table(self, table_id):
        if table_id not in self.tables:
            return {"error": f"Table with id '{table_id}' not found"}
        
        # Delete all columns belonging to this table
        columns_to_delete = [col_id for col_id, col in self.columns.items() if col["table_id"] == table_id]
        for col_id in columns_to_delete:
            del self.columns[col_id]
        
        deleted_table = self.tables.pop(table_id)
        return {
            "message": f"Table '{deleted_table['table_name']}' deleted successfully",
            "deleted_table": deleted_table,
            "deleted_columns_count": len(columns_to_delete)
        }

    # Column operations
    def create_column(self, table_id, column_name, data_type, is_nullable=True, is_primary_key=False, default_value=None):
        if table_id not in self.tables:
            return {"error": f"Table with id '{table_id}' not found"}
        
        # Check if column already exists in table
        for col in self.columns.values():
            if col["table_id"] == table_id and col["column_name"] == column_name:
                return {"error": f"Column '{column_name}' already exists in table '{table_id}'"}
        
        column_id = f"col_{self.next_column_id:03d}"
        self.next_column_id += 1
        
        new_column = {
            "column_id": column_id,
            "table_id": table_id,
            "column_name": column_name,
            "data_type": data_type,
            "is_nullable": is_nullable,
            "is_primary_key": is_primary_key,
            "default_value": default_value
        }
        self.columns[column_id] = new_column
        
        # Update table's updated_at
        self.tables[table_id]["updated_at"] = self._get_current_timestamp()
        
        return {"column": new_column, "message": f"Column '{column_name}' created successfully"}

    def get_column_by_id(self, column_id):
        if column_id not in self.columns:
            return {"error": f"Column with id '{column_id}' not found"}
        return {"column": self.columns[column_id]}

    def get_column_by_name(self, table_id, column_name):
        if table_id not in self.tables:
            return {"error": f"Table with id '{table_id}' not found"}
        
        for col in self.columns.values():
            if col["table_id"] == table_id and col["column_name"] == column_name:
                return {"column": col}
        return {"error": f"Column '{column_name}' not found in table '{table_id}'"}

    def get_columns_by_table_id(self, table_id):
        if table_id not in self.tables:
            return {"error": f"Table with id '{table_id}' not found"}
        
        columns = [col for col in self.columns.values() if col["table_id"] == table_id]
        return {"table_id": table_id, "columns": columns}

    def check_column_exists(self, table_id, column_name):
        if table_id not in self.tables:
            return {"error": f"Table with id '{table_id}' not found"}
        
        for col in self.columns.values():
            if col["table_id"] == table_id and col["column_name"] == column_name:
                return {"exists": True, "column": col}
        return {"exists": False}

    def rename_column(self, column_id, new_column_name):
        if column_id not in self.columns:
            return {"error": f"Column with id '{column_id}' not found"}
        
        column = self.columns[column_id]
        table_id = column["table_id"]
        
        # Check if new name already exists in same table
        for col in self.columns.values():
            if col["table_id"] == table_id and col["column_name"] == new_column_name and col["column_id"] != column_id:
                return {"error": f"Column '{new_column_name}' already exists in table '{table_id}'"}
        
        old_name = column["column_name"]
        column["column_name"] = new_column_name
        
        # Update table's updated_at
        self.tables[table_id]["updated_at"] = self._get_current_timestamp()
        
        return {"column": column, "message": f"Column renamed from '{old_name}' to '{new_column_name}'"}

    def update_column_type(self, column_id, new_data_type):
        if column_id not in self.columns:
            return {"error": f"Column with id '{column_id}' not found"}
        
        column = self.columns[column_id]
        old_type = column["data_type"]
        column["data_type"] = new_data_type
        
        # Update table's updated_at
        table_id = column["table_id"]
        self.tables[table_id]["updated_at"] = self._get_current_timestamp()
        
        return {"column": column, "message": f"Column type changed from '{old_type}' to '{new_data_type}'"}

    def delete_column(self, column_id):
        if column_id not in self.columns:
            return {"error": f"Column with id '{column_id}' not found"}
        
        deleted_column = self.columns.pop(column_id)
        
        # Update table's updated_at
        table_id = deleted_column["table_id"]
        if table_id in self.tables:
            self.tables[table_id]["updated_at"] = self._get_current_timestamp()
        
        return {"message": f"Column '{deleted_column['column_name']}' deleted successfully", "deleted_column": deleted_column}

    # System catalog operations
    def get_system_catalog_state(self):
        return {
            "catalog_state": {
                "total_schemas": len(self.schemas),
                "total_tables": len(self.tables),
                "total_columns": len(self.columns),
                "schemas": list(self.schemas.keys()),
                "tables_by_schema": {
                    schema_name: [t["table_name"] for t in self.tables.values() if t["schema_name"] == schema_name]
                    for schema_name in self.schemas.keys()
                }
            }
        }