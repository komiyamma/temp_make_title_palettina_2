Param(
    [Parameter(Position = 0)]
    [string]$Range,
    [Parameter(Position = 1)]
    [int]$Increment,
    [switch]$Loop
)

# --- 設定 ---
$API_KEY = $env:JULES_API_KEY
$HEADERS = @{
    "X-Goog-Api-Key" = $API_KEY
    "Content-Type"   = "application/json"
}
$BASE_URL = "https://jules.googleapis.com/v1alpha"

function Run-JulesForRange {
    param([string]$targetRange)

    if (Test-Path "G:\jules_session_list\session-limit.txt") {
        $limitNum = Get-Content "G:\jules_session_list\session-limit.txt" | Select-Object -First 1
        if ($limitNum -match '^\d+$' -and [int]$limitNum -ge 90) {
            Write-Host "⏳ セッション数が90以上 ($limitNum) です。30分間待機します..." -ForegroundColor Yellow
            Start-Sleep -Seconds (30 * 60)
        }
        if ($limitNum -match '^\d+$' -and [int]$limitNum -ge 95) {
            Write-Host "⏳ セッション数が95以上 ($limitNum) です。追加で30分間待機します..." -ForegroundColor Yellow
            Start-Sleep -Seconds (30 * 60)
        }
    }

    # セッション数制限確認ツールの実行
    Push-Location "G:\jules_session_list"
    try {
        Write-Host "🔄 セッションリスト更新ツールを実行中..." -ForegroundColor Cyan
        Start-Process -FilePath ".\winapp_jules_session_list_limit.exe" -NoNewWindow
    }
    catch {
        Write-Warning "⚠️ ツールの実行に失敗しました: $_"
    }
    finally {
        Pop-Location
    }

    if ($targetRange -notmatch '^\s*(\d+)\s*-\s*(\d+)\s*$') {
        Write-Error "形式が違います: $targetRange"
        return $false
    }

    Write-Host "🛠️ build_common_prefix_list.py を実行します..." -ForegroundColor Cyan
    python build_common_prefix_list.py
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ build_common_prefix_list.py の実行に失敗しました。"
        return $false
    }

    $listPath = Join-Path $PSScriptRoot "list.txt"
    $validListEntries = @()
    if (Test-Path $listPath) {
        $validListEntries = Get-Content $listPath | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    }

    if ($validListEntries.Count -eq 0) {
        Write-Host "🛑 list.txt に有効な文字列がないため、auto_jules.ps1 を終了します。" -ForegroundColor Yellow
        exit 0
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

    # 1. セッションの開始
    Write-Host "🚀 Jules セッションを開始します..." -ForegroundColor Cyan
    $body = @{
        prompt              = "gemini_command.md 質問は一切受け付けません。実行を遂行せよ。gemini_command.mdの書き換えは絶対禁止。"
        sourceContext       = @{
            source            = "sources/github/komiyamma/temp_make_title_palettina_2"
            githubRepoContext = @{ startingBranch = "main" }
        }
        requirePlanApproval = $false
        automationMode      = "AUTO_CREATE_PR"
        title               = "画像のタイトルを考える。($targetRange)"
    } | ConvertTo-Json -Depth 10

    $session = Invoke-RestMethod -Uri "$BASE_URL/sessions" -Method Post -Headers $HEADERS -Body $body
    $sessionName = $session.name
    $sessionId = if ($sessionName -match '^sessions/(.+)$') { $Matches[1] } else { $sessionName }
    Write-Host "✅ セッション作成完了: $sessionName"

    # 2. 3分おきに完了チェック（最大60回）
    $maxChecks = 60
    $checkCount = 0
    $isCompleted = $false
    $maxChecksReached = $false
    Write-Host "⏳ 作業完了を待機中（2分間隔、最大$maxChecks回）..." -ForegroundColor Yellow
    while ($true) {
        $checkCount++
        $current = Invoke-RestMethod -Uri "$BASE_URL/$sessionName" -Headers $HEADERS
        Write-Host "$(Get-Date -Format 'HH:mm:ss') - 現在のステータス: $($current.state)"
        
        if ($current.state -eq "COMPLETED") {
            $isCompleted = $true
            Write-Host "🎉 Jules の作業が正常に完了しました。" -ForegroundColor Green
            break
        }
        elseif ($current.state -eq "AWAITING_USER_FEEDBACK") {
            Write-Host "💡 ユーザーフィードバック待機中を検知しました。自動応答を送信します..." -ForegroundColor Yellow
            $msgBody = @{
                prompt = "続きの処理をしてください。質問は認めません。"
            } | ConvertTo-Json
            
            try {
                Invoke-RestMethod -Uri "$BASE_URL/${sessionName}:sendMessage" -Method Post -Headers $HEADERS -Body $msgBody | Out-Null
                Write-Host "✅ 自動応答を送信しました。" -ForegroundColor Green
            }
            catch {
                Write-Warning "⚠️ 自動応答の送信に失敗しました: $($_.Exception.Message)"
            }
        }
        elseif ($current.state -eq "FAILED" -or $current.state -eq "CANCELLED") {
            Write-Error "❌ Jules の作業が失敗またはキャンセルされました。 (State: $($current.state))"
            return $false
        }

        if ($checkCount -ge $maxChecks) {
            Write-Warning "⌛ 最大確認回数（$maxChecks回）に到達したため、範囲 $targetRange をスキップします。"
            $maxChecksReached = $true
            break
        }

        Start-Sleep -Seconds 120
    }

    if ($maxChecksReached) {
        Write-Host "🛑 セッションを強制終了します: $sessionName" -ForegroundColor Yellow
        try {
            Invoke-RestMethod -Uri "$BASE_URL/sessions/$sessionId" -Method Delete -Headers $HEADERS | Out-Null
            Write-Host "✅ セッションを削除しました: $sessionName" -ForegroundColor Yellow
        }
        catch {
            Write-Warning "⚠️ セッション削除に失敗しました: $sessionName / $($_.Exception.Message)"
        }
        return $false
    }

    if (-not $isCompleted) {
        return $false
    }

    # 4. GitHub CLI (gh) を使った操作
    $sessionInfo = Invoke-RestMethod -Uri "$BASE_URL/$sessionName" -Headers $HEADERS
    $prUrl = $sessionInfo.output.pullRequest.url

    if (-not $prUrl) {
        Write-Warning "PR URL が取得できませんでした。gh コマンドで最新の PR を探します。"
        $prUrl = gh pr list --repo "komiyamma/temp_make_title_palettina_2" --limit 1 --json url --jq ".[0].url"
    }

    Write-Host "🛠️ PR 承認とマージを実行します: $prUrl" -ForegroundColor Cyan
    gh pr edit $prUrl --add-assignee "komiyamma"

    # --- Verification Step Skipped ---
    Write-Host "⚠️ 整合性チェックをスキップします。PRの内容を正としてマージします。" -ForegroundColor Yellow
    # --- End Verification Step ---

    gh pr review $prUrl --approve --body "Approved by komiyamma automation script. Range: $targetRange"
    
    Write-Host "🛠️ PRをマージします: $prUrl" -ForegroundColor Cyan
    gh pr merge $prUrl --merge --delete-branch
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ PRのマージに失敗しました。処理を中断します。"
        return $false
    }

    Write-Host "⏳ GitHubへの反映と同期を待機中 (20秒)..." -ForegroundColor Gray
    Start-Sleep -Seconds 20

    # 5. ローカルへの同期
    Write-Host "📥 ローカルの main ブランチを更新します（競合時はリモート優先で上書き）..." -ForegroundColor Green
    git checkout main
    git pull origin main -s recursive -X theirs

    Write-Host "✨ 範囲 $targetRange の全工程が完了しました！" -ForegroundColor Green
    Start-Sleep -Seconds 20
    return $true
}

# --- メインロジック（分岐なしで100回反復） ---
$i = 1
for ($count = 1; $count -le 500; $count++) {
    $r = "$i-$($i + 5)"
    $success = Run-JulesForRange -targetRange $r
    if ($success) {
        $i += 6
        Start-Sleep -Seconds 5
    }
    else {
        Write-Host "⚠️ $r の実行に失敗しました。5秒後に再試行します..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
}
