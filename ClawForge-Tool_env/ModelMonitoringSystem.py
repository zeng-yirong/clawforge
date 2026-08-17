"""
Machine Learning Model Monitoring System Environment API

A machine learning model monitoring system that tracks the behavior and performance
of deployed models over time by logging predictions, actual outcomes, and derived metrics.
"""

from copy import deepcopy
from typing import Dict, List, Optional, Any
from datetime import datetime

DEFAULT_STATE = {
    # Models - deployed ML models being monitored
    "models": {
        "model_001": {
            "model_id": "model_001",
            "model_name": "fraud_detection_v1",
            "version": "1.0.0",
            "deployment_date": "2024-01-15T10:00:00"
        },
        "model_002": {
            "model_id": "model_002",
            "model_name": "sentiment_classifier",
            "version": "2.1.0",
            "deployment_date": "2024-02-01T14:30:00"
        },
        "model_003": {
            "model_id": "model_003",
            "model_name": "churn_predictor",
            "version": "1.2.0",
            "deployment_date": "2024-02-20T09:00:00"
        }
    },
    
    # Predictions - individual predictions made by models
    "predictions": {
        "pred_001": {
            "prediction_id": "pred_001",
            "model_id": "model_001",
            "input_data": {"amount": 1500, "merchant": "online_store"},
            "predicted_value": 0.85,
            "timestamp": "2024-03-01T10:15:00",
            "confidence_score": 0.92,
            "is_valid": True
        },
        "pred_002": {
            "prediction_id": "pred_002",
            "model_id": "model_001",
            "input_data": {"amount": 50, "merchant": "grocery"},
            "predicted_value": 0.12,
            "timestamp": "2024-03-01T11:30:00",
            "confidence_score": 0.95,
            "is_valid": True
        },
        "pred_003": {
            "prediction_id": "pred_003",
            "model_id": "model_002",
            "input_data": {"text": "Great product, highly recommend!"},
            "predicted_value": "positive",
            "timestamp": "2024-03-01T14:00:00",
            "confidence_score": 0.88,
            "is_valid": True
        },
        "pred_004": {
            "prediction_id": "pred_004",
            "model_id": "model_002",
            "input_data": {"text": "Terrible experience, avoid."},
            "predicted_value": "negative",
            "timestamp": "2024-03-02T09:00:00",
            "confidence_score": 0.91,
            "is_valid": True
        },
        "pred_005": {
            "prediction_id": "pred_005",
            "model_id": "model_003",
            "input_data": {"user_id": "u123", "tenure_months": 24},
            "predicted_value": 0.35,
            "timestamp": "2024-03-02T15:45:00",
            "confidence_score": 0.78,
            "is_valid": True
        }
    },
    
    # Ground truths - actual observed outcomes for predictions
    "ground_truths": {
        "pred_001": {
            "prediction_id": "pred_001",
            "actual_value": 1,
            "timestamp": "2024-03-05T10:00:00",
            "verification_status": "verified"
        },
        "pred_002": {
            "prediction_id": "pred_002",
            "actual_value": 0,
            "timestamp": "2024-03-05T10:00:00",
            "verification_status": "verified"
        },
        "pred_003": {
            "prediction_id": "pred_003",
            "actual_value": "positive",
            "timestamp": "2024-03-06T12:00:00",
            "verification_status": "pending"
        }
    },
    
    # Performance metrics - precomputed metrics over time windows
    "performance_metrics": {
        "metric_001": {
            "metric_id": "metric_001",
            "model_id": "model_001",
            "metric_type": "accuracy",
            "metric_value": 0.87,
            "timestamp_range": {"start": "2024-03-01T00:00:00", "end": "2024-03-01T23:59:59"},
            "computed_at": "2024-03-06T08:00:00"
        },
        "metric_002": {
            "metric_id": "metric_002",
            "model_id": "model_001",
            "metric_type": "precision",
            "metric_value": 0.82,
            "timestamp_range": {"start": "2024-03-01T00:00:00", "end": "2024-03-01T23:59:59"},
            "computed_at": "2024-03-06T08:00:00"
        },
        "metric_003": {
            "metric_id": "metric_003",
            "model_id": "model_002",
            "metric_type": "accuracy",
            "metric_value": 0.91,
            "timestamp_range": {"start": "2024-03-01T00:00:00", "end": "2024-03-02T23:59:59"},
            "computed_at": "2024-03-07T09:00:00"
        }
    },
    
    # Counter for generating unique IDs
    "id_counters": {
        "prediction": 6,
        "metric": 4
    },
    
    # Current user context
    "current_user": "admin_user"
}


