<?php
require "mongo_conn.php";

$data = json_decode(file_get_contents('php://input'), true);

$collection_history->insertOne($data);

echo json_encode(["status" => "saved"]);
?>
