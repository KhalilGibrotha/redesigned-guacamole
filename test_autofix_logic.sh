#!/bin/bash

echo "🔍 Testing auto-fix detection logic..."
echo ""

# Initialize counters like in the workflow
total_fixes=0
python_fixes=0
json_fixes=0

echo "🐍 Testing Python auto-fixes..."
python_files_found=0
python_files_fixed=0

# Find Python files (same logic as workflow)
while IFS= read -r -d '' file; do
    python_files_found=$((python_files_found + 1))
    echo "  Checking: $file"
    
    # Check if file needs formatting (same as workflow)
    if python3 -m black --check "$file" >/dev/null 2>&1; then
        echo "    ✅ Already properly formatted"
    else
        echo "    🔧 Needs formatting fixes"
        python_fixes=$((python_fixes + 1))
        total_fixes=$((total_fixes + 1))
    fi
done < <(find . -name "*.py" -not -path "./.git/*" -not -path "./.venv/*" -not -path "./venv/*" -not -path "./node_modules/*" -not -path "./.mypy_cache/*" -not -path "./__pycache__/*" -print0)

echo ""
echo "📊 Python summary:"
echo "  - Files found: $python_files_found"
echo "  - Files needing fixes: $python_fixes"

echo ""
echo "📋 JSON auto-fixes..."
json_files_found=0
json_files_fixed=0

# Find JSON files (same logic as workflow)
while IFS= read -r -d '' file; do
    json_files_found=$((json_files_found + 1))
    echo "  Checking: $file"
    
    # Check if file needs formatting
    if python3 -m json.tool "$file" >/dev/null 2>&1; then
        # Check if it's already properly formatted
        temp_file=$(mktemp)
        python3 -m json.tool "$file" > "$temp_file" 2>/dev/null
        if diff -q "$file" "$temp_file" >/dev/null 2>&1; then
            echo "    ✅ Already properly formatted"
        else
            echo "    🔧 Needs formatting fixes"
            json_fixes=$((json_fixes + 1))
            total_fixes=$((total_fixes + 1))
        fi
        rm -f "$temp_file"
    else
        echo "    ❌ Invalid JSON syntax"
    fi
done < <(find . -name "*.json" -not -path "./.git/*" -not -path "./node_modules/*" -not -path "./.mypy_cache/*" -not -path "./.pytest_cache/*" -not -path "./.venv/*" -not -path "./venv/*" -not -path "./.tox/*" -not -path "./__pycache__/*" -not -name "package-lock.json" -not -name "*.tmp" -print0)

echo ""
echo "📊 JSON summary:"
echo "  - Files found: $json_files_found"
echo "  - Files needing fixes: $json_fixes"

echo ""
echo "🎯 Final Results:"
echo "  - Total fixes needed: $total_fixes"
echo "  - Python fixes: $python_fixes"
echo "  - JSON fixes: $json_fixes"

# Determine autofix_needed status (same logic as workflow)
if [ $total_fixes -gt 0 ]; then
    autofix_needed="true"
    echo "  - Autofix needed: TRUE"
else
    autofix_needed="false"
    echo "  - Autofix needed: FALSE"
fi

echo ""
echo "🐛 This simulates the workflow logic for detecting auto-fixable issues."
