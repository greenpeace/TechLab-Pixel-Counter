<?php

require_once('../config.php');

/**
 * Read the database
 */
$datas = $database->select("counters", "*", [
    'counter_name' => COUNTER_NAME
]);
$counter_value = $datas[0]['counter_value'] ?? null;

/**
 * Output the counter
 */

$output = array("signups" => $counter_value );

$output = json_encode( $output);
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: ' . '*');
echo($output);

?>