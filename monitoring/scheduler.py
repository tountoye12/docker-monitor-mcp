import logging
import time

from config.thresholds import MONITORING_INTERVAL
from monitoring.engine import MonitoringEngine
from incidents.manager import IncidentManager


logger = logging.getLogger(__name__)


class MonitoringScheduler:
    """
    Schedule continuous infrastructure monitoring.
    """

    def __init__(self):
        self.engine = MonitoringEngine()
        self.incident_manager = IncidentManager()
        self.interval = MONITORING_INTERVAL

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


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    scheduler = MonitoringScheduler()
    scheduler.start()


if __name__ == "__main__":
    main()