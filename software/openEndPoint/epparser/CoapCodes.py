#defines all coap option code

option_codes = {
  #response codes
  65:"2.01 Created                  ",
  66:"2.02 Deleted                  ",
  67:"2.03 Valid                    ",
  68:"2.04 Changed                  ",
  69:"2.05 Content                  ",
 128:"4.00 Bad Request              ",
 129:"4.01 Unauthorized             ",
 130:"4.02 Bad Option               ",
 131:"4.03 Forbidden                ",
 132:"4.04 Not Found                ",
 133:"4.05 Method Not Allowed       ",
 140:"4.12 Precondition Failed      ",
 141:"4.13 Request Entity Too Large ",
 143:"4.15 Unsupported Media Type   ",
 160:"5.00 Internal Server Error    ",
 161:"5.01 Not Implemented          ",
 162:"5.02 Bad Gateway              ",
 163:"5.03 Service Unavailable      ",
 164:"5.04 Gateway Timeout          ",
 165:"5.05 Proxying Not Supported   ",
  #option number registry
 1:"Content-Type   ",
 2:"Max-Age        ",
 3:"Proxy-Uri      ",
 4:"ETag           ",
 5:"Uri-Host       ",
 6:"Location-Path  ",
 7:"Uri-Port       ",
 8:"Location-Query ",
 9:"Uri-Path       ",
 11:"Token          ",
 12:"Accept         ",
 13:"If-Match       ",
 15:"Uri-Query      ",
 21:"If-None-Match  ",
 #media types
 0:"text/plain; charset=utf-8 ",
 40:"application/link-format  ",
 41:"application/xml          ",
 42:"application/octet-stream ",
 47:"application/exi          ",
 50:"application/json         "
}
                  

                  