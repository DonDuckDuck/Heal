#!/bin/bash
# 验证所有必需文件是否存在

echo "🔍 检查 HealAPP 备份目录..."
echo ""

cd /Users/haodonghuang/Heal/HealAPP

FILES=(
  "HealApp.swift"
  "Info.plist"
  "Models/AppState.swift"
  "Models/DataModels.swift"
  "Services/APIService.swift"
  "Views/RegistrationView.swift"
  "Views/MainTabView.swift"
  "Views/CameraView.swift"
  "Views/TodayView.swift"
  "Views/ProgressView.swift"
  "Views/ProfileView.swift"
)

MISSING=0
for file in "${FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "✅ $file"
  else
    echo "❌ 缺少: $file"
    MISSING=$((MISSING + 1))
  fi
done

echo ""
echo "═══════════════════════════════════════"
if [ $MISSING -eq 0 ]; then
  echo "🎉 所有 11 个文件都存在！"
  echo "✅ 备份完整，可以安全使用！"
else
  echo "⚠️  缺少 $MISSING 个文件"
  echo "请告诉开发者恢复这些文件"
fi
echo "═══════════════════════════════════════"
