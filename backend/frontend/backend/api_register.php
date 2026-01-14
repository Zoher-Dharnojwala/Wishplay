<?php include "../components/navbar.php"; ?>

<h2>Register</h2>

<form action="../backend/auth.php" method="POST">
    <input type="text" name="name" placeholder="Full Name" required><br><br>
    <input type="email" name="email" placeholder="Email" required><br><br>
    <input type="password" name="password" placeholder="Password" required><br><br>
    <button type="submit" name="register">Register</button>
</form>
<br>
<a href="login.php">Already have an account?</a>
