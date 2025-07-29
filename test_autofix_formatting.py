#!/usr/bin/env python3

# Test file with intentional formatting issues for auto-fix testing

import os
import sys
import json
import requests


def badly_formatted_function(arg1, arg2, arg3):
    """Badly formatted function to test Black formatting."""

    if arg1 == "test":
        result = {"status": "ok", "data": arg2, "extra": arg3}
    else:
        result = {"status": "error", "message": "Invalid argument"}

    return result


class TestClass:
    """Test class with formatting issues."""

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def get_info(self):
        return f"Name: {self.name}, Value: {self.value}"


# Main execution
if __name__ == "__main__":
    test_obj = TestClass("test", 42)
    result = badly_formatted_function("test", "data", "extra")
    print(json.dumps(result, indent=2))
