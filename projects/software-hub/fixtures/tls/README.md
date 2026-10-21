# Disposable TLS test identity — NEVER production trust

The certificate authority and mirror.test server identity were generated for this repository's local TLS integration tests on 2026-10-17. The committed server key is intentionally public test material; it cannot be used as a real service credential. The CA private key is not distributed. Certificates expire in 2036; regenerate fixtures when their validation dates no longer cover the test clock.

Trust `ca.pem` only inside an isolated test SSLContext. Never install it into operating-system, browser, Docker or production trust stores. The tests bind loopback/ephemeral ports and exercise pinned numeric transport with Host/SNI/hostname/chain verification. Public-address validation is tested separately; the production target validator rejects loopback.
