<?php
header("Content-Type: application/json");
session_start();
require_once "../config.php";

if (!isset($_SESSION["user_id"])) {
    echo json_encode(["status" => "error", "message" => "Not logged in"]);
    exit;
}

$data = json_decode(file_get_contents("php://input"), true);

$username   = $data["username"];
$first_name = $data["first_name"];
$last_name  = $data["last_name"];
$email      = $data["email"];
$phone      = $data["phone"];
$gender     = $data["gender"];

$stmt = $conn->prepare("
    UPDATE users 
    SET username=?, first_name=?, last_name=?, email=?, phone=?, gender=?
    WHERE id=?
");

$stmt->bind_param("ssssssi",
    $username,
    $first_name,
    $last_name,
    $email,
    $phone,
    $gender,
    $_SESSION["user_id"]
);

if ($stmt->execute()) {
    echo json_encode(["status" => "success"]);
} else {
    echo json_encode(["status" => "error", "message" => "Update failed"]);
}
