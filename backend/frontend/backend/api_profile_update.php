<?php
session_start();
require "mongo.php";

if (!isset($_SESSION['user_id'])) exit;

$name = $_POST['name'];
$pass = $_POST['password'];

$update = ["name" => $name];

if ($pass !== "") {
    $update["password_hash"] = password_hash($pass, PASSWORD_BCRYPT);
}

$usersCollection->updateOne(
    ["_id" => new MongoDB\BSON\ObjectId($_SESSION['user_id'])],
    ['$set' => $update]
);
