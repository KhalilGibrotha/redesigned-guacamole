#!/bin/bash
# Enhanced test script to demonstrate the new rule violations analysis

echo "🔍 Testing Enhanced Rule Violations Analysis"
echo "============================================="

# Create a sample log file with the format you provided
cat > test_super_linter_enhanced.log << 'EOF'
.github/workflows/ci.yml:108:354: "github.head_ref" is potentially untrusted. avoid using it directly in inline scripts. instead, pass it through an environment variable. see https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions for more details [expression]
.github/workflows/ci.yml:164:9: shellcheck reported issue in this script: SC2129:style:1:1: Consider using { cmd1; cmd2; } >> file instead of individual redirects [shellcheck]
.github/workflows/ci.yml:164:9: shellcheck reported issue in this script: SC2126:style:1:55: Consider using 'grep -c' instead of 'grep|wc -l' [shellcheck]
.github/workflows/ci.yml:164:9: shellcheck reported issue in this script: SC2086:info:1:83: Double quote to prevent globbing and word splitting [shellcheck]
.github/workflows/ci.yml:164:9: shellcheck reported issue in this script: SC2126:style:2:38: Consider using 'grep -c' instead of 'grep|wc -l' [shellcheck]
.github/workflows/ci.yml:164:9: shellcheck reported issue in this script: SC2086:info:2:66: Double quote to prevent globbing and word splitting [shellcheck]
.github/workflows/ci.yml:164:9: shellcheck reported issue in this script: SC2126:style:3:37: Consider using 'grep -c' instead of 'grep|wc -l' [shellcheck]
.github/workflows/ci.yml:164:9: shellcheck reported issue in this script: SC2086:info:3:65: Double quote to prevent globbing and word splitting [shellcheck]
.github/workflows/ci.yml:172:9: shellcheck reported issue in this script: SC2162:info:5:59: read without -r will mangle backslashes [shellcheck]
.github/workflows/ci.yml:325:9: shellcheck reported issue in this script: SC2155:warning:18:11: Declare and assign separately to avoid masking return values [shellcheck]
EOF

echo "Sample log created with enhanced violation patterns:"
echo "---------------------------------------------------"
cat test_super_linter_enhanced.log
echo ""

echo "Running enhanced analysis script..."
echo "=================================="

# Create temporary files for processing
temp_violations="/tmp/test_violations.txt"
temp_descriptions="/tmp/test_descriptions.txt"
temp_counts="/tmp/test_rule_counts.txt"

# Extract lines with rule violations (those ending with [rulename])
grep -E '\[[a-zA-Z0-9_-]+\]$' test_super_linter_enhanced.log > "$temp_violations"

if [ -s "$temp_violations" ]; then
  echo "Processing violation details..."

  # Process each violation to extract linter, description, and rule
  while IFS= read -r line; do
    # Extract the rule/linter name (last item in brackets)
    rule=$(echo "$line" | sed -E 's/.*\[([a-zA-Z0-9_-]+)\]$/\1/')
    
    # Extract the description - different patterns for different linters
    if [[ "$line" == *"shellcheck reported issue"* ]]; then
      # For shellcheck: extract description after the rule code
      description=$(echo "$line" | sed -E 's/.*SC[0-9]+:[^:]+:[^:]+:[^:]+: ([^[]+) \[shellcheck\]$/\1/' | sed 's/^ *//' | sed 's/ *$//')
      linter="shellcheck"
    elif [[ "$line" == *"expression"* ]]; then
      # For actionlint expression warnings
      description=$(echo "$line" | sed -E 's/^[^:]*:[^:]*:[^:]*: ([^[]+) \[expression\]$/\1/' | sed 's/^ *//' | sed 's/ *$//')
      linter="actionlint"
    else
      # For other linters, try to extract description before the rule
      description=$(echo "$line" | sed -E 's/^[^:]*:[^:]*:[^:]*: ([^[]+) \[[^]]+\]$/\1/' | sed 's/^ *//' | sed 's/ *$//')
      linter="$rule"
    fi

    # Clean up description - remove extra whitespace and truncate if too long
    description=$(echo "$description" | sed 's/  */ /g' | cut -c1-80)
    
    # If description extraction failed, use a fallback
    if [[ -z "$description" || "$description" == "$line" ]]; then
      description="Rule violation detected"
    fi

    # Create a combined key for grouping: linter|description
    echo "${linter}|${description}" >> "$temp_descriptions"
  done < "$temp_violations"

  # Count occurrences of each linter|description combination
  sort "$temp_descriptions" | uniq -c | sort -nr > "$temp_counts"

  # Count total violations
  total_violations=$(wc -l < "$temp_violations")
  unique_rules=$(wc -l < "$temp_counts")

  echo "Found $total_violations total violations across $unique_rules unique rule types"
  echo ""
  echo "Enhanced Rule Violations Breakdown:"
  echo "| Linter | Description | Count |"
  echo "|--------|-------------|-------|"

  # Generate table
  total_count=0
  while IFS= read -r line; do
    # Extract count (first field)
    count=$(echo "$line" | awk '{print $1}')
    # Extract everything after the count
    rest=$(echo "$line" | awk '{$1=""; print $0}' | sed 's/^ *//')
    # Split on pipe character
    linter=$(echo "$rest" | cut -d'|' -f1)
    description=$(echo "$rest" | cut -d'|' -f2-)
    
    # Determine severity icon based on linter and patterns
    severity_icon="⚠️"
    if [[ "$linter" == "shellcheck" ]]; then
      if [[ "$description" == *"warning"* ]]; then
        severity_icon="🟡"
      elif [[ "$description" == *"error"* ]]; then
        severity_icon="🔴"
      else
        severity_icon="🔵"
      fi
    elif [[ "$linter" == "actionlint" ]]; then
      severity_icon="🟡"
    elif [[ "$description" == *"error"* ]] || [[ "$description" == *"security"* ]]; then
      severity_icon="🔴"
    elif [[ "$description" == *"warning"* ]] || [[ "$description" == *"style"* ]]; then
      severity_icon="🟡"
    elif [[ "$description" == *"info"* ]]; then
      severity_icon="🔵"
    fi

    echo "| $severity_icon **$linter** | $description | $count |"
    total_count=$((total_count + count))
  done < "$temp_counts"

  # Add total row
  echo "| 📊 **TOTAL** | **All violations** | **$total_count** |"

  echo ""
  echo "**Legend:** 🔴 Error | 🟡 Warning | 🔵 Info | ⚠️ General | 📊 Total"
else
  echo "No rule violations found in the expected format"
fi

# Clean up
rm -f test_super_linter_enhanced.log "$temp_violations" "$temp_descriptions" "$temp_counts"

echo ""
echo "✅ Enhanced test completed! This demonstrates the new three-column format with detailed descriptions."
