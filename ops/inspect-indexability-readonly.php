<?php
/** Read-only diagnostic; invoke only through an already-authorized server WP-CLI. Never installs a plugin. */
if(!defined('ABSPATH')||!defined('WP_CLI')||!WP_CLI){throw new RuntimeException('Existing WordPress CLI context required');}
global $wp_filter;
$result=['schema'=>1,'mode'=>'READ_ONLY','observed_utc'=>gmdate('c'),'blog_public'=>get_option('blog_public',null),'callbacks'=>[],'writes'=>0];
foreach(['wp_robots','wp_sitemaps_enabled','wp_headers','send_headers']as$tag){
 $result['callbacks'][$tag]=[];
 foreach(($wp_filter[$tag]->callbacks??[])as$priority=>$callbacks)foreach($callbacks as$entry){
  $fn=$entry['function'];$name='UNKNOWN';$file=null;
  try{
   if(is_string($fn)){$name=$fn;$reflection=new ReflectionFunction($fn);}
   elseif(is_array($fn)){$name=(is_object($fn[0])?get_class($fn[0]):$fn[0]).'::'.$fn[1];$reflection=new ReflectionMethod($fn[0],$fn[1]);}
   elseif($fn instanceof Closure){$name='Closure';$reflection=new ReflectionFunction($fn);}
   else continue;
   $source=$reflection->getFileName();$file=$source?basename($source):null;
  }catch(Throwable$e){$file=null;}
  $result['callbacks'][$tag][]=['priority'=>$priority,'callback'=>$name,'source_basename'=>$file];
 }
}
echo 'TN_INDEXABILITY_READONLY '.wp_json_encode($result,JSON_UNESCAPED_SLASHES)."\n";
