<?php
$file_name = "ipv4_".$_GET["hostname"].".txt";
$file_handler = fopen($file_name, "w");
$logdetails = $_SERVER['REMOTE_ADDR'];
fwrite($file_handler, $logdetails);
fclose($file_handler);
?>

<html><body>This should be accessed only by an LBR.</body></html>
