"""
BuildOS User Service
Event Producer
"""

import json
from typing import Any

import httpx

from app.core.config import settings
from app.core.exceptions import IntegrationError
from app.events.schemas import EventEnvelope


class EventProducer:
    """Publish user-service events to the configured event broker."""

    def __init__(
        self,
        broker_url: str | None = None,
    ) -> None:
        """Initialize the event producer."""
        self.broker_url = broker_url or settings.event_broker_url

    async def publish(
        self,
        event: EventEnvelope,
    ) -> None:
        """
        Publish an event to the configured broker.

        When no broker is configured, publishing is skipped. This allows
        local development and unit tests to run without RabbitMQ.
        """
        if not self.broker_url:
            return

        payload = event.model_dump(mode="json")

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    self.broker_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Service-ID": settings.service_name,
                    },
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise IntegrationError(
                f"Failed to publish event {event.event_type}: {exc}"
            ) from exc

    async def publish_raw(
        self,
        *,
        event_type: str,
        payload: dict[str, Any],
    ) -> None:
        """
        Publish a raw event payload.

        Intended for integration scenarios where the caller already has
        the complete event structure.
        """
        if not self.broker_url:
            return

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    self.broker_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "X-Service-ID": settings.service_name,
                        "X-Event-Type": event_type,
                    },
                )
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise IntegrationError(
                f"Failed to publish event {event_type}: {exc}"
            ) from exc

    @staticmethod
    def serialize(event: EventEnvelope) -> str:
        """Serialize an event to JSON."""
        return json.dumps(
            event.model_dump(mode="json"),
            separators=(",", ":"),
        )


event_producer = EventProducer()
