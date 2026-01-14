<?php
require __DIR__ . '/vendor/autoload.php'; // If using Composer

$client = new MongoDB\Client("mongodb://localhost:27017");

$db = $client->mimir_db;

// Collections
$usersCollection = $db->users;
$conversationCollection = $db->conversations;
$patientSessionCollection = $db->patient_sessions;
$categoriesCollection = $db->categories;
?>
