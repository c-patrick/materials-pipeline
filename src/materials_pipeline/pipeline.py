from datetime import UTC, datetime
from pathlib import Path

from materials_pipeline.ingestion import (
    calculate_sha256,
    to_json_compatible,
)
from materials_pipeline.models import (
    IngestionIssue,
    IngestionResult,
    ProviderName,
    RawEnvelope,
)
from materials_pipeline.providers.base import (
    MaterialProvider,
    RawRecord,
)
from materials_pipeline.storage import JsonStorage


class IngestionPipeline:
    """Coordinate raw preservation, transformation and output storage"""

    def __init__(
        self,
        project_root: Path,
        adapter_version: str = "0.1.0",
    ) -> None:
        self.adapter_version = adapter_version
        self.storage = JsonStorage(project_root)

    def ingest(
        self,
        provider: MaterialProvider,
        raw: RawRecord,
    ) -> IngestionResult:
        """Ingest one provider-native material record"""

        provider_name = self._get_provider_name(provider)
        source_id = self._get_source_id(raw)
        retrieved_at = datetime.now(UTC)

        compatible_payload = to_json_compatible(raw)

        envelope = RawEnvelope(
            provider=provider_name,
            source_id=source_id,
            retrieved_at=retrieved_at,
            adapter_version=self.adapter_version,
            payload_sha256=calculate_sha256(compatible_payload),
            payload=compatible_payload,
        )

        timestamp_token = self._timestamp_token(retrieved_at)

        raw_path = self.storage.write_raw(
            provider=provider_name.value,
            source_id=source_id,
            timestamp_token=timestamp_token,
            envelope=envelope,
        )

        try:
            material = provider.transform(raw)

            normalised_path = self.storage.write_normalised(
                record_id=str(material.record_id),
                material=material,
            )

            return IngestionResult(
                status="accepted",
                provider=provider_name,
                source_id=source_id,
                raw_path=str(raw_path),
                normalised_path=str(normalised_path),
                material=material,
            )

        except (ValueError, TypeError, KeyError) as exc:
            issue = IngestionIssue(
                code="TRANSFORMATION_FAILED",
                severity="error",
                message=str(exc),
            )

            return IngestionResult(
                status="rejected",
                provider=provider_name,
                source_id=source_id,
                raw_path=str(raw_path),
                issues=[issue],
            )

    @staticmethod
    def _get_provider_name(
        provider: MaterialProvider,
    ) -> ProviderName:
        """Read the provider name declared by an adapter"""

        provider_name = getattr(
            provider,
            "provider_name",
            None,
        )

        if not isinstance(provider_name, ProviderName):
            raise TypeError(
                'The provider adapter must declare a valid "provider_name".'
            )

        return provider_name

    @staticmethod
    def _get_source_id(raw: RawRecord) -> str:
        """Extract a provisional source identifier for raw storage."""

        value = raw.get("material_id")

        if isinstance(value, str) and value.strip():
            return value.strip()

        return "unknown-source"

    @staticmethod
    def _timestamp_token(value: datetime) -> str:
        """Create a filesystem-safe UTC timestamp."""

        return value.strftime("%Y%m%dT%H%M%S%fZ")
