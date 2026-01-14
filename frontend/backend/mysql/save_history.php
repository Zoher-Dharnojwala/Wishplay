<?php
session_start();
require "db.php";

if (!isset($_SESSION["user_id"])) exit;

$user_id  = $_SESSION["user_id"];
$speaker  = $_POST["speaker"];
$text     = $_POST["text"];
$category = $_POST["category"];

if ($speaker === "AI Afi") {
    $question = $text;
    $answer   = null;
} else {
    $question = null;
    $answer   = $text;
}

$stmt = $conn->prepare("
    INSERT INTO conversation_history (user_id, category, question, answer_text)
    VALUES (?, ?, ?, ?)
");
$stmt->bind_param("isss", $user_id, $category, $question, $answer);
$stmt->execute();

echo "saved";
?>
