<?php
session_start();
require "mongo.php";

if (!isset($_SESSION['user_id'])) {
    echo json_encode(["error" => "not_logged_in"]);
    exit;
}

$user = $usersCollection->findOne([
    "_id" => new MongoDB\BSON\ObjectId($_SESSION['user_id'])
]);

echo json_encode([
    "name" => $user->name,
    "email" => $user->email
]);
