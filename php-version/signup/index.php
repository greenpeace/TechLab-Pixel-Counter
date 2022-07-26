<?php

require_once('../config.php');

/**
 * Increase the value in the database
 */
$database->update("counters", [
	"counter_value[+]" => 1,
], [
    "counter_name" => COUNTER_NAME, 
]);

/**
 * Output image to be used as pixel
 */
header('Content-Type: image/png');
echo base64_decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAQMAAAAl21bKAAAAA1BMVEUAAACnej3aAAAAAXRSTlMAQObYZgAAAApJREFUCNdjYAAAAAIAAeIhvDMAAAAASUVORK5CYII=');

?>