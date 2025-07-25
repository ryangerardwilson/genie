# ~/Apps/genie/dummy_data_seeder.py
from typing import List
from datetime import date, timedelta
import random
from math import radians, sin, cos, sqrt, atan2, pi

# Import the NamedTuples from models
from models import Location, Lead, Customer, Partner

class DummyDataSeeder:
    def __init__(self, center_lat: float, center_lng: float, radius: float = 1000.0):
        self.center_lat = center_lat
        self.center_lng = center_lng
        self.radius = radius
        self.outer_radius = radius * 2.0
        self.num_partners = 10
        self.recent_lead_locations = 50  # Number of unique recent lead locations (and leads)
        self.customers = 20  # Number of unique customers
        self.splitter_locations = 30  # Number of unique splitter locations

        # Set seed for reproducibility, you unpredictable moron
        random.seed(42)

    def generate_locations(self, num: int, r_min: float, r_max: float, min_dist: float = 30.0) -> List[Location]:
        locations = []
        center_lat_rad = radians(self.center_lat)
        while len(locations) < num:
            theta = random.uniform(0, 2 * pi)
            u = random.uniform(0, 1)
            r_squared = u * (r_max**2 - r_min**2) + r_min**2
            r = sqrt(r_squared)
            delta_x = r * cos(theta)
            delta_y = r * sin(theta)
            delta_lat = delta_y / 111000.0
            delta_lng = delta_x / (111000.0 * cos(center_lat_rad))
            candidate_lat = round(self.center_lat + delta_lat, 6)
            candidate_lng = round(self.center_lng + delta_lng, 6)
            candidate = Location(
                lat=candidate_lat,
                lng=candidate_lng
            )
            if all(self.haversine(candidate, loc) >= min_dist for loc in locations):
                locations.append(candidate)
        return locations

    def haversine(self, loc1: Location, loc2: Location) -> float:
        R = 6371000  # Earth radius in meters
        lat1, lon1 = radians(loc1.lat), radians(loc1.lng)
        lat2, lon2 = radians(loc2.lat), radians(loc2.lng)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def seed(self) -> List[Partner]:
        center = Location(lat=self.center_lat, lng=self.center_lng)

        # Decide random % of partners to have locations outside
        random_perc = random.randint(0, 50)
        num_outside = round(self.num_partners * random_perc / 100)
        partner_indices = list(range(self.num_partners))
        random.shuffle(partner_indices)
        outside_indices = set(partner_indices[:num_outside])
        inside_indices = set(partner_indices[num_outside:])

        # Helper to generate fake Indian mobile
        def fake_mobile():
            return "+91" + "".join(random.choice("0123456789") for _ in range(9))

        # Current date
        current_date = date(2025, 7, 24)

        # Generate customer with given location and address
        def generate_customer(is_active: bool, location: Location, address: str) -> Customer:
            if is_active:
                expiry = current_date + timedelta(days=random.randint(1, 730))
            else:
                expiry = current_date - timedelta(days=random.randint(1, 365))
            return Customer(
                mobile=fake_mobile(),
                address=address,
                plan_expiry_dt=expiry,
                location=location,
                installation_speed_in_hrs=random.randint(2, 150)
            )

        # Generate lead with given location
        def generate_lead(location: Location) -> Lead:
            return Lead(
                mobile=fake_mobile(),
                location=location
            )

        # Function to generate uneven counts summing to total
        def generate_counts(total: int, n: int) -> List[int]:
            if total == 0:
                return [0] * n
            base = total // n
            variation = max(1, base // 2)  # Adjust variation based on base
            counts = [random.randint(max(0, base - variation), base + variation) for _ in range(n - 1)]
            counts.append(total - sum(counts))
            # Fix if last is negative (rare, but handle)
            if counts[-1] < 0:
                counts[-1] = 0
            return counts

        # Generate counts for leads, customers, and splitters
        lead_counts = generate_counts(self.recent_lead_locations, self.num_partners)
        customer_counts = generate_counts(self.customers, self.num_partners)
        splitter_counts = generate_counts(self.splitter_locations, self.num_partners)

        # Generate lead locations and leads
        lead_inside_num = sum(lead_counts[i] for i in inside_indices)
        lead_outside_num = sum(lead_counts[i] for i in outside_indices)
        lead_locs_inside = self.generate_locations(lead_inside_num, 0.0, self.radius)
        lead_locs_outside = self.generate_locations(lead_outside_num, self.radius, self.outer_radius)
        all_recent_leads_inside = [generate_lead(loc) for loc in lead_locs_inside]
        all_recent_leads_outside = [generate_lead(loc) for loc in lead_locs_outside]
        random.shuffle(all_recent_leads_inside)
        random.shuffle(all_recent_leads_outside)

        # Generate customer locations and customers
        customer_inside_num = sum(customer_counts[i] for i in inside_indices)
        customer_outside_num = sum(customer_counts[i] for i in outside_indices)
        customer_locs_inside = self.generate_locations(customer_inside_num, 0.0, self.radius)
        customer_locs_outside = self.generate_locations(customer_outside_num, self.radius, self.outer_radius)
        all_customers_inside = [generate_customer(random.choice([True, False]), loc, f"Inside Location {idx}") for idx, loc in enumerate(customer_locs_inside)]
        all_customers_outside = [generate_customer(random.choice([True, False]), loc, f"Outside Location {idx}") for idx, loc in enumerate(customer_locs_outside)]

        # Generate splitter locations
        splitter_inside_num = sum(splitter_counts[i] for i in inside_indices)
        splitter_outside_num = sum(splitter_counts[i] for i in outside_indices)
        splitter_locs_inside = self.generate_locations(splitter_inside_num, 0.0, self.radius)
        splitter_locs_outside = self.generate_locations(splitter_outside_num, self.radius, self.outer_radius)
        all_splitters_inside = splitter_locs_inside
        all_splitters_outside = splitter_locs_outside
        random.shuffle(all_splitters_inside)
        random.shuffle(all_splitters_outside)

        # Separate active and inactive customers
        all_active_customers_inside = [c for c in all_customers_inside if c.plan_expiry_dt > current_date]
        all_inactive_customers_inside = [c for c in all_customers_inside if c.plan_expiry_dt <= current_date]
        all_active_customers_outside = [c for c in all_customers_outside if c.plan_expiry_dt > current_date]
        all_inactive_customers_outside = [c for c in all_customers_outside if c.plan_expiry_dt <= current_date]

        # Shuffle customers
        random.shuffle(all_active_customers_inside)
        random.shuffle(all_inactive_customers_inside)
        random.shuffle(all_active_customers_outside)
        random.shuffle(all_inactive_customers_outside)

        # Generate uneven counts for active/inactive per group
        num_inside = len(inside_indices)
        num_outside = len(outside_indices)
        active_counts_inside = generate_counts(len(all_active_customers_inside), num_inside) if num_inside > 0 else []
        inactive_counts_inside = generate_counts(len(all_inactive_customers_inside), num_inside) if num_inside > 0 else []
        active_counts_outside = generate_counts(len(all_active_customers_outside), num_outside) if num_outside > 0 else []
        inactive_counts_outside = generate_counts(len(all_inactive_customers_outside), num_outside) if num_outside > 0 else []

        # Prepare indices
        lead_index_inside = lead_index_outside = 0
        active_index_inside = active_index_outside = 0
        inactive_index_inside = inactive_index_outside = 0
        splitter_index_inside = splitter_index_outside = 0
        inside_partner_idx = outside_partner_idx = 0

        partners = []
        for i in range(self.num_partners):
            if i in outside_indices:
                recent_leads = all_recent_leads_outside[lead_index_outside : lead_index_outside + lead_counts[i]]
                lead_index_outside += lead_counts[i]
                active_customers = all_active_customers_outside[active_index_outside : active_index_outside + active_counts_outside[outside_partner_idx]]
                active_index_outside += active_counts_outside[outside_partner_idx]
                inactive_customers = all_inactive_customers_outside[inactive_index_outside : inactive_index_outside + inactive_counts_outside[outside_partner_idx]]
                inactive_index_outside += inactive_counts_outside[outside_partner_idx]
                splitters = all_splitters_outside[splitter_index_outside : splitter_index_outside + splitter_counts[i]]
                splitter_index_outside += splitter_counts[i]
                outside_partner_idx += 1
            else:
                recent_leads = all_recent_leads_inside[lead_index_inside : lead_index_inside + lead_counts[i]]
                lead_index_inside += lead_counts[i]
                active_customers = all_active_customers_inside[active_index_inside : active_index_inside + active_counts_inside[inside_partner_idx]]
                active_index_inside += active_counts_inside[inside_partner_idx]
                inactive_customers = all_inactive_customers_inside[inactive_index_inside : inactive_index_inside + inactive_counts_inside[inside_partner_idx]]
                inactive_index_inside += inactive_counts_inside[inside_partner_idx]
                splitters = all_splitters_inside[splitter_index_inside : splitter_index_inside + splitter_counts[i]]
                splitter_index_inside += splitter_counts[i]
                inside_partner_idx += 1

            partner = Partner(
                long_lco_account_id=1 + i,
                zone=f"Zone{i+1}",
                active_customers=active_customers,
                inactive_but_geographically_relevant_customers=inactive_customers,
                recent_leads_interested_in=recent_leads,
                splitters=splitters,
                tenure=random.randint(1, 10)
            )
            partners.append(partner)

        return partners
