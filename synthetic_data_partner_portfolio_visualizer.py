# ~/Apps/genie/synthetic_data_partner_portfolio_visualizer.py
from typing import List
import os
import shutil
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from math import radians, cos

from models import Partner, Lead, Location

class SyntheticDataPartnerPortfolioVisualizer:
    def __init__(self, partners: List[Partner]) -> None:
        self.partners = partners

    def visualize(self, lead: Lead) -> None:
        dir_path = "synthetic_partner_portfolio_maps"
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        os.makedirs(dir_path)

        ref_lat_rad = radians(lead.location.lat)
        deg_to_m_lat = 111000  # approx meters per degree lat
        deg_to_m_lng = 111000 * cos(ref_lat_rad)  # meters per degree lng at this lat

        for partner in self.partners:
            fig, ax = plt.subplots()

            # Customers (active + inactive) in blue
            customer_locs = (
                [c.location for c in partner.active_customers] +
                [c.location for c in partner.inactive_but_geographically_relevant_customers]
            )
            customer_xs = [(loc.lng - lead.location.lng) * deg_to_m_lng for loc in customer_locs]
            customer_ys = [(loc.lat - lead.location.lat) * deg_to_m_lat for loc in customer_locs]
            if customer_xs:
                ax.scatter(customer_xs, customer_ys, c='blue', alpha=0.6, s=20, label='Customers')

            # Splitters in green
            splitter_xs = [(loc.lng - lead.location.lng) * deg_to_m_lng for loc in partner.splitters]
            splitter_ys = [(loc.lat - lead.location.lat) * deg_to_m_lat for loc in partner.splitters]
            if splitter_xs:
                ax.scatter(splitter_xs, splitter_ys, c='green', alpha=0.6, s=20, label='Splitters')

            # Recent leads of interest in orange
            interest_lead_locs = [l.location for l in partner.recent_leads_interested_in]
            interest_lead_xs = [(loc.lng - lead.location.lng) * deg_to_m_lng for loc in interest_lead_locs]
            interest_lead_ys = [(loc.lat - lead.location.lat) * deg_to_m_lat for loc in interest_lead_locs]
            if interest_lead_xs:
                ax.scatter(interest_lead_xs, interest_lead_ys, c='orange', alpha=0.6, s=20, label='Interested Leads')

            # New lead at (0,0) in red star
            ax.scatter(0, 0, c='red', marker='*', s=200, label='New Lead')

            # Add circles
            circle_500 = Circle((0, 0), 500, color='black', fill=False, linewidth=2)
            ax.add_patch(circle_500)
            circle_200 = Circle((0, 0), 200, color='black', fill=False, linewidth=1, linestyle='--')
            ax.add_patch(circle_200)
            circle_100 = Circle((0, 0), 100, color='black', fill=False, linewidth=1, linestyle='--')
            ax.add_patch(circle_100)

            ax.set_xlabel('Meters East')
            ax.set_ylabel('Meters North')
            ax.set_title(f'Portfolio Map for Partner {partner.long_lco_account_id}')
            ax.set_aspect('equal')

            # Auto-set limits based on points, min 750m
            all_xs = customer_xs + splitter_xs + interest_lead_xs + [0]
            all_ys = customer_ys + splitter_ys + interest_lead_ys + [0]
            if all_xs:
                max_dist = max(
                    max(abs(x) for x in all_xs if all_xs),
                    max(abs(y) for y in all_ys if all_ys)
                ) * 1.1
                max_dist = max(max_dist, 750)
                ax.set_xlim(-max_dist, max_dist)
                ax.set_ylim(-max_dist, max_dist)
            else:
                ax.set_xlim(-750, 750)
                ax.set_ylim(-750, 750)

            ax.legend()

            # Save plot
            fig.savefig(os.path.join(dir_path, f'partner_{partner.long_lco_account_id}.png'))
            plt.close(fig)

        print(f"Partner portfolio maps saved to {dir_path}/")
