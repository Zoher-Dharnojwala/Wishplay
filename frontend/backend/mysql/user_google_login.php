<?php
session_start();
require_once "../config.php";
require_once "save_google_user.php";

if (!isset($_SESSION["user_id"])) {
    die("Google login failed (no user ID).");
}

$user_id = $_SESSION["user_id"];

?>
<script>
localStorage.setItem("user_id", "<?php echo $_SESSION['user_id']; ?>");
window.location.href = "/wishplay/profile.html";
</script>

