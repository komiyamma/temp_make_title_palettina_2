Param(
    [Parameter(Position = 0)]
    [string]$Range,
    [Parameter(Position = 1)]
    [int]$Increment,
    [switch]$Loop
)

# --- 設定 ---
$script:StopRequested = $false
$script:HasProcessedAtLeastOneRange = $false
$script:AutoGeminiMutex = $null
$script:AutoGeminiMutexAcquired = $false

function Request-ScriptStop {
    param([string]$Message)

    if ($Message) {
        Write-Host $Message -ForegroundColor Yellow
    }

    $script:StopRequested = $true
    return $false
}

function Test-HasValidListEntry {
    param([string]$Path = "list.txt")

    if (-not (Test-Path $Path)) {
        return $false
    }

    foreach ($line in Get-Content -Path $Path) {
        if (-not [string]::IsNullOrWhiteSpace($line)) {
            return $true
        }
    }

    return $false
}

function Invoke-CommonPrefixListRefresh {
    Write-Host "🛠️ list.txt の再生成を実行します..." -ForegroundColor Cyan

    python copy_remain_file_from_src_repo.py
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ copy_remain_file_from_src_repo.py の実行に失敗しました。"
        return $false
    }

    python build_common_prefix_list.py
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ build_common_prefix_list.py の実行に失敗しました。"
        return $false
    }

    return $true
}

function Run-GeminiForRange {
    param([string]$targetRange)

    if ($targetRange -notmatch '^\s*(\d+)\s*-\s*(\d+)\s*$') {
        Write-Error "形式が違います: $targetRange"
        return $false
    }

    if (-not (Invoke-CommonPrefixListRefresh)) {
        return $false
    }

    if (-not (Test-HasValidListEntry -Path "list.txt")) {
        if (-not $script:HasProcessedAtLeastOneRange) {
            return (Request-ScriptStop "🛑 list.txt に有効な文字列がないため、auto_gemini.ps1 を終了します。")
        }

        Write-Host "🛑 これまでに処理済みのため、list.txt が空になった可能性があります。120分待機して再確認します。" -ForegroundColor Yellow
        Start-Sleep -Seconds (120 * 60)
        if (-not (Invoke-CommonPrefixListRefresh)) {
            return $false
        }
        Start-Sleep -Seconds (1 * 60)
        if (-not (Test-HasValidListEntry -Path "list.txt")) {
            return (Request-ScriptStop "🛑 60分待機後も list.txt に有効な文字列がないため、auto_gemini.ps1 を終了します。")
        }
    }

    $pendingChanges = git status --porcelain
    if ($pendingChanges) {
        Write-Host "📤 ローカル変更をコミットしてプッシュします..." -ForegroundColor Cyan
        git add -A
        if ($LASTEXITCODE -ne 0) {
            Write-Error "❌ git add に失敗しました。"
            return $false
        }

        git commit -m "addition"
        if ($LASTEXITCODE -ne 0) {
            Write-Error "❌ git commit に失敗しました。"
            return $false
        }

        git push
        if ($LASTEXITCODE -ne 0) {
            Write-Error "❌ git push に失敗しました。"
            return $false
        }
    }
    else {
        Write-Host "ℹ️ コミット対象のローカル変更はありません。" -ForegroundColor Gray
    }

    $startLine = [int]$Matches[1]
    $endLine = [int]$Matches[2]
    if ($startLine -gt $endLine) { 
        Write-Error "開始行は終了行以下にしてください: $targetRange"
        return $false
    }

    Write-Host "`n===============================================" -ForegroundColor Gray
    Write-Host "🎯 処理開始: 範囲 $targetRange" -ForegroundColor Cyan
    Write-Host "===============================================" -ForegroundColor Gray

    Write-Host "🚀 Gemini を実行します..." -ForegroundColor Cyan
    $prompt = "gemini_command.md 質問は一切受け付けません。実行を遂行せよ。gemini_command.mdの書き換えは絶対禁止。画像のタイトルを考える。($targetRange)"
    
    # Gemini CLI コマンドの実行
    gemini -y -p $prompt
    if ($LASTEXITCODE -ne 0) {
        Write-Warning "⚠️ gemini コマンドがエラー終了した可能性があります (ExitCode: $LASTEXITCODE)。処理は継続します。"
    }

    Write-Host "✨ 範囲 $targetRange の全工程が完了しました！" -ForegroundColor Green
    Start-Sleep -Seconds 20
    return $true
}

$mutexName = "Global\temp_make_title_palettina_auto_gemini"
$script:AutoGeminiMutex = [System.Threading.Mutex]::new($false, $mutexName)

try {
    try {
        $script:AutoGeminiMutexAcquired = $script:AutoGeminiMutex.WaitOne(0)
    }
    catch [System.Threading.AbandonedMutexException] {
        $script:AutoGeminiMutexAcquired = $true
        Write-Warning "⚠️ 前回の auto_gemini.ps1 が異常終了していたため、放棄された Mutex を引き継ぎます。"
    }

    if (-not $script:AutoGeminiMutexAcquired) {
        Write-Host "⚠️ すでに auto_gemini.ps1 が実行中です。二重起動を防ぐため終了します。" -ForegroundColor Yellow
        return
    }

    # --- メインロジック（分岐なしで6000回反復） ---
    $i = 1
    for ($count = 1; $count -le 12000; $count++) {
        if ($script:StopRequested) {
            break
        }

        python copy_remain_file_from_src_repo.py

        if ($script:StopRequested) {
            break
        }

        $r = "$i-$($i + 1)"
        $success = Run-GeminiForRange -targetRange $r
        if ($script:StopRequested) {
            break
        }

        if ($success) {
            $script:HasProcessedAtLeastOneRange = $true
            $i += 2
            Start-Sleep -Seconds 5
        }
        else {
            Write-Host "⚠️ $r の実行に失敗しました。5秒後に再試行します..." -ForegroundColor Yellow
            Start-Sleep -Seconds 5
        }
    }
}
finally {
    if ($script:AutoGeminiMutex -and $script:AutoGeminiMutexAcquired) {
        try {
            $script:AutoGeminiMutex.ReleaseMutex() | Out-Null
        }
        catch {
            Write-Warning "⚠️ Mutex の解放に失敗しました: $($_.Exception.Message)"
        }
        finally {
            $script:AutoGeminiMutex.Dispose()
        }
    }
    elseif ($script:AutoGeminiMutex) {
        $script:AutoGeminiMutex.Dispose()
    }
}
