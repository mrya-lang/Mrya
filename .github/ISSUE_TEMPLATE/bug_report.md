---
name: Bug report
about: Create a report to help us improve
title: "[BUG]"
labels: ''
assignees: ''

---

# Bug Report

> Please fill out **every section** of this form to ensure we can fix the issue as quickly as possible. Incomplete reports may be delayed or closed.

---

## Summary

**Describe the bug in one or two sentences.**  
What is going wrong?

---

## Code Sample

> Paste the **shortest, complete** Mrya program that demonstrates the issue.

Example:
   ```mrya
   let x = 10 * 5
   output(x)
```

If applicable, include multiple files, external dependencies, or inputs the code relies on.

---

## Steps to reproduce

**Explain how to trigger the bug**  - step-by-step. Be as specific as possible.

Example:

1. Downloaded Mrya from Release vX.X.X
2. Edited examples/hello.mrya to include:
    ```mrya
    let a = 5
    output( a + )
    ```
3. Ran:
    ```bash
    python mrya_main.py
    ```
4. Received error message or unexpected behaviour

---

## Expected Behaviour

**What did you expect to happen?**

Describe the correct output, state, or behaviour you anticipated.

Example:
It should print 5 to the terminal without crashing.

---

## Actual Behaviour

**What actually happened instead?**

Paste the full error message (if any), and describe incorrect behaviour.

Example:
   ```bash
   Traceback (most recent call last):
      File "mrya_main.py", line 12, in <module>
         ...
    ```

---

## Environment Details

Please fill out all fields accurately:

- **Operating System:** (e.g Windows 11, macOS 14.3, Ubuntu 22.04)
- **Python Version:** (Run python --version)
- **Mrya Version:** (e.g. v0.1.0 - check release zip folder)

---

## File Paths Used (if relevant)

If the bug involves reading from or writing to files, include:

- Exact paths used
- Any .mrya file contents
- Directory structure if relevant

---

## Additional Context

Is there anything else we should know?

- Did this work in a previous version?
- Is the bug random or consistent?
- Have you modified the interpreter or example files?
- Include screenshots or recordings if visual

---

## Checklist

- I have searched existing issues to avoid duplicates
- I am running the latest version of Mrya
- I have attached a minimal code example
- I have filled in all applicable sections of this form

Thank you for helping improve Mrya!
