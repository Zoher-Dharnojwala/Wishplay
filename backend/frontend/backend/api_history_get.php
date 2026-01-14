<?php
session_start();
require "mongo.php";

if (!isset($_SESSION['user_id'])) exit;

$cursor = $conversationsCollection->find(
    ["user_id" => $_SESSION['user_id']],
    ["sort" => ["timestamp" => -1]]
);

$result = [];
foreach ($cursor as $doc) {
    $result[] = [
        "category" => $doc->category,
        "question" => $doc->question,
        "answer_text" => $doc->answer_text
    ];
}

echo json_encode($result);
