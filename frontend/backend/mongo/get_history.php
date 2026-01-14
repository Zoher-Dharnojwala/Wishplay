<?php
require "mongo_conn.php";

$patient_id = $_GET['patient_id'];

$result = $collection_history->find(["patient_id" => $patient_id]);

echo json_encode(iterator_to_array($result));
?>
