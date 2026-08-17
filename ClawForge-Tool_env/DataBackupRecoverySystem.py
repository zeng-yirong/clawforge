"""
Data Backup and Recovery System Environment API

A stateful environment for managing data backups, supporting operations such as
backup creation, restoration, deletion, and status verification.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import uuid

DEFAULT_STATE: Dict[str, Any] = {
    "backups": [
        {
            "backup_id": "BKP-001",
            "creation_timestamp": "2024-01-15T08:30:00",
            "status": "completed",
            "data_location": "/backups/storage/bkp001",
            "size": 1073741824,  # 1 GB
            "checksum": "a1b2c3d4e5f6g7h8i9j0",
            "source_system": "production-db-01"
        },
        {
            "backup_id": "BKP-002",
            "creation_timestamp": "2024-01-16T10:45:00",
            "status": "completed",
            "data_location": "/backups/storage/bkp002",
            "size": 2147483648,  # 2 GB
            "checksum": "b2c3d4e5f6g7h8i9j0k1",
            "source_system": "production-db-02"
        },
        {
            "backup_id": "BKP-003",
            "creation_timestamp": "2024-01-17T14:20:00",
            "status": "in-progress",
            "data_location": "/backups/storage/bkp003",
            "size": 536870912,  # 512 MB
            "checksum": "c3d4e5f6g7h8i9j0k1l2",
            "source_system": "staging-db-01"
        },
        {
            "backup_id": "BKP-004",
            "creation_timestamp": "2024-01-10T06:00:00",
            "status": "failed",
            "data_location": "/backups/storage/bkp004",
            "size": 0,
            "checksum": "",
            "source_system": "production-db-01"
        },
        {
            "backup_id": "BKP-005",
            "creation_timestamp": "2024-01-18T09:15:00",
            "status": "restored",
            "data_location": "/backups/storage/bkp005",
            "size": 1610612736,  # 1.5 GB
            "checksum": "d4e5f6g7h8i9j0k1l2m3",
            "source_system": "production-db-01"
        }
    ],
    "operation_logs": [
        {
            "log_id": "LOG-001",
            "backup_id": "BKP-001",
            "operation_type": "create",
            "timestamp": "2024-01-15T08:30:00",
            "status": "success",
            "operator": "system-scheduler"
        },
        {
            "log_id": "LOG-002",
            "backup_id": "BKP-002",
            "operation_type": "create",
            "timestamp": "2024-01-16T10:45:00",
            "status": "success",
            "operator": "admin-user"
        },
        {
            "log_id": "LOG-003",
            "backup_id": "BKP-003",
            "operation_type": "create",
            "timestamp": "2024-01-17T14:20:00",
            "status": "in-progress",
            "operator": "system-scheduler"
        },
        {
            "log_id": "LOG-004",
            "backup_id": "BKP-005",
            "operation_type": "restore",
            "timestamp": "2024-01-18T11:00:00",
            "status": "success",
            "operator": "admin-user"
        }
    ],
    "system_configuration": {
        "retention_policy": {
            "max_backups": 100,
            "retention_days": 30,
            "delete_failed_after_days": 7
        },
        "auto_backup_enabled": True,
        "last_audit_time": "2024-01-18T00:00:00"
    },
    "current_user": "admin-user",
    "deleted_backup_ids": [],
    "restoring_backup_ids": []
}


class DataBackupRecoverySystem:
    """
    A data backup and recovery system environment API.
    
    This class provides methods to manage data backups including creation,
    restoration, deletion, and status verification. It maintains backup
    metadata, operation logs, and system configuration for comprehensive
    backup lifecycle management.
    """

    def __init__(self) -> None:
        """
        Initialize the DataBackupRecoverySystem environment.
        
        Declares all state attributes with type hints and sets up the API description.
        
        Args:
            None
            
        Returns:
            None
        """
        self.backups: List[Dict[str, Any]] = []
        self.operation_logs: List[Dict[str, Any]] = []
        self.system_configuration: Dict[str, Any] = {}
        self.current_user: str = ""
        self.deleted_backup_ids: List[str] = []
        self.restoring_backup_ids: List[str] = []
        
        self._api_description = (
            "A data backup and recovery system for managing backup creation, "
            "restoration, deletion, and integrity verification operations."
        )

    def _timestamp(self) -> str:
        """
        Generate a unified ISO format timestamp string.
        
        Args:
            None
        
        Returns:
            str: Current timestamp in ISO format (YYYY-MM-DDTHH:MM:SS).
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def _generate_id(self, prefix: str) -> str:
        """
        Generate a unique identifier with the given prefix.
        
        Args:
            prefix: The prefix for the ID (e.g., 'BKP', 'LOG').
            
        Returns:
            str: A unique identifier string.
        """
        return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"

    def _generate_checksum(self, data: str) -> str:
        """
        Generate a checksum for data integrity verification.
        
        Args:
            data: The data string to generate checksum for.
            
        Returns:
            str: A checksum hash string.
        """
        return hashlib.md5(data.encode()).hexdigest()[:20]

    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from the provided scenario dictionary.
        
        If a key is not present in the scenario, falls back to DEFAULT_STATE.
        
        Args:
            scenario: Dictionary containing the initial state configuration.
            long_context: Flag for extended context loading (unused in basic impl).
            
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
        Return the current state of all environment variables.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - backups: List of all backup records
                - operation_logs: List of all operation log entries
                - system_configuration: Current system settings
                - current_user: The current operator user
                - deleted_backup_ids: List of IDs of deleted backups
                - restoring_backup_ids: List of IDs currently being restored
        """
        return {
            "backups": deepcopy(self.backups),
            "operation_logs": deepcopy(self.operation_logs),
            "system_configuration": deepcopy(self.system_configuration),
            "current_user": self.current_user,
            "deleted_backup_ids": deepcopy(self.deleted_backup_ids),
            "restoring_backup_ids": deepcopy(self.restoring_backup_ids)
        }

    def _find_backup_by_id(self, backup_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a backup by its ID.
        
        Args:
            backup_id: The unique identifier of the backup.
            
        Returns:
            Optional[Dict[str, Any]]: The backup record if found, None otherwise.
        """
        for backup in self.backups:
            if backup["backup_id"] == backup_id:
                return backup
        return None

    # ==================== QUERY OPERATIONS ====================

    def list_all_backups(self) -> Dict[str, Any]:
        """
        Retrieve a list of all existing backups with their metadata.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: A dictionary containing:
                - backups: List of all backup records (excluding deleted ones)
                - count: Total number of backups
        """
        active_backups = [
            b for b in self.backups 
            if b["backup_id"] not in self.deleted_backup_ids
        ]
        return {
            "backups": deepcopy(active_backups),
            "count": len(active_backups)
        }

    def get_backup_by_id(self, backup_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific backup.
        
        Args:
            backup_id: The unique identifier of the backup to retrieve.
            
        Returns:
            Dict[str, Any]: The backup details if found, or an error dictionary.
        """
        if not backup_id:
            return {"error": "backup_id is required"}
        
        if backup_id in self.deleted_backup_ids:
            return {"error": f"Backup '{backup_id}' has been deleted"}
        
        backup = self._find_backup_by_id(backup_id)
        if not backup:
            return {"error": f"Backup '{backup_id}' not found"}
        
        return {"backup": deepcopy(backup)}

    def get_latest_n_backups(self, n: int) -> Dict[str, Any]:
        """
        Retrieve the N most recent backups sorted by creation_timestamp.
        
        Args:
            n: The number of recent backups to retrieve.
            
        Returns:
            Dict[str, Any]: A dictionary containing the list of recent backups.
        """
        if not isinstance(n, int) or n <= 0:
            return {"error": "n must be a positive integer"}
        
        active_backups = [
            b for b in self.backups 
            if b["backup_id"] not in self.deleted_backup_ids
        ]
        sorted_backups = sorted(
            active_backups,
            key=lambda x: x["creation_timestamp"],
            reverse=True
        )
        return {
            "backups": deepcopy(sorted_backups[:n]),
            "count": min(n, len(sorted_backups))
        }

    def get_oldest_n_backups(self, n: int) -> Dict[str, Any]:
        """
        Retrieve the N oldest backups sorted by creation_timestamp.
        
        Args:
            n: The number of oldest backups to retrieve.
            
        Returns:
            Dict[str, Any]: A dictionary containing the list of oldest backups.
        """
        if not isinstance(n, int) or n <= 0:
            return {"error": "n must be a positive integer"}
        
        active_backups = [
            b for b in self.backups 
            if b["backup_id"] not in self.deleted_backup_ids
        ]
        sorted_backups = sorted(
            active_backups,
            key=lambda x: x["creation_timestamp"]
        )
        return {
            "backups": deepcopy(sorted_backups[:n]),
            "count": min(n, len(sorted_backups))
        }

    def get_backup_status(self, backup_id: str) -> Dict[str, Any]:
        """
        Return the current status of a backup.
        
        Args:
            backup_id: The unique identifier of the backup.
            
        Returns:
            Dict[str, Any]: The backup status or an error dictionary.
        """
        if not backup_id:
            return {"error": "backup_id is required"}
        
        if backup_id in self.deleted_backup_ids:
            return {"backup_id": backup_id, "status": "deleted"}
        
        backup = self._find_backup_by_id(backup_id)
        if not backup:
            return {"error": f"Backup '{backup_id}' not found"}
        
        is_restoring = backup_id in self.restoring_backup_ids
        return {
            "backup_id": backup_id,
            "status": backup["status"],
            "is_currently_restoring": is_restoring
        }

    def verify_backup_checksum(self, backup_id: str, provided_checksum: Optional[str] = None) -> Dict[str, Any]:
        """
        Validate the integrity of a backup by comparing checksums.
        
        Args:
            backup_id: The unique identifier of the backup.
            provided_checksum: Optional checksum to verify against stored value.
            
        Returns:
            Dict[str, Any]: Verification result with validity status.
        """
        if not backup_id:
            return {"error": "backup_id is required"}
        
        if backup_id in self.deleted_backup_ids:
            return {"error": f"Backup '{backup_id}' has been deleted"}
        
        backup = self._find_backup_by_id(backup_id)
        if not backup:
            return {"error": f"Backup '{backup_id}' not found"}
        
        stored_checksum = backup.get("checksum", "")
        if not stored_checksum:
            return {
                "backup_id": backup_id,
                "valid": False,
                "message": "No checksum stored for this backup"
            }
        
        if provided_checksum:
            is_valid = stored_checksum == provided_checksum
            return {
                "backup_id": backup_id,
                "valid": is_valid,
                "stored_checksum": stored_checksum,
                "provided_checksum": provided_checksum,
                "message": "Checksum match" if is_valid else "Checksum mismatch"
            }
        
        return {
            "backup_id": backup_id,
            "valid": True,
            "stored_checksum": stored_checksum,
            "message": "Checksum is present and available for verification"
        }

    def list_backup_operations(self, backup_id: str) -> Dict[str, Any]:
        """
        Retrieve all operation log entries associated with a backup.
        
        Args:
            backup_id: The unique identifier of the backup.
            
        Returns:
            Dict[str, Any]: List of operation logs for the specified backup.
        """
        if not backup_id:
            return {"error": "backup_id is required"}
        
        operations = [
            log for log in self.operation_logs 
            if log["backup_id"] == backup_id
        ]
        return {
            "backup_id": backup_id,
            "operations": deepcopy(operations),
            "count": len(operations)
        }

    def get_system_configuration(self) -> Dict[str, Any]:
        """
        Retrieve current system settings.
        
        Args:
            None
        
        Returns:
            Dict[str, Any]: The current system configuration including
                retention policy, auto-backup status, and last audit time.
        """
        return {
            "configuration": deepcopy(self.system_configuration)
        }

    def check_restoration_eligibility(self, backup_id: str) -> Dict[str, Any]:
        """
        Determine if a backup can be restored.
        
        A backup is eligible for restoration if its status is "completed"
        and it has not been deleted.
        
        Args:
            backup_id: The unique identifier of the backup.
            
        Returns:
            Dict[str, Any]: Eligibility status with reason if ineligible.
        """
        if not backup_id:
            return {"error": "backup_id is required"}
        
        if backup_id in self.deleted_backup_ids:
            return {
                "backup_id": backup_id,
                "eligible": False,
                "reason": "Backup has been deleted"
            }
        
        backup = self._find_backup_by_id(backup_id)
        if not backup:
            return {"error": f"Backup '{backup_id}' not found"}
        
        if backup["status"] != "completed":
            return {
                "backup_id": backup_id,
                "eligible": False,
                "reason": f"Backup status is '{backup['status']}', must be 'completed'"
            }
        
        return {
            "backup_id": backup_id,
            "eligible": True,
            "reason": "Backup is eligible for restoration"
        }

    def check_deletion_eligibility(self, backup_id: str) -> Dict[str, Any]:
        """
        Determine if a backup can be safely deleted.
        
        A backup cannot be deleted if it is in-progress or being restored.
        
        Args:
            backup_id: The unique identifier of the backup.
            
        Returns:
            Dict[str, Any]: Eligibility status with reason if ineligible.
        """
        if not backup_id:
            return {"error": "backup_id is required"}
        
        if backup_id in self.deleted_backup_ids:
            return {
                "backup_id": backup_id,
                "eligible": False,
                "reason": "Backup has already been deleted"
            }
        
        backup = self._find_backup_by_id(backup_id)
        if not backup:
            return {"error": f"Backup '{backup_id}' not found"}
        
        if backup["status"] == "in-progress":
            return {
                "backup_id": backup_id,
                "eligible": False,
                "reason": "Backup is currently in-progress"
            }
        
        if backup_id in self.restoring_backup_ids:
            return {
                "backup_id": backup_id,
                "eligible": False,
                "reason": "Backup is currently being restored"
            }
        
        return {
            "backup_id": backup_id,
            "eligible": True,
            "reason": "Backup is eligible for deletion"
        }

    # ==================== STATE CHANGE OPERATIONS ====================

    def create_backup(
        self,
        source_system: str,
        data_location: Optional[str] = None,
        size: int = 0
    ) -> Dict[str, Any]:
        """
        Initiate a new backup process, generate metadata, and log the creation.
        
        Args:
            source_system: The source system identifier for the backup.
            data_location: Optional storage location for the backup.
            size: Size of the backup in bytes.
            
        Returns:
            Dict[str, Any]: The created backup details or an error dictionary.
        """
        if not source_system:
            return {"error": "source_system is required"}
        
        backup_id = self._generate_id("BKP")
        timestamp = self._timestamp()
        
        if not data_location:
            data_location = f"/backups/storage/{backup_id.lower()}"
        
        checksum = self._generate_checksum(f"{backup_id}{timestamp}{source_system}")
        
        new_backup = {
            "backup_id": backup_id,
            "creation_timestamp": timestamp,
            "status": "completed",
            "data_location": data_location,
            "size": size,
            "checksum": checksum,
            "source_system": source_system
        }
        
        self.backups.append(new_backup)
        
        self.log_backup_operation(
            backup_id=backup_id,
            operation_type="create",
            status="success"
        )
        
        return {
            "success": True,
            "backup": deepcopy(new_backup),
            "message": f"Backup '{backup_id}' created successfully"
        }

    def restore_backup(self, backup_id: str, target_system: Optional[str] = None) -> Dict[str, Any]:
        """
        Restore a completed backup to the target system.
        
        Verifies checksum before restoration and updates status to "restored".
        
        Args:
            backup_id: The unique identifier of the backup to restore.
            target_system: Optional target system for restoration.
            
        Returns:
            Dict[str, Any]: Restoration result or an error dictionary.
        """
        if not backup_id:
            return {"error": "backup_id is required"}
        
        eligibility = self.check_restoration_eligibility(backup_id)
        if "error" in eligibility:
            return eligibility
        if not eligibility.get("eligible"):
            return {"error": eligibility.get("reason", "Backup not eligible for restoration")}
        
        backup = self._find_backup_by_id(backup_id)
        if not backup:
            return {"error": f"Backup '{backup_id}' not found"}
        
        if not backup.get("checksum"):
            return {"error": "Cannot restore backup: checksum verification failed (no checksum)"}
        
        self.restoring_backup_ids.append(backup_id)
        
        backup["status"] = "restored"
        
        self.restoring_backup_ids.remove(backup_id)
        
        self.log_backup_operation(
            backup_id=backup_id,
            operation_type="restore",
            status="success"
        )
        
        target = target_system or backup["source_system"]
        
        return {
            "success": True,
            "backup_id": backup_id,
            "restored_to": target,
            "message": f"Backup '{backup_id}' restored successfully to '{target}'"
        }

    def delete_backup(self, backup_id: str) -> Dict[str, Any]:
        """
        Remove a backup from active management if eligible.
        
        Preserves the backup entry in operation logs for auditability.
        
        Args:
            backup_id: The unique identifier of the backup to delete.
            
        Returns:
            Dict[str, Any]: Deletion result or an error dictionary.
        """
        if not backup_id:
            return {"error": "backup_id is required"}
        
        eligibility = self.check_deletion_eligibility(backup_id)
        if "error" in eligibility:
            return eligibility
        if not eligibility.get("eligible"):
            return {"error": eligibility.get("reason", "Backup not eligible for deletion")}
        
        self.deleted_backup_ids.append(backup_id)
        
        self.log_backup_operation(
            backup_id=backup_id,
            operation_type="delete",
            status="success"
        )
        
        return {
            "success": True,
            "backup_id": backup_id,
            "message": f"Backup '{backup_id}' deleted successfully"
        }

    def update_backup_status(self, backup_id: str, new_status: str) -> Dict[str, Any]:
        """
        Change the status of a backup as part of lifecycle management.
        
        Args:
            backup_id: The unique identifier of the backup.
            new_status: The new status to set (e.g., 'completed', 'failed').
            
        Returns:
            Dict[str, Any]: Update result or an error dictionary.
        """
        if not backup_id:
            return {"error": "backup_id is required"}
        if not new_status:
            return {"error": "new_status is required"}
        
        valid_statuses = ["completed", "in-progress", "failed", "restored"]
        if new_status not in valid_statuses:
            return {"error": f"Invalid status '{new_status}'. Must be one of: {valid_statuses}"}
        
        if backup_id in self.deleted_backup_ids:
            return {"error": f"Cannot update status of deleted backup '{backup_id}'"}
        
        backup = self._find_backup_by_id(backup_id)
        if not backup:
            return {"error": f"Backup '{backup_id}' not found"}
        
        old_status = backup["status"]
        backup["status"] = new_status
        
        return {
            "success": True,
            "backup_id": backup_id,
            "old_status": old_status,
            "new_status": new_status,
            "message": f"Backup status updated from '{old_status}' to '{new_status}'"
        }

    def log_backup_operation(
        self,
        backup_id: str,
        operation_type: str,
        status: str = "success",
        operator: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Append a new entry to the operation log for auditability.
        
        Args:
            backup_id: The backup ID associated with the operation.
            operation_type: Type of operation (create, restore, delete, etc.).
            status: Status of the operation (success, failed, in-progress).
            operator: The user who performed the operation.
            
        Returns:
            Dict[str, Any]: The created log entry or an error dictionary.
        """
        if not backup_id:
            return {"error": "backup_id is required"}
        if not operation_type:
            return {"error": "operation_type is required"}
        
        valid_operations = ["create", "restore", "delete", "update", "force_delete", "rollback"]
        if operation_type not in valid_operations:
            return {"error": f"Invalid operation_type '{operation_type}'. Must be one of: {valid_operations}"}
        
        log_id = self._generate_id("LOG")
        timestamp = self._timestamp()
        
        log_entry = {
            "log_id": log_id,
            "backup_id": backup_id,
            "operation_type": operation_type,
            "timestamp": timestamp,
            "status": status,
            "operator": operator or self.current_user
        }
        
        self.operation_logs.append(log_entry)
        
        return {
            "success": True,
            "log_entry": deepcopy(log_entry)
        }

    def force_delete_backup(self, backup_id: str, reason: str) -> Dict[str, Any]:
        """
        Override deletion restrictions to remove a backup forcefully.
        
        Used for emergency or admin purposes with explicit logging.
        
        Args:
            backup_id: The unique identifier of the backup to force delete.
            reason: The reason for forcing the deletion.
            
        Returns:
            Dict[str, Any]: Deletion result or an error dictionary.
        """
        if not backup_id:
            return {"error": "backup_id is required"}
        if not reason:
            return {"error": "reason is required for force deletion"}
        
        if backup_id in self.deleted_backup_ids:
            return {"error": f"Backup '{backup_id}' has already been deleted"}
        
        backup = self._find_backup_by_id(backup_id)
        if not backup:
            return {"error": f"Backup '{backup_id}' not found"}
        
        if backup_id in self.restoring_backup_ids:
            self.restoring_backup_ids.remove(backup_id)
        
        self.deleted_backup_ids.append(backup_id)
        
        self.log_backup_operation(
            backup_id=backup_id,
            operation_type="force_delete",
            status="success"
        )
        
        return {
            "success": True,
            "backup_id": backup_id,
            "message": f"Backup '{backup_id}' forcefully deleted",
            "reason": reason
        }

    def rollback_restoration(self, backup_id: str, revert_status: str = "completed") -> Dict[str, Any]:
        """
        Revert a restored system state and update the backup's status.
        
        Args:
            backup_id: The unique identifier of the backup to rollback.
            revert_status: The status to set after rollback (default: 'completed').
            
        Returns:
            Dict[str, Any]: Rollback result or an error dictionary.
        """
        if not backup_id:
            return {"error": "backup_id is required"}
        
        if backup_id in self.deleted_backup_ids:
            return {"error": f"Cannot rollback deleted backup '{backup_id}'"}
        
        backup = self._find_backup_by_id(backup_id)
        if not backup:
            return {"error": f"Backup '{backup_id}' not found"}
        
        if backup["status"] != "restored":
            return {"error": f"Backup '{backup_id}' is not in 'restored' status, cannot rollback"}
        
        valid_statuses = ["completed", "in-progress", "failed"]
        if revert_status not in valid_statuses:
            return {"error": f"Invalid revert_status '{revert_status}'. Must be one of: {valid_statuses}"}
        
        old_status = backup["status"]
        backup["status"] = revert_status
        
        self.log_backup_operation(
            backup_id=backup_id,
            operation_type="rollback",
            status="success"
        )
        
        return {
            "success": True,
            "backup_id": backup_id,
            "old_status": old_status,
            "new_status": revert_status,
            "message": f"Restoration of backup '{backup_id}' rolled back successfully"
        }


__TEST_CASES__ = [
    {
        "name": "Full backup lifecycle: create, verify, restore, and rollback",
        "steps": [
            {"tool_call": "create_backup(source_system='test-db-01', size=1048576)", "expect_success": True},
            {"tool_call": "list_all_backups()", "expect_success": True},
            {"tool_call": "get_backup_by_id(backup_id='BKP-001')", "expect_success": True},
            {"tool_call": "verify_backup_checksum(backup_id='BKP-001')", "expect_success": True},
            {"tool_call": "check_restoration_eligibility(backup_id='BKP-001')", "expect_success": True},
            {"tool_call": "restore_backup(backup_id='BKP-001')", "expect_success": True},
            {"tool_call": "rollback_restoration(backup_id='BKP-001')", "expect_success": True}
        ]
    },
    {
        "name": "Backup deletion workflow with eligibility check",
        "steps": [
            {"tool_call": "check_deletion_eligibility(backup_id='BKP-002')", "expect_success": True},
            {"tool_call": "delete_backup(backup_id='BKP-002')", "expect_success": True},
            {"tool_call": "get_backup_by_id(backup_id='BKP-002')", "expect_success": False},
            {"tool_call": "list_backup_operations(backup_id='BKP-002')", "expect_success": True}
        ]
    },
    {
        "name": "Error handling: attempt to delete in-progress backup",
        "steps": [
            {"tool_call": "get_backup_status(backup_id='BKP-003')", "expect_success": True},
            {"tool_call": "check_deletion_eligibility(backup_id='BKP-003')", "expect_success": True},
            {"tool_call": "delete_backup(backup_id='BKP-003')", "expect_success": False},
            {"tool_call": "force_delete_backup(backup_id='BKP-003')", "expect_success": True}
        ]
    },
    {
        "name": "Storage policy management",
        "steps": [
            {"tool_call": "get_storage_policy(policy_id='POL-001')", "expect_success": True},
            {"tool_call": "update_storage_policy(policy_id='POL-001', retention_days=60)", "expect_success": True},
            {"tool_call": "apply_storage_policy(backup_id='BKP-001', policy_id='POL-001')", "expect_success": True},
            {"tool_call": "list_storage_policies()", "expect_success": True}
        ]
    },
    {
        "name": "Backup scheduling and automation",
        "steps": [
            {"tool_call": "create_backup_schedule(source_system='test-db-02', cron_expression='0 2 * * *')", "expect_success": True},
            {"tool_call": "list_backup_schedules()", "expect_success": True},
            {"tool_call": "get_schedule_by_id(schedule_id='SCH-001')", "expect_success": True},
            {"tool_call": "disable_backup_schedule(schedule_id='SCH-001')", "expect_success": True},
            {"tool_call": "enable_backup_schedule(schedule_id='SCH-001')", "expect_success": True},
            {"tool_call": "delete_backup_schedule(schedule_id='SCH-001')", "expect_success": True}
        ]
    },
    {
        "name": "Error handling: non-existent backup operations",
        "steps": [
            {"tool_call": "get_backup_by_id(backup_id='BKP-NONEXISTENT')", "expect_success": False},
            {"tool_call": "verify_backup_checksum(backup_id='BKP-NONEXISTENT')", "expect_success": False},
            {"tool_call": "restore_backup(backup_id='BKP-NONEXISTENT')", "expect_success": False},
            {"tool_call": "delete_backup(backup_id='BKP-NONEXISTENT')", "expect_success": False}
        ]
    },
    {
        "name": "Backup metrics and reporting",
        "steps": [
            {"tool_call": "get_backup_metrics(source_system='test-db-01')", "expect_success": True},
            {"tool_call": "get_storage_usage()", "expect_success": True},
            {"tool_call": "generate_backup_report(start_date='2024-01-01', end_date='2024-01-31')", "expect_success": True}
        ]
    }
]


def get_storage_policy(policy_id: str) -> dict:
    """
    Retrieve details of a storage policy by its ID.
    
    Args:
        policy_id: The unique identifier of the storage policy
        
    Returns:
        dict: Policy details or error information
    """
    if not policy_id or not isinstance(policy_id, str):
        return {"error": "Invalid policy_id: must be a non-empty string"}
    
    if policy_id not in _storage_policies:
        return {"error": f"Storage policy '{policy_id}' not found"}
    
    policy = _storage_policies[policy_id].copy()
    return {
        "success": True,
        "policy": policy
    }


def update_storage_policy(policy_id: str, retention_days: int = None, compression_enabled: bool = None,
                          encryption_enabled: bool = None, storage_tier: str = None) -> dict:
    """
    Update an existing storage policy.
    
    Args:
        policy_id: The unique identifier of the storage policy
        retention_days: Number of days to retain backups
        compression_enabled: Whether to enable compression
        encryption_enabled: Whether to enable encryption
        storage_tier: Storage tier (hot, warm, cold, archive)
        
    Returns:
        dict: Updated policy details or error information
    """
    if not policy_id or not isinstance(policy_id, str):
        return {"error": "Invalid policy_id: must be a non-empty string"}
    
    if policy_id not in _storage_policies:
        return {"error": f"Storage policy '{policy_id}' not found"}
    
    valid_tiers = ["hot", "warm", "cold", "archive"]
    if storage_tier is not None and storage_tier not in valid_tiers:
        return {"error": f"Invalid storage_tier: must be one of {valid_tiers}"}
    
    if retention_days is not None and (not isinstance(retention_days, int) or retention_days < 1):
        return {"error": "Invalid retention_days: must be a positive integer"}
    
    policy = _storage_policies[policy_id]
    old_values = policy.copy()
    
    if retention_days is not None:
        policy["retention_days"] = retention_days
    if compression_enabled is not None:
        policy["compression_enabled"] = compression_enabled
    if encryption_enabled is not None:
        policy["encryption_enabled"] = encryption_enabled
    if storage_tier is not None:
        policy["storage_tier"] = storage_tier
    
    policy["updated_at"] = _get_current_timestamp()
    
    return {
        "success": True,
        "policy_id": policy_id,
        "old_values": old_values,
        "new_values": policy.copy(),
        "message": f"Storage policy '{policy_id}' updated successfully"
    }


def apply_storage_policy(backup_id: str, policy_id: str) -> dict:
    """
    Apply a storage policy to a specific backup.
    
    Args:
        backup_id: The unique identifier of the backup
        policy_id: The unique identifier of the storage policy
        
    Returns:
        dict: Result of applying the policy or error information
    """
    if not backup_id or not isinstance(backup_id, str):
        return {"error": "Invalid backup_id: must be a non-empty string"}
    
    if not policy_id or not isinstance(policy_id, str):
        return {"error": "Invalid policy_id: must be a non-empty string"}
    
    if backup_id not in _backups:
        return {"error": f"Backup '{backup_id}' not found"}
    
    if policy_id not in _storage_policies:
        return {"error": f"Storage policy '{policy_id}' not found"}
    
    backup = _backups[backup_id]
    old_policy = backup.get("policy_id")
    backup["policy_id"] = policy_id
    backup["updated_at"] = _get_current_timestamp()
    
    _log_operation(backup_id, "apply_policy", "completed", {
        "old_policy": old_policy,
        "new_policy": policy_id
    })
    
    return {
        "success": True,
        "backup_id": backup_id,
        "policy_id": policy_id,
        "old_policy_id": old_policy,
        "message": f"Storage policy '{policy_id}' applied to backup '{backup_id}'"
    }


def list_storage_policies() -> dict:
    """
    List all available storage policies.
    
    Returns:
        dict: List of all storage policies
    """
    policies = [policy.copy() for policy in _storage_policies.values()]
    return {
        "success": True,
        "count": len(policies),
        "policies": policies
    }


def create_backup_schedule(source_system: str, cron_expression: str, backup_type: str = "incremental",
                           retention_policy_id: str = None, enabled: bool = True) -> dict:
    """
    Create a new backup schedule.
    
    Args:
        source_system: The source system to back up
        cron_expression: Cron expression for scheduling
        backup_type: Type of backup (full, incremental, differential)
        retention_policy_id: Optional policy ID to apply
        enabled: Whether the schedule is enabled
        
    Returns:
        dict: Created schedule details or error information
    """
    if not source_system or not isinstance(source_system, str):
        return {"error": "Invalid source_system: must be a non-empty string"}
    
    if not cron_expression or not isinstance(cron_expression, str):
        return {"error": "Invalid cron_expression: must be a non-empty string"}
    
    valid_types = ["full", "incremental", "differential"]
    if backup_type not in valid_types:
        return {"error": f"Invalid backup_type: must be one of {valid_types}"}
    
    if retention_policy_id and retention_policy_id not in _storage_policies:
        return {"error": f"Storage policy '{retention_policy_id}' not found"}
    
    schedule_id = f"SCH-{str(len(_backup_schedules) + 1).zfill(3)}"
    timestamp = _get_current_timestamp()
    
    schedule = {
        "schedule_id": schedule_id,
        "source_system": source_system,
        "cron_expression": cron_expression,
        "backup_type": backup_type,
        "retention_policy_id": retention_policy_id,
        "enabled": enabled,
        "created_at": timestamp,
        "updated_at": timestamp,
        "last_run": None,
        "next_run": None
    }
    
    _backup_schedules[schedule_id] = schedule
    
    return {
        "success": True,
        "schedule_id": schedule_id,
        "schedule": schedule.copy(),
        "message": f"Backup schedule '{schedule_id}' created successfully"
    }


def list_backup_schedules() -> dict:
    """
    List all backup schedules.
    
    Returns:
        dict: List of all backup schedules
    """
    schedules = [schedule.copy() for schedule in _backup_schedules.values()]
    return {
        "success": True,
        "count": len(schedules),
        "schedules": schedules
    }


def get_schedule_by_id(schedule_id: str) -> dict:
    """
    Retrieve a backup schedule by its ID.
    
    Args:
        schedule_id: The unique identifier of the schedule
        
    Returns:
        dict: Schedule details or error information
    """
    if not schedule_id or not isinstance(schedule_id, str):
        return {"error": "Invalid schedule_id: must be a non-empty string"}
    
    if schedule_id not in _backup_schedules:
        return {"error": f"Backup schedule '{schedule_id}' not found"}
    
    return {
        "success": True,
        "schedule": _backup_schedules[schedule_id].copy()
    }


def disable_backup_schedule(schedule_id: str) -> dict:
    """
    Disable a backup schedule.
    
    Args:
        schedule_id: The unique identifier of the schedule
        
    Returns:
        dict: Result of disabling the schedule or error information
    """
    if not schedule_id or not isinstance(schedule_id, str):
        return {"error": "Invalid schedule_id: must be a non-empty string"}
    
    if schedule_id not in _backup_schedules:
        return {"error": f"Backup schedule '{schedule_id}' not found"}
    
    schedule = _backup_schedules[schedule_id]
    if not schedule["enabled"]:
        return {"error": f"Backup schedule '{schedule_id}' is already disabled"}
    
    schedule["enabled"] = False
    schedule["updated_at"] = _get_current_timestamp()
    
    return {
        "success": True,
        "schedule_id": schedule_id,
        "enabled": False,
        "message": f"Backup schedule '{schedule_id}' disabled successfully"
    }


def enable_backup_schedule(schedule_id: str) -> dict:
    """
    Enable a backup schedule.
    
    Args:
        schedule_id: The unique identifier of the schedule
        
    Returns:
        dict: Result of enabling the schedule or error information
    """
    if not schedule_id or not isinstance(schedule_id, str):
        return {"error": "Invalid schedule_id: must be a non-empty string"}
    
    if schedule_id not in _backup_schedules:
        return {"error": f"Backup schedule '{schedule_id}' not found"}
    
    schedule = _backup_schedules[schedule_id]
    if schedule["enabled"]:
        return {"error": f"Backup schedule '{schedule_id}' is already enabled"}
    
    schedule["enabled"] = True
    schedule["updated_at"] = _get_current_timestamp()
    
    return {
        "success": True,
        "schedule_id": schedule_id,
        "enabled": True,
        "message": f"Backup schedule '{schedule_id}' enabled successfully"
    }


def delete_backup_schedule(schedule_id: str) -> dict:
    """
    Delete a backup schedule.
    
    Args:
        schedule_id: The unique identifier of the schedule
        
    Returns:
        dict: Result of deleting the schedule or error information
    """
    if not schedule_id or not isinstance(schedule_id, str):
        return {"error": "Invalid schedule_id: must be a non-empty string"}
    
    if schedule_id not in _backup_schedules:
        return {"error": f"Backup schedule '{schedule_id}' not found"}
    
    deleted_schedule = _backup_schedules.pop(schedule_id)
    
    return {
        "success": True,
        "schedule_id": schedule_id,
        "deleted_schedule": deleted_schedule,
        "message": f"Backup schedule '{schedule_id}' deleted successfully"
    }


def get_backup_metrics(source_system: str = None) -> dict:
    """
    Get backup metrics and statistics.
    
    Args:
        source_system: Optional filter by source system
        
    Returns:
        dict: Backup metrics and statistics
    """
    backups = list(_backups.values())
    
    if source_system:
        backups = [b for b in backups if b.get("source_system") == source_system]
    
    total_backups = len(backups)
    total_size = sum(b.get("size", 0) for b in backups)
    
    status_counts = {}
    type_counts = {}
    
    for backup in backups:
        status = backup.get("status", "unknown")
        backup_type = backup.get("backup_type", "unknown")
        
        status_counts[status] = status_counts.get(status, 0) + 1
        type_counts[backup_type] = type_counts.get(backup_type, 0) + 1
    
    successful_backups = [b for b in backups if b.get("status") == "completed"]
    success_rate = (len(successful_backups) / total_backups * 100) if total_backups > 0 else 0
    
    return {
        "success": True,
        "metrics": {
            "total_backups": total_backups,
            "total_size_bytes": total_size,
            "status_breakdown": status_counts,
            "type_breakdown": type_counts,
            "success_rate_percent": round(success_rate, 2),
            "source_system_filter": source_system
        }
    }


def get_storage_usage() -> dict:
    """
    Get overall storage usage information.
    
    Returns:
        dict: Storage usage statistics
    """
    total_size = sum(b.get("size", 0) for b in _backups.values())
    
    usage_by_system = {}
    usage_by_tier = {}
    
    for backup in _backups.values():
        source = backup.get("source_system", "unknown")
        usage_by_system[source] = usage_by_system.get(source, 0) + backup.get("size", 0)
        
        policy_id = backup.get("policy_id")
        if policy_id and policy_id in _storage_policies:
            tier = _storage_policies[policy_id].get("storage_tier", "standard")
        else:
            tier = "standard"
        usage_by_tier[tier] = usage_by_tier.get(tier, 0) + backup.get("size", 0)
    
    return {
        "success": True,
        "storage_usage": {
            "total_bytes": total_size,
            "total_gb": round(total_size / (1024 ** 3), 2),
            "by_source_system": usage_by_system,
            "by_storage_tier": usage_by_tier,
            "backup_count": len(_backups)
        }
    }


def generate_backup_report(start_date: str, end_date: str, source_system: str = None) -> dict:
    """
    Generate a backup report for a specified date range.
    
    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        source_system: Optional filter by source system
        
    Returns:
        dict: Backup report or error information
    """
    if not start_date or not isinstance(start_date, str):
        return {"error": "Invalid start_date: must be a non-empty string in YYYY-MM-DD format"}
    
    if not end_date or not isinstance(end_date, str):
        return {"error": "Invalid end_date: must be a non-empty string in YYYY-MM-DD format"}
    
    try:
        from datetime import datetime
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format: use YYYY-MM-DD"}
    
    if start_dt > end_dt:
        return {"error": "start_date must be before or equal to end_date"}
    
    backups_in_range = []
    operations_in_range = []
    
    for backup in _backups.values():
        created_at = backup.get("created_at", "")
        if created_at:
            try:
                backup_date = datetime.fromisoformat(created_at.replace("Z", "+00:00")).replace(tzinfo=None)
                if start_dt <= backup_date <= end_dt:
                    if source_system is None or backup.get("source_system") == source_system:
                        backups_in_range.append(backup.copy())
            except (ValueError, AttributeError):
                pass
    
    for ops_list in _operations.values():
        for op in ops_list:
            op_time = op.get("timestamp", "")
            if op_time:
                try:
                    op_date = datetime.fromisoformat(op_time.replace("Z", "+00:00")).replace(tzinfo=None)
                    if start_dt <= op_date <= end_dt:
                        operations_in_range.append(op.copy())
                except (ValueError, AttributeError):
                    pass
    
    total_size = sum(b.get("size", 0) for b in backups_in_range)
    successful = len([b for b in backups_in_range if b.get("status") == "completed"])
    failed = len([b for b in backups_in_range if b.get("status") == "failed"])
    
    return {
        "success": True,
        "report": {
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "source_system_filter": source_system,
            "summary": {
                "total_backups": len(backups_in_range),
                "successful_backups": successful,
                "failed_backups": failed,
                "total_size_bytes": total_size,
                "total_operations": len(operations_in_range)
            },
            "backups": backups_in_range,
            "operations": operations_in_range,
            "generated_at": _get_current_timestamp()
        }
    }


def force_delete_backup(backup_id: str, reason: str = None) -> dict:
    """
    Force delete a backup regardless of its status.
    
    Args:
        backup_id: The unique identifier of the backup
        reason: Optional reason for force deletion
        
    Returns:
        dict: Result of the force deletion or error information
    """
    if not backup_id or not isinstance(backup_id, str):
        return {"error": "Invalid backup_id: must be a non-empty string"}
    
    if backup_id not in _backups:
        return {"error": f"Backup '{backup_id}' not found"}
    
    backup = _backups[backup_id]
    old_status = backup.get("status")
    
    _log_operation(backup_id, "force_delete", "completed", {
        "reason": reason or "No reason provided",
        "previous_status": old_status
    })
    
    deleted_backup = _backups.pop(backup_id)
    
    return {
        "success": True,
        "backup_id": backup_id,
        "deleted_backup": deleted_backup,
        "force_deleted": True,
        "reason": reason,
        "message": f"Backup '{backup_id}' force deleted successfully"
    }