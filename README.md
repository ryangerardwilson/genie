# Step 1: Quick Start

Just run main.py. It hardcodes a lead's lat/lng (some spot in East Delhi, because why not). It'll spit out synthetic partners, filter them, run a basic model, and visualize stuff. No fancy args; tweak the code if you care.

# Step 2: Check the Maps

After running, peek at the PNGs in `synthetic_partner_portfolio_maps/`. Each partner's portfolio is plotted around the lead—customers in blue, splitters in green, interested leads in orange, with the new lead as a red star. Notice how it mimics real-world crap: clustered points like urban density, outliers because life sucks, and circles for 100m/200m/500m radii. Realistic enough to fool a manager.

# Step 3: Simulate Dense vs. Sparse Areas and Business Logic Based Filters

- The `SyntheticDataSeeder` init lets you control chaos. Crank up `num_partners`, customers, splitters, etc., and `tighten cluster_sigma_m` values for dense urban hellholes. Loosen them and drop counts for sparse rural areas. Outlier rates add that "unexpected BS" factor. 
- `business_filter.py` is the gatekeeper before the model. It filters notifiable partners purely on business rules: 500m radius cutoff, plus 100m/200m tweaks for high-competition zones (e.g., if >5 unique partners in 200m or >=3 in 100m, it caps and sorts additions). No ML fluff here—just logic to avoid notifying every idiot in town.

# Step 4: Enhance the Model: Bare-Bones right now

In main.py, the MatchMakingModel is minimalistic: it scores partners by inverse distance (preferring recent leads), normalizes to [0,1], and ranks descending. It works, but enhance it — add weights for tenure, installation speed, active/inactive ratios, or whatever. Make it return a smarter rank order; right now, it's just not sucking completely.

