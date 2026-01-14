<?php
header("Content-Type: application/json");
require_once "../config.php";

$data = json_decode(file_get_contents("php://input"), true);

$user_id = $data["user_id"];
$username = $data["username"];
$first = $data["first_name"];
$last = $data["last_name"];
$email = $data["email"];
$phone = $data["phone"];
$gender = $data["gender"];

$stmt = $conn->prepare("
    UPDATE users 
    SET username=?, first_name=?, last_name=?, email=?, phone=?, gender=?
    WHERE id=?
");

$stmt->bind_param("ssssssi",
    $username,
    $first,
    $last,
    $email,
    $phone,
    $gender,
    $user_id
);

if ($stmt->execute()) {
    echo json_encode(["status" => "success"]);
} else {
    echo json_encode(["status" => "error", "message" => "Profile update failed"]);
}
?>
