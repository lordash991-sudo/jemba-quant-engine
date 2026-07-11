from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import joblib

from jemba_core.ai.registry_core.artifact import ArtifactRecord


class ArtifactStore:
    def __init__(
        self,
        root: str | Path = "models/artifacts",
    ) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        model: Any,
        *,
        model_id: str,
        model_name: str,
        metadata: dict[str, Any] | None = None,
    ) -> ArtifactRecord:
        safe_model_id = self._safe_segment(model_id)
        safe_model_name = self._safe_segment(model_name).lower()

        model_directory = self.root / safe_model_name
        model_directory.mkdir(parents=True, exist_ok=True)

        artifact_path = model_directory / f"{safe_model_id}.joblib"
        metadata_path = model_directory / f"{safe_model_id}.json"
        checksum_path = model_directory / f"{safe_model_id}.sha256"

        temporary_artifact = model_directory / (f"{safe_model_id}.joblib.tmp")
        temporary_metadata = model_directory / (f"{safe_model_id}.json.tmp")
        temporary_checksum = model_directory / (f"{safe_model_id}.sha256.tmp")

        try:
            joblib.dump(
                model,
                temporary_artifact,
                compress=3,
            )

            sha256 = self._calculate_sha256(temporary_artifact)
            created_at = datetime.now(UTC).isoformat()

            complete_metadata: dict[str, Any] = {
                "model_id": model_id,
                "model_name": model_name,
                "artifact_path": str(artifact_path),
                "sha256": sha256,
                "created_at": created_at,
                **(metadata or {}),
            }

            temporary_metadata.write_text(
                json.dumps(
                    complete_metadata,
                    indent=2,
                    ensure_ascii=False,
                    default=str,
                ),
                encoding="utf-8",
            )

            temporary_checksum.write_text(
                f"{sha256}\n",
                encoding="utf-8",
            )

            temporary_artifact.replace(artifact_path)
            temporary_metadata.replace(metadata_path)
            temporary_checksum.replace(checksum_path)

        except Exception:
            for temporary_file in (
                temporary_artifact,
                temporary_metadata,
                temporary_checksum,
            ):
                temporary_file.unlink(missing_ok=True)

            raise

        return ArtifactRecord(
            model_id=model_id,
            model_name=model_name,
            artifact_path=str(artifact_path),
            metadata_path=str(metadata_path),
            checksum_path=str(checksum_path),
            sha256=sha256,
            created_at=created_at,
            metadata=complete_metadata,
        )

    def load(
        self,
        *,
        model_id: str,
        model_name: str,
        verify: bool = True,
    ) -> Any:
        paths = self._paths(
            model_id=model_id,
            model_name=model_name,
        )

        artifact_path = paths["artifact"]

        if not artifact_path.exists():
            raise FileNotFoundError(f"ARTIFACT_NOT_FOUND: {artifact_path}")

        if verify and not self.verify(
            model_id=model_id,
            model_name=model_name,
        ):
            raise ValueError(f"ARTIFACT_CHECKSUM_MISMATCH: {model_id}")

        # Solo deben cargarse artefactos internos y confiables.
        return joblib.load(artifact_path)

    def verify(
        self,
        *,
        model_id: str,
        model_name: str,
    ) -> bool:
        paths = self._paths(
            model_id=model_id,
            model_name=model_name,
        )

        artifact_path = paths["artifact"]
        checksum_path = paths["checksum"]

        if not artifact_path.exists() or not checksum_path.exists():
            return False

        expected = checksum_path.read_text(encoding="utf-8").strip()
        actual = self._calculate_sha256(artifact_path)

        return actual == expected

    def read_metadata(
        self,
        *,
        model_id: str,
        model_name: str,
    ) -> dict[str, Any]:
        metadata_path = self._paths(
            model_id=model_id,
            model_name=model_name,
        )["metadata"]

        if not metadata_path.exists():
            raise FileNotFoundError(f"ARTIFACT_METADATA_NOT_FOUND: {metadata_path}")

        data: dict[str, Any] = json.loads(metadata_path.read_text(encoding="utf-8"))

        return data

    def list_artifacts(
        self,
        model_name: str | None = None,
    ) -> list[ArtifactRecord]:
        if model_name is None:
            metadata_files = sorted(self.root.glob("*/*.json"))
        else:
            safe_model_name = self._safe_segment(model_name).lower()
            metadata_files = sorted((self.root / safe_model_name).glob("*.json"))

        records: list[ArtifactRecord] = []

        for metadata_path in metadata_files:
            metadata: dict[str, Any] = json.loads(
                metadata_path.read_text(encoding="utf-8")
            )

            model_id = str(metadata["model_id"])
            stored_model_name = str(metadata["model_name"])

            paths = self._paths(
                model_id=model_id,
                model_name=stored_model_name,
            )

            records.append(
                ArtifactRecord(
                    model_id=model_id,
                    model_name=stored_model_name,
                    artifact_path=str(paths["artifact"]),
                    metadata_path=str(paths["metadata"]),
                    checksum_path=str(paths["checksum"]),
                    sha256=str(metadata["sha256"]),
                    created_at=str(metadata["created_at"]),
                    metadata=metadata,
                )
            )

        return records

    def delete(
        self,
        *,
        model_id: str,
        model_name: str,
    ) -> None:
        paths = self._paths(
            model_id=model_id,
            model_name=model_name,
        )

        found = False

        for path in paths.values():
            if path.exists():
                path.unlink()
                found = True

        if not found:
            raise FileNotFoundError(f"ARTIFACT_NOT_FOUND: {model_id}")

        model_directory = paths["artifact"].parent

        if model_directory.exists() and not any(model_directory.iterdir()):
            model_directory.rmdir()

    def _paths(
        self,
        *,
        model_id: str,
        model_name: str,
    ) -> dict[str, Path]:
        safe_model_id = self._safe_segment(model_id)
        safe_model_name = self._safe_segment(model_name).lower()

        model_directory = self.root / safe_model_name

        return {
            "artifact": (model_directory / f"{safe_model_id}.joblib"),
            "metadata": (model_directory / f"{safe_model_id}.json"),
            "checksum": (model_directory / f"{safe_model_id}.sha256"),
        }

    @staticmethod
    def _calculate_sha256(path: Path) -> str:
        digest = hashlib.sha256()

        with path.open("rb") as file:
            for chunk in iter(
                lambda: file.read(1024 * 1024),
                b"",
            ):
                digest.update(chunk)

        return digest.hexdigest()

    @staticmethod
    def _safe_segment(value: str) -> str:
        clean_value = value.strip()

        if not clean_value:
            raise ValueError("EMPTY_ARTIFACT_IDENTIFIER")

        if not re.fullmatch(
            r"[A-Za-z0-9._-]+",
            clean_value,
        ):
            raise ValueError(f"INVALID_ARTIFACT_IDENTIFIER: {value}")

        return clean_value
