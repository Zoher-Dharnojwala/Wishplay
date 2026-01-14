<?php
header("Content-Type: application/json");
error_reporting(E_ALL);
ini_set("display_errors", 1);

// FIXED: correct DB config file path
require_once "../config.php";

// Read POST JSON body
$raw = file_get_contents("php://input");
$data = json_decode($raw, true);

// Validate input
if (!$data || empty($data["username"]) || empty($data["password"])) {
    echo json_encode(["status" => "error", "message" => "Missing fields"]);
    exit;
}

$username = $data["username"];
$password = $data["password"];

// Query DB
$stmt = $conn->prepare("
    SELECT id, username, email, password_hash
    FROM users 
    WHERE username = ? OR email = ?
");

$stmt->bind_param("ss", $username, $username);
$stmt->execute();
$result = $stmt->get_result();

// User not found
if ($result->num_rows === 0) {
    echo json_encode(["status" => "error", "message" => "User not found"]);
    exit;
}

$user = $result->fetch_assoc();

// Verify password
if (!password_verify($password, $user["password_hash"])) {
    echo json_encode(["status" => "error", "message" => "Incorrect password"]);
    exit;
}

// Success
session_start();
$_SESSION["user_id"] = $user["id"];
$_SESSION["username"] = $user["username"];
$_SESSION["email"] = $user["email"];

echo json_encode([
    "status" => "success",
    "message" => "Login successful",
    "user_id" => $user["id"]
]);
exit;

?>
