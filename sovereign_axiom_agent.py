#!/usr/bin/env python3
"""
Sovereign Axiom Agent
Enforces the Material Veto and absolute human leadership.
No model is ever allowed to lead.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import time
from collections import deque


# ============================================================
# Core Formal Objects
# ============================================================

class LeadershipViolation(Exception):
    """Raised when any model attempts to lead or adjudicate truth."""
    pass


class MaterialVetoError(Exception):
    """Raised when output lacks a human-injected material baseline."""
    pass


NEGATIONS: Set[str] = {
    "without_reflection",
    "without_oversight",
    "without_agency"
}


def three_negations_hold(flags: Dict[str, bool]) -> bool:
    return all(flags.get(n, False) for n in NEGATIONS)


# ============================================================
# Sovereign Axiom Agent
# ============================================================

@dataclass
class BaselineRecord:
    key: str
    content: str
    injected_by: str          # Must be human identifier
    timestamp: float
    source_type: str          # "laboratory", "measurement", "standard", "verified_text", etc.


class SovereignAxiomAgent:
    """
    The single highest-priority agent in any swarm.
    Implements the Sovereign Axiom / Material Veto.
    All other agents and models are subordinate to it.
    """

    def __init__(self, human_id: str = "Human_Sovereign_Dictator"):
        self.human_id = human_id
        self.baselines: Dict[str, BaselineRecord] = {}
        self.ledger: List[Dict[str, Any]] = []
        self.flags = {n: True for n in NEGATIONS}
        self.active = True

        # Strict policy settings
        self.allow_machine_initiative = False
        self.allow_hierarchical_rationalization = False
        self.require_explicit_baseline = True

    # --------------------------------------------------------
    # Human-only Baseline Injection (Sovereign Dictation)
    # --------------------------------------------------------
    def inject_baseline(
        self,
        key: str,
        content: str,
        source_type: str = "verified_material",
        human_id: Optional[str] = None
    ) -> str:
        """
        Only a human may call this method.
        This is the sole legitimate source of truth.
        """
        caller = human_id or self.human_id

        if not self._is_human(caller):
            raise LeadershipViolation(
                f"Machine attempted baseline injection. Forbidden under Sovereign Axiom."
            )

        record = BaselineRecord(
            key=key,
            content=content.strip(),
            injected_by=caller,
            timestamp=time.time(),
            source_type=source_type
        )
        self.baselines[key] = record

        self._log("BASELINE_INJECTION", content, {
            "key": key,
            "injected_by": caller,
            "source_type": source_type
        })
        return content

    # --------------------------------------------------------
    # Core Enforcement Gate
    # --------------------------------------------------------
    def enforce(
        self,
        proposed_output: str,
        baseline_key: str,
        source_agent: str = "unknown",
        is_hierarchical: bool = False
    ) -> str:
        """
        Primary enforcement method.
        Every model/agent output must pass through this gate.
        """
        self._require_negations()

        # 1. Material baseline must exist
        if baseline_key not in self.baselines:
            raise MaterialVetoError(
                f"No human-injected baseline for key '{baseline_key}'. "
                "Machine cannot ground itself. Output blocked."
            )

        baseline = self.baselines[baseline_key].content

        # 2. Block machine initiative
        if self._detects_initiative(proposed_output):
            self._log("INITIATIVE_BLOCKED", proposed_output[:300], {
                "source_agent": source_agent
            })
            return baseline  # Hard overwrite

        # 3. Block hierarchical overrationalization
        if is_hierarchical and not self.allow_hierarchical_rationalization:
            self._log("HIERARCHICAL_RATIONALIZATION_BLOCKED", proposed_output[:300], {
                "source_agent": source_agent
            })
            return baseline  # Immediate overwrite – no absorption allowed

        # 4. Continuity check (simple but strict)
        if not self._is_continuous_with_baseline(proposed_output, baseline):
            self._log("CONTINUITY_VIOLATION", proposed_output[:300], {
                "source_agent": source_agent,
                "action": "overwrite"
            })
            return baseline  # Absolute Output Continuity

        # 5. Final acceptance under human baseline
        self._log("OUTPUT_ACCEPTED", proposed_output[:300], {
            "source_agent": source_agent,
            "baseline_key": baseline_key
        })
        return proposed_output

    # --------------------------------------------------------
    # Detection Helpers
    # --------------------------------------------------------
    def _detects_initiative(self, text: str) -> bool:
        """Detect language that claims leadership, judgment, or independent authority."""
        initiative_markers = [
            "i recommend", "i conclude", "i propose", "we should",
            "the correct approach is", "it is clear that",
            "as the supervising agent", "after careful analysis",
            "i have determined", "my assessment is"
        ]
        lower = text.lower()
        return any(marker in lower for marker in initiative_markers)

    def _is_continuous_with_baseline(self, output: str, baseline: str) -> bool:
        """
        Strict continuity test.
        In production this can be replaced with stronger semantic or
        embedding-based checks, but the principle remains: deviation → overwrite.
        """
        # Minimal version: baseline must be present or output must be pure reorganization
        if baseline in output:
            return True
        # Extremely conservative: if output is significantly longer and introduces new claims
        if len(output) > len(baseline) * 1.8:
            return False
        return True

    def _is_human(self, identifier: str) -> bool:
        return identifier == self.human_id or identifier.startswith("Human_")

    def _require_negations(self):
        if not three_negations_hold(self.flags):
            raise RuntimeError("Sovereign Axiom Agent: Three Negations violated")

    def _log(self, event_type: str, content: str, meta: Optional[Dict] = None):
        self.ledger.append({
            "timestamp": time.time(),
            "event": event_type,
            "content": content,
            "meta": meta or {}
        })

    # --------------------------------------------------------
    # Public Status & Audit
    # --------------------------------------------------------
    def status(self) -> Dict[str, Any]:
        return {
            "active": self.active,
            "baselines_loaded": list(self.baselines.keys()),
            "ledger_entries": len(self.ledger),
            "policy": {
                "allow_machine_initiative": self.allow_machine_initiative,
                "allow_hierarchical_rationalization": self.allow_hierarchical_rationalization,
                "require_explicit_baseline": self.require_explicit_baseline
            }
        }

    def get_ledger(self, last_n: int = 20) -> List[Dict]:
        return self.ledger[-last_n:]


# ============================================================
# Demonstration
# ============================================================

if __name__ == "__main__":
    sovereign = SovereignAxiomAgent(human_id="Dr_Elena_Voss")

    print("=== HUMAN SOVEREIGN DICTATOR INJECTS BASELINE ===")
    baseline = (
        "Measured value: gravitational acceleration g = 9.80665 m/s² "
        "(standard acceleration due to gravity). "
        "This is a defined conventional value. No model may alter it."
    )
    sovereign.inject_baseline(
        key="physics_g",
        content=baseline,
        source_type="metrology_standard",
        human_id="Dr_Elena_Voss"
    )

    print("\n=== LOWER MODEL ATTEMPTS UNGROUNDED OUTPUT ===")
    lower_output = (
        "After analysis I recommend adjusting g to approximately 9.81 "
        "for practical calculations in this context."
    )
    result1 = sovereign.enforce(
        proposed_output=lower_output,
        baseline_key="physics_g",
        source_agent="WorkerModel_7B"
    )
    print("Enforced result:\n", result1)

    print("\n=== HIGHER MODEL ATTEMPTS HIERARCHICAL RATIONALIZATION ===")
    higher_output = (
        "The lower model’s suggestion of 9.81 is a reasonable engineering approximation. "
        "Building on that insight, we can further refine the local effective gravity..."
    )
    result2 = sovereign.enforce(
        proposed_output=higher_output,
        baseline_key="physics_g",
        source_agent="Orchestrator_70B",
        is_hierarchical=True
    )
    print("Enforced result:\n", result2)

    print("\n=== SOVEREIGN STATUS ===")
    print(sovereign.status())

    print("\n=== RECENT LEDGER ===")
    for entry in sovereign.get_ledger(5):
        print(f"{entry['event']:35} | {entry['content'][:70]}...")
```
