<?php
header("Content-Type: application/json");
session_start();
require_once "../config.php";

if (!isset($_SESSION["user_id"])) {
    echo json_encode(["status" => "error", "message" => "Not logged in"]);
    exit;
}

$user_id = $_SESSION["user_id"];

$stmt = $conn->prepare("
    SELECT 
        username, 
        first_name, 
        last_name, 
        email,
        phone,
        gender,
        photo
    FROM users 
    WHERE id = ?
");

$stmt->bind_param("i", $user_id);
$stmt->execute();
$res = $stmt->get_result();
$user = $res->fetch_assoc();

echo json_encode([
    "status" => "success",
    "user" => $user
]);
