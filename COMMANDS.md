# Mrya Language Guide

Welcome to the official command and syntax reference for the Mrya programming language.

## Table of Contents
1.  [Basic Syntax](#1-basic-syntax)
2.  [Data Types](#2-data-types)
3.  [Control Flow](#3-control-flow)
4.  [Functions](#4-functions)
5.  [Built-in Functions](#5-built-in-functions)
6.  [Error Types](#6-error-types)
7.  [Best Practices](#7-best-practices)

---

## 1. Basic Syntax

### Variables
Variables are declared with `let` and can be reassigned using `=`.
You can create immutable constants with `let const`.

```mrya
// Declaration
let my_variable = "Hello, Mrya!"
let my_number = 123

// Constant declaration (cannot be reassigned)
let const PI = 3.14159
// The following line would cause a MryaRuntimeError:
// PI = 3.14

// Re-assignment
my_number = 456

// Declaration with Type Annotation (enforced at runtime)
let name as string = "Shark"
let age as int = 10
// The following line would cause a MryaTypeError:
// age = "ten" 
```

### Output
Use `output()` to print a value to the console.

```mrya
output("Hello, World!")
let name = "Mrya"
output("This is " + name)
```

### Comments
Single-line comments start with `//`.

```mrya
// This is a comment. It will be ignored.
let x = 10 // Comments can also be at the end of a line.
```

### Modules
Include code from other files or native modules using the `import()` function. Since `import()` returns a module object, you must assign it to a variable.

```mrya
// Import a native module
let time = import("time")
output("The time is: " + time.datetime())
time.sleep(1) // Pauses for 1 second

// You can also import your own .mrya files
let my_utils = import("utils.mrya")

// Import with an alias by choosing a different variable name
let t = import("time")
output("Current epoch: " + t.time())
```

---

## 2. Data Types

-   **Number**: `10`, `3.14`, `-55`
-   **String**: `"Hello"`, `"Mrya is fun!"` (concatenated with `+`)
-   **Boolean**: `true`, `false`
-   **List (Array)**: An ordered collection of items.
    ```mrya
    let my_list = [1, "two", true]
    output(my_list[1]) // Outputs: "two"
    my_list[2] = false // Update an element
    ```
-   **Map (Dictionary)**: A collection of key-value pairs.
    ```mrya
    let my_map = { "name": "Shark", "age": 10, "is_cool": true }
    output(my_map["name"]) // Outputs: "Shark"
    my_map["age"] = 11 // Update a value
    ```

---

## 3. Control Flow

### If-Else Statements
Execute code conditionally. You can chain conditions with `else if`. The final `else` block is optional.

```mrya
let score = 85
if (score >= 90) {
    output("Grade: A")
} else if (score >= 80) {
    output("Grade: B")
} else if (score >= 70) {
    output("Grade: C")
} else {
    output("Fail")
}
```

### While Loops
Repeat a block of code as long as a condition is `true`.

```mrya
let i = 0
while (i < 3) {
    output(i)
    i = i + 1
}

### Try/Catch/End Statements
Handle potential runtime errors gracefully.

```mrya
try {
    // Code that might fail
    let result = 10 / 0
    output("This will not be printed.")
} catch MryaRuntimeError {
    // Runs if a MryaRuntimeError occurs
    output("Caught a runtime error!")
} catch {
    // Runs for any other Mrya error if the first catch didn't match
    output("Caught some other error.")
} end {
    // This block always runs, error or not.
    output("Cleanup complete.")
}
```
```

---

## 4. Functions

### Declaration
Define reusable blocks of code with `func` and `define`.

```mrya
func add = define(a, b) {
    return a + b
}
```

### Calling
Execute a function by using its name with parentheses.

```mrya
let sum = add(5, 10)
output(sum) // Prints 15
```

---

## 5. Built-in Functions

### User Input
-   `request(prompt)`: Asks the user for string input.
-   `request(prompt, "number")`: Validates for a number.
-   `request(prompt, "bool")`: Validates for a boolean (`true`/`false`, `yes`/`no`).
-   `request(prompt, type, default_value)`: Provides a default if input is empty.

### Type Conversion
-   `to_int(value)`: Converts a value to an integer.
-   `to_float(value)`: Converts a value to a float (decimal number).
-   `to_bool(value)`: Converts a value to a boolean.

### File I/O
-   `fetch(path)`: Reads the content of a file. If the file does not exist, it will be created with empty content.
-   `store(path, content)`: Writes content to a file, overwriting it.
-   `append_to(path, content)`: Appends content to the end of a file.

### File System Functions (via `fs` module)
Import with `let fs = import("fs")`.
-   `fs.exists(path)`: Returns `true` if a file or directory exists at the path.
-   `fs.is_file(path)`: Returns `true` if the path points to a file.
-   `fs.is_dir(path)`: Returns `true` if the path points to a directory.
-   `fs.list_dir(path)`: Returns a list of file and directory names in a given directory.
-   `fs.get_size(path)`: Returns the size of a file in bytes.
-   `fs.make_dir(path)`: Creates a new directory.
-   `fs.remove_file(path)`: Deletes a file.
-   `fs.remove_dir(path)`: Deletes a directory and all of its contents.

### List (Array) Functions
-   `list(item1, item2, ...)`: Creates a new list (or use `[]` literal).
-   `append(list, item)`: Adds an item to the end of a list.
-   `length(list)`: Returns the number of items in a list.
-   `list_slice(list, start, end)`: Returns a new list containing a slice of the original.

### Map (Dictionary) Functions
-   `map_has(map, key)`: Returns `true` if the key exists in the map.
-   `map_keys(map)`: Returns a list of all keys in the map.
-   `map_values(map)`: Returns a list of all values in the map.
-   `map_delete(map, key)`: Removes a key-value pair from the map.

### String Functions (via `string` module)
Import with `let str_utils = import("string")`.
-   `str_utils.upper(string)`: Converts string to uppercase.
-   `str_utils.lower(string)`: Converts string to lowercase.
-   `str_utils.trim(string)`: Removes leading/trailing whitespace.
-   `str_utils.replace(string, old, new)`: Replaces occurrences of a substring.
-   `str_utils.split(string, separator)`: Splits a string into a list.
-   `str_utils.startsWith(string, prefix)`: Returns `true` if the string starts with the prefix.
-   `str_utils.endsWith(string, suffix)`: Returns `true` if the string ends with the suffix.
-   `str_utils.contains(string, substring)`: Returns `true` if the string contains the substring.
-   `str_utils.slice(string, start, end)`: Returns a slice of the string. `end` is optional.
-   `separator.join(list)`: Joins a list of items into a string, separated by `separator`.
-   *All are also available as methods*: `"hello".upper()`, `",".join(["a","b"])`

### Math Functions
-   `abs(number)`: Returns the absolute value.
-   `round(number)`: Rounds to the nearest integer.
-   `up(number)`: Rounds up to the next integer (ceiling).
-   `down(number)`: Rounds down to the previous integer (floor).
-   `root(number)`: Calculates the square root.
-   `random()`: Returns a random float between 0.0 and 1.0.
-   `randint(min, max)`: Returns a random integer between min and max (inclusive).

### Errors
-   `raise(message)`: Raises a custom exception.
-   `assert(value, expected)`: Raises an exception if the values aren't equal.

---

## 6. Error Types

-   **Parse Error**: This happens when your code has a syntax mistake (e.g., a missing parenthesis, an invalid statement). The parser cannot understand the code.
-   **MryaRuntimeError**: This happens while the code is running. Common causes include:
    -   Using a variable that hasn't been defined.
    -   Calling a function that doesn't exist.
    -   Trying to perform an operation on incompatible types (e.g., `"hello" / 5`).
    -   Division by zero.
    -   List index out of bounds.
-   **MryaTypeError**: This happens when you try to assign a value to a variable that violates its type annotation (e.g., assigning a string to a variable declared `as int`).

---

## 7. Best Practices

-   **Use Clear Names**: Choose descriptive names for variables and functions (e.g., `user_age` instead of `ua`).
-   **Don't Repeat Yourself (DRY)**: If you find yourself writing the same code multiple times, put it in a function.
-   **Organize with Modules**: For larger projects, split your code into multiple `.mrya` files and use `import()` to connect them.
-   **Comment Your Code**: Use `//` to explain complex parts of your code for yourself and others.