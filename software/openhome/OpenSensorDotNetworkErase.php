<?
$apiKey= "DqApznQuoaayVuVtIunc8oM1UXCPDMNiQdf+eqjvLmo=";

//find all datastreamIds

$data          = array();
$sensorTypes   = array();
$sensornodeIds = array();

$httpRequest  = "GET /rest/resources/datastreams?search=OpenWSN HTTP/1.1\n";
$httpRequest .= "Host: sensor.network.com\n";
$httpRequest .= "X-SensorNetworkAPIKey: ".$apiKey."\n";
$httpRequest .= "Accept: text/plain\n";
$httpRequest .= "\n";

$socket = socket_create(AF_INET, SOCK_STREAM, 0);
socket_connect($socket, 'sensor.network.com', 80) or die("<br/>The sensor.network.com servers are down :(");
socket_write($socket,$httpRequest) or die ("Could not write to socket.");
$httpReply = socket_read($socket,2048) or die ("Could not read from socket.");
socket_close($socket);

$httpReply = explode("\r\n\r\n",$httpReply);
$httpReply = $httpReply[1];
$httpReply = explode("\r\n",$httpReply);
$lines     = explode("\n",$httpReply[1]);

for ($counter=0;$counter<sizeof($lines)-1;$counter++) {
   $line = $lines[$counter];
   //sensornodeId
   $sensornodeId = explode(",",$line);
   $sensornodeId = $sensornodeId[0];
   $sensornodeId = explode("_",$sensornodeId);
   $sensornodeId = $sensornodeId[2];
   //datastreamId
   $datastreamId = explode(", ",$line);
   $datastreamId = $datastreamId[1];
   //datastreamName
   $datastreamName = explode(",",$line);
   $datastreamName = $datastreamName[0];
   $datastreamName = explode("_",$datastreamName);
   $datastreamName = $datastreamName[3];
   //fill in sensornodeIds
   if (in_array($sensornodeId,$sensornodeIds)==FALSE) {
      array_push($sensornodeIds,$sensornodeId);
   }
   //fill in sensorTypes
   if (in_array($datastreamName,$sensorTypes)==FALSE) {
      array_push($sensorTypes,$datastreamName);
   }
   //fill in data
   if (array_key_exists($sensornodeId,$data)==FALSE) {
      $data[$sensornodeId]=array();
   }
   $data[$sensornodeId][$datastreamName] = $datastreamId;
}

/*echo "<br/>sensornodeIds:<br/>";
print_r($sensornodeIds);
echo "<br/>sensorTypes:<br/>";
print_r($sensorTypes);
echo "<br/>data:<br/>";
print_r($data);*/

//erase the datastreamIds provided in the $_GET url, if any

$sensornodeIdToErase   = $_GET['sensornodeIdToErase'];

if ($sensornodeIdToErase!='') {
   echo "Erasing datastreams associated with mote ".$sensornodeIdToErase."...<br/>";
   //finding datastreamIdsToErase
   foreach (array_keys($data) as $temp) {
      if ($temp==$sensornodeIdToErase) {
         $datastreamIdsToErase = array_values($data[$sensornodeIdToErase]);
      }
   }
   //erasing one by one
   foreach ($datastreamIdsToErase as $temp) {
      echo "<br/>".$temp."<br/>";

      $httpRequest  = "DELETE /rest/resources/datastreams/".$temp."\n";
      $httpRequest .= "Host: sensor.network.com\n";
      $httpRequest .= "X-SensorNetworkAPIKey: ".$apiKey."\n";
      $httpRequest .= "Accept: text/plain\n";
      $httpRequest .= "\n";

      //echo "httpRequest:<br/>".$httpRequest;

      $socket = socket_create(AF_INET, SOCK_STREAM, 0);
      socket_connect($socket, 'sensor.network.com', 80) or die("<br/>The sensor.network.com servers are down :(");
      socket_write($socket,$httpRequest) or die ("Could not write to socket.");
      $httpReply = socket_read($socket,1024);

      //echo "<br/>httpReply:<br/>".$httpReply;

      socket_close($socket);
   }
   echo "<br/>Done.<br/>";
}
?>

<html>
   <head>
      <title>OpenSensorDotNetwork<title>
      <script type='text/javascript' src='http://www.google.com/jsapi'></script>
   </head>
   <body>

   <form method="get">
         <? foreach ($sensornodeIds as $temp) {
            if ($temp!=$sensornodeIdToErase) {
               echo "<br/><input type=\"radio\" name=\"sensornodeIdToErase\" value=\"".$temp."\">".$temp."\n";
            }
         }?>
      <br/><input type="submit" text="erase">
   </form>

   </body>
</html>

