import logging
import time

from config.thresholds import MONITORING_INTERVAL
from monitoring.engine import MonitoringEngine


logger = logging.getLogger(__name__)


class MonitoringScheduler:
    """
    Schedule continuous infrastructure monitoring.
    """

    def __init__(self):
        self.engine = MonitoringEngine()
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

                    logger.info(
                        "Monitoring summary: %s",
                        report["summary"]
                    )

                except Exception:
                    logger.exception("Monitoring cycle failed.")

                time.sleep(self.interval)

        except KeyboardInterrupt:
            logger.info("Monitoring scheduler stopped.")


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    scheduler = MonitoringScheduler()
    scheduler.start()


if __name__ == "__main__":
    main()