import logging
from datetime import datetime, timezone


logger = logging.getLogger(__name__)

class IncidentManager:
    """
    Manage infrastructure incidents and prevent duplicate alerts.
    """

    def __init__(self):
        self.active_incidents = {}
        self.incident_history = []

        logger.info("Incident manager initialized.")

    def generate_incident_id(
        self, container_id: str, metric: str
    ) -> str:
        """
        Generate a consistent identifier for a container metric.
        """
        return f"{container_id}:{metric}"


    def open_incident(
        self,
        container_id: str,
        container_name: str,
        metric: str,
        severity: str,
        value
    ) -> dict:
        """
        Register a new infrastructure incident.
        """

        incident_id = self.generate_incident_id(
            container_id, metric
        )

        timestamp = datetime.now(timezone.utc).isoformat()

        incident = {
            "incident_id": incident_id,
            "container_id": container_id,
            "container_name": container_name,
            "metric": metric,
            "severity": severity,
            "value": value,
            "status": "active",
            "opened_at": timestamp,
            "updated_at": timestamp,
        }

        self.active_incidents[incident_id] = incident

        self.incident_history.append({
            **incident,
            "event": "opened"
        })

        logger.warning(
            "New incident opened: %s - %s",
            incident_id, severity
        )

        return incident

    

    def update_incident(
        self,
        incident_id: str,
        severity: str,
        value
    ) -> dict:
        """
        Update an active incident and track severity changes.
        """

        incident = self.active_incidents[incident_id]

        previous_severity = incident["severity"]

        incident["severity"] = severity
        incident["value"] = value
        incident["updated_at"] = (
            datetime.now(timezone.utc).isoformat()
        )

        if previous_severity != severity:

            if severity == "critical":
                event = "escalated"
            else:
                event = "deescalated"

            self.incident_history.append({
                **incident,
                "previous_severity": previous_severity,
                "event": event
            })

            logger.warning(
                "Incident %s: %s - %s to %s",
                event,
                incident_id,
                previous_severity,
                severity
            )

        return incident

    
    def resolve_incident(
        self, incident_id: str, value
    ) -> dict:
        """
        Resolve an active infrastructure incident.
        """

        incident = self.active_incidents.pop(incident_id)

        timestamp = datetime.now(timezone.utc).isoformat()

        incident["previous_severity"] = incident["severity"]
        incident["severity"] = "normal"
        incident["value"] = value
        incident["status"] = "resolved"
        incident["updated_at"] = timestamp
        incident["resolved_at"] = timestamp

        self.incident_history.append({
            **incident,
            "event": "resolved"
        })

        logger.info(
            "Incident resolved: %s",
            incident_id
        )

        return incident

    def process_incident(
        self,
        container_id: str,
        container_name: str,
        metric: str,
        severity: str,
        value
    ) -> dict | None:
        """
        Process a metric observation and manage its incident lifecycle.
        """

        incident_id = self.generate_incident_id(
            container_id, metric
        )

        # Ignore unavailable or non-applicable metrics
        if severity in {"unknown", "not_applicable"}:
            return None

        # Handle abnormal conditions
        if severity in {"warning", "critical"}:

            if incident_id in self.active_incidents:
                return self.update_incident(
                    incident_id, severity, value
                )

            return self.open_incident(
                container_id,
                container_name,
                metric,
                severity,
                value
            )

        # Handle recovery
        if severity == "normal":
            if incident_id in self.active_incidents:
                return self.resolve_incident(
                    incident_id, value
                )

        return None