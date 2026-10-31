import logging
import asyncio
from typing import Dict, Any, Optional

from disputeshield.models import (
    PayPalDisputeItem, RebuttalDossier, DisputeStatus
)
from disputeshield.carrier_client import CarrierTelemetryClient
from disputeshield.ce3_engine import CompellingEvidence3Engine
from disputeshield.rebuttal_synthesizer import RebuttalSynthesizer
from disputeshield.paypal_client import PayPalDisputesClient

logger = logging.getLogger("disputeshield.swarm")

class DisputeDefenseSwarm:
    """
    Autonomous Defense Swarm coordinating:
    - Harvester Agent (Carrier Telemetry & Digital Footprint)
    - Card Brand Rules Agent (Visa CE 3.0 / Mastercard First-Party Misuse)
    - Legal Synthesizer Agent (Airtight LLM Memorandum Generation)
    - Autonomous Controller (Auto-submission or Human-in-the-Loop Escrow)
    """

    def __init__(self, paypal_client: PayPalDisputesClient):
        self.paypal_client = paypal_client

    # Mapping of dispute transaction to carrier tracking numbers
    _TRACKING_LOOKUP = {
        "PP-D-948102-US": "UPS-1Z9999999999999999",
        "PP-D-882193-US": "FDX-99281-US",
        "PP-D-773812-US": "DHL-7718291029",
        "PP-D-665201-US": "FDX-LOST-00192",  # Carrier lost package
        "PP-D-551094-US": "UPS-1Z9999999999999999",
        "PP-D-441829-US": "FDX-99281-US",
        "PP-D-330192-US": "DHL-7718291029",
        "PP-D-229104-US": "FDX-99281-US",
    }

    async def process_dispute(self, dispute_id: str) -> RebuttalDossier:
        """Runs the complete multi-agent pipeline on a dispute."""
        dispute = self.paypal_client.get_dispute(dispute_id)
        if not dispute:
            raise ValueError(f"Dispute {dispute_id} does not exist.")

        logger.info(f"[DisputeShield Swarm] Processing dispute {dispute_id} ({dispute.reason.value})")

        # 1. Carrier Telemetry Harvester
        tracking_num = self._TRACKING_LOOKUP.get(dispute_id, f"FDX-{dispute_id[-6:]}-US")
        carrier_telemetry = CarrierTelemetryClient.get_carrier_telemetry(
            tracking_num, fallback_address=dispute.buyer.shipping_address
        )

        # 2. CE 3.0 Statutory Rule Engine
        ce3_match = CompellingEvidence3Engine.evaluate_ce3_eligibility(dispute.buyer)
        dispute.ce3_qualified = ce3_match.ce3_qualified

        # 3. Legal Brief Synthesis & Confidence Calculation
        dossier = await RebuttalSynthesizer.synthesize_dossier(dispute, carrier_telemetry, ce3_match)
        dispute.confidence_score = dossier.confidence_score
        dispute.evidence_dossier = dossier

        # 4. Autonomous Routing & Guardrail Policy
        # Rule A: If carrier shows lost in transit, advise merchant refund to save $15 fee
        if carrier_telemetry and carrier_telemetry.delivery_status == "EXCEPTION_LOST_IN_TRANSIT":
            dispute.status = DisputeStatus.REQUIRES_MANUAL_REVIEW
            logger.info(f"[DisputeShield Swarm] Package lost in transit. Flagged for merchant refund.")
        # Rule B: High confidence >= 90.0% -> Autonomous Straight-Through Processing
        elif dossier.confidence_score >= 90.0:
            logger.info(f"[DisputeShield Swarm] Confidence {dossier.confidence_score}% >= 90.0%. Auto-submitting evidence to PayPal.")
            receipt = self.paypal_client.submit_evidence(dispute_id, dossier)
            dossier.auto_submitted = True
            dossier.paypal_submission_receipt = receipt
        # Rule C: Confidence < 90.0% -> Flag for 1-click human review
        else:
            dispute.status = DisputeStatus.REQUIRES_MANUAL_REVIEW
            dossier.auto_submitted = False
            logger.info(f"[DisputeShield Swarm] Confidence {dossier.confidence_score}% < 90.0%. Flagged for merchant review.")

        self.paypal_client.update_dispute(dispute)
        return dossier

    async def process_all_pending_disputes(self) -> Dict[str, Any]:
        """Scans all disputes and autonomously handles them."""
        disputes = self.paypal_client.list_disputes()
        processed = []
        auto_won = 0
        flagged_review = 0
        total_amount_protected = 0.0

        for d in disputes:
            if d.status in [DisputeStatus.WAITING_FOR_SELLER_RESPONSE, DisputeStatus.OPEN]:
                dossier = await self.process_dispute(d.dispute_id)
                processed.append({
                    "dispute_id": d.dispute_id,
                    "confidence": dossier.confidence_score,
                    "auto_submitted": dossier.auto_submitted,
                    "amount": float(d.dispute_amount.value)
                })
                if dossier.auto_submitted:
                    auto_won += 1
                    total_amount_protected += float(d.dispute_amount.value)
                else:
                    flagged_review += 1

        return {
            "processed_count": len(processed),
            "auto_submitted_count": auto_won,
            "flagged_for_review": flagged_review,
            "total_capital_defended_usd": total_amount_protected,
            "items": processed
        }
