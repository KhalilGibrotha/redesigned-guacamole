#!/bin/bash

echo "🧪 Testing Repository Context Detection for Confluence Publishing"
echo "================================================================="
echo ""

# Test different repository scenarios
test_repos=(
    "KhalilGibrotha/redesigned-guacamole"
    "SomeUser/external-repo"
    "AnotherOrg/project-name"
    "Enterprise/redesigned-guacamole-fork"
)

echo "🔍 Testing Repository Detection Logic:"
echo ""

for repo in "${test_repos[@]}"; do
    echo "📋 Testing repository: $repo"
    
    # Simulate the workflow logic
    if [[ "$repo" == *"redesigned-guacamole" ]]; then
        same_repo="true"
        echo "  🏠 Detected as: SAME REPOSITORY"
        echo "  📥 Checkout calling repo: SKIPPED (symlink will be created)"
        echo "  🔗 Symlink step: WILL RUN"
    else
        same_repo="false"
        echo "  🌐 Detected as: REMOTE REPOSITORY"
        echo "  📥 Checkout calling repo: WILL RUN"
        echo "  🔗 Symlink step: SKIPPED"
    fi
    
    echo "  ✅ same-repo output: $same_repo"
    echo ""
done

echo "🐛 Common Issues and Fixes:"
echo "=========================="
echo ""
echo "❌ ISSUE 1: Checkout Calling Repository step gets skipped"
echo "   Root Cause: Repository detection incorrectly identifies remote repo as same repo"
echo "   Detection Logic: if [[ \"\${{ github.repository }}\" == *\"redesigned-guacamole\" ]]"
echo "   Fix: Debug output added to verify github.repository value"
echo ""
echo "❌ ISSUE 2: Python setup looks for requirements.txt in wrong path"
echo "   Root Cause: actions/setup-python@v5 auto-detects project files in current working directory"
echo "   Problem Path: /home/runner/work/temp_*/requirements.txt"
echo "   Fix: Temporarily move project files during Python setup to prevent auto-detection"
echo ""
echo "✅ DEBUGGING ADDED:"
echo "   🐛 Repository context detection with github.repository value"
echo "   🐛 Directory contents after each checkout step"
echo "   🐛 File location verification for requirements.txt"
echo "   🐛 Symlink verification when same-repo=true"

echo ""
echo "🏁 Repository Detection Test Complete!"
