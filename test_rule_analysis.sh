#!/bin/bash
# Test script to demonstrate how the rule violations analysis works

echo "🔍 Testing Rule Violations Analysis"
echo "=================================="

# Create a sample log file with the format you provided
cat > test_super_linter.log << 'EOF'
.github/workflows/ci.yml:108:354: "github.head_ref" is potentially untrusted. avoid using it directly in inline scripts. instead, pass it through an environment variable. see https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions for more details [expression]
.github/workflows/ci.yml:164:9: shellcheck reported issue in this script: SC2129:style:1:1: Consider using { cmd1; cmd2; } >> file instead of individual redirects [shellcheck]
.github/workflows/ci.yml:164:9: shellcheck reported issue in this script: SC2126:style:1:55: Consider using 'grep -c' instead of 'grep|wc -l' [shellcheck]
.github/workflows/ci.yml:164:9: shellcheck reported issue in this script: SC2086:info:1:83: Double quote to prevent globbing and word splitting [shellcheck]
.github/workflows/ci.yml:164:9: shellcheck reported issue in this script: SC2126:style:2:38: Consider using 'grep -c' instead of 'grep|wc -l' [shellcheck]
.github/workflows/ci.yml:164:9: shellcheck reported issue in this script: SC2086:info:2:66: Double quote to prevent globbing and word splitting [shellcheck]
playbook.yml:15:20: syntax error: expected <block end>, but found <scalar> [yaml-syntax-error]
playbook.yml:25:5: wrong indentation: expected 4 but found 5 [indentation]
test.py:10:5: E302 expected 2 blank lines, found 1 [pycodestyle]
test.py:15:80: E501 line too long (95 > 79 characters) [pycodestyle]
EOF

echo "Sample log created with the following violations:"
echo "------------------------------------------------"
cat test_super_linter.log
echo ""

echo "Running analysis script..."
echo "========================="

# Extract rule violations and count them (same logic as workflow)
temp_violations="/tmp/test_violations.txt"
temp_counts="/tmp/test_rule_counts.txt"

# Extract lines with rule violations (those ending with [rulename])
grep -E '\[[a-zA-Z0-9_-]+\]$' test_super_linter.log > "$temp_violations"

if [ -s "$temp_violations" ]; then
  # Extract just the rule names and count occurrences
  sed -E 's/.*\[([a-zA-Z0-9_-]+)\]$/\1/' "$temp_violations" | sort | uniq -c | sort -nr > "$temp_counts"

  # Count total violations
  total_violations=$(wc -l < "$temp_violations")
  unique_rules=$(wc -l < "$temp_counts")

  echo "Found $total_violations total violations across $unique_rules unique rules"
  echo ""
  echo "Rule Violations Breakdown:"
  echo "| Rule | Occurrences |"
  echo "|------|-------------|"

  # Generate table
  while read -r count rule; do
    # Determine severity icon based on rule patterns
    severity_icon="⚠️"
    if [[ "$rule" == *"error"* ]] || [[ "$rule" == *"security"* ]]; then
      severity_icon="🔴"
    elif [[ "$rule" == *"warning"* ]] || [[ "$rule" == *"style"* ]]; then
      severity_icon="🟡"
    elif [[ "$rule" == *"info"* ]]; then
      severity_icon="🔵"
    fi

    echo "| $severity_icon \`$rule\` | $count |"
  done < "$temp_counts"

  echo ""
  echo "**Legend:** 🔴 Error/Security | 🟡 Warning/Style | 🔵 Info | ⚠️ General"
else
  echo "No rule violations found in the expected format"
fi

# Clean up
rm -f test_super_linter.log "$temp_violations" "$temp_counts"

echo ""
echo "✅ Test completed! This demonstrates how the workflow will analyze real Super Linter logs."
