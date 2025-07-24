from typing import List, Tuple, NamedTuple
from datetime import date, timedelta

class Location(NamedTuple):
    lat: float
    lng: float
    address: str

class Lead(NamedTuple):
    mobile: str
    location: Location

class Customer(NamedTuple):
    mobile: str
    plan_expiry_dt: date
    location: Location

class Partner(NamedTuple):
    long_lco_account_id: int
    zone: str
    active_customers: List[Customer]
    inactive_but_geographically_relevant_customers: List[Customer]
    competitor_connections_within_polygon: int
    polygon_area_in_sq_mt: float
    recent_leads_interested_in: List[Lead]
    tenure: int
