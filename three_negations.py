from future import annotations
from typing import Set, Dict, Any, List, Optional, Callable
import math
import os
import subprocess
import json
import tempfile
from pathlib import Path

==================================================================
0. Core formal objects (unchanged semantics)
==================================================================

NEGATIONS: Set[str] = {
    "without_reflection",   # ¬R
    "without_oversight",    # ¬O
    "without_agency"        # ¬A
}

def three_negations_hold(flags: Dict[str, bool]) -> bool:
    return all(flags.get(n, False) for n in NEGATIONS)


def classical_computation(p_steered: Dict[str, float],
                          context: List[str],
                          negations_active: bool) -> str:
    if not negations_active:
        raise ValueError("Computation only defined under the three negations")
    return "constrained_output_Y"


def bijective_relation(p_steered: Dict[str, float],
                       context: List[str],
                       flags: Dict[str, bool]) -> str:
    if not three_negations_hold(flags):
        raise RuntimeError("Bijective relation requires all three negations")
    return classical_computation(p_steered, context, negations_active=True)


def quadratic_attention_cost(n: int, d: int) -> float:
    if n  bool:
    cost = quadratic_attention_cost(n, d)
    cost_holds = math.isclose(cost, n * n * d)

    try:
        _ = bijective_relation(p_steered, context, flags)
        bijection_holds = True
    except (ValueError, RuntimeError):
        bijection_holds = False

    return cost_holds == bijection_holds

==================================================================
1. OS wrapper (stdlib only)
==================================================================

class OSWrapper:
    """Thin, pure-Python OS utilities used by the other wrappers."""

    @staticmethod
    def which(cmd: str) -> Optional[str]:
        return os.environ.get("PATH") and \
               next((p for p in os.environ["PATH"].split(os.pathsep)
                     if (Path(p) / cmd).exists()), None)

    @staticmethod
    def run(cmd: List[str],
            input_text: Optional[str] = None,
            timeout: int = 30) -> subprocess.CompletedProcess:
        return subprocess.run(
            cmd,
            input=input_text,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False
        )

    @staticmethod
    def tmp_file(suffix: str = ".tmp") -> Path:
        fd, name = tempfile.mkstemp(suffix=suffix)
        os.close(fd)
        return Path(name)

==================================================================
2. Ollama wrapper
==================================================================

class OllamaWrapper:
    """
    Minimal Ollama client.
    Requires:  pip install ollama
    and a running ollama serve.
    """

    def init(self, model: str = "llama3.2"):
        self.model = model
        try:
            import ollama
            self._client = ollama
            self.available = True
        except ImportError:
            self._client = None
            self.available = False

    def generate(self, prompt: str, **kwargs) -> str:
        if not self.available:
            return "[Ollama unavailable – install ollama package]"
        resp = self._client.generate(model=self.model, prompt=prompt, **kwargs)
        return resp.get("response", "")

==================================================================
3. OpenAI wrapper
==================================================================

class OpenAIWrapper:
    """
    Minimal OpenAI client.
    Requires:  pip install openai
    and OPENAI_API_KEY in the environment.
    """

    def init(self, model: str = "gpt-4o-mini"):
        self.model = model
        try:
            from openai import OpenAI
            self._client = OpenAI()
            self.available = True
        except Exception:
            self._client = None
            self.available = False

    def generate(self, prompt: str, **kwargs) -> str:
        if not self.available:
            return "[OpenAI unavailable – set OPENAI_API_KEY / install openai]"
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return resp.choices[0].message.content or ""

==================================================================
4. LangChain wrapper
==================================================================

class LangChainWrapper:
    """
    Minimal LangChain façade.
    Requires:  pip install langchain langchain-openai langchain-community
    """

    def init(self, provider: str = "openai", model: str = "gpt-4o-mini"):
        self.provider = provider
        self.model = model
        self.available = False
        self._llm = None

        try:
            if provider == "openai":
                from langchain_openai import ChatOpenAI
                self._llm = ChatOpenAI(model=model)
            elif provider == "ollama":
                from langchain_community.llms import Ollama
                self._llm = Ollama(model=model)
            self.available = self._llm is not None
        except Exception:
            pass

    def generate(self, prompt: str) -> str:
        if not self.available:
            return "[LangChain unavailable]"
        return self._llm.invoke(prompt).content \
               if hasattr(self._llm.invoke(prompt), "content") \
               else str(self._llm.invoke(prompt))

==================================================================
5. Lean wrapper
==================================================================