class ModelMonitoringSystem:
    """
    A machine learning model monitoring system API that tracks the behavior and
    performance of deployed models over time by logging predictions, actual outcomes,
    and derived metrics. It maintains time-stamped records to enable retrospective
    analysis, detect drift, and ensure model reliability.
    """
    
    def __init__(self):
        """
        Initialize the ModelMonitoringSystem with all state attributes.
        """
        self.models: Dict[str, Dict[str, Any]] = {}
        self.predictions: Dict[str, Dict[str, Any]] = {}
        self.ground_truths: Dict[str, Dict[str, Any]] = {}
        self.performance_metrics: Dict[str, Dict[str, Any]] = {}
        self.id_counters: Dict[str, int] = {}
        self.current_user: str = ""
        
        self._api_description = "ML model monitoring system for tracking predictions, ground truths, and performance metrics of deployed models."
    
    def _timestamp(self) -> str:
        """
        Generate a consistent ISO format timestamp string.
        
        Returns:
            str: Current timestamp in ISO format.
        """
        return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    
    def _load_scenario(self, scenario: dict, long_context: bool = False) -> None:
        """
        Load initial state from a scenario dictionary.
        
        Args:
            scenario: Dictionary containing the initial state configuration.
            long_context: Flag for long context scenarios (unused in this implementation).
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
        Return a dictionary containing the current environment state.
        
        Returns:
            dict: A dictionary with all internal state variables including:
                - models: All deployed models being monitored
                - predictions: All logged predictions
                - ground_truths: All recorded ground truth entries
                - performance_metrics: All computed performance metrics
                - id_counters: Current ID counters for generating unique IDs
                - current_user: The current user context
        """
        return {
            "models": deepcopy(self.models),
            "predictions": deepcopy(self.predictions),
            "ground_truths": deepcopy(self.ground_truths),
            "performance_metrics": deepcopy(self.performance_metrics),
            "id_counters": deepcopy(self.id_counters),
            "current_user": self.current_user
        }
    
    def _extract_date(self, timestamp: str) -> str:
        """
        Extract date portion from an ISO timestamp.
        
        Args:
            timestamp: ISO format timestamp string.
            
        Returns:
            str: Date in YYYY-MM-DD format.
        """
        return timestamp.split("T")[0]
    
    def _is_in_date_range(self, timestamp: str, start_date: str, end_date: str) -> bool:
        """
        Check if a timestamp falls within a date range (inclusive).
        
        Args:
            timestamp: ISO format timestamp to check.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            
        Returns:
            bool: True if timestamp is within range.
        """
        ts_date = self._extract_date(timestamp)
        return start_date <= ts_date <= end_date
    
    # ==================== QUERY OPERATIONS ====================
    
    def get_predictions_by_date(self, date: str) -> Dict[str, Any]:
        """
        Retrieve all predictions made on a specific calendar date.
        
        Args:
            date: The calendar date in YYYY-MM-DD format (e.g., "2024-03-01").
            
        Returns:
            dict: A dictionary containing:
                - predictions: List of prediction records for the specified date
                - count: Number of predictions found
                - date: The queried date
                Or an error dictionary if the date format is invalid.
        """
        if not date or len(date) != 10 or date[4] != '-' or date[7] != '-':
            return {"error": "Invalid date format. Expected YYYY-MM-DD."}
        
        matching_predictions = []
        for pred_id, pred in self.predictions.items():
            if self._extract_date(pred["timestamp"]) == date:
                matching_predictions.append(deepcopy(pred))
        
        return {
            "predictions": matching_predictions,
            "count": len(matching_predictions),
            "date": date
        }
    
    def get_predictions_by_model_and_date(
        self, 
        model_id: str, 
        start_date: str, 
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve predictions for a specific model within a given date range.
        
        Args:
            model_id: The unique identifier of the model.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format. If None, uses start_date as single day.
            
        Returns:
            dict: A dictionary containing:
                - predictions: List of prediction records
                - count: Number of predictions found
                - model_id: The queried model ID
                - date_range: The queried date range
                Or an error dictionary if model not found.
        """
        if model_id not in self.models:
            return {"error": f"Model '{model_id}' not found."}
        
        if end_date is None:
            end_date = start_date
        
        matching_predictions = []
        for pred_id, pred in self.predictions.items():
            if pred["model_id"] == model_id and pred["is_valid"]:
                if self._is_in_date_range(pred["timestamp"], start_date, end_date):
                    matching_predictions.append(deepcopy(pred))
        
        return {
            "predictions": matching_predictions,
            "count": len(matching_predictions),
            "model_id": model_id,
            "date_range": {"start": start_date, "end": end_date}
        }
    
    def check_ground_truth_coverage(
        self, 
        model_id: str, 
        start_date: str, 
        end_date: str
    ) -> Dict[str, Any]:
        """
        Check the percentage of predictions with corresponding ground truth entries.
        
        Args:
            model_id: The unique identifier of the model.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            
        Returns:
            dict: A dictionary containing:
                - total_predictions: Total number of predictions in range
                - with_ground_truth: Number of predictions with ground truth
                - coverage_percentage: Percentage of predictions with ground truth
                - model_id: The queried model ID
                Or an error dictionary if model not found.
        """
        if model_id not in self.models:
            return {"error": f"Model '{model_id}' not found."}
        
        total_preds = 0
        with_gt = 0
        
        for pred_id, pred in self.predictions.items():
            if pred["model_id"] == model_id and pred["is_valid"]:
                if self._is_in_date_range(pred["timestamp"], start_date, end_date):
                    total_preds += 1
                    if pred_id in self.ground_truths:
                        with_gt += 1
        
        coverage = (with_gt / total_preds * 100) if total_preds > 0 else 0.0
        
        return {
            "total_predictions": total_preds,
            "with_ground_truth": with_gt,
            "coverage_percentage": round(coverage, 2),
            "model_id": model_id,
            "date_range": {"start": start_date, "end": end_date}
        }
    
    def get_ground_truth_by_prediction_id(self, prediction_id: str) -> Dict[str, Any]:
        """
        Retrieve the actual observed value and verification status for a prediction.
        
        Args:
            prediction_id: The unique identifier of the prediction.
            
        Returns:
            dict: A dictionary containing the ground truth entry with:
                - prediction_id: The prediction ID
                - actual_value: The actual observed outcome
                - timestamp: When the ground truth was recorded
                - verification_status: Current verification status
                Or an error dictionary if not found.
        """
        if prediction_id not in self.predictions:
            return {"error": f"Prediction '{prediction_id}' not found."}
        
        if prediction_id not in self.ground_truths:
            return {"error": f"No ground truth recorded for prediction '{prediction_id}'."}
        
        return {"ground_truth": deepcopy(self.ground_truths[prediction_id])}
    
    def list_all_models(self) -> Dict[str, Any]:
        """
        Retrieve a list of all deployed models with their basic information.
        
        Returns:
            dict: A dictionary containing:
                - models: List of model records with IDs, names, and versions
                - count: Total number of models
        """
        models_list = []
        for model_id, model in self.models.items():
            models_list.append({
                "model_id": model["model_id"],
                "model_name": model["model_name"],
                "version": model["version"],
                "deployment_date": model["deployment_date"]
            })
        
        return {
            "models": models_list,
            "count": len(models_list)
        }
    
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Retrieve detailed information about a specific model.
        
        Args:
            model_id: The unique identifier of the model.
            
        Returns:
            dict: A dictionary containing the complete model information
                Or an error dictionary if model not found.
        """
        if model_id not in self.models:
            return {"error": f"Model '{model_id}' not found."}
        
        return {"model": deepcopy(self.models[model_id])}
    
    def get_performance_metrics_by_date(
        self, 
        start_date: str, 
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve precomputed performance metrics for a specific date or time window.
        
        Args:
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format. If None, uses start_date.
            
        Returns:
            dict: A dictionary containing:
                - metrics: List of matching performance metric records
                - count: Number of metrics found
                - date_range: The queried date range
        """
        if end_date is None:
            end_date = start_date
        
        matching_metrics = []
        for metric_id, metric in self.performance_metrics.items():
            metric_start = self._extract_date(metric["timestamp_range"]["start"])
            metric_end = self._extract_date(metric["timestamp_range"]["end"])
            
            # Check if metric's time range overlaps with query range
            if not (metric_end < start_date or metric_start > end_date):
                matching_metrics.append(deepcopy(metric))
        
        return {
            "metrics": matching_metrics,
            "count": len(matching_metrics),
            "date_range": {"start": start_date, "end": end_date}
        }
    
    def get_performance_metrics_by_model(self, model_id: str) -> Dict[str, Any]:
        """
        Retrieve all performance metrics associated with a specific model.
        
        Args:
            model_id: The unique identifier of the model.
            
        Returns:
            dict: A dictionary containing:
                - metrics: List of performance metric records for the model
                - count: Number of metrics found
                - model_id: The queried model ID
                Or an error dictionary if model not found.
        """
        if model_id not in self.models:
            return {"error": f"Model '{model_id}' not found."}
        
        model_metrics = []
        for metric_id, metric in self.performance_metrics.items():
            if metric["model_id"] == model_id:
                model_metrics.append(deepcopy(metric))
        
        return {
            "metrics": model_metrics,
            "count": len(model_metrics),
            "model_id": model_id
        }
    
    def get_metric_computation_status(
        self, 
        model_id: str, 
        start_date: str, 
        end_date: str
    ) -> Dict[str, Any]:
        """
        Check whether performance metrics for a given time range are available.
        
        Args:
            model_id: The unique identifier of the model.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            
        Returns:
            dict: A dictionary containing:
                - metrics_available: Boolean indicating if metrics exist
                - existing_metrics: List of matching metrics if available
                - needs_computation: Boolean indicating if computation is needed
                - ground_truth_coverage: Coverage percentage for the range
                Or an error dictionary if model not found.
        """
        if model_id not in self.models:
            return {"error": f"Model '{model_id}' not found."}
        
        # Find existing metrics for this model and time range
        existing_metrics = []
        for metric_id, metric in self.performance_metrics.items():
            if metric["model_id"] != model_id:
                continue
            metric_start = self._extract_date(metric["timestamp_range"]["start"])
            metric_end = self._extract_date(metric["timestamp_range"]["end"])
            if metric_start == start_date and metric_end == end_date:
                existing_metrics.append(deepcopy(metric))
        
        # Check ground truth coverage
        coverage_result = self.check_ground_truth_coverage(model_id, start_date, end_date)
        coverage_pct = coverage_result.get("coverage_percentage", 0)
        
        return {
            "metrics_available": len(existing_metrics) > 0,
            "existing_metrics": existing_metrics,
            "needs_computation": len(existing_metrics) == 0,
            "ground_truth_coverage": coverage_pct,
            "can_compute": coverage_pct > 0,
            "model_id": model_id,
            "date_range": {"start": start_date, "end": end_date}
        }
    
    def get_predictions_with_missing_ground_truth(
        self, 
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        List predictions that lack verified ground truth entries.
        
        Args:
            model_id: Optional model ID to filter by. If None, returns all.
            
        Returns:
            dict: A dictionary containing:
                - predictions: List of predictions without ground truth
                - count: Number of predictions found
                Or an error dictionary if model_id provided but not found.
        """
        if model_id is not None and model_id not in self.models:
            return {"error": f"Model '{model_id}' not found."}
        
        missing_gt = []
        for pred_id, pred in self.predictions.items():
            if not pred["is_valid"]:
                continue
            if model_id is not None and pred["model_id"] != model_id:
                continue
            
            if pred_id not in self.ground_truths:
                missing_gt.append(deepcopy(pred))
            elif self.ground_truths[pred_id]["verification_status"] != "verified":
                missing_gt.append(deepcopy(pred))
        
        return {
            "predictions": missing_gt,
            "count": len(missing_gt),
            "filter_model_id": model_id
        }
    
    def get_model_health_status(self, model_id: str) -> Dict[str, Any]:
        """
        Get comprehensive health status for a model.
        
        Args:
            model_id: The unique identifier of the model.
            
        Returns:
            dict: A dictionary containing:
                - model_id: The model ID
                - status: Health status ('healthy', 'warning', 'critical')
                - issues: List of detected issues
                - prediction_count: Number of predictions for the model
                - ground_truth_count: Number of ground truth entries
                - latest_metrics: Most recent performance metrics
                Or an error dictionary if model not found.
        """
        if model_id not in self.models:
            return {"error": f"Model '{model_id}' not found."}
        
        model_info = self.models[model_id]
        
        # Count predictions for this model
        prediction_count = sum(
            1 for pred in self.predictions.values() 
            if pred["model_id"] == model_id and pred["is_valid"]
        )
        
        # Count ground truths for this model's predictions
        ground_truth_count = sum(
            1 for pred_id, pred in self.predictions.items()
            if pred["model_id"] == model_id and pred_id in self.ground_truths
        )
        
        # Get latest metrics for this model
        model_metrics = [
            metric for metric in self.performance_metrics.values()
            if metric["model_id"] == model_id
        ]
        latest_metrics = {}
        if model_metrics:
            # Sort by computed_at and get the most recent for each metric type
            for metric in sorted(model_metrics, key=lambda x: x["computed_at"], reverse=True):
                if metric["metric_type"] not in latest_metrics:
                    latest_metrics[metric["metric_type"]] = metric["metric_value"]
        
        # Determine health status and issues
        issues = []
        status = "healthy"
        
        if prediction_count == 0:
            issues.append("No predictions recorded for this model")
            status = "warning"
        
        if prediction_count > 0 and ground_truth_count == 0:
            issues.append("No ground truth entries available")
            status = "warning"
        
        coverage = (ground_truth_count / prediction_count * 100) if prediction_count > 0 else 0
        if 0 < coverage < 50:
            issues.append(f"Low ground truth coverage: {coverage:.1f}%")
            status = "warning"
        
        if not model_metrics:
            issues.append("No performance metrics computed")
            if status == "healthy":
                status = "warning"
        
        # Check for low accuracy
        if "accuracy" in latest_metrics and latest_metrics["accuracy"] < 0.7:
            issues.append(f"Low accuracy: {latest_metrics['accuracy']:.2f}")
            status = "critical"
        
        return {
            "model_id": model_id,
            "model_name": model_info["model_name"],
            "version": model_info["version"],
            "status": status,
            "issues": issues,
            "prediction_count": prediction_count,
            "ground_truth_count": ground_truth_count,
            "ground_truth_coverage": round(coverage, 2),
            "latest_metrics": latest_metrics
        }
    
    def export_monitoring_report(
        self, 
        model_id: str, 
        format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export a comprehensive monitoring report for a model.
        
        Args:
            model_id: The unique identifier of the model.
            format: Export format ('json' or 'summary').
            
        Returns:
            dict: A dictionary containing:
                - success: Boolean indicating success
                - report: The complete monitoring report (for json format)
                - summary: Text summary (for summary format)
                Or an error dictionary if model not found or invalid format.
        """
        if model_id not in self.models:
            return {"error": f"Model '{model_id}' not found."}
        
        if format not in ["json", "summary"]:
            return {"error": f"Invalid format '{format}'. Must be 'json' or 'summary'."}
        
        model_info = self.models[model_id]
        health_status = self.get_model_health_status(model_id)
        metrics_result = self.get_performance_metrics_by_model(model_id)
        
        # Get predictions for this model
        model_predictions = [
            pred for pred in self.predictions.values()
            if pred["model_id"] == model_id
        ]
        
        report = {
            "model_id": model_id,
            "model_name": model_info["model_name"],
            "version": model_info["version"],
            "deployment_date": model_info["deployment_date"],
            "generated_at": self._timestamp(),
            "health_status": health_status,
            "statistics": {
                "total_predictions": len(model_predictions),
                "total_ground_truth_entries": health_status.get("ground_truth_count", 0),
                "ground_truth_coverage": health_status.get("ground_truth_coverage", 0),
                "metrics_count": metrics_result.get("count", 0)
            },
            "metrics_history": metrics_result.get("metrics", [])
        }
        
        if format == "summary":
            summary_text = (
                f"Model: {report['model_name']} v{report['version']}\n"
                f"Status: {health_status['status']}\n"
                f"Total Predictions: {report['statistics']['total_predictions']}\n"
                f"Ground Truth Coverage: {report['statistics']['ground_truth_coverage']}%\n"
                f"Issues: {len(health_status['issues'])}"
            )
            if health_status['issues']:
                summary_text += "\n- " + "\n- ".join(health_status['issues'])
            
            return {
                "success": True,
                "summary": summary_text
            }
        
        return {
            "success": True,
            "report": report
        }
    
    # ==================== STATE CHANGE OPERATIONS ====================
    
    def log_prediction(
        self,
        model_id: str,
        prediction_id: str,
        input_data: Dict[str, Any],
        predicted_value: Any,
        confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Log a new prediction made by a model.
        
        Args:
            model_id: The unique identifier of the model.
            prediction_id: Unique identifier for this prediction.
            input_data: The input data used for prediction.
            predicted_value: The predicted output value.
            confidence: Optional confidence score (0-1).
            
        Returns:
            dict: A dictionary containing:
                - success: Boolean indicating success
                - prediction_id: The prediction ID
                - prediction: The created prediction record
                Or an error dictionary if validation fails.
        """
        if model_id not in self.models:
            return {"error": f"Model '{model_id}' not found."}
        
        if prediction_id in self.predictions:
            return {"error": f"Prediction '{prediction_id}' already exists."}
        
        if confidence is not None and (confidence < 0 or confidence > 1):
            return {"error": "Confidence score must be between 0 and 1."}
        
        prediction_record = {
            "prediction_id": prediction_id,
            "model_id": model_id,
            "input_data": deepcopy(input_data),
            "predicted_value": predicted_value,
            "timestamp": self._timestamp(),
            "confidence_score": confidence,
            "is_valid": True
        }
        
        self.predictions[prediction_id] = prediction_record
        
        return {
            "success": True,
            "prediction_id": prediction_id,
            "prediction": deepcopy(prediction_record)
        }
    
    def record_ground_truth(
        self, 
        prediction_id: str, 
        actual_value: Any,
        verification_status: str = "pending",
        action: str = "overwrite",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add or update a ground truth entry for a given prediction.
        
        Args:
            prediction_id: The unique identifier of the prediction.
            actual_value: The actual observed outcome.
            verification_status: Status of verification (default: "pending").
            action: Action to take if entry exists ('overwrite' or 'skip').
            metadata: Optional metadata for the ground truth.
            
        Returns:
            dict: Result dictionary with success, ground_truth, and action, or error.
        """
        if prediction_id not in self.predictions:
            return {"error": f"Prediction '{prediction_id}' not found."}
        
        if verification_status not in ["pending", "verified", "disputed", "rejected"]:
            return {"error": f"Invalid verification status '{verification_status}'. Must be 'pending', 'verified', 'disputed', or 'rejected'."}
            
        if action not in ["overwrite", "skip"]:
            return {"error": f"Invalid action '{action}'. Must be 'overwrite' or 'skip'."}
            
        if prediction_id in self.ground_truths:
            if action == "skip":
                return {
                    "success": False,
                    "action": "skipped",
                    "error": f"Ground truth for prediction '{prediction_id}' already exists."
                }
            result_action = "overwritten"
        else:
            result_action = "created"
            
        gt_entry = {
            "prediction_id": prediction_id,
            "actual_value": actual_value,
            "timestamp": self._timestamp(),
            "verification_status": verification_status
        }
        if metadata is not None:
            gt_entry["metadata"] = deepcopy(metadata)
            
        self.ground_truths[prediction_id] = gt_entry
        
        return {
            "success": True,
            "ground_truth": deepcopy(gt_entry),
            "action": result_action
        }
    
    def update_ground_truth_verification_status(
        self, 
        prediction_id: str, 
        new_status: str
    ) -> Dict[str, Any]:
        """
        Change the verification status of a ground truth entry.
        
        Args:
            prediction_id: The prediction ID whose ground truth to update.
            new_status: New verification status (e.g., 'pending', 'verified', 'disputed').
            
        Returns:
            dict: A dictionary containing:
                - success: Boolean indicating success
                - ground_truth: Updated ground truth data (if successful)
                - previous_status: The status before update
                Or an error dictionary if unsuccessful.
        """
        if prediction_id not in self.ground_truths:
            return {"error": f"No ground truth found for prediction ID: {prediction_id}"}
        
        valid_statuses = ['pending', 'verified', 'disputed', 'rejected']
        if new_status not in valid_statuses:
            return {"error": f"Invalid status: {new_status}. Must be one of {valid_statuses}"}
        
        previous_status = self.ground_truths[prediction_id].get("verification_status", "pending")
        self.ground_truths[prediction_id]["verification_status"] = new_status
        self.ground_truths[prediction_id]["updated_at"] = self._timestamp()
        
        return {
            "success": True,
            "ground_truth": deepcopy(self.ground_truths[prediction_id]),
            "previous_status": previous_status
        }
    
    def get_ground_truth(self, prediction_id: str) -> Dict[str, Any]:
        """
        Retrieve ground truth for a specific prediction.
        
        Args:
            prediction_id: The prediction ID to look up.
            
        Returns:
            dict: A dictionary containing:
                - success: Boolean indicating if ground truth was found
                - ground_truth: The ground truth data (if found)
                Or an error dictionary if not found.
        """
        if prediction_id not in self.ground_truths:
            return {"error": f"No ground truth found for prediction ID: {prediction_id}"}
        
        return {
            "success": True,
            "ground_truth": deepcopy(self.ground_truths[prediction_id])
        }
    
    def list_ground_truths(
        self, 
        status_filter: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        List all ground truths, optionally filtered by status.
        
        Args:
            status_filter: Optional status to filter by.
            limit: Maximum number of results to return.
            
        Returns:
            dict: A dictionary containing:
                - success: Boolean indicating success
                - ground_truths: List of ground truth entries
                - total_count: Total number of entries (before limit)
        """
        results = []
        for pred_id, gt_data in self.ground_truths.items():
            if status_filter is None or gt_data.get("verification_status") == status_filter:
                entry = deepcopy(gt_data)
                entry["prediction_id"] = pred_id
                results.append(entry)
        
        total_count = len(results)
        results = results[:limit]
        
        return {
            "success": True,
            "ground_truths": results,
            "total_count": total_count
        }
    
    def delete_ground_truth(self, prediction_id: str) -> Dict[str, Any]:
        """
        Delete a ground truth entry.
        
        Args:
            prediction_id: The prediction ID whose ground truth to delete.
            
        Returns:
            dict: A dictionary containing:
                - success: Boolean indicating success
                - deleted_ground_truth: The deleted data (if successful)
                Or an error dictionary if not found.
        """
        if prediction_id not in self.ground_truths:
            return {"error": f"No ground truth found for prediction ID: {prediction_id}"}
        
        deleted_data = self.ground_truths.pop(prediction_id)
        
        return {
            "success": True,
            "deleted_ground_truth": deleted_data
        }


__TEST_CASES__ = [
    {
        "name": "test_record_ground_truth_success",
        "method": "record_ground_truth",
        "input": {
            "prediction_id": "pred_004",
            "actual_value": "negative",
            "metadata": {"source": "manual_entry"}
        },
        "expected": {
            "success": True,
            "action": "created"
        }
    },
    {
        "name": "test_record_ground_truth_skip",
        "method": "record_ground_truth",
        "input": {
            "prediction_id": "pred_001",
            "actual_value": 0,
            "action": "skip"
        },
        "expected": {
            "success": False,
            "action": "skipped",
            "error": "Ground truth for prediction 'pred_001' already exists."
        }
    },
    {
        "name": "test_record_ground_truth_overwrite",
        "method": "record_ground_truth",
        "input": {
            "prediction_id": "pred_001",
            "actual_value": 0,
            "action": "overwrite"
        },
        "expected": {
            "success": True,
            "action": "overwritten"
        }
    },
    {
        "name": "test_update_ground_truth_verification_status",
        "method": "update_ground_truth_verification_status",
        "input": {
            "prediction_id": "pred_001",
            "new_status": "disputed"
        },
        "expected": {
            "success": True,
            "previous_status": "verified"
        }
    },
    {
        "name": "test_update_ground_truth_verification_status_invalid",
        "method": "update_ground_truth_verification_status",
        "input": {
            "prediction_id": "pred_001",
            "new_status": "invalid_status"
        },
        "expected": {
            "error": "Invalid status: invalid_status. Must be one of ['pending', 'verified', 'disputed', 'rejected']"
        }
    }
]