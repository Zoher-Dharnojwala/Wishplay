<?php
session_start();

if (!isset($_SESSION["user_id"])) {
    echo json_encode(["status" => "error", "message" => "Not logged in"]);
    exit;
}

$userId = $_SESSION["user_id"];
$targetDir = "../../assets/images/profile_photos/";

if (!is_dir($targetDir)) {
    mkdir($targetDir, 0777, true);
}

if (!isset($_FILES["profile_photo"])) {
    echo json_encode(["status" => "error", "message" => "No file uploaded"]);
    exit;
}

$file = $_FILES["profile_photo"];
$allowed = ["jpg", "jpeg", "png", "webp"];
$ext = strtolower(pathinfo($file["name"], PATHINFO_EXTENSION));

if (!in_array($ext, $allowed)) {
    echo json_encode(["status" => "error", "message" => "Invalid file type"]);
    exit;
}

$filename = "user_" . $userId . "." . $ext;
$targetFile = $targetDir . $filename;

if (move_uploaded_file($file["tmp_name"], $targetFile)) {

    require "db.php";
    $stmt = $conn->prepare("UPDATE users SET photo=? WHERE id=?");
    $stmt->bind_param("si", $filename, $userId);
    $stmt->execute();

    echo json_encode([
        "status" => "success",
        "path" => "assets/images/profile_photos/$filename"
    ]);
} 
else {
    echo json_encode(["status" => "error", "message" => "Upload failed"]);
}
?>
