<?php
/** Standalone contract tests for TehNet_Store_Tickets pure validation. No WordPress loaded. */
define('ABSPATH', __DIR__ . '/');
require __DIR__ . '/../site/plugins/tehnet-store/includes/class-tickets.php';
$count = 0;
function check(bool $ok, string $label): void {
    global $count;
    if (!$ok) { throw new RuntimeException('FAIL: ' . $label); }
    ++$count;
    echo "PASS: $label\n";
}

$v = TehNet_Store_Tickets::validate_ticket('امیر رضایی', 'amir@example.com', 'سفارش من رهنمون شد', 'شرح مشکل با حداقل ده کاراکتر');
check($v['ok'] === true && $v['reference'] === '', 'valid ticket without reference');
check(TehNet_Store_Tickets::validate_ticket('امیر', 'a@b.co', 'سفارش من', 'شرح مشکل با حداقل ده کاراکتر', 'TN-SN-18002')['ok'] === true, 'valid ticket with reference');
check(in_array('name', TehNet_Store_Tickets::validate_ticket('ا', 'a@b.co', 'موضوع', 'شرح مشکل با حداقل ده کاراکتر')['errors'], true), 'short name rejected');
check(in_array('email', TehNet_Store_Tickets::validate_ticket('امیر', 'bad', 'موضوع', 'شرح مشکل با حداقل ده کاراکتر')['errors'], true), 'bad email rejected');
check(in_array('subject', TehNet_Store_Tickets::validate_ticket('امیر', 'a@b.co', 'ab', 'شرح مشکل با حداقل ده کاراکتر')['errors'], true), 'short subject rejected');
check(in_array('subject', TehNet_Store_Tickets::validate_ticket('امیر', 'a@b.co', str_repeat('م', 141), 'شرح مشکل با حداقل ده کاراکتر')['errors'], true), 'long subject rejected');
check(in_array('message', TehNet_Store_Tickets::validate_ticket('امیر', 'a@b.co', 'موضوع', 'کوتاه است')['errors'], true), 'short message rejected');
check(in_array('message', TehNet_Store_Tickets::validate_ticket('امیر', 'a@b.co', 'موضوع', str_repeat('ش', 3001))['errors'], true), 'long message rejected');
check(in_array('reference', TehNet_Store_Tickets::validate_ticket('امیر', 'a@b.co', 'موضوع', 'شرح مشکل با حداقل ده کاراکتر', str_repeat('ر', 81))['errors'], true), 'long reference rejected');

echo "TICKETS_CONTRACTS=PASSED checks=$count\n";
