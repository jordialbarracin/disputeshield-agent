from disputeshield.models import BuyerTelemetry, Address
from disputeshield.ce3_engine import CompellingEvidence3Engine

def test_ce3_qualified_buyer():
    """Tests that a buyer with historical settled orders qualifies under Visa CE 3.0."""
    buyer = BuyerTelemetry(
        email="h.simpson@springfield.org",
        name="Homer Simpson",
        ip_address="198.51.100.44",
        device_fingerprint="dev_fp_9921_springfield_chromebook",
        shipping_address=Address(
            street="742 Evergreen Terrace",
            city="Springfield",
            state="OR",
            postal_code="97477",
            country_code="US"
        )
    )

    assessment = CompellingEvidence3Engine.evaluate_ce3_eligibility(buyer)
    assert assessment.ce3_qualified is True
    assert len(assessment.prior_transaction_ids) >= 2
    assert assessment.ip_match is True
    assert assessment.device_fingerprint_match is True

def test_ce3_unqualified_new_buyer():
    """Tests that an unknown buyer without prior historical orders is NOT qualified."""
    buyer = BuyerTelemetry(
        email="brand.new.user@unknown.com",
        name="John Doe",
        ip_address="203.0.113.99",
        device_fingerprint="fp_hash_brand_new_device_9999",
        shipping_address=Address(
            street="100 First St",
            city="Seattle",
            state="WA",
            postal_code="98101",
            country_code="US"
        )
    )

    assessment = CompellingEvidence3Engine.evaluate_ce3_eligibility(buyer)
    assert assessment.ce3_qualified is False
    assert len(assessment.prior_transaction_ids) == 0
