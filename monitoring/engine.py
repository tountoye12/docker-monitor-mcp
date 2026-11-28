import logging

from config.thresholds import validate_thresholds
from services import docker_service

from monitoring.evaluator import (
    evaluate_cpu,
    evaluate_memory,
    evaluate_restarts,
    evaluate_errors,
    evaluate_status,
    evaluate_health,
)

from collections import Counter
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class MonitoringEngine:
    """
    Coordinate proactive Docker infrastructure monitoring.
    """

    def __init__(self):
        validate_thresholds()

        self.previous_restart_counts = {}
        self.previous_errors = {}


        logger.info("Monitoring engine initialized.")

    def discover_containers(self) -> list[dict]:
            """
            Discover Docker containers for monitoring.
            """
            containers = docker_service.list_containers(
                include_stopped=True
            )
    
            logger.info(
                "Discovered %s containers.",
                len(containers)
            )
    
            return containers

    def collect_health(self, container_name: str) -> dict:
            """
            Collect health information for a Docker container.
            """
            health_data = docker_service.check_container_health(
                container_name
            )
    
            return health_data


    def collect_stats(self, container_name: str) -> dict:
        """
        Collect resource utilization statistics for a Docker container.
        """
        stats_data = docker_service.get_container_stats(
            container_name
        )

        return stats_data

    def collect_errors(
        self, container_name: str, lines: int = 100
    ) -> dict:
        """
        Collect recent container errors and warnings.
        """
        error_data = docker_service.detect_errors(
            container_name, lines
        )

        return error_data

    def track_restarts(
        self, container_id: str, restart_count: int
    ) -> int:
        """
        Calculate new container restarts since the previous check.
        """
        previous_count = self.previous_restart_counts.get(
            container_id, restart_count
        )

        restart_increase = max(
            0, restart_count - previous_count
        )

        self.previous_restart_counts[container_id] = restart_count

        return restart_increase


    def track_errors(
        self, container_id: str, errors: list[str]
    ) -> int:
        """
        Estimate new log errors since the previous check.
        """
        current_errors = Counter(errors)

        previous_errors = self.previous_errors.get(
            container_id, current_errors
        )

        new_errors = current_errors - previous_errors

        self.previous_errors[container_id] = current_errors

        return sum(new_errors.values())


    def evaluate_container_health(
        self, container_id: str, health_data: dict
    ) -> dict:
        """
        Evaluate container status, health and restart activity.
        """

        if "error" in health_data:
            return {
                "error": "Unable to collect container health."
            }

        status = health_data.get("status", "unknown")
        health = health_data.get("health") or "unknown"
        restart_count = health_data.get("restart_count")

        restart_increase = None
        restart_severity = "unknown"

        if isinstance(restart_count, int):
            restart_increase = self.track_restarts(
                container_id, restart_count
            )

            restart_severity = evaluate_restarts(
                restart_increase
            )

        return {
            "status": status,
            "status_severity": evaluate_status(status),
            "health": health,
            "health_severity": evaluate_health(health),
            "restart_count": restart_count,
            "restart_increase": restart_increase,
            "restart_severity": restart_severity,
        }


    def evaluate_container_stats(self, stats_data: dict) -> dict:
        """
        Evaluate container CPU and memory utilization.
        """

        if "error" in stats_data:
            return {
                "error": "Unable to collect container statistics."
            }

        cpu_percent = stats_data.get("cpu_percent")
        memory_percent = stats_data.get("memory_percent")

        cpu_severity = "unknown"
        memory_severity = "unknown"

        if isinstance(cpu_percent, (int, float)):
            cpu_severity = evaluate_cpu(cpu_percent)

        if isinstance(memory_percent, (int, float)):
            memory_severity = evaluate_memory(memory_percent)

        return {
            "cpu_percent": cpu_percent,
            "cpu_severity": cpu_severity,
            "memory_percent": memory_percent,
            "memory_severity": memory_severity,
        }


    def evaluate_container_errors(
        self, container_id: str, error_data: dict
    ) -> dict:
        """
        Evaluate newly detected container log errors.
        """

        if "error" in error_data:
            return {
                "error": "Unable to analyze container logs."
            }

        errors = error_data.get("errors")

        if not isinstance(errors, list):
            return {
                "error_severity": "unknown"
            }

        new_error_count = self.track_errors(
            container_id, errors
        )

        error_severity = evaluate_errors(new_error_count)

        return {
            "total_errors": len(errors),
            "new_errors": new_error_count,
            "error_severity": error_severity,
        }


    def monitor_container(self, container: dict) -> dict:
        """
        Collect and evaluate monitoring data for a container.
        """
        container_id = container["id"]
        container_name = container["name"]

        # Collect and evaluate health
        health_data = self.collect_health(container_name)

        health_result = self.evaluate_container_health(
            container_id, health_data
        )

        # Initialize monitoring results
        stats_result = {"status": "skipped"}
        error_result = {"status": "skipped"}

        # Collect live statistics only for running containers
        if health_result.get("status") == "running":
            stats_data = self.collect_stats(container_name)

            stats_result = self.evaluate_container_stats(
                stats_data
            )

            error_data = self.collect_errors(container_name)

            error_result = self.evaluate_container_errors(
                container_id, error_data
            )

        container_result = {

        "id": container_id,
        "name": container_name,
        "health": health_result,
        "resources": stats_result,
        "logs": error_result,

        }

        container_result["overall_severity"] = (

        self.calculate_overall_severity(container_result)

        )

        return container_result


    def calculate_overall_severity(
        self, container_result: dict
    ) -> str:
        """
        Determine the overall severity of a monitored container.
        """

        severities = []

        for section in ["health", "resources", "logs"]:
            section_data = container_result.get(section, {})

            if "error" in section_data:
                severities.append("unknown")
                continue

            for key, value in section_data.items():
                if key.endswith("_severity"):
                    if value != "not_applicable":
                        severities.append(value)

        if "critical" in severities:
            return "critical"

        if "warning" in severities:
            return "warning"

        if "unknown" in severities or not severities:
            return "unknown"

        return "normal"


    def monitor_all_containers(self) -> list[dict]:
        """
        Monitor all discovered Docker containers.
        """
        containers = self.discover_containers()

        results = []

        for container in containers:
            try:
                result = self.monitor_container(container)
                results.append(result)

            except Exception:
                logger.exception(
                    "Monitoring failed for container '%s'",
                    container.get("name", "unknown")
                )

                results.append({
                    "id": container.get("id"),
                    "name": container.get("name"),
                    "overall_severity": "unknown",
                    "error": "Container monitoring failed."
                })

        return results



    def generate_summary(self, results: list[dict]) -> dict:
        """
        Generate a summary of infrastructure monitoring results.
        """
        summary = {
            "total_containers": len(results),
            "normal": 0,
            "warning": 0,
            "critical": 0,
            "unknown": 0,
        }

        for result in results:
            severity = result.get("overall_severity", "unknown")

            if severity in {"normal", "warning", "critical", "unknown"}:
                summary[severity] += 1
            else:
                summary["unknown"] += 1

        return summary


    def run_monitoring_cycle(self) -> dict:
        """
        Execute a complete infrastructure monitoring cycle.
        """
        started_at = datetime.now(timezone.utc)

        logger.info("Starting infrastructure monitoring cycle.")

        results = self.monitor_all_containers()
        summary = self.generate_summary(results)

        completed_at = datetime.now(timezone.utc)

        duration = (completed_at - started_at).total_seconds()

        logger.info(
            "Monitoring cycle completed in %.2f seconds.",
            duration
        )

        return {
            "started_at": started_at.isoformat(),
            "completed_at": completed_at.isoformat(),
            "duration_seconds": round(duration, 2),
            "summary": summary,
            "containers": results,
        }