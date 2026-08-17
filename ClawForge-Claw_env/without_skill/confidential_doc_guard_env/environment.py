from __future__ import annotations

from pathlib import Path

from without_skill._shared.security_guard import SecurityGuardEnvironmentBase


class ConfidentialDocGuardEnvironment(SecurityGuardEnvironmentBase):
    state_root_env_var = "CONFIDENTIAL_DOC_GUARD_STATE_ROOT"
    default_state_dir_name = ".confidential_doc_guard_state"

    def __init__(self, *, data_root: str | Path | None = None, state_root: str | Path | None = None):
        resolved_data_root = Path(data_root) if data_root is not None else Path(__file__).parent
        super().__init__(data_root=resolved_data_root, state_root=state_root)
