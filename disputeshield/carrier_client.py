import hashlib
from typing import Optional, Dict
from disputeshield.models import CarrierTelemetry, Address

class CarrierTelemetryClient:
    """Simulates carrier API telemetry with Proof of Delivery, GPS coords, and signature capture."""
    
    _MOCK_DATABASE: Dict[str, Dict] = {
        "FDX-99281-US": {
            "carrier_name": "FedEx Express",
            "tracking_number": "FDX-99281-US",
            "ship_date": "2026-10-14T09:12:00Z",
            "delivery_date": "2026-10-16T14:22:31Z",
            "delivery_status": "DELIVERED",
            "delivery_address": {
                "street": "742 Evergreen Terrace",
                "city": "Springfield",
                "state": "OR",
                "postal_code": "97477",
                "country_code": "US"
            },
            "recipient_signed_by": "H. SIMPSON (Direct Signature Required)",
            "delivery_gps": "44.0521° N, 123.0189° W (Front Porch, ±1.8m accuracy)",
            "photo_pod_url": "/static/evidence/pod_FDX-99281-US.jpg",
            "carrier_proof_valid": True
        },
        "UPS-1Z9999999999999999": {
            "carrier_name": "UPS Worldwide Express",
            "tracking_number": "UPS-1Z9999999999999999",
            "ship_date": "2026-10-18T11:00:00Z",
            "delivery_date": "2026-10-20T16:05:12Z",
            "delivery_status": "DELIVERED",
            "delivery_address": {
                "street": "450 Serra Mall, Bldg 500",
                "city": "Stanford",
                "state": "CA",
                "postal_code": "94305",
                "country_code": "US"
            },
            "recipient_signed_by": "J. DOE (Dock Master / Stanford Receiving)",
            "delivery_gps": "37.4275° N, 122.1697° W (Authorized Mailroom)",
            "photo_pod_url": "/static/evidence/pod_UPS-1Z999.jpg",
            "carrier_proof_valid": True
        },
        "DHL-7718291029": {
            "carrier_name": "DHL Express Global",
            "tracking_number": "DHL-7718291029",
            "ship_date": "2026-10-10T08:30:00Z",
            "delivery_date": "2026-10-13T10:15:00Z",
            "delivery_status": "DELIVERED",
            "delivery_address": {
                "street": "100 Innovation Way, Suite 400",
                "city": "Austin",
                "state": "TX",
                "postal_code": "78701",
                "country_code": "US"
            },
            "recipient_signed_by": "A. MERCER (Electronic Stylus Signature)",
            "delivery_gps": "30.2672° N, 97.7431° W (Reception Desk)",
            "photo_pod_url": "/static/evidence/pod_DHL-771829.jpg",
            "carrier_proof_valid": True
        },
        "FDX-LOST-00192": {
            "carrier_name": "FedEx Ground",
            "tracking_number": "FDX-LOST-00192",
            "ship_date": "2026-10-19T14:00:00Z",
            "delivery_date": "2026-10-22T19:00:00Z",
            "delivery_status": "EXCEPTION_LOST_IN_TRANSIT",
            "delivery_address": {
                "street": "1200 Market Street",
                "city": "Philadelphia",
                "state": "PA",
                "postal_code": "19107",
                "country_code": "US"
            },
            "recipient_signed_by": None,
            "delivery_gps": None,
            "photo_pod_url": None,
            "carrier_proof_valid": False
        }
    }

    @classmethod
    def get_carrier_telemetry(cls, tracking_number: str, fallback_address: Optional[Address] = None) -> Optional[CarrierTelemetry]:
        """Fetch real-time carrier telemetry and POD verification."""
        data = cls._MOCK_DATABASE.get(tracking_number)
        if not data:
            # Generate deterministic fallback telemetry if unknown tracking number
            h = int(hashlib.md5(tracking_number.encode()).hexdigest()[:6], 16)
            is_valid = (h % 5 != 0)  # 80% valid
            addr = fallback_address.model_dump() if fallback_address else {
                "street": "101 Metro Blvd", "city": "Seattle", "state": "WA", "postal_code": "98101", "country_code": "US"
            }
            return CarrierTelemetry(
                carrier_name="FedEx Priority" if h % 2 == 0 else "UPS Ground",
                tracking_number=tracking_number,
                ship_date="2026-10-15T10:00:00Z",
                delivery_date="2026-10-17T15:30:00Z" if is_valid else "2026-10-24T00:00:00Z",
                delivery_status="DELIVERED" if is_valid else "IN_TRANSIT",
                delivery_address=Address(**addr),
                recipient_signed_by="VERIFIED RECIPIENT SIGNATURE" if is_valid else None,
                delivery_gps="37.7749° N, 122.4194° W (Delivery Geo-pin)" if is_valid else None,
                photo_pod_url=f"/static/evidence/pod_{tracking_number}.jpg" if is_valid else None,
                carrier_proof_valid=is_valid
            )

        return CarrierTelemetry(
            carrier_name=data["carrier_name"],
            tracking_number=data["tracking_number"],
            ship_date=data["ship_date"],
            delivery_date=data["delivery_date"],
            delivery_status=data["delivery_status"],
            delivery_address=Address(**data["delivery_address"]),
            recipient_signed_by=data["recipient_signed_by"],
            delivery_gps=data["delivery_gps"],
            photo_pod_url=data["photo_pod_url"],
            carrier_proof_valid=data["carrier_proof_valid"]
        )
