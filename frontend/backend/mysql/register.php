<?php
header("Content-Type: application/json");
require_once "../config.php";

$data = json_decode(file_get_contents("php://input"), true);

$username = $data["username"];
$first = $data["first_name"];
$last = $data["last_name"];
$email = $data["email"];
$password = $data["password"];
$phone = $data["phone"];
$gender = $data["gender"];

if (!$username || !$email || !$password) {
    echo json_encode(["status" => "error", "message" => "Missing required fields"]);
    exit;
}

// Check for duplicate email or username
$check = $conn->prepare("SELECT id FROM users WHERE email=? OR username=?");
$check->bind_param("ss", $email, $username);
$check->execute();
$check->store_result();

if ($check->num_rows > 0) {
    echo json_encode(["status" => "error", "message" => "Email or username already exists"]);
    exit;
}

$hashed = password_hash($password, PASSWORD_BCRYPT);

$stmt = $conn->prepare("
    INSERT INTO users (username, first_name, last_name, email, password_hash, phone, gender, oauth_provider)
    VALUES (?, ?, ?, ?, ?, ?, ?, 'local')
");

$stmt->bind_param("sssssss",
    $username,
    $first,
    $last,
    $email,
    $hashed,
    $phone,
    $gender
);

if ($stmt->execute()) {
    echo json_encode(["status" => "success"]);
} else {
    echo json_encode(["status" => "error", "message" => "Registration failed"]);
}

?>
