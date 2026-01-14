<?php
session_start();
$user = $_SESSION["user_id"];

$db = new mysqli("localhost","root","","wishplay");

$db->query("DELETE FROM users WHERE id='$user'");
session_destroy();

echo json_encode(["status"=>"success"]);
?>
