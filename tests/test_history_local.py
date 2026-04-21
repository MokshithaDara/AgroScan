from pathlib import Path
import importlib
import sys
import types


def _load_history_with_fake_database():
    fake_db = types.ModuleType("database")
    fake_db.scans_collection = None
    sys.modules["database"] = fake_db
    if "utils.history" in sys.modules:
        return importlib.reload(sys.modules["utils.history"])
    return importlib.import_module("utils.history")


def _clean(path: Path) -> None:
    if path.exists():
        path.unlink()


def test_local_history_fallback_roundtrip(tmp_path, monkeypatch):
    history = _load_history_with_fake_database()
    local_path = tmp_path / "agroscan.db"
    _clean(local_path)

    monkeypatch.setenv("SQLITE_PATH", str(local_path))
    history.save_scan(
        user_id="farmer_abc12345",
        location="Bhimavaram",
        disease="Chilli - Whitefly",
        treatment="Use neem spray",
        treatment_steps=["Step 1", "Step 2"],
        products_recommended=["Neem Oil"],
    )
    history.save_scan(
        user_id="farmer_abc12345",
        location="Vijayawada",
        disease="Groundnut - Rust",
        treatment="Use fungicide",
    )

    assert history.get_total_scans("farmer_abc12345") == 2

    rows = history.get_history("farmer_abc12345", limit=10, skip=0)
    assert len(rows) == 2
    assert rows[0]["user_id"] == "farmer_abc12345"
    assert "treatment_steps" in rows[0]
    assert "products_recommended" in rows[0]


def test_local_history_pagination(tmp_path, monkeypatch):
    history = _load_history_with_fake_database()
    local_path = tmp_path / "agroscan_page.db"
    _clean(local_path)

    monkeypatch.setenv("SQLITE_PATH", str(local_path))
    for idx in range(5):
        history.save_scan(
            user_id="farmer_page1234",
            location=f"Loc-{idx}",
            disease=f"Disease-{idx}",
        )

    first_page = history.get_history("farmer_page1234", limit=2, skip=0)
    second_page = history.get_history("farmer_page1234", limit=2, skip=2)

    assert len(first_page) == 2
    assert len(second_page) == 2
