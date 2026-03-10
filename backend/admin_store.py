import json
import re
import shutil
from pathlib import Path
from typing import Any, Iterable


DATA_DIR = Path("data")
USERS_FILE = DATA_DIR / "users.json"
CLASSES_FILE = DATA_DIR / "classes.json"
CLASS_UPLOADS_DIR = DATA_DIR / "pdfs" / "classes"

FIXED_ADMIN_EMAILS = {
    "adrian.balan@gmail.com",
    "adrian.balan@airl.ro",
    "adrian.runceanu@gmail.com",
    "laviniu.gavanescu@gmail.com",
}

PROTECTED_CLASS_IDS = {
    "sql",
}


def _normalize_email(email: str | None) -> str:
    return (email or "").strip().lower()


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.strip().lower()).strip("-")
    return slug or "class"


def _safe_filename(filename: str) -> str:
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", Path(filename).name).strip("._")
    if not sanitized:
        return "document.pdf"
    if not sanitized.lower().endswith(".pdf"):
        return f"{sanitized}.pdf"
    return sanitized


def _read_json(path: Path, fallback: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return fallback
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return fallback


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def _discover_default_sql_pdfs() -> list[str]:
    sql_pdfs = sorted(
        path.as_posix()
        for path in (DATA_DIR / "pdfs").glob("*.pdf")
        if path.is_file()
    )
    if sql_pdfs:
        return sql_pdfs
    return sorted(path.as_posix() for path in Path("data_pdf").glob("*.pdf") if path.is_file())


def _sanitize_classes(raw_classes: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    classes: list[dict[str, Any]] = []
    used_ids: set[str] = set()

    for raw_class in raw_classes:
        class_name = str(raw_class.get("name", "")).strip()
        if not class_name:
            continue

        class_id = str(raw_class.get("id", "")).strip() or _slugify(class_name)
        unique_id = class_id
        suffix = 2
        while unique_id in used_ids:
            unique_id = f"{class_id}-{suffix}"
            suffix += 1
        used_ids.add(unique_id)

        pdfs = [
            str(pdf_path).strip()
            for pdf_path in raw_class.get("pdfs", [])
            if str(pdf_path).strip()
        ]
        classes.append({"id": unique_id, "name": class_name, "pdfs": pdfs})

    return sorted(classes, key=lambda item: item["name"].lower())


def _load_users() -> list[dict[str, Any]]:
    payload = _read_json(USERS_FILE, {"users": []})
    by_email: dict[str, dict[str, Any]] = {}

    for raw_user in payload.get("users", []):
        email = _normalize_email(raw_user.get("email"))
        if not email:
            continue
        by_email[email] = {
            "email": email,
            "name": str(raw_user.get("name", "")).strip(),
            "is_admin": bool(raw_user.get("is_admin", False)),
        }

    for admin_email in FIXED_ADMIN_EMAILS:
        if admin_email not in by_email:
            by_email[admin_email] = {
                "email": admin_email,
                "name": "",
                "is_admin": True,
            }
        else:
            by_email[admin_email]["is_admin"] = True

    users = sorted(by_email.values(), key=lambda user: user["email"])
    _write_json(USERS_FILE, {"users": users})
    return users


def _load_classes() -> list[dict[str, Any]]:
    payload = _read_json(CLASSES_FILE, {"classes": []})
    classes = _sanitize_classes(payload.get("classes", []))

    class_names = {class_obj["name"].strip().lower() for class_obj in classes}
    if "sql" not in class_names:
        classes.append(
            {
                "id": _slugify("SQL"),
                "name": "SQL",
                "pdfs": _discover_default_sql_pdfs(),
            }
        )
    classes = _sanitize_classes(classes)
    _write_json(CLASSES_FILE, {"classes": classes})
    return classes


def initialize_admin_data() -> None:
    CLASS_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    _load_users()
    _load_classes()


def get_users() -> list[dict[str, Any]]:
    initialize_admin_data()
    return _load_users()


def register_user(email: str | None, name: str | None = None) -> None:
    normalized_email = _normalize_email(email)
    if not normalized_email:
        return

    users = _load_users()
    for user in users:
        if user["email"] == normalized_email:
            if name and not user.get("name"):
                user["name"] = name.strip()
            _write_json(USERS_FILE, {"users": sorted(users, key=lambda item: item["email"])})
            return

    users.append(
        {
            "email": normalized_email,
            "name": (name or "").strip(),
            "is_admin": normalized_email in FIXED_ADMIN_EMAILS,
        }
    )
    _write_json(USERS_FILE, {"users": sorted(users, key=lambda item: item["email"])})


def set_user_admin(email: str, is_admin: bool) -> None:
    normalized_email = _normalize_email(email)
    if not normalized_email:
        return

    if normalized_email in FIXED_ADMIN_EMAILS:
        is_admin = True

    users = _load_users()
    updated = False
    for user in users:
        if user["email"] == normalized_email:
            user["is_admin"] = bool(is_admin)
            updated = True
            break

    if not updated:
        users.append(
            {
                "email": normalized_email,
                "name": "",
                "is_admin": bool(is_admin),
            }
        )

    _write_json(USERS_FILE, {"users": sorted(users, key=lambda item: item["email"])})


def is_fixed_admin_email(email: str | None) -> bool:
    return _normalize_email(email) in FIXED_ADMIN_EMAILS


def is_admin_user(email: str | None) -> bool:
    normalized_email = _normalize_email(email)
    if not normalized_email:
        return False

    users = _load_users()
    for user in users:
        if user["email"] == normalized_email:
            return bool(user.get("is_admin", False))
    return False


def get_classes() -> list[dict[str, Any]]:
    initialize_admin_data()
    return _load_classes()


def add_class(class_name: str, uploaded_files: Iterable[Any]) -> dict[str, Any]:
    clean_name = class_name.strip()
    if not clean_name:
        raise ValueError("Class name is required.")

    classes = _load_classes()
    if clean_name.lower() in {class_obj["name"].lower() for class_obj in classes}:
        raise ValueError(f"Class '{clean_name}' already exists.")

    class_ids = {class_obj["id"] for class_obj in classes}
    base_id = _slugify(clean_name)
    class_id = base_id
    suffix = 2
    while class_id in class_ids:
        class_id = f"{base_id}-{suffix}"
        suffix += 1

    class_pdf_paths: list[str] = []
    files = list(uploaded_files or [])
    if files:
        class_folder = CLASS_UPLOADS_DIR / class_id
        class_folder.mkdir(parents=True, exist_ok=True)

        for uploaded_file in files:
            if not getattr(uploaded_file, "name", ""):
                continue
            if not uploaded_file.name.lower().endswith(".pdf"):
                continue

            safe_name = _safe_filename(uploaded_file.name)
            destination = class_folder / safe_name
            counter = 2
            while destination.exists():
                destination = class_folder / f"{Path(safe_name).stem}_{counter}.pdf"
                counter += 1

            with destination.open("wb") as out_file:
                out_file.write(uploaded_file.getbuffer())

            class_pdf_paths.append(destination.as_posix())

    new_class = {
        "id": class_id,
        "name": clean_name,
        "pdfs": class_pdf_paths,
    }
    classes.append(new_class)
    _write_json(CLASSES_FILE, {"classes": _sanitize_classes(classes)})
    return new_class


def delete_class(class_id: str) -> dict[str, Any]:
    target_class_id = (class_id or "").strip()
    if not target_class_id:
        raise ValueError("Class id is required.")

    if target_class_id in PROTECTED_CLASS_IDS:
        raise ValueError("This default class cannot be deleted.")

    classes = _load_classes()
    target_class = next((class_obj for class_obj in classes if class_obj["id"] == target_class_id), None)
    if target_class is None:
        raise ValueError("Class not found.")

    remaining_classes = [class_obj for class_obj in classes if class_obj["id"] != target_class_id]
    _write_json(CLASSES_FILE, {"classes": _sanitize_classes(remaining_classes)})

    class_folder = CLASS_UPLOADS_DIR / target_class_id
    if class_folder.exists():
        shutil.rmtree(class_folder, ignore_errors=True)

    return target_class
