<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Register</title>
</head>
<body>
<h1>Register</h1>
<% if (request.getAttribute("error") != null) { %>
    <p style="color:red"><%= request.getAttribute("error") %></p>
<% } %>
<form method="post" action="register">
    <label>Username:<input name="username" required /></label><br/>
    <label>Password:<input type="password" name="password" required /></label><br/>
    <button type="submit">Sign Up</button>
</form>
<p><a href="login">Back to login</a></p>
</body>
</html>
