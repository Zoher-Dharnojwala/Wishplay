<?php
require 'vendor/autoload.php';

$mongoClient = new MongoDB\Client("mongodb://localhost:27017");
$mongoDB = $mongoClient->wishplay;
$collection_history = $mongoDB->conversations;
?>
