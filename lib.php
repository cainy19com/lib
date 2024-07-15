<?php
define("PLZ_LOGIN",  "Please login first");

define("INVALID_EMAIL",    "Invalid email");
define("INVALID_PASSWORD", "Invalid password");
define("INVALID_CODE",     "Invalid code");

define("WRONG_PASSWORD", "Wrong password");
define("WRONG_CODE",     "Wrong code");

define("NO_USER",    "No user found");
define("NO_RECORD",  "No record found");
define("NO_SERVICE", "Service unavailable, please try again later");

define("DB_CONN_FAILED", "DB connection failed");
define("QUERY_FAILED",   "Query failed");
define("UPDATE_WITH_SAME_VALUE", "Trying to update with same value");


function res(int $code, string $msg = "", string $data = "") {
    $arr = array();

    $arr["code"] = $code;
    $arr["msg"] = $msg;
    $arr["data"] = $data;

    echo json_encode($arr);
    exit();
}


function conn($db, $pass) {
    $conn = new mysqli("localhost", "root", $pass, $db);
    $conn->connect_error and res(1, DB_CONN_FAILED);
    return $conn;
}


function is_logged_in() {
    session_start();
    return $_SESSION["id"] ? true : false;
}


function echo_pre($str) {
    echo "<pre>" . $str . "</pre>";
}


function get_post() {
  $json_str = file_get_contents("php://input");
  $json_obj = json_decode($json_str);
  $json_arr = json_decode($json_str, true);
  $json_arr = array_map("trim", $json_arr);
  return $json_arr;
}

