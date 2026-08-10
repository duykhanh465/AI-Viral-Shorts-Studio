"""Independent Verify script for Phase 3.2 (Revision 2).

Runs in a fresh interpreter process. Does NOT reuse any prior
verify output. Checks public contract + observable behavior.

Revision 2: fix verify script bugs.
  - String annotations (from __future__ import annotations) compared as strings.
  - asyncio.get_event_loop() replaced with asyncio.new_event_loop().
"""

import asyncio
import importlib
import inspect
import sys
import traceback
from pathlib import Path


REPO = Path("d:/Repo Git/AI-Viral-Shorts-Studio")
sys.path.insert(0, str(REPO / "apps/api"))


def main() -> int:
    results: list[tuple[str, bool, str]] = []

    # V-3.2-01: Class exists
    try:
        mod = importlib.import_module("app.services.transcription_service")
        assert hasattr(mod, "TranscriptionService"), "missing class"
        cls = mod.TranscriptionService
        assert inspect.isclass(cls), "not a class"
        results.append(("V-3.2-01 Class exists", True, ""))
    except Exception:
        results.append(("V-3.2-01 Class exists", False, traceback.format_exc()))

    # V-3.2-02: transcribe is async
    try:
        assert inspect.iscoroutinefunction(cls.transcribe), "not async"
        results.append(("V-3.2-02 transcribe is async", True, ""))
    except Exception:
        results.append(("V-3.2-02 transcribe is async", False, traceback.format_exc()))

    # V-3.2-03: signature matches I-3.2-02
    # NOTE: source uses `from __future__ import annotations`, so annotations
    # are strings (PEP 563). Compare strings, not identity.
    try:
        from app.schemas.transcript import WhisperModelSize, Transcript
        sig = inspect.signature(cls.transcribe)
        params = list(sig.parameters.values())
        assert params[0].name == "self", f"first param is {params[0].name}"
        assert params[1].name == "video_path", f"param[1]={params[1].name}"
        assert str(params[1].annotation) == "str", f"video_path annotation={params[1].annotation}"
        assert params[2].name == "model_size", f"param[2]={params[2].name}"
        assert params[2].default is WhisperModelSize.BASE, f"default={params[2].default}"
        assert str(params[2].annotation) == "WhisperModelSize", f"model_size annotation={params[2].annotation}"
        assert str(sig.return_annotation) == "Transcript", f"return={sig.return_annotation}"
        results.append(("V-3.2-03 signature matches I-3.2-02", True, ""))
    except Exception:
        results.append(("V-3.2-03 signature matches I-3.2-02", False, traceback.format_exc()))

    # V-3.2-04: callable raises NotImplementedError
    try:
        instance = cls()
        coro = instance.transcribe("dummy.mp4")
        assert inspect.iscoroutine(coro), "transcribe did not return coroutine"

        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(coro)
            results.append(("V-3.2-04 raises NotImplementedError", False, "no exception raised"))
        except NotImplementedError:
            results.append(("V-3.2-04 raises NotImplementedError", True, ""))
        except Exception as e:
            results.append(("V-3.2-04 raises NotImplementedError", False, f"raised {type(e).__name__}: {e}"))
        finally:
            loop.close()
    except Exception:
        results.append(("V-3.2-04 raises NotImplementedError", False, traceback.format_exc()))

    # V-3.2-05: __all__ contains "TranscriptionService"
    try:
        assert hasattr(mod, "__all__"), "no __all__"
        assert mod.__all__ == ["TranscriptionService"], f"__all__={mod.__all__}"
        results.append(("V-3.2-05 __all__ = ['TranscriptionService']", True, ""))
    except Exception:
        results.append(("V-3.2-05 __all__ = ['TranscriptionService']", False, traceback.format_exc()))

    # V-3.2-06: type hints resolve
    try:
        from app.schemas.transcript import WhisperModelSize as WMS
        from app.schemas.transcript import Transcript as TR
        assert WMS.BASE.value == "base"
        assert hasattr(TR, "model_fields")
        results.append(("V-3.2-06 type hints resolve", True, ""))
    except Exception:
        results.append(("V-3.2-06 type hints resolve", False, traceback.format_exc()))

    # V-3.2-07: scope file present
    try:
        target = REPO / "apps/api/app/services/transcription_service.py"
        assert target.exists(), "file not created"
        results.append(("V-3.2-07 scope file present", True, ""))
    except Exception:
        results.append(("V-3.2-07 scope file present", False, traceback.format_exc()))

    # Print results
    passed = 0
    failed = 0
    for name, ok, err in results:
        if ok:
            passed += 1
            print(f"PASS  {name}")
        else:
            failed += 1
            print(f"FAIL  {name}")
            if err:
                print(f"      {err}")
    print(f"\n{passed}/{len(results)} verify items passed.")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
