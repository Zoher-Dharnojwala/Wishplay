<?php
session_start();
require "mongo.php";

// REGISTER
if (isset($_POST['register'])) {

    $name  = $_POST['name'];
    $email = $_POST['email'];
    $pass  = $_POST['password'];

    // Does user exist?
    $existing = $usersCollection->findOne(['email' => $email]);
    if ($existing) {
        echo "Email already exists";
        exit;
    }

    $usersCollection->insertOne([
        "name" => $name,
        "email" => $email,
        "password_hash" => password_hash($pass, PASSWORD_BCRYPT),
        "created_at" => new MongoDB\BSON\UTCDateTime()
    ]);

    header("Location: ../pages/login.php");
    exit;
}


// LOGIN
if (isset($_POST['login'])) {

    $email = $_POST['email'];
    $pass  = $_POST['password'];

    $user = $usersCollection->findOne(['email' => $email]);

    if (!$user) {
        echo "User not found";
        exit;
    }

    if (!password_verify($pass, $user->password_hash)) {
        echo "Wrong password";
        exit;
    }

    $_SESSION['user_id'] = (string)$user->_id;
    $_SESSION['name']    = $user->name;

    header("Location: ../pages/home.php");
    exit;
}
?>
