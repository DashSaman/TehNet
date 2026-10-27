<?php
defined('ABSPATH') || exit;

/** Exact arithmetic at the store/ERP/payment boundary. */
final class TehNet_Store_Policy {
    private const CF_V4=['173.245.48.0/20','103.21.244.0/22','103.22.200.0/22','103.31.4.0/22','141.101.64.0/18','108.162.192.0/18','190.93.240.0/20','188.114.96.0/20','197.234.240.0/22','198.41.128.0/17','162.158.0.0/15','104.16.0.0/13','104.24.0.0/14','172.64.0.0/13','131.0.72.0/22'];
    private const CF_V6=['2400:cb00::/32','2606:4700::/32','2803:f800::/32','2405:b500::/32','2405:8100::/32','2a06:98c0::/29','2c0f:f248::/32'];

    /** True only when the direct peer is a published Cloudflare range, making CF-Connecting-IP trustworthy. */
    public static function is_cloudflare(string $peer): bool {
        if (filter_var($peer,FILTER_VALIDATE_IP,FILTER_FLAG_IPV4)) {
            $packed=ip2long($peer);
            foreach (self::CF_V4 as $cidr) {
                [$net,$bits]=explode('/',$cidr);
                if (($packed >> (32-(int)$bits)) === (ip2long($net) >> (32-(int)$bits))) { return true; }
            }
            return false;
        }
        $peer_bin=@inet_pton($peer);
        if ($peer_bin===false || strlen($peer_bin)!==16) { return false; }
        foreach (self::CF_V6 as $cidr) {
            [$net,$bits]=explode('/',$cidr);
            $net_bin=@inet_pton($net);
            if ($net_bin===false) { continue; }
            $bytes=(int)$bits >> 3; $rest=(int)$bits & 7;
            if (substr($peer_bin,0,$bytes)!==substr($net_bin,0,$bytes)) { continue; }
            if ($rest===0) { return true; }
            if ((ord($peer_bin[$bytes]) >> (8-$rest)) === (ord($net_bin[$bytes]) >> (8-$rest))) { return true; }
        }
        return false;
    }

    /** Per-IP submission throttle for public forms. Returns true when the submission may proceed. */
    public static function throttle(string $bucket,int $max = 5,int $window = 3600): bool {
        $ip='unknown';
        $remote=isset($_SERVER['REMOTE_ADDR']) && is_string($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '';
        $cf=isset($_SERVER['HTTP_CF_CONNECTING_IP']) && is_string($_SERVER['HTTP_CF_CONNECTING_IP']) ? trim($_SERVER['HTTP_CF_CONNECTING_IP']) : '';
        if ($cf!=='' && filter_var($cf,FILTER_VALIDATE_IP) && $remote!=='' && self::is_cloudflare($remote)) { $ip=$cf; }
        elseif ($remote!=='') { $ip=$remote; }
        $key='tn_th_'.md5($bucket.'|'.preg_replace('/[^0-9a-fA-F:.]/','',substr($ip,0,45)));
        $count=(int)get_transient($key);
        if ($count >= $max) { return false; }
        set_transient($key,$count+1,$window);
        return true;
    }

    private static function digits(string $value): string {
        return strtr($value, ['۰'=>'0','۱'=>'1','۲'=>'2','۳'=>'3','۴'=>'4','۵'=>'5','۶'=>'6','۷'=>'7','۸'=>'8','۹'=>'9','٠'=>'0','١'=>'1','٢'=>'2','٣'=>'3','٤'=>'4','٥'=>'5','٦'=>'6','٧'=>'7','٨'=>'8','٩'=>'9']);
    }
    public static function irr($value, string $currency): int {
        if (!is_string($value) && !is_int($value)) { throw new InvalidArgumentException('Money must be an integer or decimal string'); }
        $value=self::digits(trim((string)$value));
        if (!preg_match('/^(0|[1-9][0-9]*)(?:\.([0-9]+))?$/D',$value,$m) || strlen($m[1])>12) { throw new InvalidArgumentException('Invalid or excessive money'); }
        $fraction=rtrim($m[2]??'','0');
        $whole=(int)$m[1];
        if ($currency==='IRR' && $fraction==='') { return $whole; }
        if ($currency==='IRT' && strlen($fraction)<=1 && $whole<=99999999999) { return $whole*10+(int)($fraction?:'0'); }
        throw new InvalidArgumentException('Unknown currency or fractional rial');
    }
    public static function quantity_milli(string $quantity): int {
        $quantity=self::digits(trim($quantity));
        if (!preg_match('/^(0|[1-9][0-9]*)(?:\.([0-9]{1,3}))?$/D',$quantity,$m) || strlen($m[1])>6) { throw new InvalidArgumentException('Invalid quantity'); }
        $result=(int)$m[1]*1000+(int)str_pad($m[2]??'',3,'0');
        if ($result<=0) { throw new InvalidArgumentException('Quantity must be positive'); }
        return $result;
    }
    public static function line_total(int $quantity_milli, int $unit_price_irr): int {
        if ($quantity_milli<1 || $unit_price_irr<0 || ($unit_price_irr>0 && $quantity_milli>intdiv(PHP_INT_MAX,$unit_price_irr))) { throw new InvalidArgumentException('Amount overflow'); }
        $scaled=$quantity_milli*$unit_price_irr;
        if ($scaled%1000!==0) { throw new InvalidArgumentException('Fractional rial requires explicit repricing'); }
        return intdiv($scaled,1000);
    }
    public static function can_sell(array $row,int $now): bool {
        try {
            return ($row['approved']??'')==='yes'
                && self::irr($row['price']??'','IRR')>0
                && self::quantity_milli((string)($row['stock']??'0'))>0
                && in_array($row['unit']??'',['piece','meter','reel','pack'],true)
                && self::quantity_milli((string)($row['minimum']??'0'))>0
                && (int)($row['erp_fresh_until']??0)>$now
                && ($row['erp_ready']??false)===true;
        } catch (InvalidArgumentException $e) { return false; }
    }
}
