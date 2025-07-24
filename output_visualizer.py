from typing import List
from math import radians, sin, cos, sqrt, atan2
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
import subprocess

from models import Partner, Lead, Location

class OutputVisualizer:
    def __init__(self, partners: List[Partner]) -> None:
        self.partners = partners

    def haversine(self, loc1: Location, loc2: Location) -> float:
        R = 6371000  # Earth radius in meters
        lat1, lon1 = radians(loc1.lat), radians(loc1.lng)
        lat2, lon2 = radians(loc2.lat), radians(loc2.lng)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return R * c

    def visualize(self, lead: Lead) -> None:
        # Collect unique customer locations (active + inactive)
        customer_locations = set()
        for partner in self.partners:
            for customer in partner.active_customers:
                customer_locations.add(customer.location)
            for customer in partner.inactive_but_geographically_relevant_customers:
                customer_locations.add(customer.location)

        # Collect unique recent lead locations
        recent_lead_locations = set()
        for partner in self.partners:
            for l in partner.recent_leads_interested_in:
                recent_lead_locations.add(l.location)

        customer_locations = list(customer_locations)
        recent_lead_locations = list(recent_lead_locations)

        # Compute distances for customers
        customer_dists = [self.haversine(lead.location, loc) for loc in customer_locations]
        # Filter close customers (within 1000m)
        close_customer_indices = [i for i, dist in enumerate(customer_dists) if dist <= 1000]
        close_customers = [customer_locations[i] for i in close_customer_indices]
        close_customer_dists = [customer_dists[i] for i in close_customer_indices]

        # Compute distances for recent leads
        recent_dists = [self.haversine(lead.location, loc) for loc in recent_lead_locations]
        # Filter close recent leads (within 1000m)
        close_recent_indices = [i for i, dist in enumerate(recent_dists) if dist <= 1000]
        close_recent = [recent_lead_locations[i] for i in close_recent_indices]
        close_recent_dists = [recent_dists[i] for i in close_recent_indices]

        # Collect nearest location per partner within 1000m
        nearest_locations = []
        for partner in self.partners:
            all_locs = (
                [c.location for c in partner.active_customers] +
                [c.location for c in partner.inactive_but_geographically_relevant_customers] +
                [l.location for l in partner.recent_leads_interested_in]
            )
            if not all_locs:
                continue
            dists = [self.haversine(lead.location, loc) for loc in all_locs]
            min_dist = min(dists)
            if min_dist > 1000:
                continue
            min_index = dists.index(min_dist)
            nearest_loc = all_locs[min_index]
            nearest_locations.append(nearest_loc)

        if not close_customer_indices and not close_recent_indices and not nearest_locations:
            print("No locations within 1000m. Nothing to plot.")
            return

        # Project to meters, with lead at (0,0)
        ref_lat_rad = radians(lead.location.lat)
        deg_to_m_lat = 111000  # approx meters per degree lat
        deg_to_m_lng = 111000 * cos(ref_lat_rad)  # meters per degree lng at this lat

        # Project customers
        customer_xs = []
        customer_ys = []
        for loc in close_customers:
            delta_lat = loc.lat - lead.location.lat
            delta_lng = loc.lng - lead.location.lng
            x = delta_lng * deg_to_m_lng
            y = delta_lat * deg_to_m_lat
            customer_xs.append(x)
            customer_ys.append(y)

        # Project recent leads
        recent_xs = []
        recent_ys = []
        for loc in close_recent:
            delta_lat = loc.lat - lead.location.lat
            delta_lng = loc.lng - lead.location.lng
            x = delta_lng * deg_to_m_lng
            y = delta_lat * deg_to_m_lat
            recent_xs.append(x)
            recent_ys.append(y)

        # Project nearest partner locations
        nearest_xs = []
        nearest_ys = []
        for loc in nearest_locations:
            delta_lat = loc.lat - lead.location.lat
            delta_lng = loc.lng - lead.location.lng
            x = delta_lng * deg_to_m_lng
            y = delta_lat * deg_to_m_lat
            nearest_xs.append(x)
            nearest_ys.append(y)

        # Plot
        fig, ax = plt.subplots()

        # Plot customers in green
        if customer_xs:
            ax.scatter(customer_xs, customer_ys, c='green', alpha=0.6, s=20, label='Customers')

        # Plot recent leads in blue
        if recent_xs:
            ax.scatter(recent_xs, recent_ys, c='blue', alpha=0.6, s=20, label='Recent Leads')

        # Plot nearest partner locations in red
        if nearest_xs:
            ax.scatter(nearest_xs, nearest_ys, c='red', alpha=0.6, s=30, label='Nearest Partner Locs')

        # Plot central lead in red star (keep it distinct)
        ax.scatter(0, 0, c='red', marker='*', s=200, label='New Lead')

        # Add 500m circle
        circle_500 = Circle((0, 0), 500, color='black', fill=False, linewidth=2)
        ax.add_patch(circle_500)

        # Add thin 200m circle
        circle_200 = Circle((0, 0), 200, color='black', fill=False, linewidth=1, linestyle='--')
        ax.add_patch(circle_200)

        # Add thin 100m circle
        circle_100 = Circle((0, 0), 100, color='black', fill=False, linewidth=1, linestyle='--')
        ax.add_patch(circle_100)

        ax.set_xlabel('Meters East')
        ax.set_ylabel('Meters North')
        ax.set_title('Map of Coordinates around Lead (customers green, recent leads blue, nearest partner locs red)')
        ax.set_aspect('equal')
        ax.set_xlim(-750, 750)
        ax.set_ylim(-750, 750)
        ax.legend()

        # Save to PNG instead of showing, because non-interactive backends are trash
        fig.savefig('lead_plot.png')
        print("Plot saved to lead_plot.png. Opening it with xdg-open...")

        # Open with xdg-open; if this fails, your env is broken—fix it
        subprocess.call(['xdg-open', 'lead_plot.png'])
