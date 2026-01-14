<?php
session_start();

$raw = file_get_contents("php://input");
$data = json_decode($raw, true);

$_SESSION["google_user"] = [
    "google_id"   => $data["uid"] ?? $data["localId"] ?? $data["id"] ?? null,
    "email"       => $data["email"] ?? "",
    "first_name"  => explode(" ", $data["displayName"] ?? "")[0] ?? "",
    "last_name"   => explode(" ", $data["displayName"] ?? "")[1] ?? "",
    "photo"       => $data["photoURL"] ?? ""
];

echo "OK";
