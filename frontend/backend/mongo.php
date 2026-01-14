<?php
require __DIR__ . "/vendor/autoload.php";  // Composer autoload

$client = new MongoDB\Client("mongodb://localhost:27017");

// Select the database and collections
$db = $client->mimir_db;

// USERS collection (for login + profile)
$users = $db->users;

// HISTORY collection (AI conversation answers)
$history = $db->history;

// ANSWERS / AUDIO (optional)
$answers = $db->answers;
?>
