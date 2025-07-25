from typing import List, Tuple, NamedTuple
from datetime import date, timedelta

class Location(NamedTuple):
    lat: float
    lng: float

class Lead(NamedTuple):
    mobile: str
    location: Location

class Customer(NamedTuple):
    mobile: str
    address: str
    plan_expiry_dt: date
    location: Location
    installation_speed_in_hrs: int

class Partner(NamedTuple):
    long_lco_account_id: int
    zone: str
    active_customers: List[Customer]
    inactive_but_geographically_relevant_customers: List[Customer]
    recent_leads_interested_in: List[Lead]
    splitters: List[Location]
    tenure: int
