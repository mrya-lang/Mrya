# Mrya Language Guide

Welcome to the official command and syntax reference for the Mrya programming language.

## Table of Contents
1.  [Basic Syntax](#1-basic-syntax)
2.  [Data Types](#2-data-types)
3.  [Control Flow](#3-control-flow)
4.  [Functions](#4-functions)
5.  [Classes (OOP)](#5-classes-oop)
6.  [Decorators](#6-decorators)
7.  [Built-in Functions](#7-built-in-functions)
8.  [Error Handling](#8-error-handling)
9.  [Error Types](#9-error-types)
10. [Best Practices](#10-best-practices)
11. [Unit Tests](#11-unit-tests)

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

// Compound Assignment
let score = 10
score += 5 // score is now 15
score -= 2 // score is now 13
score *= 2 // score is now 26
score /= 2 // score is now 13

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
-   **Nil**: `nil` (represents absence of value)
-   **List (Array)**: An ordered collection of items.
    ```mrya
    let my_list = [1, "two", true]
    output(my_list[1]) // Outputs: "two"
    my_list[2] = false // Update an element
    ```
-   **H-String (Formatted String)**: A string that can embed expressions.
    ```mrya
    let name = "Mrya"
    let version = 1.0
    output(#"Welcome to <name> version <version>!") // Outputs: Welcome to Mrya version 1.0!
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
```

### For Loops
Iterate over collections or ranges.

```mrya
let items = ["apple", "banana", "cherry"]
for (item in items) {
    output(item)
}

// For loops also support break and continue
for (item in items) {
    if (item == "banana") {
        continue // Skip this iteration
    }
    if (item == "cherry") {
        break // Exit the loop
    }
    output(item)
}
```

### Break and Continue
- `break`: Exit the current loop immediately
- `continue`: Skip to the next iteration of the current loop

```mrya
let i = 0
while (i < 10) {
    i += 1
    if (i == 3) {
        continue // Skip printing 3
    }
    if (i == 7) {
        break // Exit loop at 7
    }
    output(i)
}
```

---

## 4. Functions

### Declaration
Define reusable blocks of code with `func` and `define`.

```mrya
func add = define(a, b) {
    return a + b
}

// Functions can be nested
func outer = define() {
    func inner = define() {
        output("Hi from inner!")
    }
    inner()
}
```

### Calling
Execute a function by using its name with parentheses.

```mrya
let sum = add(5, 10)
output(sum) // Prints 15

// Functions can return nil if no return statement
func nothing = define() {
    return
}
let x = nothing() // x is nil
```

### Return Values
Functions can return values using `return`. If no return statement is provided, the function returns `nil`.

---

## 6. Decorators

Decorators are special functions that modify or enhance other functions or classes. They are declared using the `%` symbol right before a function or class definition. A decorator is a function that takes a function or class as its only argument and returns a new (or modified) function or class.

```mrya
// A simple decorator that logs when a function is called.
func log_call = define(fn) {
    func wrapper = define(args) {
        output(#"Calling function: <fn.name.lexeme>..."#)
        let result = fn(...args)
        output("...function finished.")
        return result
    }
    return wrapper
}

// Apply the decorator to a function
%log_call
func greet = define(name) {
    output(#"Hello, <name>!"#)
}

greet("Mrya")
// Output:
// Calling function: greet...
// Hello, Mrya!
// ...function finished.
```

---

## 5. Classes (OOP)

Mrya supports object-oriented programming with classes and inheritance.

### Class Declaration
Define a blueprint for objects using the `class` keyword. Methods are defined inside the class using the standard `func` syntax.

```mrya
class Dog {
    // The initializer is a special function called _start_
    func _start_ = define(name, age) {
        this.name = name
        this.age = age
    }

    func bark = define() {
        output(this.name + " says: Woof!")
    }

    // --- Special Methods ---

    // Provides a custom string for output()
    func _out_ = define() {
        return this.name + " is a good dog."
    }

    // Allows the length() function to work on instances
    func _len_ = define() {
        // Example: return the length of the dog's name
        return length(this.name)
    }

    // Allows instances to be added with the '+' operator
    func _plus_ = define(other) {
        // Example: create a puppy
        let puppy_name = this.name + " & " + other.name + " Jr."
        return Dog(puppy_name, 0)
    }
}

// Create a new instance of the Dog class
let my_dog = Dog("Rex", 5)
my_dog.bark() // Outputs: Rex says: Woof!
output(my_dog.age) // Outputs: 5
output(my_dog) // Outputs: Rex is a good dog.
output(length(my_dog)) // Outputs: 3 (from "Rex")
```

### Inheritance
Classes can inherit from other classes using the `<` operator.

```mrya
class Animal {
    func _start_ = define(name) {
        this.name = name
    }
    
    func speak = define() {
        output(this.name + " makes a sound")
    }
}

class Cat < Animal {
    func _start_ = define(name, breed) {
        inherit._start_(name) // Call parent constructor
        this.breed = breed
    }
    
    func speak = define() {
        output(this.name + " says: Meow!")
    }
}

let my_cat = Cat("Whiskers", "Persian")
my_cat.speak() // Outputs: Whiskers says: Meow!
```

### Special Methods
- `_start_`: Constructor (called when creating an instance)
- `_out_`: Custom string representation for `output()`
- `_len_`: Custom length calculation for `length()`
- `_plus_`: Custom addition behavior for `+` operator
- `_minus_`: Custom subtraction behavior for `-` operator
- `_times_`: Custom multiplication behavior for `*` operator
- `_divide_`: Custom division behavior for `/` operator
- `_equals_`: Custom equality behavior for `==` operator

---

## 7. Built-in Functions

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
-   `get(list, index)`: Gets an item from a list by index.
-   `set(list, index, value)`: Sets an item in a list by index.

### Map (Dictionary) Functions
-   `map()`: Creates a new empty map (or use `{}` literal).
-   `map_has(map, key)`: Returns `true` if the key exists in the map.
-   `map_keys(map)`: Returns a list of all keys in the map.
-   `map_values(map)`: Returns a list of all values in the map.
-   `map_delete(map, key)`: Removes a key-value pair from the map.
-   `map_get(map, key)`: Gets a value from a map by key.
-   `map_set(map, key, value)`: Sets a value in a map by key.

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

### JSoft (JSON) Functions (via `jsoft` package)
Import with `let jsoft = import("package:jsoft")`.
-   `jsoft.parse(string)`: Parses a JSON-formatted string into a Mrya map or list.
-   `jsoft.stringify(map_or_list, [indent])`: Converts a Mrya map or list into a JSON-formatted string. `indent` is an optional integer for pretty-printing.
-   `jsoft.load(path)`: Reads a JSON file from `path` and returns it as a Mrya map or list.
-   `jsoft.dump(path, data, [indent])`: Writes the Mrya `data` to a file at `path` as a JSON string. `indent` is an optional integer for pretty-printing.

### Math Functions (via `math` module)
Import with `let math = import("math")`.
-   `math.abs(number)`: Returns the absolute value of a number.
-   `math.round(number)`: Rounds a number to the nearest integer.
-   `math.ceil(number)`: Rounds a number up to the nearest integer.
-   `math.floor(number)`: Rounds a number down to the nearest integer.
-   `math.sqrt(number)`: Returns the square root of a number.
-   `math.random()`: Returns a random float between 0.0 and 1.0.
-   `math.randint(min, max)`: Returns a random integer between min and max (inclusive).
-   `math.sin(x)`: Returns the sine of x (x in radians).
-   `math.cos(x)`: Returns the cosine of x (x in radians).
-   `math.tan(x)`: Returns the tangent of x (x in radians).
-   `math.log(x)`: Returns the natural logarithm (base e) of x. x must be positive.
-   `math.exp(x)`: Returns e raised to the power of x.
-   `math.pow(base, exponent)`: Returns base raised to the power of exponent.

### Time Functions (via `time` module)
Import with `let time = import("time")`.
-   `time.sleep(seconds)`: Pauses execution for the specified number of seconds. Useful for creating delays in scripts or simulations.
-   `time.time()`: Returns the current Unix timestamp as a number (seconds since January 1, 1970). Useful for measuring elapsed time or generating unique identifiers.
-   `time.datetime()`: Returns the current date and time as a formatted string in the format "YYYY-MM-DD HH:MM:SS". Useful for logging or displaying timestamps.
-   `time.format_time(format_str)`: Formats the current time using a custom strftime format string. For example, `time.format_time("%Y-%m-%d %H:%M:%S")` returns the same as `time.datetime()`. Refer to Python's strftime documentation for format codes.
-   `time.get_time()`: Returns the current time as a string in 24-hour format "HH:MM:SS". Useful for displaying just the time component.
-   `time.get_date()`: Returns the current date as a string in "YYYY-MM-DD" format. Useful for displaying just the date component.
-   `time.format_datetime(format_str)`: Alias for `time.format_time()`. Formats the current date and time using a custom strftime format string.
-   `time.military_time()`: Returns the current time in 24-hour format "HH:MM:SS". Same as `time.get_time()`.
-   `time.twelve_hour_time()`: Returns the current time in 12-hour format with AM/PM indicator, e.g., "02:30:45 PM". Useful for user-friendly time displays.

### Error Functions
-   `raise(message)`: Raises a custom exception.
-   `assert(value, expected)`: Raises an exception if the values aren't equal.

### Window Functions (via `window` module)
Import with `let window = import("window")`.

-   `window.init()`: Initializes the window system.
-   `window.create_display(width, height)`: Creates a display window with the given dimensions.
-   `window.update(tick)`: Updates the window display and limits FPS to `tick`.
-   `window.get_events()`: Returns the list of current event objects.
-   `window.get_event_type(event)`: Returns the type of an event (e.g., `QUIT`, `KEYDOWN`).
-   `window.get_event_key(event)`: Returns the key code for a keyboard event.
-   `window.get_const(name)`: Gets a constant by name (e.g., `"K_w"`, `"QUIT"`).
-   `window.fill(r, g, b)`: Fills the display surface with a solid color.
-   `window.rect(x, y, sx, sy, r, g, b)`: Draws a rectangle at `(x, y)` with size `(sx, sy)` and color `(r, g, b)`.
-   `window.circle(x, y, radius, width, r, g, b)`: Draws a circle centered at `(x, y)` with color `(r, g, b)`.
-   `window.text(x, y, text, size, font, r, g, b)`: Renders text at `(x, y)` using the specified font, size, and color.
-   `window.update_key_states()`: Updates the current key state cache.
-   `window.get_key_state(key)`: Returns `true` if the specified key is currently pressed.
-   `window.load_image(path)`: Loads an image from the specified file path and returns an image object.
-   `window.set_background(image)`: Sets the background image for the display.
-   `window.create_sprite(image, x, y)`: Creates a sprite object from an image at the specified position.
-   `window.draw_sprite(sprite)`: Draws the specified sprite on the display.
-   `window.update_sprites()`: Updates all sprites in the sprite group.
-   `window.draw_all_sprites()`: Draws all sprites in the sprite group on the display.

### GUI Functions (via `gui` package)
Import with `let gui = import("package:gui")`.

#### Window Management
-   `gui.create_window(title, width, height)`: Creates a new GUI window with the specified title and dimensions, returning a window ID.
-   `gui.set_title(window, title)`: Sets the title of the specified window.
-   `gui.set_geometry(window, width, height)`: Changes the size of the specified window.
-   `gui.show_window(window)`: Makes the specified window visible.
-   `gui.hide_window(window)`: Hides the specified window.
-   `gui.close_window(window)`: Closes and destroys the specified window.

#### Widgets
-   `gui.add_button(window, text, x, y, width, height, command)`: Adds a button to the window at position (x, y) with the given dimensions and callback function.
-   `gui.add_label(window, text, x, y)`: Adds a text label to the window at position (x, y).
-   `gui.add_entry(window, x, y, width)`: Adds a text entry field to the window at position (x, y) with the specified width.
-   `gui.add_text(window, x, y, width, height)`: Adds a multi-line text widget to the window.
-   `gui.add_checkbox(window, text, x, y)`: Adds a checkbox with label to the window.
-   `gui.add_radio_button(window, text, x, y, group)`: Adds a radio button to the specified group.
-   `gui.add_listbox(window, x, y, width, height)`: Adds a listbox widget for displaying selectable items.
-   `gui.add_canvas(window, x, y, width, height)`: Adds a drawing canvas to the window.
-   `gui.add_menu(window, label)`: Adds a menu bar item to the window.
-   `gui.add_menu_item(menu, label, command)`: Adds an item to the specified menu with a callback.

#### Widget Manipulation
-   `gui.get_button_text(button)`: Retrieves the text of the specified button.
-   `gui.set_button_text(button, text)`: Sets the text of the specified button.
-   `gui.get_label_text(label)`: Retrieves the text of the specified label.
-   `gui.set_label_text(label, text)`: Sets the text of the specified label.
-   `gui.get_entry_text(entry)`: Retrieves the text from the specified entry field.
-   `gui.set_entry_text(entry, text)`: Sets the text in the specified entry field.
-   `gui.get_text_content(text_widget)`: Retrieves the content of the specified text widget.
-   `gui.set_text_content(text_widget, content)`: Sets the content of the specified text widget.
-   `gui.insert_text(text_widget, text)`: Inserts text at the end of the specified text widget.
-   `gui.delete_text(text_widget, start, end_pos)`: Deletes text from the specified text widget between start and end_pos indices.
-   `gui.get_checkbox_state(checkbox)`: Returns the checked state of the specified checkbox.
-   `gui.set_checkbox_state(checkbox, state)`: Sets the checked state of the specified checkbox.
-   `gui.get_selected_radio(group)`: Returns the selected value from the specified radio button group.
-   `gui.set_selected_radio(radio_button)`: Selects the specified radio button.
-   `gui.get_listbox_selection(listbox)`: Returns the currently selected item from the listbox.
-   `gui.set_listbox_items(listbox, items)`: Sets the list of items in the specified listbox.
-   `gui.add_listbox_item(listbox, item)`: Adds an item to the specified listbox.
-   `gui.remove_listbox_item(listbox, index)`: Removes the item at the specified index from the listbox.
-   `gui.clear_listbox(listbox)`: Removes all items from the specified listbox.

#### Canvas Drawing
-   `gui.draw_line(canvas, x1, y1, x2, y2, color, width)`: Draws a line on the canvas from (x1, y1) to (x2, y2).
-   `gui.draw_rectangle(canvas, x, y, width, height, fill_color, outline_color, outline_width)`: Draws a rectangle on the canvas.
-   `gui.draw_oval(canvas, x, y, width, height, fill_color, outline_color, outline_width)`: Draws an oval on the canvas.
-   `gui.draw_text(canvas, x, y, text, font, color)`: Draws text on the canvas at the specified position.
-   `gui.clear_canvas(canvas)`: Clears all drawings from the specified canvas.

#### Events and Dialogs
-   `gui.bind_event(widget, event, callback)`: Binds a callback function to a widget event.
-   `gui.message_box(title, message, type)`: Displays a message box dialog (types: "info", "warning", "error", "question", "yesno", "okcancel", "retrycancel").
-   `gui.input_dialog(title, prompt)`: Displays an input dialog and returns the user's input.
-   `gui.file_dialog(title, filetypes, save)`: Displays a file open/save dialog.
-   `gui.color_chooser(title, initial_color)`: Displays a color selection dialog.

#### Main Loop
-   `gui.start_main_loop()`: Starts the GUI event loop (blocks until the window is closed).
-   `gui.quit_main_loop()`: Quits the GUI event loop.

---

## 8. Error Handling

### Try/Catch/End Statements
Handle potential runtime errors gracefully. End statements are optional, but there must be a try and catch statement present.

```mrya
try {
    // Code that might fail
    let result = 10 / 0
    output("This will not be printed.")
} catch MryaRuntimeError {
    // Runs if a MryaRuntimeError occurs
    output("Caught a runtime error!")
} catch MryaTypeError {
    // Runs if a MryaTypeError occurs
    output("Caught a type error!")
} catch MryaRaisedError {
    // Runs if a MryaRaisedError occurs
    output("Caught a raised error!")
} catch {
    // Runs for any other Mrya error if the previous catches didn't match
    output("Caught some other error.")
} end {
    // This block always runs, error or not.
    output("Cleanup complete.")
}
```

### Specific Error Catching
You can catch specific error types by specifying the error class name after `catch`.

```mrya
try {
    let x as int = 25
    x = "twenty-five" // This will raise a MryaTypeError
} catch MryaTypeError {
    output("Successfully caught a MryaTypeError!")
}
```

---

## 9. Error Types

-   **ParseError**: This happens when your code has a syntax mistake (e.g., a missing parenthesis, an invalid statement). The parser cannot understand the code.
-   **MryaRuntimeError**: This happens while the code is running. Common causes include:
    -   Using a variable that hasn't been defined.
    -   Calling a function that doesn't exist.
    -   Trying to perform an operation on incompatible types (e.g., `"hello" / 5`).
    -   Division by zero.
    -   List index out of bounds.
    -   Map key not found.
-   **MryaTypeError**: This happens when you try to assign a value to a variable that violates its type annotation (e.g., assigning a string to a variable declared `as int`).
-   **MryaRaisedError**: This happens when the `raise()` function is called with a custom error message.
-   **ClassFunctionError**: This happens when a special class method is expected but not found.

---

## 10. Best Practices

-   **Use Clear Names**: Choose descriptive names for variables and functions (e.g., `user_age` instead of `ua`).
-   **Don't Repeat Yourself (DRY)**: If you find yourself writing the same code multiple times, put it in a function.
-   **Organize with Modules**: For larger projects, split your code into multiple `.mrya` files and use `import()` to connect them.
-   **Comment Your Code**: Use `//` to explain complex parts of your code for yourself and others.
-   **Use Type Annotations**: When you know the expected type, use `as type` to catch errors early.
-   **Handle Errors Gracefully**: Use try-catch blocks around code that might fail.
-   **Use Constants**: Use `let const` for values that shouldn't change.
-   **Test Your Code**: Use `assert()` to verify your code works as expected.

---

## Quick Reference

### Operators
- **Arithmetic**: `+`, `-`, `*`, `/`
- **Comparison**: `==`, `!=`, `<`, `<=`, `>`, `>=`
- **Logical**: `and`, `or`, `!` (not)
- **Assignment**: `=`, `+=`, `-=`, `*=`, `/=`

### Keywords
- **Declaration**: `let`, `let const`, `func`, `class`
- **Control Flow**: `if`, `else`, `while`, `for`, `break`, `continue`
- **Functions**: `return`, `define`
- **Classes**: `this`, `inherit`
- **Error Handling**: `try`, `catch`, `end`
- **Types**: `as`
- **Values**: `true`, `false`, `nil`

### Data Type Literals
- **Numbers**: `123`, `3.14`, `-42`
- **Strings**: `"hello"`, `#"Hello <name>!"#`
- **Booleans**: `true`, `false`
- **Nil**: `nil`
- **Lists**: `[1, 2, 3]`
- **Maps**: `{"key": "value", "num": 42}`

## 11. Unit Tests
Making unit tests are really useful. You can create a folder called `tests` in your workspace. Then you can throw mrya files in there, and then you can run `mrya_suite0.7` or `mrya_suite`. Keep in mind, while suiting output doesn't work. You can run them individually with `mrya <test\file.mrya>`.