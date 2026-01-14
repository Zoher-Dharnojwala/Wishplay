<?php
session_start();
$user = $_SESSION["user_id"];

$db = new mysqli("localhost","root","","wishplay");

$old = $_POST["old_pass"];
$new = $_POST["new_pass"];

$res = $db->query("SELECT password FROM users WHERE id='$user'");
$row = $res->fetch_assoc();

if (!password_verify($old, $row["password"])) {
    echo json_encode(["status"=>"error", "message"=>"Incorrect old password"]);
    exit;
}

$hashed = password_hash($new, PASSWORD_DEFAULT);
$db->query("UPDATE users SET password='$hashed' WHERE id='$user'");

echo json_encode(["status"=>"success"]);
?>
