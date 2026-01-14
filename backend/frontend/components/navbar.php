<?php session_start(); ?>

<nav style="padding: 10px; background:#f4f4f4; margin-bottom:20px;">
    <a href="/frontend/pages/home.php" style="margin-right:20px;">HOME</a>
    <a href="/frontend/pages/life_questions.php" style="margin-right:20px;">LIFE QUESTIONS</a>
    <a href="/frontend/pages/profile.php" style="margin-right:20px;">PROFILE</a>

    <?php if (isset($_SESSION['user_id'])): ?>
        <a href="/frontend/backend/logout.php">SIGN OUT</a>
    <?php else: ?>
        <a href="/frontend/pages/login.php">LOGIN</a>
    <?php endif; ?>
</nav>
