from disputeshield.carrier_client import CarrierTelemetryClient

def test_harvest_valid_fedex_pod():
    """Tests carrier telemetry harvesting for a delivered FedEx shipment."""
    telemetry = CarrierTelemetryClient.get_carrier_telemetry("FDX-99281-US")
    
    assert "FedEx" in telemetry.carrier_name
    assert telemetry.delivery_status == "DELIVERED"
    assert telemetry.carrier_proof_valid is True
    assert telemetry.recipient_signed_by is not None
    assert "GPS" in telemetry.delivery_gps or "°" in telemetry.delivery_gps

def test_harvest_lost_in_transit():
    """Tests carrier exception detection when a package is lost in transit."""
    telemetry = CarrierTelemetryClient.get_carrier_telemetry("FDX-LOST-00192")
    
    assert telemetry.carrier_proof_valid is False
    assert "LOST" in telemetry.delivery_status or "EXCEPTION" in telemetry.delivery_status
