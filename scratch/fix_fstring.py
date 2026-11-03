# -*- coding: utf-8 -*-
with open("Institute_Ledger.py", "r", encoding="utf-8") as f:
    code = f.read()

bad_block = '''                messagebox.showinfo("Restore Complete / بحالی مکمل", "Backup restored successfully!\\nPre-restore safety copy saved at:\\n" + str(safety_copy) + "\\n\\nThe application will now refresh.", parent=win)
The application will now refresh.", parent=win)
                win.destroy()
                self.dashboard()
            except Exception as exc:
                messagebox.showerror("Restore Failed", f"Could not complete restore:
{exc}
Your previous data was preserved.", parent=win)'''

clean_block = '''                messagebox.showinfo("Restore Complete / بحالی مکمل", "Backup restored successfully!\\nPre-restore safety copy saved at:\\n" + str(safety_copy) + "\\n\\nThe application will now refresh.", parent=win)
                win.destroy()
                self.dashboard()
            except Exception as exc:
                messagebox.showerror("Restore Failed", "Could not complete restore:\\n" + str(exc) + "\\nYour previous data was preserved.", parent=win)'''

assert bad_block in code, "bad_block not found"
code = code.replace(bad_block, clean_block, 1)

with open("Institute_Ledger.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Fixed restore messagebox.")
