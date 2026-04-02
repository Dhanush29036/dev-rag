<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Login</title>
</head>
<body>
<h1>Login</h1>
<% if (request.getAttribute("error") != null) { %>
    <p style="color:red"><%= request.getAttribute("error") %></p>
<% } %>
<form method="post" action="login">
    <label>Username:<input name="username" required /></label><br/>
    <label>Password:<input type="password" name="password" required /></label><br/>
    <button type="submit">Sign In</button>
</form>
<p><a href="register">Register</a></p>
</body>
</html>
