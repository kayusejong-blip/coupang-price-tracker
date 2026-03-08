@echo off
chcp 65001 > nul
title 쿠팡 가격변동 알림이 - GitHub 배포 도구

echo ===================================================
echo 🚀 GitHub 배포를 시작합니다.
echo ===================================================
echo.

set "repo_url=https://github.com/kayusejong-blip/coupang-price-tracker"

echo [1] 저장된 레포지토리 주소 사용: %repo_url%
echo.

echo [2] 원격 저장소 동기화 중...
git remote remove origin >nul 2>&1
git remote add origin %repo_url%
git branch -M main
git pull origin main --rebase

echo.
echo [3] GitHub로 업로드 중... (최초 1회 로그인 필요할 수 있음)
git add .
git commit -m "Update Product List and Price Data" >nul 2>&1
git push -u origin main

echo.
echo [4] 완료되었습니다! 
echo 깃허브의 Actions 탭에서 작동 여부를 확인해 보세요.
echo.
pause
