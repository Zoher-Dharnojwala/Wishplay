<?php
session_start();
$user = $_SESSION["user_id"];

$db = new mysqli("localhost","root","","wishplay");

$opt = $_POST["store_history"];
$db->query("UPDATE users SET store_history='$opt' WHERE id='$user'");

echo "OK";
?>
