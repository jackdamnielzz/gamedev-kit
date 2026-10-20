# Create a new game folder with gamedev-kit enabled for that folder only, then open it in VS Code.
#
#   .\scripts\new-game.ps1 -Name MyGame
#   .\scripts\new-game.ps1 -Name MyGame -Root D:\Programmeren\Games
#
# The kit is installed with project scope: it is written to <game>\.claude\settings.json, is active
# only inside that folder, and travels with the game's git repo. Other projects are not affected.

param(
    [Parameter(Mandatory = $true)][string]$Name,
    [string]$Root = "D:\Programmeren"
)

$ErrorActionPreference = "Stop"
$dir = Join-Path $Root $Name

if ((Test-Path $dir) -and ((Get-ChildItem -Force $dir | Measure-Object).Count -gt 0)) {
    throw "$dir already exists and is not empty. For an existing game, run the two 'claude plugin' commands from the README inside that folder instead."
}

New-Item -ItemType Directory -Force -Path $dir | Out-Null
Set-Location $dir
git init -q

claude plugin marketplace add jackdamnielzz/gamedev-kit --scope project
claude plugin install gamedev-kit@gamedev-kit --scope project

Write-Host ""
Write-Host "Done. In VS Code, start Claude Code and run:  /gamedev-kit:new-game $Name"
code .
