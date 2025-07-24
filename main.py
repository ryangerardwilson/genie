from typing import List, Tuple
from datetime import date, timedelta
from math import radians, sin, cos, sqrt, atan2
from pprint import pprint
import random

from models import Location, Lead, Customer, Partner
from dummy_data_seeder import DummyDataSeeder
from output_visualizer import OutputVisualizer
from business_filter import BusinessFilter

class MatchMakingModel:
    def __init__(self, partners: List[Partner]) -> None:
        self.partners = partners

    def match(self, lead: Lead) -> List[Tuple[Partner, float]]:
        def haversine(loc1: Location, loc2: Location) -> float:
            R = 6371000  # Earth radius in meters
            lat1, lon1 = radians(loc1.lat), radians(loc1.lng)
            lat2, lon2 = radians(loc2.lat), radians(loc2.lng)
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            return R * c

        candidates = []
        for partner in self.partners:
            all_locations = (
                [c.location for c in partner.active_customers] +
                [c.location for c in partner.inactive_but_geographically_relevant_customers] +
                [l.location for l in partner.recent_leads_interested_in]
            )
            if not all_locations:
                continue  # Skip partners with no reference locations

            min_dist_all = min(haversine(lead.location, loc) for loc in all_locations)
            if min_dist_all > 500:
                continue  # Not within 500m

            # Compute score: prefer closest recent lead, fallback to closest customer
            recent_locs = [l.location for l in partner.recent_leads_interested_in]
            customer_locs = (
                [c.location for c in partner.active_customers] +
                [c.location for c in partner.inactive_but_geographically_relevant_customers]
            )
            if recent_locs:
                min_dist = min(haversine(lead.location, loc) for loc in recent_locs)
            elif customer_locs:
                min_dist = min(haversine(lead.location, loc) for loc in customer_locs)
            else:
                continue  # Shouldn't reach here due to all_locations check

            score = 1 / (1 + min_dist / 500)  # Normalize; tweak divisor if you want different sensitivity

            candidates.append((partner, score))

        # Sort by score descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates

# Example usage to test
if __name__ == "__main__":

    # Instantiate with center coords (old East Delhi average)
    lead_lat=28.65
    lead_lng=77.275
    lead_mobile="+91333333333"

    seeder = DummyDataSeeder(center_lat=lead_lat, center_lng=lead_lng)
    partners = seeder.seed()
    business_filter = BusinessFilter(partners)
    # Sample lead near center
    sample_location = Location(lat=lead_lat, lng=lead_lng, address="Sample Center")
    sample_lead = Lead(mobile=lead_mobile, location=sample_location)
    notified = business_filter.notified_partners(sample_lead)
    model = MatchMakingModel(notified)
    matches = model.match(sample_lead)
    pprint(matches)  # Pretty print the full matches

    # Simple list of partners and their probability scores
    simple_list = [
        {"partner_id": partner.long_lco_account_id, "score": round(score, 4)}
        for partner, score in matches
    ]
    print("\nSimple list of partners and scores:")
    pprint(simple_list)

    visualizer = OutputVisualizer(partners)
    visualizer.visualize(sample_lead)
