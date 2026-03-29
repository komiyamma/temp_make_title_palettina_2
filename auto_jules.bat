cd /d "%~dp0"

call python copy_remain_file_from_src_repo.py
git add -A
git commit -m "addition"
git push
pwsh -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0auto_jules.ps1" %*
