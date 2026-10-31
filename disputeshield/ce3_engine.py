from typing import List, Dict, Tuple, Optional
from disputeshield.models import CE3Match, BuyerTelemetry

class CompellingEvidence3Engine:
    """
    Visa & Mastercard Compelling Evidence 3.0 (CE 3.0) Evaluation Engine.
    Statutory Framework: Visa Core Rules & Visa Product and Service Rules ID# 0030260 (Reason Code 10.4).
    Mastercard First-Party Trust / Revised Misuse Standards (Rule 4.1.2).
    """

    # In-memory merchant ledger of historical settled undisputed transactions
    _HISTORICAL_TRANSACTIONS: List[Dict] = [
        {
            "transaction_id": "TXN-HIST-2025-88190",
            "date": "2025-11-12T14:30:00Z",
            "email": "h.simpson@springfield.org",
            "ip_address": "198.51.100.44",
            "device_fingerprint": "dev_fp_9921_springfield_chromebook",
            "shipping_street": "742 Evergreen Terrace",
            "shipping_zip": "97477",
            "amount": 289.00,
            "undisputed": True
        },
        {
            "transaction_id": "TXN-HIST-2026-02104",
            "date": "2026-02-18T19:15:00Z",
            "email": "h.simpson@springfield.org",
            "ip_address": "198.51.100.44",
            "device_fingerprint": "dev_fp_9921_springfield_chromebook",
            "shipping_street": "742 Evergreen Terrace",
            "shipping_zip": "97477",
            "amount": 145.50,
            "undisputed": True
        },
        {
            "transaction_id": "TXN-HIST-2025-41092",
            "date": "2025-10-04T10:00:00Z",
            "email": "j.doe@stanford.edu",
            "ip_address": "171.67.215.200",
            "device_fingerprint": "dev_fp_apple_m3_max_macbookpro_99a8",
            "shipping_street": "450 Serra Mall, Bldg 500",
            "shipping_zip": "94305",
            "amount": 1499.00,
            "undisputed": True
        },
        {
            "transaction_id": "TXN-HIST-2026-01115",
            "date": "2026-01-22T08:45:00Z",
            "email": "j.doe@stanford.edu",
            "ip_address": "171.67.215.200",
            "device_fingerprint": "dev_fp_apple_m3_max_macbookpro_99a8",
            "shipping_street": "450 Serra Mall, Bldg 500",
            "shipping_zip": "94305",
            "amount": 750.00,
            "undisputed": True
        },
        {
            "transaction_id": "TXN-HIST-2025-77210",
            "date": "2025-12-05T12:00:00Z",
            "email": "alex.m@biotech-innovations.com",
            "ip_address": "192.0.2.88",
            "device_fingerprint": "dev_fp_thinkpad_x1_carbon_44b1",
            "shipping_street": "100 Innovation Way, Suite 400",
            "shipping_zip": "78701",
            "amount": 3200.00,
            "undisputed": True
        },
        {
            "transaction_id": "TXN-HIST-2026-03014",
            "date": "2026-03-01T15:20:00Z",
            "email": "alex.m@biotech-innovations.com",
            "ip_address": "192.0.2.88",
            "device_fingerprint": "dev_fp_thinkpad_x1_carbon_44b1",
            "shipping_street": "100 Innovation Way, Suite 400",
            "shipping_zip": "78701",
            "amount": 1850.00,
            "undisputed": True
        }
    ]

    @classmethod
    def evaluate_ce3_eligibility(cls, buyer: BuyerTelemetry) -> CE3Match:
        """
        Cross-examines the disputed buyer telemetry against historical merchant ledger.
        Requirements for Visa CE 3.0 / Mastercard First-Party Misuse:
        1. >= 2 prior settled undisputed transactions.
        2. At least 2 digital footprint criteria match identically across prior orders:
           - IP Address match
           - Device Fingerprint ID match
           - Physical Delivery Address (Street + Postal Code) match
        """
        matches = [
            t for t in cls._HISTORICAL_TRANSACTIONS
            if t["email"].lower() == buyer.email.lower() and t["undisputed"]
        ]

        if len(matches) < 2:
            return CE3Match(
                ce3_qualified=False,
                legal_statute_note="Insufficient prior undisputed transaction history (< 2 required historical settled orders)."
            )

        prior_ids = [m["transaction_id"] for m in matches[:2]]
        prior_dates = [m["date"] for m in matches[:2]]

        # Verify criteria across both transactions
        ip_match = all(m["ip_address"] == buyer.ip_address for m in matches[:2])
        device_match = all(m["device_fingerprint"] == buyer.device_fingerprint for m in matches[:2])
        address_match = all(
            m["shipping_street"].lower() == buyer.shipping_address.street.lower() and
            m["shipping_zip"] == buyer.shipping_address.postal_code
            for m in matches[:2]
        )

        match_count = sum([ip_match, device_match, address_match])
        ce3_qualified = match_count >= 2

        if ce3_qualified:
            statute_note = (
                f"CE 3.0 QUALIFIED: Transaction conclusively satisfies Visa CE 3.0 (Reason Code 10.4) & "
                f"Mastercard Rule 4.1.2. Buyer digital footprint matches {match_count}/3 statutory criteria "
                f"(IP: {ip_match}, Device: {device_match}, Delivery Address: {address_match}) across 2 prior undisputed orders "
                f"({', '.join(prior_ids)}). Precludes issuer chargeback under card brand regulations."
            )
        else:
            statute_note = (
                f"CE 3.0 CRITERIA NOT MET: Found 2 prior orders, but only {match_count}/3 criteria matched "
                f"(Minimum 2 required under Visa CE 3.0)."
            )

        return CE3Match(
            prior_transaction_ids=prior_ids,
            prior_transaction_dates=prior_dates,
            ip_match=ip_match,
            device_fingerprint_match=device_match,
            delivery_address_match=address_match,
            ce3_qualified=ce3_qualified,
            legal_statute_note=statute_note
        )
