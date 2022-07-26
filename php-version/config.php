<?php

require 'libs/Medoo.php';
     
use Medoo\Medoo;

/**
 * Database config, supports any Medoo supported database
 */
$database = new Medoo([
    'database_type' => 'mysql',
    'database_name' => 'sqlpixels',
    'server' => 'db',
    'username' => 'admin',
    'password' => 'admin',
 
]);

/**
 * Row in the counters table, one per counter
 */
define('COUNTER_NAME', 'example');

?>