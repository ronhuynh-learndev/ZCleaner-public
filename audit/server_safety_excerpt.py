"""READ-ONLY EXCERPT from ZCleaner's server.py: the functions that decide what can be touched or deleted.

NOT RUNNABLE on its own. Copied verbatim (comments and logic unchanged) so anyone can verify:
  * the local server only accepts requests from this machine (trusted_host, bind_server),
  * a file is only acted on if it is unchanged since the scan (current_source),
  * only items you selected and confirmed are processed (validated_selection, trash_selected, delete_selected),
  * protected files are never processed (protected_inodes, apply_protected).
The rest of the application is not published.
"""

def trusted_host(self):
    return self.headers.get("Host") in {f"127.0.0.1:{PORT}", f"localhost:{PORT}"}


def scan_token_ok(self, supplied):
    token = self.active_token
    return bool(token) and isinstance(supplied, str) and _same_secret(supplied, token)


def current_source(item):
    """Reject a moved, replaced, or linked path before reading a catalog entry."""
    source = Path(item["path"])
    if source.is_symlink() or not source.is_file():
        raise ValueError("Tệp đã thay đổi. Hãy quét lại")
    try:
        resolved = source.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise ValueError("Tệp không còn tồn tại") from exc
    if not any(resolved.is_relative_to(root) for root in ROOTS) or not same_scanned_file(item, source.stat()):
        raise ValueError("Tệp đã thay đổi. Hãy quét lại")
    return source


def protected_inodes():
    return {ITEM_BY_PATH[p]["inode"] for p in PROTECTED if p in ITEM_BY_PATH}


