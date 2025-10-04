# Mrya Programming Language

**Mrya** is a dynamic, object-oriented scripting language with a clean and approachable syntax. It's designed to be easy to learn for beginners while being powerful enough for building applications, from command-line tools to web servers.

## Features

-   **Object-Oriented Programming**: Full support for `class`, inheritance (`<`), and special methods (`_start_`, `_out_`).
-   **Built-in Web Framework**: Create web servers with an elegant decorator-based routing system (`%web.route`).
-   **HTML Templating**: Dynamically render HTML templates with the native `html` package.
-   **Rich Standard Library**: Includes modules for file system operations (`fs`), time, string manipulation, and more.
-   **Modern Syntax**: Features like H-Strings for formatting (`#"Hello <name>!"#`), lists (`[]`), and maps (`{}`).
-   **Robust Error Handling**: Gracefully manage errors with `try`/`catch`/`end` blocks.
-   **First-Class Functions**: Use functions as variables and enhance them with decorators (`%`).

## Documentation

The complete language syntax, features, and a list of all built-in functions are documented in **COMMANDS.md**.

For building web applications, see the **Web Package Guide**.

## Roadmap

This roadmap outlines the planned features and goals leading up to the Mrya 1.0.0 stable release.

### v0.7.0 - Quality of Life & Web Enhancements
-   **JSON Module**: A crucial native module with `json.parse()` and `json.stringify()` to make the web framework's API capabilities much more powerful.
-   **Multi-line Comments**: Add support for C-style block comments (`/* ... */`) for better code documentation.
-   **Dynamic URL Paths**: Enhance the web package to support routes with parameters, like `%web.route("/users/<id>")`.

### v0.8.0 - Advanced Control Flow & Tooling
-   **Switch Statement**: Implement a `switch` statement for cleaner, more efficient handling of multiple conditions, as an alternative to long `if-else if` chains.
-   **POST Request Body Parsing**: Automatically parse `application/x-www-form-urlencoded` and `application/json` request bodies in the web framework, making them available in the `request` object.

### v0.9.0 - The Big Polish
-   **Package Manager (Alpha)**: Introduce a basic command-line tool for fetching and managing third-party Mrya packages from Git repositories.
-   **Standard Library Expansion**: Add more utility functions to the `string`, `fs`, and `math` modules based on community feedback.
-   **Performance Profiling**: Analyze and optimize the interpreter for common bottlenecks before the stable release.

### v1.0.0 - Stable Release
-   **Bug Squashing**: Focus entirely on fixing any remaining bugs and ensuring maximum stability. No new features will be added.
-   **Complete Documentation Review**: Ensure `COMMANDS.md`, `web_package.md`, and all other documentation are complete, accurate, and ready for a stable release.
-   **Official Version 1 Release!**

## Versions

[Versions](https://github.com/mrya-lang/mrya/releases)
Check the [wiki](https://github.com/sharkblocks00/Mrya/wiki) for information on how to setup and use Mrya.

## License

Mrya is licensed under a custom [License](LICENSE.md). 

## Author

Created by SharkBlocks00  
GitHub: [https://github.com/sharkblocks00](https://github.com/sharkbocks00)  
Website: [https://sharkblocks00.com](https://sharkblocks00.com)
