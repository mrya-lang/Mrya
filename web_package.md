# Mrya Web Package Guide

Welcome to the official guide for the Mrya Web Package. This document provides a comprehensive overview of the `web` and `html` packages, which allow you to build powerful, route-based web applications and APIs using an elegant decorator-based syntax.

## Table of Contents
1.  Introduction
2.  Getting Started: Your First Server
3.  Configuration (`web.config`)
4.  Routing with Decorators (`%web.route`)
5.  Rendering HTML Templates (`html.render`)
6.  Serving Static Files
7.  Accessing Request Data
8.  Building a JSON API
9.  Full Example: A Complete Web App
10. Best Practices & Do's and Don'ts

---

## 1. Introduction

The Mrya Web Package is a set of native packages that provide a high-level framework for web development. It allows you to build everything from simple APIs to data-driven websites with minimal boilerplate.

---

## 2. Getting Started: Your First Server

Creating a web server is simple. You import the `web` package, define functions for your pages, and decorate them with `%web.route`.

```mrya
// main.mrya

// 1. Import the web package
let web = import("package:web")

// 2. Define a function for the homepage
%web.route("/")
func home_page = define() {
    return "<h1>Hello, World!</h1>"
}

// 3. Run the server
output("Server starting on http://127.0.0.1:8000")
web.run("127.0.0.1", 8000)
```

---

## 3. Configuration (`web.config`)

You can configure the server's behavior by setting properties on the `web.config` map **before** calling `web.run()`.

-   **`DEBUG`**: (Boolean) If `true`, the server will auto-reload when it detects changes to `.mrya`, `.html`, or other web files. Highly recommended for development.
-   **`ALLOWED_IPS`**: (List of Strings) If set, the server will only accept connections from these IP addresses.
-   **`STATIC_FOLDER`**: (String) The name of the local directory containing your static files (e.g., `"public"`).
-   **`STATIC_URL_PATH`**: (String) The URL prefix to serve static files from (e.g., `"/static"`).

**Example Configuration:**
```mrya
web.config.DEBUG = true
web.config.ALLOWED_IPS = ["127.0.0.1"]
web.config.STATIC_FOLDER = "static_files"
web.config.STATIC_URL_PATH = "/assets"
```

---

## 4. Routing with Decorators (`%web.route`)

The core of the framework is the `%web.route` decorator. It links a URL path to a Mrya function. When a user visits that URL, the decorated function is executed, and its return value is sent to the browser.

```mrya
%web.route("/about")
func about_page = define() {
    return "<h1>About Us</h1><p>This is a web server written in Mrya.</p>"
}

%web.route("/contact")
func contact_page = define() {
    return "<h1>Contact</h1><p>Email us at contact%example.com</p>"
}
```

---

## 5. Rendering HTML Templates (`html.render`)

For more complex pages, you should separate your HTML into template files. The `html` package provides a simple and powerful templating engine. Placeholders in your HTML are identified by `[$ variable_name $]`.

### Importing the Package
`let html = import("package:html")`

### `html.render(template_path, context)`
-   **`template_path`**: The path to your HTML template file (e.g., `"templates/profile.html"`).
-   **`context`**: A Map where keys match the placeholder names in your template.

**Example Template (`templates/profile.html`):**
```html
<h1>Hello, [$ user_name $]!</h1>
<p>Your user ID is [$ user_id $].</p>
```

**Using it in a Route:**
```mrya
%web.route("/profile")
func profile_page = define() {
    let user_data = {
        "user_name": "Alex",
        "user_id": 12345
    }
    // The rendered HTML is returned to the browser
    return html.render("templates/profile.html", user_data)
}
```

---

## 6. Serving Static Files

The framework can automatically serve static files like CSS, JavaScript, and images. Simply configure the `STATIC_FOLDER` and `STATIC_URL_PATH` properties.

**Example:**
If `web.config.STATIC_FOLDER = "public"` and `web.config.STATIC_URL_PATH = "/static"`, a request to `http://.../static/style.css` will serve the file located at `public/style.css`.

---

## 7. Accessing Request Data

For dynamic routes, APIs, or forms, you need access to the incoming request. If you define your route handler with a parameter, the framework will automatically inject a `request` map.

```mrya
%web.route("/search")
func search_handler = define(request) {
    let query = request.query["q"] // Access query params from /search?q=...
    return #"You searched for: <query>"#
}
```

The `request` map contains:
-   **`path`**: The requested URL path.
-   **`method`**: The HTTP method (`"GET"`, `"POST"`, etc.).
-   **`query`**: A map of query string parameters.
-   **`headers`**: A map of request headers.
-   **`body`**: The raw request body, useful for handling POST data.

---

## 8. Building a JSON API

To build an API, return a map from your route handler. The framework will automatically convert it to a JSON string and set the correct `Content-Type` header.

```mrya
%web.route("/api/user")
func user_api = define() {
    // This map will be automatically sent as JSON
    return {
        "id": 123,
        "name": "Alex",
        "email": "alex%example.com"
    }
}
```

---

## 9. Full Example: A Complete Web App

**Directory Structure:**
```
/
|- server.mrya
|- views/
|  |- index.html
|- public/
   |- style.css
```

**`server.mrya`:**

```mrya
let server = import("http_server")
let renderer = import("html_renderer")

func main_handler = define(request) {
    let path = request.path
    let method = request.method

    // Route for the HTML homepage
    if (path == "/" and method == "GET") {
        let context = { "title": "Homepage" }
        return { "status": 200, "body": renderer.render("views/index.html", context) }
    } 
    // Route for the CSS file
    else if (path == "/style.css") {
        return { "status": 200, "body": fetch_raw("public/style.css") }
    } 
    // Route for the JSON API
    else if (path == "/api/status" and method == "GET") {
        let api_response = #"{"status": "ok", "message": "Server is running!"}"#
        return {
            "status": 200,
            "body": api_response,
            "headers": { "Content-Type": "application/json" }
        }
    } else {
        return { "status": 404, "body": "Not Found" }
    }
}

output("Server starting on http://127.0.0.1:8080")
server.run(main_handler, "127.0.0.1", 8080, { "DEBUG": true })
```

**`views/index.html`:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>[$ title $]</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <h1>Welcome to the Mrya [$ title $]!</h1>
    <p>Check the <a href="/api/status">API status</a>.</p>
</body>
</html>
```

**`public/style.css`:**

```css
body {
    font-family: sans-serif;
    background-color: #f0f0f0;
}
```

---

## 7. Best Practices & Do's and Don'ts

-   **Do** enable `DEBUG: true` during development for a much faster workflow.
-   **Do** organize your files. Keep templates in a `views/` directory and static assets (CSS, JS) in a `public/` directory.
-   **Do** create a router function if your handler gets complex. This function can call other functions based on the request path.
-   **Don't** put sensitive information directly in your code. In the future, Mrya may support environment variables for this.
-   **Don't** perform long-running, blocking operations inside your handler, as it will make the server unresponsive to other requests.
-   **Don't** forget to handle the "else" case in your handler to return a `404 Not Found` error for unknown paths.
```