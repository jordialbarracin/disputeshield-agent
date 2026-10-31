import logging
from datetime import datetime
from typing import List, Dict, Optional, Any
import httpx

from disputeshield.config import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_API_BASE
from disputeshield.models import (
    PayPalDisputeItem, DisputeReason, DisputeStatus, DisputeLifeCycleStage,
    DisputeChannel, Money, Address, BuyerTelemetry, RebuttalDossier
)

logger = logging.getLogger("disputeshield.paypal")

class PayPalDisputesClient:
    """
    Client for PayPal Customer Disputes API v1.
    Includes stateful in-memory store preloaded with realistic disputes.
    """

    def __init__(self):
        self._disputes_db: Dict[str, PayPalDisputeItem] = {}
        self._seed_default_disputes()

    def _seed_default_disputes(self):
        """Pre-seeds 8 diverse enterprise disputes across varied chargeback vectors."""
        seeds = [
            PayPalDisputeItem(
                dispute_id="PP-D-948102-US",
                create_time="2026-10-23T11:20:00Z",
                update_time="2026-10-23T11:20:00Z",
                reason=DisputeReason.MERCHANDISE_OR_SERVICE_NOT_RECEIVED,
                status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
                dispute_life_cycle_stage=DisputeLifeCycleStage.CHARGEBACK,
                dispute_channel=DisputeChannel.PAYPAL,
                dispute_amount=Money(currency_code="USD", value="1499.00"),
                fee_amount=Money(currency_code="USD", value="15.00"),
                seller_transaction_id="TXN-SELLER-991204",
                buyer_transaction_id="TXN-BUYER-881920",
                buyer=BuyerTelemetry(
                    email="j.doe@stanford.edu",
                    name="John Doe",
                    ip_address="171.67.215.200",
                    device_fingerprint="dev_fp_apple_m3_max_macbookpro_99a8",
                    shipping_address=Address(
                        street="450 Serra Mall, Bldg 500",
                        city="Stanford",
                        state="CA",
                        postal_code="94305",
                        country_code="US"
                    ),
                    account_created_at="2024-03-10"
                ),
                order_item_description="NVIDIA RTX 4090 Enterprise GPU 24GB",
                order_amount=Money(currency_code="USD", value="1499.00"),
                response_due_date="2026-11-02T23:59:59Z"
            ),
            PayPalDisputeItem(
                dispute_id="PP-D-882193-US",
                create_time="2026-10-22T08:15:00Z",
                update_time="2026-10-22T08:15:00Z",
                reason=DisputeReason.UNAUTHORIZED,
                status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
                dispute_life_cycle_stage=DisputeLifeCycleStage.CHARGEBACK,
                dispute_channel=DisputeChannel.CREDIT_CARD,
                dispute_amount=Money(currency_code="USD", value="289.00"),
                fee_amount=Money(currency_code="USD", value="15.00"),
                seller_transaction_id="TXN-SELLER-441209",
                buyer_transaction_id="TXN-BUYER-339182",
                buyer=BuyerTelemetry(
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
                    ),
                    account_created_at="2023-11-05"
                ),
                order_item_description="Automated Power Calibration Unit & Inverter",
                order_amount=Money(currency_code="USD", value="289.00"),
                response_due_date="2026-11-01T23:59:59Z"
            ),
            PayPalDisputeItem(
                dispute_id="PP-D-773812-US",
                create_time="2026-10-24T09:40:00Z",
                update_time="2026-10-24T09:40:00Z",
                reason=DisputeReason.UNAUTHORIZED,
                status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
                dispute_life_cycle_stage=DisputeLifeCycleStage.CHARGEBACK,
                dispute_channel=DisputeChannel.CREDIT_CARD,
                dispute_amount=Money(currency_code="USD", value="3200.00"),
                fee_amount=Money(currency_code="USD", value="15.00"),
                seller_transaction_id="TXN-SELLER-110294",
                buyer_transaction_id="TXN-BUYER-771829",
                buyer=BuyerTelemetry(
                    email="alex.m@biotech-innovations.com",
                    name="Alex Mercer",
                    ip_address="192.0.2.88",
                    device_fingerprint="dev_fp_thinkpad_x1_carbon_44b1",
                    shipping_address=Address(
                        street="100 Innovation Way, Suite 400",
                        city="Austin",
                        state="TX",
                        postal_code="78701",
                        country_code="US"
                    ),
                    account_created_at="2024-01-18"
                ),
                order_item_description="Annual Enterprise AI Inference License (100k API Units)",
                order_amount=Money(currency_code="USD", value="3200.00"),
                response_due_date="2026-11-03T23:59:59Z"
            ),
            PayPalDisputeItem(
                dispute_id="PP-D-665201-US",
                create_time="2026-10-21T14:10:00Z",
                update_time="2026-10-21T14:10:00Z",
                reason=DisputeReason.MERCHANDISE_OR_SERVICE_NOT_RECEIVED,
                status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
                dispute_life_cycle_stage=DisputeLifeCycleStage.INQUIRY,
                dispute_channel=DisputeChannel.PAYPAL,
                dispute_amount=Money(currency_code="USD", value="89.00"),
                fee_amount=Money(currency_code="USD", value="15.00"),
                seller_transaction_id="TXN-SELLER-994102",
                buyer_transaction_id="TXN-BUYER-552019",
                buyer=BuyerTelemetry(
                    email="r.tyler@outlook.com",
                    name="Rachel Tyler",
                    ip_address="203.0.113.19",
                    device_fingerprint="dev_fp_pixel_9_pro_android",
                    shipping_address=Address(
                        street="1200 Market Street",
                        city="Philadelphia",
                        state="PA",
                        postal_code="19107",
                        country_code="US"
                    ),
                    account_created_at="2025-08-12"
                ),
                order_item_description="Precision Soldering Station Kit with Micro-Tips",
                order_amount=Money(currency_code="USD", value="89.00"),
                response_due_date="2026-10-31T23:59:59Z"
            ),
            PayPalDisputeItem(
                dispute_id="PP-D-551094-US",
                create_time="2026-10-20T16:00:00Z",
                update_time="2026-10-20T16:00:00Z",
                reason=DisputeReason.MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED,
                status=DisputeStatus.REQUIRES_MANUAL_REVIEW,
                dispute_life_cycle_stage=DisputeLifeCycleStage.CHARGEBACK,
                dispute_channel=DisputeChannel.CREDIT_CARD,
                dispute_amount=Money(currency_code="USD", value="650.00"),
                fee_amount=Money(currency_code="USD", value="15.00"),
                seller_transaction_id="TXN-SELLER-772911",
                buyer_transaction_id="TXN-BUYER-448102",
                buyer=BuyerTelemetry(
                    email="g.vasquez@cybertech.io",
                    name="Gabriel Vasquez",
                    ip_address="198.51.100.99",
                    device_fingerprint="dev_fp_lenovo_legion_ubuntu",
                    shipping_address=Address(
                        street="500 Tech Parkway NW",
                        city="Atlanta",
                        state="GA",
                        postal_code="30332",
                        country_code="US"
                    ),
                    account_created_at="2025-02-14"
                ),
                order_item_description="Modular Rack-Mount Server Enclosure 4U",
                order_amount=Money(currency_code="USD", value="650.00"),
                response_due_date="2026-10-30T23:59:59Z"
            ),
            PayPalDisputeItem(
                dispute_id="PP-D-441829-US",
                create_time="2026-10-19T10:30:00Z",
                update_time="2026-10-19T10:30:00Z",
                reason=DisputeReason.MERCHANDISE_OR_SERVICE_NOT_RECEIVED,
                status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
                dispute_life_cycle_stage=DisputeLifeCycleStage.CHARGEBACK,
                dispute_channel=DisputeChannel.PAYPAL,
                dispute_amount=Money(currency_code="USD", value="840.00"),
                fee_amount=Money(currency_code="USD", value="15.00"),
                seller_transaction_id="TXN-SELLER-883912",
                buyer_transaction_id="TXN-BUYER-220194",
                buyer=BuyerTelemetry(
                    email="s.connor@cyberdyne.org",
                    name="Sarah Connor",
                    ip_address="203.0.113.88",
                    device_fingerprint="dev_fp_rugged_panasonic_toughbook",
                    shipping_address=Address(
                        street="840 Terminator Way",
                        city="Los Angeles",
                        state="CA",
                        postal_code="90001",
                        country_code="US"
                    ),
                    account_created_at="2023-05-20"
                ),
                order_item_description="Rugged Thermal Imaging Scope & Sensor Array",
                order_amount=Money(currency_code="USD", value="840.00"),
                response_due_date="2026-10-29T23:59:59Z"
            ),
            PayPalDisputeItem(
                dispute_id="PP-D-330192-US",
                create_time="2026-10-18T13:45:00Z",
                update_time="2026-10-18T13:45:00Z",
                reason=DisputeReason.CANCELED_RECURRING_BILLING,
                status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
                dispute_life_cycle_stage=DisputeLifeCycleStage.CHARGEBACK,
                dispute_channel=DisputeChannel.CREDIT_CARD,
                dispute_amount=Money(currency_code="USD", value="199.00"),
                fee_amount=Money(currency_code="USD", value="15.00"),
                seller_transaction_id="TXN-SELLER-664819",
                buyer_transaction_id="TXN-BUYER-119284",
                buyer=BuyerTelemetry(
                    email="d.vader@imperial-fleet.space",
                    name="Darth Vader",
                    ip_address="192.0.2.140",
                    device_fingerprint="dev_fp_deathstar_workstation_cmd01",
                    shipping_address=Address(
                        street="1 Death Star Trench",
                        city="Coruscant",
                        state="NV",
                        postal_code="89101",
                        country_code="US"
                    ),
                    account_created_at="2022-09-01"
                ),
                order_item_description="Annual Cloud Cluster Monitoring Tier 3",
                order_amount=Money(currency_code="USD", value="199.00"),
                response_due_date="2026-10-28T23:59:59Z"
            ),
            PayPalDisputeItem(
                dispute_id="PP-D-229104-US",
                create_time="2026-10-17T17:20:00Z",
                update_time="2026-10-17T17:20:00Z",
                reason=DisputeReason.MERCHANDISE_OR_SERVICE_NOT_RECEIVED,
                status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
                dispute_life_cycle_stage=DisputeLifeCycleStage.CHARGEBACK,
                dispute_channel=DisputeChannel.PAYPAL,
                dispute_amount=Money(currency_code="USD", value="420.00"),
                fee_amount=Money(currency_code="USD", value="15.00"),
                seller_transaction_id="TXN-SELLER-551029",
                buyer_transaction_id="TXN-BUYER-993812",
                buyer=BuyerTelemetry(
                    email="m.murdock@nelsonmurdock.legal",
                    name="Matt Murdock",
                    ip_address="198.51.100.201",
                    device_fingerprint="dev_fp_braille_accessible_mac_terminal",
                    shipping_address=Address(
                        street="463 8th Avenue",
                        city="New York",
                        state="NY",
                        postal_code="10001",
                        country_code="US"
                    ),
                    account_created_at="2024-07-04"
                ),
                order_item_description="Acoustic Spatial Resonance Analyzer",
                order_amount=Money(currency_code="USD", value="420.00"),
                response_due_date="2026-10-27T23:59:59Z"
            )
        ]

        for d in seeds:
            self._disputes_db[d.dispute_id] = d

    def list_disputes(self) -> List[PayPalDisputeItem]:
        """Returns all disputes sorted by create_time descending."""
        return sorted(list(self._disputes_db.values()), key=lambda x: x.create_time, reverse=True)

    def get_dispute(self, dispute_id: str) -> Optional[PayPalDisputeItem]:
        return self._disputes_db.get(dispute_id)

    def update_dispute(self, dispute: PayPalDisputeItem) -> PayPalDisputeItem:
        dispute.update_time = datetime.utcnow().isoformat() + "Z"
        self._disputes_db[dispute.dispute_id] = dispute
        return dispute

    def submit_evidence(self, dispute_id: str, dossier: RebuttalDossier) -> Dict[str, Any]:
        """Simulates or calls live POST /v1/customer/disputes/{id}/provide-evidence."""
        dispute = self._disputes_db.get(dispute_id)
        if not dispute:
            raise ValueError(f"Dispute {dispute_id} not found")

        dispute.evidence_dossier = dossier
        dispute.status = DisputeStatus.EVIDENCE_SUBMITTED
        dispute.update_time = datetime.utcnow().isoformat() + "Z"
        self._disputes_db[dispute_id] = dispute

        receipt_id = f"REC-PAYPAL-SEC-{dispute_id[:8].upper()}-{int(datetime.utcnow().timestamp())}"
        receipt = {
            "dispute_id": dispute_id,
            "status": "EVIDENCE_SUBMITTED",
            "receipt_id": receipt_id,
            "submission_timestamp": datetime.utcnow().isoformat() + "Z",
            "evidence_count": len(dossier.evidence_documents),
            "confidence_score": dossier.confidence_score,
            "seller_protection_eligible": True
        }
        return receipt

    def accept_claim(self, dispute_id: str, reason: str = "Merchant goodwill refund") -> Dict[str, Any]:
        """Accept dispute claim and refund buyer (e.g., when carrier confirms lost package)."""
        dispute = self._disputes_db.get(dispute_id)
        if not dispute:
            raise ValueError(f"Dispute {dispute_id} not found")

        dispute.status = DisputeStatus.RESOLVED_BUYER_WON
        dispute.update_time = datetime.utcnow().isoformat() + "Z"
        self._disputes_db[dispute_id] = dispute

        return {
            "dispute_id": dispute_id,
            "status": "RESOLVED_BUYER_WON",
            "action": "MERCHANT_ACCEPTED_CLAIM",
            "refund_amount": dispute.dispute_amount.model_dump(),
            "dispute_fee_waived": True,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
