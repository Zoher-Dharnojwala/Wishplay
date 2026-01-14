<?php include "../components/navbar.php"; ?>

<h2>Login</h2>

<form action="../backend/auth.php" method="POST">
    <input type="email" name="email" placeholder="Email" required><br><br>
    <input type="password" name="password" placeholder="Password" required><br><br>
    <button type="submit" name="login">Login</button>
</form>
<br>
<a href="register.php">Create an account</a>
