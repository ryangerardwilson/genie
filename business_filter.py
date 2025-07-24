from typing import List
from math import radians, sin, cos, sqrt, atan2

from models import Location, Lead, Customer, Partner

class BusinessFilter:
    def __init__(self, partners: List[Partner], x: int = 5) -> None:
        self.partners = partners
        self.x = x

    def haversine(self, loc1: Location, loc2: Location) -> float:
        R = 6371000  # Earth radius in meters
        lat1, lon1 = radians(loc1.lat), radians(loc1.lng)
        lat2, lon2 = radians(loc2.lat), radians(loc2.lng)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def get_locations(self, partner: Partner) -> List[Location]:
        return (
            [c.location for c in partner.active_customers] +
            [c.location for c in partner.inactive_but_geographically_relevant_customers] +
            [l.location for l in partner.recent_leads_interested_in]
        )

    def min_distance(self, lead_loc: Location, partner: Partner) -> float:
        locs = self.get_locations(partner)
        if not locs:
            return float('inf')
        return min(self.haversine(lead_loc, loc) for loc in locs)

    def notified_partners(self, lead: Lead) -> List[Partner]:
        lead_loc = lead.location
        # Eligible: partners with min_dist <= 500m (rule a)
        eligible = [p for p in self.partners if self.min_distance(lead_loc, p) <= 500]
        if not eligible:
            return []

        # Check competition: unique partners with customers within 200m
        unique_partner_ids = set()
        for p in self.partners:
            for c in p.active_customers + p.inactive_but_geographically_relevant_customers:
                if self.haversine(lead_loc, c.location) <= 200:
                    unique_partner_ids.add(p.long_lco_account_id)
                    break  # No need to check further for this partner

        # Additional check: partners within 100m
        partners_within_100 = [p for p in self.partners if self.min_distance(lead_loc, p) <= 100]

        high_comp = (len(unique_partner_ids) > 5) or (len(partners_within_100) >= 3)

        # Print the competition level for this location
        print(f"Location deemed {'high' if high_comp else 'low'} competition")

        if not high_comp:
            # Low comp: just return all eligible (no scoring here)
            return eligible

        else:
            # High comp (rule b): all partners within 200m
            within_200 = [p for p in eligible if self.min_distance(lead_loc, p) <= 200]
            num_within = len(within_200)
            if num_within >= 10:
                return within_200

            # Less than 10: add up to x additional from remaining, sorted by min_dist
            remaining = [p for p in eligible if p not in within_200]
            remaining_sorted = sorted(remaining, key=lambda p: self.min_distance(lead_loc, p))
            num_add = min(10 - num_within, self.x, len(remaining_sorted))
            additional = remaining_sorted[:num_add]
            return within_200 + additional
