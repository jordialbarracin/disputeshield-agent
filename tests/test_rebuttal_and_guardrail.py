import asyncio
from disputeshield.models import (
    PayPalDisputeItem, DisputeReason, DisputeStatus, Money, Address, BuyerTelemetry
)
from disputeshield.rebuttal_synthesizer import RebuttalSynthesizer
from disputeshield.ce3_engine import CompellingEvidence3Engine
from disputeshield.carrier_client import CarrierTelemetryClient
from disputeshield.paypal_client import PayPalDisputesClient
from disputeshield.swarm import DisputeDefenseSwarm

def test_legal_rebuttal_synthesis_and_checksums():
    """Tests that the rebuttal synthesizer generates markdown briefs with valid SHA-256 hashes."""
    async def _run():
        item = PayPalDisputeItem(
            dispute_id="PP-D-773812-US",
            create_time="2026-10-24T10:00:00Z",
            update_time="2026-10-24T10:00:00Z",
            reason=DisputeReason.MERCHANDISE_OR_SERVICE_NOT_RECEIVED,
            status=DisputeStatus.WAITING_FOR_SELLER_RESPONSE,
            dispute_amount=Money(currency_code="USD", value="1499.00"),
            seller_transaction_id="TXN-S-773812",
            buyer_transaction_id="TXN-B-773812",
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
                )
            ),
            order_item_description="Industrial Multimeter",
            order_amount=Money(currency_code="USD", value="1499.00"),
            response_due_date="2026-11-03T23:59:59Z"
        )

        ce3 = CompellingEvidence3Engine.evaluate_ce3_eligibility(item.buyer)
        telemetry = CarrierTelemetryClient.get_carrier_telemetry("DHL-7718291029", fallback_address=item.buyer.shipping_address)

        dossier = await RebuttalSynthesizer.synthesize_dossier(item, telemetry, ce3)
        assert dossier is not None
        assert dossier.dispute_id == item.dispute_id
        assert len(dossier.legal_memo_markdown) > 50
        assert len(dossier.evidence_documents) > 0
        for doc in dossier.evidence_documents:
            assert len(doc.sha256_hash) == 64

    asyncio.run(_run())

def test_swarm_end_to_end_pipeline():
    """Tests that DisputeDefenseSwarm processes a dispute end-to-end and computes a confidence score."""
    async def _run():
        paypal_client = PayPalDisputesClient()
        swarm = DisputeDefenseSwarm(paypal_client=paypal_client)

        dossier = await swarm.process_dispute("PP-D-773812-US")
        assert dossier.dispute_id == "PP-D-773812-US"
        assert dossier.confidence_score >= 80.0

    asyncio.run(_run())
