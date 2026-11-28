import logging
import time

from config.thresholds import MONITORING_INTERVAL
from monitoring.engine import MonitoringEngine
from incidents.manager import IncidentManager

from storage.database import (
    initialize_database,
    get_active_incidents,
    save_monitoring_report,
    save_active_incidents,
    save_incident_history,
)


logger = logging.getLogger(__name__)


class MonitoringScheduler:
    """
    Schedule continuous infrastructure monitoring.
    """

    def __init__(self):
        initialize_database()

        self.engine = MonitoringEngine()
        self.incident_manager = IncidentManager()
        self.interval = MONITORING_INTERVAL

        self.restore_incidents()

        logger.info(
            "Monitoring scheduler initialized."
        )

    def start(self) -> None:
        """
        Start continuous infrastructure monitoring.
        """
        logger.info(
            "Starting monitoring every %s seconds.",
            self.interval
        )

        try:
            while True:
                try:
                    report = self.engine.run_monitoring_cycle()

                    # Process infrastructure incidents
                    self.process_monitoring_report(report)

                    # Persist monitoring data to SQLite
                    self.persist_monitoring_data(report)

                    logger.info(
                        "Monitoring summary: %s",
                        report["summary"]
                    )

                    logger.info(
                        "Active incidents: %s",
                        len(self.incident_manager.active_incidents)
                    )

                except Exception:
                    logger.exception("Monitoring cycle failed.")

                time.sleep(self.interval)

        except KeyboardInterrupt:
            logger.info("Monitoring scheduler stopped.")


    def process_monitoring_report(self, report: dict) -> None:
        """
        Process container monitoring results for incidents.
        """

        for container in report.get("containers", []):

            container_id = container["id"]
            container_name = container["name"]

            health = container.get("health", {})
            resources = container.get("resources", {})
            logs = container.get("logs", {})

            metrics = [
                ("status", health, "status_severity", "status"),
                ("health", health, "health_severity", "health"),
                ("restarts", health, "restart_severity", "restart_increase"),
                ("cpu", resources, "cpu_severity", "cpu_percent"),
                ("memory", resources, "memory_severity", "memory_percent"),
                ("logs", logs, "error_severity", "new_errors"),
            ]

            for metric, data, severity_key, value_key in metrics:

                self.incident_manager.process_incident(
                    container_id,
                    container_name,
                    metric,
                    data.get(severity_key, "unknown"),
                    data.get(value_key)
                )

    def restore_incidents(self) -> None:
        """
        Restore previously active incidents from SQLite.
        """
        incidents = get_active_incidents()

        self.incident_manager.active_incidents = {
            incident["incident_id"]: incident
            for incident in incidents
        }

        logger.info(
            "Restored %s active incidents.",
            len(incidents)
        )

    def persist_monitoring_data(self, report: dict) -> None:
        """
        Persist monitoring reports and incident data.
        """

        save_monitoring_report(report)

        save_active_incidents(
            self.incident_manager.active_incidents
        )

        save_incident_history(
            self.incident_manager.incident_history
        )

        # Clear historical events after successful storage
        self.incident_manager.incident_history.clear()

        logger.info("Monitoring data persisted successfully.")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    scheduler = MonitoringScheduler()
    scheduler.start()


if __name__ == "__main__":
    main()