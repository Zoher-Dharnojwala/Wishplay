<?php
session_start();
require_once "db.php";

// User must be logged in
if (!isset($_SESSION["user_id"])) {
    echo json_encode(["status" => "error", "message" => "Not logged in"]);
    exit;
}

$user_id = $_SESSION["user_id"];

if (!isset($_FILES["photo"])) {
    echo json_encode(["status" => "error", "message" => "No file uploaded"]);
    exit;
}

$file = $_FILES["photo"];
$ext = strtolower(pathinfo($file["name"], PATHINFO_EXTENSION));

$allowed = ["jpg", "jpeg", "png", "gif"];

if (!in_array($ext, $allowed)) {
    echo json_encode(["status" => "error", "message" => "Invalid file type"]);
    exit;
}

$filename = "user_" . $user_id . "_" . time() . "." . $ext;
$target_dir = "../../uploads/profile_photos/";
$target_file = $target_dir . $filename;

// Ensure folder exists
if (!file_exists($target_dir)) {
    mkdir($target_dir, 0777, true);
}

if (move_uploaded_file($file["tmp_name"], $target_file)) {

    // Save path in DB
    $stmt = $conn->prepare("UPDATE users SET photo=? WHERE id=?");
    $relative_path = "uploads/profile_photos/" . $filename;
    $stmt->bind_param("si", $relative_path, $user_id);
    $stmt->execute();

    echo json_encode([
        "status" => "success",
        "path" => $relative_path
    ]);
} else {
    echo json_encode(["status" => "error", "message" => "File upload failed"]);
}
?>