def load_protected():
    try:
        data = json.loads(PROTECTED_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not isinstance(data.get("paths"), list):
            raise ValueError("Invalid protection format")
        PROTECTED.clear()
        PROTECTED.update(p for p in data.get("paths", []) if isinstance(p, str))
    except (OSError, ValueError, TypeError):
        PROTECTED.clear()


def save_protected():
    write_private_json(PROTECTED_FILE, {"paths": sorted(PROTECTED)})


def apply_protected(self, ids, protect):
    paths = self.paths_sharing_inode(ids)
    self.update_path_set(PROTECTED, paths, protect, save_protected)
    warning = None
    if protect:
        SELECTED.difference_update(paths)
        try:
            save_selection()
        except OSError:
            warning = "Đã bảo vệ tệp nhưng không lưu được danh sách chọn."
    return {"count": len(PROTECTED), "protectedIds": [ITEM_BY_PATH[p]["id"] for p in paths if p in PROTECTED],
            "warning": warning}


def validated_selection(ids):
    if not ids or len(ids) > len(ITEMS) or len(ids) != len(set(ids)):
        raise ValueError("Danh sách chọn không hợp lệ")
    requested = [ITEMS[i] for i in ids]
    blocked = protected_inodes()
    if any(item["path"] not in SELECTED or item["inode"] in blocked or item.get("removed") for item in requested):
        raise ValueError("Danh sách chọn đã thay đổi. Hãy tải lại trang")
    for item in requested:
        current_source(item)
    return requested


def move_to_trash(path):
    """Move one file to the Trash. On macOS the system says where it went (e.g. ~/.Trash/photo 2.jpg) and that is returned,
    so History can put it back; elsewhere returns None (the file is still in the Recycle Bin, just not restorable here)."""
    if sys.platform == "darwin":
        try:
            from Foundation import NSURL, NSFileManager
        except ImportError:
            pass
        else:
            outcome = NSFileManager.defaultManager().trashItemAtURL_resultingItemURL_error_(NSURL.fileURLWithPath_(str(path)), None, None)
            if not outcome[0]:
                error = outcome[2]
                raise OSError(str(error.localizedFailureReason() or error.localizedDescription()) if error is not None else "Không chuyển được vào Thùng rác")
            return str(outcome[1].path()) if outcome[1] is not None else None
    if send2trash is None:
        raise RuntimeError("Chưa cài thành phần chuyển vào Thùng rác")
    send2trash(str(path))
    return None


def trash_selected(ids):
    if send2trash is None and sys.platform != "darwin":
        raise RuntimeError("Chưa cài thành phần chuyển vào Thùng rác")
    if not ids or len(ids) > len(ITEMS) or len(ids) != len(set(ids)):
        raise ValueError("Danh sách chọn không hợp lệ")
    requested = [ITEMS[i] for i in ids]
    blocked = protected_inodes()
    moved = []
    moved_ids = []
    failures = []
    batch = secrets.token_hex(4)  # one "Chuyển vào Thùng rác" click
    for item in requested:
        source = Path(item["path"])
        try:
            if item["path"] not in SELECTED or item["inode"] in blocked or item.get("removed"):
                raise ValueError("Lựa chọn đã thay đổi. Hãy quét lại")
            current_source(item)
            trashed = move_to_trash(source)
        except Exception as exc:
            failures.append(str(exc))
            continue
        item["removed"] = True
        SELECTED.discard(item["path"])
        moved_ids.append(item["id"])
        entry = {"original": str(source), "size": item["size"], "time": int(time.time()), "batch": batch}
        if trashed:
            entry["trashed"] = trashed
        moved.append(entry)
    warning = None
    if moved:
        try:
            append_private_log(TRASH_LOG, moved)
        except OSError:
            warning = "Đã chuyển tệp nhưng không lưu được nhật ký."
        try:
            save_selection()
        except OSError:
            warning = (warning or "") + " Không lưu được danh sách chọn."
    return {"moved": len(moved), "movedIds": moved_ids, "failed": len(failures), "bytes": sum(x["size"] for x in moved), "error": failures[0] if failures else None, "warning": warning}


def delete_selected(ids):
    """Permanently unlink selected paths after a separate explicit UI confirmation."""
    requested = validated_selection(ids)
    deleted = []
    deleted_ids = []
    failure = None
    for item in requested:
        source = Path(item["path"])
        try:
            # Recheck each entry immediately before unlinking. A symlink is never followed.
            current_source(item)
            source.unlink()
        except (OSError, ValueError) as exc:
            failure = str(exc)
            break
        item["removed"] = True
        SELECTED.discard(item["path"])
        deleted_ids.append(item["id"])
        deleted.append({"original": str(source), "size": item["size"], "time": int(time.time())})
    warning = None
    if deleted:
        try:
            append_private_log(DELETE_LOG, deleted)
        except OSError:
            warning = "Đã xóa tệp nhưng không lưu được nhật ký."
        try:
            save_selection()
        except OSError:
            warning = (warning or "") + " Không lưu được danh sách chọn."
    return {"deleted": len(deleted), "deletedIds": deleted_ids,
            "failed": len(requested) - len(deleted), "bytes": sum(x["size"] for x in deleted),
            "error": failure, "warning": warning}


def in_trash_folder(path):
    """Only files inside a Trash folder (~/.Trash, or .Trashes on another disk) are ever moved by Khôi phục."""
    return any(part in {".Trash", ".Trashes"} for part in Path(path).parts)


def restore_from_trash(history_ids):
    """Put trashed files back where they were. A file whose old place is taken, or that is no longer in the Trash, is skipped."""
    wanted = set(history_ids)
    restored = restored_history_ids()
    done, done_ids, failure = [], [], None
    for entry in read_log(TRASH_LOG):
        ident = history_id(entry)
        if ident not in wanted or ident in restored:
            continue
        wanted.discard(ident)
        if not can_restore(entry):
            failure = "Tệp không còn trong Thùng rác, hoặc vị trí cũ đã có tệp khác."
            continue
        original, trashed = Path(entry["original"]), Path(entry["trashed"])
        try:
            original.parent.mkdir(parents=True, exist_ok=True)
            if original.exists():
                raise FileExistsError(original)
            shutil.move(str(trashed), str(original))  # a rename on the same disk: name, dates and inode unchanged
        except OSError as exc:
            failure = str(exc)
            continue
        done.append({"id": ident, "original": str(original), "time": int(time.time())})
        item = ITEM_BY_PATH.get(str(original))
        try:
            if item is not None and item.get("removed") and same_scanned_file(item, original.stat()):
                item["removed"] = False  # back in the list without a new scan
                done_ids.append(item["id"])
        except OSError:
            pass
    warning = None
    if done:
        try:
            append_private_log(RESTORE_LOG, done)
        except OSError:
            warning = "Đã khôi phục tệp nhưng không lưu được nhật ký."
    return {"restored": len(done), "restoredIds": done_ids, "failed": len(history_ids) - len(done),
            "error": failure, "warning": warning}


def bind_server(preferred_port: int) -> ThreadingHTTPServer:
    """Use the requested loopback port or the next free one for app launches."""
    for candidate in range(preferred_port, min(preferred_port + 16, 65536)):
        try:
            return ThreadingHTTPServer(("127.0.0.1", candidate), Handler)
        except OSError as exc:
            if exc.errno != errno.EADDRINUSE and getattr(exc, "winerror", None) != 10013:
                raise
    raise OSError(f"Không có cổng trống từ {preferred_port} đến {candidate}")


