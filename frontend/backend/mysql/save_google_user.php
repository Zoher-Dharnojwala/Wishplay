<?php
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

require_once "../config.php";

$g = $_SESSION["google_user"] ?? null;

if (!$g) {
    die("No Google session data.");
}

$google_id  = $g["google_id"];
$email      = $g["email"];
$first      = $g["first_name"];
$last       = $g["last_name"];
$photo      = $g["photo"];

// FIRST: check if this exact Google ID exists
$stmt = $conn->prepare("SELECT id FROM users WHERE google_id=?");
$stmt->bind_param("s", $google_id);
$stmt->execute();
$res = $stmt->get_result();

if ($res->num_rows > 0) {
    // User exists → update basic info
    $user = $res->fetch_assoc();
    $uid  = $user["id"];

    $stmt = $conn->prepare("
        UPDATE users SET first_name=?, last_name=?, email=?, photo=?
        WHERE id=?
    ");
    $stmt->bind_param("ssssi", $first, $last, $email, $photo, $uid);
    $stmt->execute();

    $_SESSION["user_id"] = $uid;
    return;
}

// SECOND: check if email exists → link Google ID to existing user
$stmt = $conn->prepare("SELECT id FROM users WHERE email=?");
$stmt->bind_param("s", $email);
$stmt->execute();
$res = $stmt->get_result();

if ($res->num_rows > 0) {
    $user = $res->fetch_assoc();
    $uid  = $user["id"];

    $stmt = $conn->prepare("UPDATE users SET google_id=?, photo=? WHERE id=?");
    $stmt->bind_param("ssi", $google_id, $photo, $uid);
    $stmt->execute();

    $_SESSION["user_id"] = $uid;
    return;
}

// THIRD: create new account
$stmt = $conn->prepare("
    INSERT INTO users (google_id, first_name, last_name, email, photo)
    VALUES (?, ?, ?, ?, ?)
");
$stmt->bind_param("sssss", $google_id, $first, $last, $email, $photo);
$stmt->execute();

$_SESSION["user_id"] = $conn->insert_id;
