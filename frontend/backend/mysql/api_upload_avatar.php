<?php
session_start();
$user = $_SESSION["user_id"];

$targetDir = "../../uploads/";
if(!file_exists($targetDir)) mkdir($targetDir, 0777, true);

$fileName = "avatar_" . $user . ".png";
$targetFile = $targetDir . $fileName;

if(move_uploaded_file($_FILES["avatar"]["tmp_name"], $targetFile)){

    $db = new mysqli("localhost","root","","wishplay");
    $path = "uploads/" . $fileName;

    $db->query("UPDATE users SET avatar='$path' WHERE id='$user'");

    echo json_encode(["status"=>"success","path"=>$path]);
} else {
    echo json_encode(["status"=>"error"]);
}
?>
