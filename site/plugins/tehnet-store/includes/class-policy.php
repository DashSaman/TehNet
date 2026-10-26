<?php
defined('ABSPATH') || exit;

/** Exact arithmetic at the store/ERP/payment boundary. */
final class TehNet_Store_Policy {
    /** Per-IP submission throttle for public forms. Returns true when the submission may proceed. */
    public static function throttle(string $bucket,int $max = 5,int $window = 3600): bool {
        $ip='unknown';
        if (isset($_SERVER['HTTP_CF_CONNECTING_IP']) && is_string($_SERVER['HTTP_CF_CONNECTING_IP'])) { $ip=$_SERVER['HTTP_CF_CONNECTING_IP']; }
        elseif (isset($_SERVER['REMOTE_ADDR']) && is_string($_SERVER['REMOTE_ADDR'])) { $ip=$_SERVER['REMOTE_ADDR']; }
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
