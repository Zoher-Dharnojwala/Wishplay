<?php
session_start();
require "mongo.php";

if (!isset($_SESSION['user_id'])) {
    echo json_encode(["error" => "Not logged in"]);
    exit;
}

$user_id  = $_SESSION['user_id'];
$question = $_POST['question'];
$answer   = $_POST['answer'];
$category = $_POST['category'];
$audio    = $_POST['audio_path'];

$conversationsCollection->insertOne([
    "user_id"     => $user_id,
    "category"    => $category,
    "question"    => $question,
    "answer_text" => $answer,
    "audio_path"  => $audio,
    "timestamp"   => new MongoDB\BSON\UTCDateTime()
]);

echo json_encode(["status" => "saved"]);
?>
