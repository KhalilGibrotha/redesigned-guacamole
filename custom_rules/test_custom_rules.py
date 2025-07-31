"""
Test file to validate custom ansible-lint rules.
This file can be used to test the custom rules locally.
"""

# Simple test playbook content to trigger the custom rule
TEST_PLAYBOOK_CONTENT = """
---
- name: Test playbook for custom rules
  hosts: localhost
  tasks:
    - name: Install package using yum (should trigger CUSTOM001)
      yum:
        name: httpd
        state: present

    - name: Install package using apt (should trigger CUSTOM001)
      apt:
        name: apache2
        state: present

    - name: Install package using package (correct way)
      package:
        name: httpd
        state: present
"""

if __name__ == "__main__":
    print("Custom rule test content:")
    print(TEST_PLAYBOOK_CONTENT)
