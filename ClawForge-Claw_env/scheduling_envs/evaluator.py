"""Evaluator for scheduling environment."""
from typing import Any


class ScheduleEvaluator:
    def __init__(self, scenario: dict[str, Any]):
        self.scenario = scenario
        self.schedule_weight = scenario.get("schedule_weight", 0.4)
        self.device_control_weight = scenario.get("device_control_weight", 0.3)
        self.task_execution_weight = scenario.get("task_execution_weight", 0.3)
    
    def evaluate(self, session: dict[str, Any]) -> dict[str, Any]:
        schedule_score = self._evaluate_schedules(session)
        device_score = self._evaluate_device_control(session)
        task_score = self._evaluate_task_execution(session)
        
        total_score = (
            schedule_score * self.schedule_weight +
            device_score * self.device_control_weight +
            task_score * self.task_execution_weight
        )
        
        return {
            "total_score": round(total_score, 2),
            "breakdown": {
                "schedule_score": round(schedule_score, 2),
                "device_control_score": round(device_score, 2),
                "task_execution_score": round(task_score, 2),
            },
            "weights": {
                "schedule": self.schedule_weight,
                "device_control": self.device_control_weight,
                "task_execution": self.task_execution_weight,
            },
            "metrics": session.get("metrics", {}),
        }
    
    def _evaluate_schedules(self, session: dict[str, Any]) -> float:
        schedules = session.get("schedules", [])
        if not schedules:
            return 0.0
        
        score = 0.0
        
        enabled_count = sum(1 for s in schedules if s.get("enabled", False))
        score += (enabled_count / len(schedules)) * 0.4
        
        with_runs = sum(1 for s in schedules if s.get("run_count", 0) > 0)
        score += (with_runs / len(schedules)) * 0.3
        
        has_recurring = sum(1 for s in schedules if s.get("repeat_type") != "once")
        score += (has_recurring / len(schedules)) * 0.3
        
        return min(score, 1.0)
    
    def _evaluate_device_control(self, session: dict[str, Any]) -> float:
        actions = session.get("actions", [])
        if not actions:
            return 0.0
        
        device_actions = [a for a in actions if a.get("action", "").startswith(("turn_", "control_", "set_"))]
        if not device_actions:
            return 0.0
        
        score = 0.0
        
        diverse_actions = len(set(a.get("device_id") for a in device_actions if a.get("device_id")))
        total_devices = len(session.get("devices", {}))
        if total_devices > 0:
            score += (diverse_actions / total_devices) * 0.5
        
        has_setting_changes = sum(1 for a in device_actions if "setting" in a or "brightness" in a or "temperature" in a)
        if len(device_actions) > 0:
            score += (has_setting_changes / len(device_actions)) * 0.5
        
        return min(score, 1.0)
    
    def _evaluate_task_execution(self, session: dict[str, Any]) -> float:
        schedules = session.get("schedules", [])
        if not schedules:
            return 0.0
        
        total_runs = sum(s.get("run_count", 0) for s in schedules)
        max_possible_runs = len(schedules) * 10
        
        if max_possible_runs == 0:
            return 0.0
        
        execution_ratio = min(total_runs / max_possible_runs, 1.0)
        
        successful_executions = sum(
            1 for s in schedules 
            if s.get("run_count", 0) > 0 and s.get("last_run") is not None
        )
        
        if schedules:
            success_ratio = successful_executions / len(schedules)
        else:
            success_ratio = 0.0
        
        score = execution_ratio * 0.5 + success_ratio * 0.5
        return min(score, 1.0)
