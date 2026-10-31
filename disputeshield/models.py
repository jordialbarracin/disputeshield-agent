from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class DisputeReason(str, Enum):
    MERCHANDISE_OR_SERVICE_NOT_RECEIVED = "MERCHANDISE_OR_SERVICE_NOT_RECEIVED"
    UNAUTHORIZED = "UNAUTHORIZED"
    MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED = "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED"
    CANCELED_RECURRING_BILLING = "CANCELED_RECURRING_BILLING"
    INCORRECT_AMOUNT = "INCORRECT_AMOUNT"

class DisputeStatus(str, Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    WAITING_FOR_SELLER_RESPONSE = "WAITING_FOR_SELLER_RESPONSE"
    EVIDENCE_SUBMITTED = "EVIDENCE_SUBMITTED"
    RESOLVED_MERCHANT_WON = "RESOLVED_MERCHANT_WON"
    RESOLVED_BUYER_WON = "RESOLVED_BUYER_WON"
    REQUIRES_MANUAL_REVIEW = "REQUIRES_MANUAL_REVIEW"

class DisputeLifeCycleStage(str, Enum):
    INQUIRY = "INQUIRY"
    CHARGEBACK = "CHARGEBACK"
    PRE_ARBITRATION = "PRE_ARBITRATION"
    ARBITRATION = "ARBITRATION"

class DisputeChannel(str, Enum):
    INTERNAL = "INTERNAL"
    PAYPAL = "PAYPAL"
    CREDIT_CARD = "CREDIT_CARD"

class Money(BaseModel):
    currency_code: str = "USD"
    value: str = "0.00"

class Address(BaseModel):
    street: str
    city: str
    state: str
    postal_code: str
    country_code: str = "US"

class BuyerTelemetry(BaseModel):
    email: str
    name: str
    ip_address: str
    device_fingerprint: str
    shipping_address: Address
    login_timestamp: Optional[str] = None
    account_created_at: Optional[str] = None

class CarrierTelemetry(BaseModel):
    carrier_name: str  # e.g., "FedEx", "UPS", "DHL"
    tracking_number: str
    ship_date: str
    delivery_date: str
    delivery_status: str  # "DELIVERED", "IN_TRANSIT", "RETURNED_TO_SENDER"
    delivery_address: Address
    recipient_signed_by: Optional[str] = None
    delivery_gps: Optional[str] = None  # e.g., "37.7749 N, 122.4194 W"
    photo_pod_url: Optional[str] = None
    carrier_proof_valid: bool = True

class CE3Match(BaseModel):
    """Visa/Mastercard Compelling Evidence 3.0 (CE 3.0) Correlation Match."""
    rule_applied: str = "Visa CE 3.0 / Mastercard First-Party Misuse Rule"
    prior_transaction_ids: List[str] = Field(default_factory=list)
    prior_transaction_dates: List[str] = Field(default_factory=list)
    ip_match: bool = False
    device_fingerprint_match: bool = False
    delivery_address_match: bool = False
    ce3_qualified: bool = False
    legal_statute_note: str = ""

class EvidenceDocument(BaseModel):
    document_type: str  # "CARRIER_PROOF_OF_DELIVERY", "CE3_LEDGER_EXPORT", "TERMS_OF_SERVICE_ACCEPTANCE", "LOGIN_AUDIT_LOG"
    title: str
    filename: str
    sha256_hash: str
    download_url: str
    description: str

class RebuttalDossier(BaseModel):
    dispute_id: str
    synthesized_at: str
    confidence_score: float = Field(ge=0.0, le=100.0)  # e.g. 96.5%
    auto_submitted: bool = False
    executive_summary: str
    legal_memo_markdown: str
    ce3_match: Optional[CE3Match] = None
    carrier_telemetry: Optional[CarrierTelemetry] = None
    evidence_documents: List[EvidenceDocument] = Field(default_factory=list)
    paypal_submission_receipt: Optional[Dict[str, Any]] = None

class PayPalDisputeItem(BaseModel):
    dispute_id: str
    create_time: str
    update_time: str
    reason: DisputeReason
    status: DisputeStatus
    dispute_life_cycle_stage: DisputeLifeCycleStage = DisputeLifeCycleStage.CHARGEBACK
    dispute_channel: DisputeChannel = DisputeChannel.PAYPAL
    dispute_amount: Money
    fee_amount: Money = Field(default_factory=lambda: Money(currency_code="USD", value="15.00"))
    seller_transaction_id: str
    buyer_transaction_id: str
    buyer: BuyerTelemetry
    order_item_description: str
    order_amount: Money
    response_due_date: str
    confidence_score: Optional[float] = None
    ce3_qualified: bool = False
    evidence_dossier: Optional[RebuttalDossier] = None

class BenchmarkCaseResult(BaseModel):
    case_id: str
    case_name: str
    reason: str
    claimed_amount: float
    ground_truth_verdict: str  # "MERCHANT_WON", "REFUND_MERITED"
    agent_verdict: str
    confidence_score: float
    ce3_triggered: bool
    processing_time_ms: float
    won: bool
    explanation: str

class BenchmarkReport(BaseModel):
    benchmark_suite: str = "DisputeShield Canonical FinTech 5-Vector Benchmark"
    executed_at: str
    total_cases: int
    merchant_won_cases: int
    legitimate_refund_cases: int
    win_rate_percentage: float
    total_gmv_disputed_usd: float
    total_gmv_recovered_usd: float
    chargeback_fees_prevented_usd: float
    avg_latency_ms: float
    cases: List[BenchmarkCaseResult]