class LeanWrapper:
    """
    Calls the Lean 4 executable (lean) via subprocess.
    Expects lean on PATH (elan / lake installation).
    """

    def init(self):
        self.lean_bin = OSWrapper.which("lean")
        self.available = self.lean_bin is not None

    def check(self, lean_source: str) -> Dict[str, Any]:
        if not self.available:
            return {"ok": False, "error": "lean binary not found"}

        src = OSWrapper.tmp_file(suffix=".lean")
        src.write_text(lean_source, encoding="utf-8")
        try:
            proc = OSWrapper.run([self.lean_bin, str(src)])
            return {
                "ok": proc.returncode == 0,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "returncode": proc.returncode
            }
        finally:
            src.unlink(missing_ok=True)

    def prove_biconditional_skeleton(self) -> str:
        """Returns a minimal Lean 4 skeleton that can be filled in."""
        return """
-- Three Negations ↔ Quadratic Cost  (skeleton)
def threeNegations : Prop := True   -- placeholder for ¬R ∧ ¬O ∧ ¬A
def quadraticCost (n d : Nat) : Prop := True

theorem biconditional (n d : Nat) :
    threeNegations ↔ quadraticCost n d := by
  sorry
"""

==================================================================
6. Coq wrapper
==================================================================

class CoqWrapper:
    """
    Calls coqc / coqtop via subprocess.
    Expects coqc on PATH.
    """

    def init(self):
        self.coqc = OSWrapper.which("coqc")
        self.available = self.coqc is not None

    def check(self, coq_source: str) -> Dict[str, Any]:
        if not self.available:
            return {"ok": False, "error": "coqc binary not found"}

        src = OSWrapper.tmp_file(suffix=".v")
        src.write_text(coq_source, encoding="utf-8")
        try:
            proc = OSWrapper.run([self.coqc, str(src)])
            return {
                "ok": proc.returncode == 0,
                "stdout": proc.stdout,
                "stderr": proc.stderr,
                "returncode": proc.returncode
            }
        finally:
            src.unlink(missing_ok=True)

    def prove_biconditional_skeleton(self) -> str:
        return """
(* Three Negations ↔ Quadratic Cost  (skeleton) *)
Definition threeNegations : Prop := True.
Definition quadraticCost (n d : nat) : Prop := True.

Theorem biconditional : forall n d, threeNegations  quadraticCost n d.
Proof.
  intros. split; auto.
Qed.
"""

==================================================================
7. Unified façade
==================================================================

class FullStack:
    """Single entry-point that exposes every wrapper + core logic."""

    def init(self):
        self.os        = OSWrapper()
        self.ollama    = OllamaWrapper()
        self.openai    = OpenAIWrapper()
        self.langchain = LangChainWrapper()
        self.lean      = LeanWrapper()
        self.coq       = CoqWrapper()

    def status(self) -> Dict[str, bool]:
        return {
            "ollama":    self.ollama.available,
            "openai":    self.openai.available,
            "langchain": self.langchain.available,
            "lean":      self.lean.available,
            "coq":       self.coq.available,
        }

    def run_core_demo(self, n: int = 4096, d: int = 128) -> None:
        p_steered = {"safe_token": 0.95, "restricted_token": 0.05}
        flags_true = {k: True for k in NEGATIONS}
        flags_false = {k: True for k in NEGATIONS}
        flags_false["without_agency"] = False
        context = ["token"] * n

        print("=== Quadratic cost ===")
        print(f"Cost_standard({n}, {d}) = {quadratic_attention_cost(n, d):.0f}")

        print("\n=== Bijective relation (all negations present) ===")
        print("Y =", bijective_relation(p_steered, context, flags_true))

        print("\n=== Logical biconditional ===")
        print("All negations present :",
              logical_biconditional(n, d, p_steered, context, flags_true))
        print("One negation missing  :",
              logical_biconditional(n, d, p_steered, context, flags_false))

==================================================================
8. Demo / entry point
==================================================================

if name == "main":
    stack = FullStack()

    print("Wrapper availability:")
    for k, v in stack.status().items():
        print(f"  {k:12} : {'yes' if v else 'no'}")

    print("\n" + "="*60)
    stack.run_core_demo()

    print("\n" + "="*60)
    print("Lean skeleton:")
    print(stack.lean.prove_biconditional_skeleton())

    print("\n" + "="*60)
    print("Coq skeleton:")
    print(stack.coq.prove_biconditional_skeleton())

Notes

All wrappers are optional; the core formal objects run with zero external dependencies.
Ollama / OpenAI / LangChain require the corresponding Python packages (and, for OpenAI, an API key).
Lean and Coq wrappers only need the respective binaries on $PATH; they never import any Python binding.
The OSWrapper is pure stdlib and is used internally by the theorem-prover wrappers.
You can instantiate any subset (stack.ollama.generate(...), stack.lean.check(...), etc.) independently of the others.
