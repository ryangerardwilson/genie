# ~/Apps/genie/synthetic_data_seeder.py
from typing import List
from datetime import date, timedelta
import random
from math import radians, sin, cos, sqrt, atan2, pi

# Import the NamedTuples from models
from models import Location, Lead, Customer, Partner

class SyntheticDataSeeder:
    def __init__(self, center_lat: float, center_lng: float, radius: float = 1000.0):
        self.center_lat = center_lat
        self.center_lng = center_lng
        self.radius = radius
        self.outer_radius = radius * 2.0
        self.num_partners = 10
        self.recent_lead_locations = 50  # Number of unique recent lead locations (and leads)
        self.customers = 20  # Number of unique customers
        self.splitter_locations = 30  # Number of unique splitter locations
        self.customer_cluster_sigma_m = 50.0
        self.lead_cluster_sigma_m = 200.0
        self.splitter_cluster_sigma_m = 100.0
        self.outlier_rate = 0.02
        self.special_outlier_rate = 0.10

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

    def generate_gaussian_locations(self, num: int, center: Location, sigma_m: float, min_dist: float = 5.0) -> List[Location]:
        locations = []
        center_lat_rad = radians(center.lat)
        sigma_lat = sigma_m / 111000.0
        sigma_lng = sigma_lat / cos(center_lat_rad) if cos(center_lat_rad) != 0 else sigma_lat
        while len(locations) < num:
            delta_lat = random.gauss(0, sigma_lat)
            delta_lng = random.gauss(0, sigma_lng)
            candidate_lat = round(center.lat + delta_lat, 6)
            candidate_lng = round(center.lng + delta_lng, 6)
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
        # Decide random % of partners to have centers outside
        random_perc = random.randint(0, 50)
        num_outside = round(self.num_partners * random_perc / 100)
        partner_indices = list(range(self.num_partners))
        random.shuffle(partner_indices)
        outside_indices = set(partner_indices[:num_outside])
        inside_indices = set(partner_indices[num_outside:])

        # Generate partner centers
        partner_centers_inside = self.generate_locations(len(inside_indices), 0.0, self.radius, min_dist=100.0)
        partner_centers_outside = self.generate_locations(len(outside_indices), self.radius, self.outer_radius, min_dist=100.0)

        # Function to generate uneven counts summing to total
        def generate_counts(total: int, n: int) -> List[int]:
            if total == 0:
                return [0] * n
            base = total // n
            variation = max(1, base // 2)
            counts = [random.randint(max(0, base - variation), base + variation) for _ in range(n - 1)]
            counts.append(total - sum(counts))
            if counts[-1] < 0:
                counts[-1] = 0
            return counts

        # Generate counts for leads, customers, and splitters
        lead_counts = generate_counts(self.recent_lead_locations, self.num_partners)
        customer_counts = generate_counts(self.customers, self.num_partners)
        splitter_counts = generate_counts(self.splitter_locations, self.num_partners)

        # Helper to generate fake Indian mobile
        def fake_mobile():
            return "+91" + "".join(random.choice("0123456789") for _ in range(9))

        # Current date
        current_date = date(2025, 7, 25)

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

        partners = []
        inside_idx = outside_idx = 0
        for i in range(self.num_partners):
            if i in outside_indices:
                partner_center = partner_centers_outside[outside_idx]
                outside_idx += 1
            else:
                partner_center = partner_centers_inside[inside_idx]
                inside_idx += 1

            # Generate recent leads
            lead_locs = self.generate_gaussian_locations(lead_counts[i], partner_center, self.lead_cluster_sigma_m)
            recent_leads = [generate_lead(loc) for loc in lead_locs]

            # Generate splitters
            splitters = self.generate_gaussian_locations(splitter_counts[i], partner_center, self.splitter_cluster_sigma_m)

            # Generate customers
            customer_locs = self.generate_gaussian_locations(customer_counts[i], partner_center, self.customer_cluster_sigma_m)
            # Uneven active/inactive: roughly half, but varied
            num_cust = customer_counts[i]
            if num_cust > 0:
                base_active = num_cust // 2
                variation = max(1, base_active // 2)
                num_active = random.randint(max(0, base_active - variation), min(num_cust, base_active + variation))
            else:
                num_active = 0
            active_locs = random.sample(customer_locs, num_active)
            inactive_locs = [loc for loc in customer_locs if loc not in active_locs]
            active_customers = [generate_customer(True, loc, f"Partner {i} Active Location") for loc in active_locs]
            inactive_customers = [generate_customer(False, loc, f"Partner {i} Inactive Location") for loc in inactive_locs]

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

        # Now handle outliers, including special cases for the 10% requirement
        all_customers = []
        for p in partners:
            all_customers.extend(p.active_customers)
            all_customers.extend(p.inactive_but_geographically_relevant_customers)
        total_cust = len(all_customers)
        num_outliers = round(self.outlier_rate * total_cust)

        # Compute natural candidates (partners with any point <=500m from lead)
        lead_loc = Location(lat=self.center_lat, lng=self.center_lng)
        natural_candidates = []
        for p in partners:
            all_locs = (
                [c.location for c in p.active_customers] +
                [c.location for c in p.inactive_but_geographically_relevant_customers] +
                [l.location for l in p.recent_leads_interested_in] +
                p.splitters
            )
            if all_locs:
                min_d = min(self.haversine(lead_loc, loc) for loc in all_locs)
                if min_d <= 500:
                    natural_candidates.append(p)

        n_natural = len(natural_candidates)
        # Calculate num_special for >=10% where closest is outlier
        if n_natural == 0:
            num_special = 0
        else:
            num_special = max(1, int((self.special_outlier_rate * n_natural) / (1 - self.special_outlier_rate)))

        non_candidates = [p for p in partners if p not in natural_candidates]
        if len(non_candidates) < num_special:
            num_special = len(non_candidates)
        special_partners = random.sample(non_candidates, num_special) if num_special > 0 else []

        # Apply special outliers: move one customer per special partner close to lead
        outlier_customers = []
        for sp in special_partners:
            sp_customers = sp.active_customers + sp.inactive_but_geographically_relevant_customers
            if not sp_customers:
                continue
            cust = random.choice(sp_customers)
            # Generate location within 100m of lead
            close_locs = self.generate_locations(1, 0.0, 100.0, min_dist=0.0)
            new_loc = close_locs[0]
            new_cust = Customer(
                mobile=cust.mobile,
                address=cust.address,
                plan_expiry_dt=cust.plan_expiry_dt,
                location=new_loc,
                installation_speed_in_hrs=cust.installation_speed_in_hrs
            )
            if cust in sp.active_customers:
                idx = sp.active_customers.index(cust)
                sp.active_customers[idx] = new_cust
            else:
                idx = sp.inactive_but_geographically_relevant_customers.index(cust)
                sp.inactive_but_geographically_relevant_customers[idx] = new_cust
            outlier_customers.append(new_cust)

        # Apply remaining regular outliers: move to far away (2000-10000m)
        remaining_outliers = num_outliers - len(outlier_customers)
        if remaining_outliers > 0:
            possible_cust = [c for c in all_customers if c not in outlier_customers]
            if len(possible_cust) < remaining_outliers:
                remaining_outliers = len(possible_cust)
            selected = random.sample(possible_cust, remaining_outliers)
            for cust in selected:
                far_locs = self.generate_locations(1, 2000.0, 10000.0, min_dist=0.0)
                new_loc = far_locs[0]
                new_cust = Customer(
                    mobile=cust.mobile,
                    address=cust.address,
                    plan_expiry_dt=cust.plan_expiry_dt,
                    location=new_loc,
                    installation_speed_in_hrs=cust.installation_speed_in_hrs
                )
                # Replace in partner
                replaced = False
                for p in partners:
                    if cust in p.active_customers:
                        idx = p.active_customers.index(cust)
                        p.active_customers[idx] = new_cust
                        replaced = True
                        break
                    elif cust in p.inactive_but_geographically_relevant_customers:
                        idx = p.inactive_but_geographically_relevant_customers.index(cust)
                        p.inactive_but_geographically_relevant_customers[idx] = new_cust
                        replaced = True
                        break
                if replaced:
                    outlier_customers.append(new_cust)

        return partners
