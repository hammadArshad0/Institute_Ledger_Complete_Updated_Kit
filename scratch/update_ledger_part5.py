# -*- coding: utf-8 -*-
with open("Institute_Ledger.py", "r", encoding="utf-8") as f:
    code = f.read()

old_worker = '''        def worker():
            try:
                os.makedirs(folder, exist_ok=True)
                target = os.path.join(folder, "taha_auto_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".sqlite3")
                self._make_verified_backup_from_path(target)
                prune_backups(folder, keep_count, "taha_auto_", ".sqlite3")
                result_queue.put((True, target))
            except Exception as exc:
                result_queue.put((False, str(exc)))'''

new_worker = '''        def worker():
            try:
                primary = self.settings.get("backup_primary_folder", _default_backup_dir()).strip() or _default_backup_dir()
                os.makedirs(primary, exist_ok=True)
                target = os.path.join(primary, "taha_auto_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".sqlite3")
                self._make_verified_backup_from_path(target)
                prune_backups(primary, keep_count, "taha_auto_", ".sqlite3")
                sec = self.settings.get("backup_second_folder", "").strip()
                if sec and os.path.isdir(sec):
                    try:
                        sec_target = os.path.join(sec, "taha_auto_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".sqlite3")
                        self._make_verified_backup_from_path(sec_target)
                        prune_backups(sec, keep_count, "taha_auto_", ".sqlite3")
                    except Exception:
                        pass
                result_queue.put((True, target))
            except Exception as exc:
                result_queue.put((False, str(exc)))'''

assert old_worker in code, "old_worker not found"
code = code.replace(old_worker, new_worker, 1)

# Also update folder check in run_auto_backup_async
old_folder_check = '''        folder = self.settings.get("backup_second_folder", "").strip()
        if not folder:
            return False, "No second backup folder is set."'''

new_folder_check = '''        folder = self.settings.get("backup_primary_folder", _default_backup_dir()).strip() or _default_backup_dir()'''

assert old_folder_check in code, "old_folder_check not found"
code = code.replace(old_folder_check, new_folder_check, 1)

# Also update run_auto_backup
old_sync_backup = '''    def run_auto_backup(self):
        """Back up to the second folder, trim old copies. Returns (ok, file_or_error_message)."""
        folder = self.settings.get("backup_second_folder", "").strip()
        if not folder:
            return False, "No second backup folder is set."
        try:
            os.makedirs(folder, exist_ok=True)
            target = os.path.join(folder, "taha_auto_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".sqlite3")
            self.make_verified_backup(target)
            prune_backups(folder, self.settings.get("backup_keep", "30"), "taha_auto_", ".sqlite3")
            self._save_setting("backup_last_auto", timestamp())
            return True, target
        except Exception as exc:
            return False, str(exc)'''

new_sync_backup = '''    def run_auto_backup(self):
        """Back up to the dedicated persistent folder and optional second folder, trim old copies. Returns (ok, file_or_error_message)."""
        folder = self.settings.get("backup_primary_folder", _default_backup_dir()).strip() or _default_backup_dir()
        try:
            os.makedirs(folder, exist_ok=True)
            target = os.path.join(folder, "taha_auto_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".sqlite3")
            self.make_verified_backup(target)
            prune_backups(folder, self.settings.get("backup_keep", "30"), "taha_auto_", ".sqlite3")
            sec = self.settings.get("backup_second_folder", "").strip()
            if sec and os.path.isdir(sec):
                try:
                    sec_target = os.path.join(sec, "taha_auto_" + datetime.now().strftime("%Y%m%d_%H%M%S") + ".sqlite3")
                    self.make_verified_backup(sec_target)
                    prune_backups(sec, self.settings.get("backup_keep", "30"), "taha_auto_", ".sqlite3")
                except Exception:
                    pass
            self._save_setting("backup_last_auto", timestamp())
            return True, target
        except Exception as exc:
            return False, str(exc)'''

assert old_sync_backup in code, "old_sync_backup not found"
code = code.replace(old_sync_backup, new_sync_backup, 1)

with open("Institute_Ledger.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated backup routines successfully.")

