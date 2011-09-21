<?
$data          = array();
$sensorTypes   = array();
$sensornodeIds = array();

$apiKey= "DqApznQuoaayVuVtIunc8oM1UXCPDMNiQdf+eqjvLmo=";
$httpHeader  = "GET /rest/resources/datastreams?search=OpenWSN HTTP/1.1\n";
$httpHeader .= "Host: incoherent.sunlabs.com\n";
$httpHeader .= "X-SensorNetworkAPIKey: ".$apiKey."\n";
$httpHeader .= "Accept: text/plain\n";
$httpHeader .= "\n";

$socket = socket_create(AF_INET, SOCK_STREAM, 0);
socket_connect($socket, 'incoherent.sunlabs.com', 80) or die("<br/>The incoherent.sunlabs.com server are down :(");
socket_write($socket,$httpHeader) or die ("Could not write to socket.");
$httpReply = socket_read($socket,2048) or die ("Could not read from socket.");

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
?>

<? echo '<?xml version="1.0" encoding="ISO-8859-1"?>'?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
   <head>
      <title>OpenHome</title>
      <meta http-equiv = "Content-Type" content = "text/html; charset=iso-8859-1"/>
      <script type='text/javascript' src='http://www.google.com/jsapi'></script>
      <style type='text/css'>#sn_link {display:block; padding:0 10px 0 10px !important; font: 11px Arial, Helvetica, Sans serif !important; color:#117ba2 !important;}#sn_viz_wrapper a:hover,#sn_viz_wrapper a:link,#sn_viz_wrapper a:active,#sn_viz_wrapper a:visited {text-decoration:none !important; background:inherit !important;color:#117ba2;}</style>
   </head>
   <body>

   <?
      $sensornodeId   = $_GET['sensornodeId'];
      $sensorType     = $_GET['sensorType'];
      $numLastMinutes = $_GET['numLastMinutes'];
      $browser        = $_SERVER['HTTP_USER_AGENT'];
      if (substr_count($browser, 'iPhone')) {
         $iPhone = TRUE;
      } else {
         $iPhone = FALSE;
      }
      if ($sensornodeId=='') {$sensornodeId=2;}
      if ($sensorType=='')   {$sensorType='lightvisible';}

      if ($iPhone) {
              $graphType = 'lc';
      } else {
              $graphType = 'atl';
      }
      if ($numLastMinutes!='') {
         $startTime =  date('YmdHis',time()-($numLastMinutes*60));
      } else {
         $startTime =  '';
      }
    ?>

      <h1>Mote <? echo $sensornodeId; ?>, <? echo $sensorType; ?><? if ($startTime!='') {echo ', since '.$startTime;}?></h1>

      <p><span id='sn_viz_wrapper'>
         <a href='http://openwsn.berkeley.edu/' id='sn_link'><strong><span style='color:#666'>Data gathered by </span>OpenWSN.<span style='color:#96b23c'>berkeley</span>.edu</strong></a>
         <script type='text/javascript' src='http://incoherent.sunlabs.com/resources/visualizations?type=<? echo $graphType; ?>&amp;width=600&amp;height=250&amp;start=<? echo $startTime; ?>&amp;end=&amp;data=<? echo $data[$sensornodeId][$sensorType]; ?>.0'></script>
      </span></p>

   <p><br/></p>

   <form method="get" action="">
      <p>
      <select name="sensornodeId">
         <? foreach ($sensornodeIds as $temp) {
            if ($sensornodeId==$temp) {
               echo "<option selected=\"selected\">".$temp."</option>";
            } else {
               echo "<option>".$temp."</option>";
            }
         }?>
      </select>
      <select name="sensorType">
         <? foreach ($sensorTypes as $temp) {
            if ($sensorType==$temp) {
               echo "<option selected=\"selected\">".$temp."</option>";
            } else {
               echo "<option>".$temp."</option>";
            }
         }?>
      </select>
      </p><p>
      last
      <input type="text" name="numLastMinutes" value="<? echo $numLastMinutes; ?>" size="5" />
      minutes (leave blank for full range)
      </p><p>
      <input type="submit"/>
      </p>
   </form>

  <p>
    <a href="http://validator.w3.org/check?uri=referer"><img
        src="http://www.w3.org/Icons/valid-xhtml10"
        alt="Valid XHTML 1.0 Strict" height="31" width="88" /></a>
  </p>

   </body>
</html>

