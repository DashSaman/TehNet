<?php
/** Standalone contract tests for TehNet_Store_QA pure validation. No WordPress loaded. */
define('ABSPATH', __DIR__ . '/');
require __DIR__ . '/../site/plugins/tehnet-store/includes/class-qa.php';
$count = 0;
function check(bool $ok, string $label): void {
    global $count;
    if (!$ok) { throw new RuntimeException('FAIL: ' . $label); }
    ++$count;
    echo "PASS: $label\n";
}

$q = TehNet_Store_QA::validate_question('امیر', 'این کابل برای دوربین مناسب است؟', '');
check($q['ok'] === true && $q['name'] === 'امیر', 'valid question accepted and trimmed');
check(TehNet_Store_QA::validate_question('ا', 'سؤال معتبر اینجا', '')['ok'] === false, 'too-short name rejected');
check(TehNet_Store_QA::validate_question(str_repeat('ن', 81), 'سؤال معتبر اینجا', '')['ok'] === false, 'too-long name rejected');
check(TehNet_Store_QA::validate_question('امیر', 'کوتا', '')['ok'] === false, 'too-short body rejected');
check(TehNet_Store_QA::validate_question('امیر', str_repeat('س', 1001), '')['ok'] === false, 'too-long body rejected');
check(in_array('spam', TehNet_Store_QA::validate_question('امیر', 'سؤال معتبر اینجا', 'x')['errors'], true), 'honeypot filled flags spam');

$f = TehNet_Store_QA::validate_feedback(5, 'پاسخ سریع و دقیق بود', '');
check($f['ok'] === true && $f['rating'] === 5, 'valid feedback accepted');
check(TehNet_Store_QA::validate_feedback(0, 'پاسخ سریع بود', '')['ok'] === false, 'rating below range rejected');
check(TehNet_Store_QA::validate_feedback(6, 'پاسخ سریع بود', '')['ok'] === false, 'rating above range rejected');
check(TehNet_Store_QA::validate_feedback(4, 'خب', '')['ok'] === false, 'too-short comment rejected');
check(TehNet_Store_QA::validate_feedback(4, str_repeat('خ', 501), '')['ok'] === false, 'too-long comment rejected');
check(in_array('email', TehNet_Store_QA::validate_feedback(4, 'پاسخ خوب بود', 'not-an-email')['errors'], true), 'invalid email rejected');
check(TehNet_Store_QA::validate_feedback(4, 'پاسخ خوب بود', 'user@example.com')['ok'] === true, 'valid optional email accepted');

echo "QA_CONTRACTS=PASSED checks=$count\n";
