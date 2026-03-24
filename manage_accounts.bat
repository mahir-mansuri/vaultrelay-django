@echo off
REM VaultRelay Automatic Account Deletion Script
REM This script helps manage inactive user accounts

echo VaultRelay Account Management
echo ============================
echo.
echo Choose an option:
echo 1. Check inactive users and send emails
echo 2. Auto-delete marked accounts (DRY RUN)
echo 3. Auto-delete marked accounts (ACTUAL DELETION)
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo Checking inactive users and sending emails...
    python manage.py check_inactive_users
    pause
) else if "%choice%"=="2" (
    echo.
    echo Running DRY RUN deletion (no accounts will be deleted)...
    python manage.py auto_delete_inactive_accounts --dry-run
    pause
) else if "%choice%"=="3" (
    echo.
    echo WARNING: This will actually delete accounts!
    set /p confirm="Are you sure? Type 'YES' to confirm: "
    if "%confirm%"=="YES" (
        echo Running actual deletion...
        python manage.py auto_delete_inactive_accounts
    ) else (
        echo Deletion cancelled.
    )
    pause
) else if "%choice%"=="4" (
    echo Goodbye!
    exit
) else (
    echo Invalid choice. Please run the script again.
    pause
)

