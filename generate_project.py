"""
Flipkart Analytics Hub - SQL Project Generator (v2 - Fixed)
===========================================================
Run:   python generate_project.py

Generates five files in the same directory:
    schema.sql        8-table database schema (unchanged structure, fixed data)
    sample_data.sql   Realistic Indian e-commerce data (Oct 2025 - Sep 2026)
    queries.sql       15 advanced analytical SQL queries (all v1 bugs fixed)
    validation.sql    13 integrity checks (every result must be bad_rows = 0)
    README.md         Accurate project documentation with real measured stats

Fixed issues vs v1
------------------
A - sample_data.sql
  1.  Users: 97 rows - all user_ids referenced by orders exist (v1 had orphan 91-95).
  2.  Every order has 1-4 order_items. orders.total_amount = SUM(qty*unit_price).
  3.  order_items.unit_price = product.price exactly (no discount rounding errors).
  4.  orders.region = user.region (derived, never inconsistent).
  5.  Status mix: ~77% Delivered, ~8% Cancelled, ~7% Returned, ~4% Shipped,
      ~2% Confirmed, ~2% Pending.
  6.  Returns only on Delivered/Returned orders. Every Returned order has a return row.
  7.  Reviews: only users who have a Delivered order for that product may review it.
  8.  sellers.total_products = actual product count per seller.
  9.  Dates cover Oct 2025 - Sep 2026; orders always after user signup_date.
      Festival spikes: Oct/Nov 2025, Jan 2026, Mar 2026, Aug 2026.
 10.  Payment: ~60% COD, ~20% UPI, ~20% Cards/Wallet (seed=42, deterministic).

B - queries.sql
  Q7  NTILE: direction corrected - score 5 = best. Champion = highest spenders.
  Q7/Q9: SET @as_of = MAX(order_date) replaces CURDATE() for reproducibility.
  Q9:  Cancelled orders excluded from purchase count (WHERE order_status <> 'Cancelled').
  Q13: NULLIF(total_orders,1) -> NULLIF(total_orders,0).
  Q14: Renamed "Time-to-First-Purchase & CLV". CTE rewritten to one row per user.
  Q15: order_status filter moved inside subquery (was in LEFT JOIN ON - had no effect).
  Q6/Q10: Returns pre-aggregated in CTE to prevent fan-out.
  Q3:  Comment updated to match actual ~60% COD share.
"""

import os, random
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict

RANDOM_SEED = 42
random.seed(RANDOM_SEED)

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def fmt_date(d):
    return d.strftime('%Y-%m-%d')

def D(v):
    return Decimal(str(v))

def rand_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(0, delta)))

def esc(s):
    return s.replace("'", "''")


# ---------------------------------------------------------------------------
# master data
# ---------------------------------------------------------------------------

USERS = [
    # North (ids 1-20)
    ('Aarav_Sharma',      'aarav.sharma@gmail.com',      'Delhi',         'North', '2023-01-15', 'VIP'),
    ('Priya_Gupta',       'priya.gupta@yahoo.com',        'Delhi',         'North', '2023-02-10', 'Premium'),
    ('Rohit_Verma',       'rohit.verma@outlook.com',      'Jaipur',        'North', '2023-03-05', 'Regular'),
    ('Sneha_Singh',       'sneha.singh@gmail.com',        'Lucknow',       'North', '2023-04-20', 'Regular'),
    ('Amit_Kumar',        'amit.kumar01@gmail.com',       'Delhi',         'North', '2023-05-12', 'Premium'),
    ('Kavita_Rao',        'kavita.rao@rediffmail.com',    'Chandigarh',    'North', '2023-06-08', 'Regular'),
    ('Vikas_Jain',        'vikas.jain@gmail.com',         'Noida',         'North', '2023-07-14', 'VIP'),
    ('Pooja_Mishra',      'pooja.mishra@gmail.com',       'Agra',          'North', '2023-08-25', 'Regular'),
    ('Deepak_Tiwari',     'deepak.tiwari@gmail.com',      'Lucknow',       'North', '2023-09-18', 'Regular'),
    ('Anjali_Saxena',     'anjali.saxena@gmail.com',      'Delhi',         'North', '2023-10-02', 'Premium'),
    ('Rahul_Pandey',      'rahul.pandey@gmail.com',       'Varanasi',      'North', '2023-11-15', 'Regular'),
    ('Nisha_Agarwal',     'nisha.agarwal@gmail.com',      'Noida',         'North', '2023-12-01', 'Regular'),
    ('Suresh_Yadav',      'suresh.yadav@gmail.com',       'Delhi',         'North', '2024-01-10', 'Regular'),
    ('Rekha_Dwivedi',     'rekha.dwivedi@gmail.com',      'Jaipur',        'North', '2024-02-14', 'Regular'),
    ('Manish_Trivedi',    'manish.trivedi@gmail.com',     'Agra',          'North', '2024-03-20', 'Regular'),
    ('Suman_Bhatt',       'suman.bhatt@gmail.com',        'Dehradun',      'North', '2024-04-05', 'Regular'),
    ('Ajay_Chauhan',      'ajay.chauhan@gmail.com',       'Jaipur',        'North', '2024-05-18', 'Regular'),
    ('Meena_Rawat',       'meena.rawat@gmail.com',        'Delhi',         'North', '2024-06-12', 'Premium'),
    ('Vijay_Pathak',      'vijay.pathak@gmail.com',       'Chandigarh',    'North', '2024-07-22', 'Regular'),
    ('Geeta_Shukla',      'geeta.shukla@gmail.com',       'Lucknow',       'North', '2024-08-08', 'Regular'),
    # South (ids 21-40)
    ('Arjun_Reddy',       'arjun.reddy@gmail.com',        'Hyderabad',     'South', '2023-01-20', 'VIP'),
    ('Lakshmi_Iyer',      'lakshmi.iyer@gmail.com',       'Chennai',       'South', '2023-02-28', 'Premium'),
    ('Karthik_Nair',      'karthik.nair@gmail.com',       'Bangalore',     'South', '2023-03-15', 'Regular'),
    ('Divya_Menon',       'divya.menon@gmail.com',        'Kochi',         'South', '2023-04-10', 'Regular'),
    ('Suresh_Pillai',     'suresh.pillai@gmail.com',      'Trivandrum',    'South', '2023-05-25', 'Regular'),
    ('Preethi_Rao',       'preethi.rao@gmail.com',        'Bangalore',     'South', '2023-06-18', 'Premium'),
    ('Venkat_Subbu',      'venkat.subbu@gmail.com',       'Chennai',       'South', '2023-07-08', 'Regular'),
    ('Ananya_Krishna',    'ananya.krishna@gmail.com',     'Hyderabad',     'South', '2023-08-14', 'VIP'),
    ('Ravi_Shankar',      'ravi.shankar@gmail.com',       'Mysore',        'South', '2023-09-05', 'Regular'),
    ('Poornima_Bhat',     'poornima.bhat@gmail.com',      'Mangalore',     'South', '2023-10-20', 'Regular'),
    ('Sunil_Varma',       'sunil.varma@gmail.com',        'Hyderabad',     'South', '2023-11-12', 'Regular'),
    ('Kavya_Prasad',      'kavya.prasad@gmail.com',       'Bangalore',     'South', '2023-12-08', 'Regular'),
    ('Naresh_Babu',       'naresh.babu@gmail.com',        'Visakhapatnam', 'South', '2024-01-15', 'Regular'),
    ('Sudha_Murthy',      'sudha.murthy99@gmail.com',     'Bangalore',     'South', '2024-02-20', 'VIP'),
    ('Ganesh_Rajan',      'ganesh.rajan@gmail.com',       'Coimbatore',    'South', '2024-03-14', 'Regular'),
    ('Meera_Pillai',      'meera.pillai@gmail.com',       'Kochi',         'South', '2024-04-28', 'Regular'),
    ('Arun_Kumar_S',      'arun.kumar.s@gmail.com',       'Chennai',       'South', '2024-05-10', 'Regular'),
    ('Sridevi_R',         'sridevi.r@gmail.com',          'Bangalore',     'South', '2024-06-22', 'Regular'),
    ('Prakash_K',         'prakash.k@gmail.com',          'Hyderabad',     'South', '2024-07-04', 'Regular'),
    ('Usha_Rani',         'usha.rani@gmail.com',          'Chennai',       'South', '2024-08-15', 'Regular'),
    # West (ids 41-60)
    ('Rahul_Mehta',       'rahul.mehta@gmail.com',        'Mumbai',        'West',  '2023-01-25', 'VIP'),
    ('Priya_Patel',       'priya.patel@gmail.com',        'Ahmedabad',     'West',  '2023-02-18', 'Premium'),
    ('Nikhil_Shah',       'nikhil.shah@gmail.com',        'Pune',          'West',  '2023-03-22', 'Regular'),
    ('Ruchi_Desai',       'ruchi.desai@gmail.com',        'Mumbai',        'West',  '2023-04-15', 'Regular'),
    ('Hardik_Trivedi',    'hardik.trivedi@gmail.com',     'Surat',         'West',  '2023-05-08', 'Regular'),
    ('Mira_Kapoor',       'mira.kapoor@gmail.com',        'Mumbai',        'West',  '2023-06-28', 'Premium'),
    ('Yash_Modi',         'yash.modi@gmail.com',          'Vadodara',      'West',  '2023-07-18', 'Regular'),
    ('Swati_Joshi',       'swati.joshi@gmail.com',        'Pune',          'West',  '2023-08-05', 'Regular'),
    ('Kiran_Parekh',      'kiran.parekh@gmail.com',       'Ahmedabad',     'West',  '2023-09-24', 'VIP'),
    ('Dipti_Kulkarni',    'dipti.kulkarni@gmail.com',     'Nagpur',        'West',  '2023-10-14', 'Regular'),
    ('Akash_Bhatt',       'akash.bhatt@gmail.com',        'Mumbai',        'West',  '2023-11-20', 'Regular'),
    ('Sonali_Thakur',     'sonali.thakur@gmail.com',      'Pune',          'West',  '2023-12-12', 'Regular'),
    ('Rohan_Sawant',      'rohan.sawant@gmail.com',       'Goa',           'West',  '2024-01-08', 'Regular'),
    ('Neha_Shirke',       'neha.shirke@gmail.com',        'Mumbai',        'West',  '2024-02-25', 'Regular'),
    ('Pramod_Naik',       'pramod.naik@gmail.com',        'Nashik',        'West',  '2024-03-18', 'Regular'),
    ('Smita_Chavan',      'smita.chavan@gmail.com',       'Pune',          'West',  '2024-04-10', 'Regular'),
    ('Tushar_Gaikwad',    'tushar.gaikwad@gmail.com',     'Aurangabad',    'West',  '2024-05-05', 'Regular'),
    ('Varsha_Patil',      'varsha.patil@gmail.com',       'Kolhapur',      'West',  '2024-06-15', 'Regular'),
    ('Aditya_Rane',       'aditya.rane@gmail.com',        'Mumbai',        'West',  '2024-07-10', 'Premium'),
    ('Sheetal_Londhe',    'sheetal.londhe@gmail.com',     'Pune',          'West',  '2024-08-20', 'Regular'),
    # East (ids 61-80)
    ('Sourav_Das',        'sourav.das@gmail.com',         'Kolkata',       'East',  '2023-01-30', 'VIP'),
    ('Rina_Chatterjee',   'rina.chatterjee@gmail.com',    'Kolkata',       'East',  '2023-02-22', 'Regular'),
    ('Bikash_Saha',       'bikash.saha@gmail.com',        'Bhubaneswar',   'East',  '2023-03-10', 'Regular'),
    ('Debojit_Roy',       'debojit.roy@gmail.com',        'Guwahati',      'East',  '2023-04-25', 'Regular'),
    ('Moumita_Sen',       'moumita.sen@gmail.com',        'Kolkata',       'East',  '2023-05-15', 'Regular'),
    ('Tanmoy_Ghosh',      'tanmoy.ghosh@gmail.com',       'Durgapur',      'East',  '2023-06-08', 'Regular'),
    ('Sanchita_Mondal',   'sanchita.mondal@gmail.com',    'Kolkata',       'East',  '2023-07-22', 'Premium'),
    ('Pritam_Banerjee',   'pritam.banerjee@gmail.com',    'Howrah',        'East',  '2023-08-18', 'Regular'),
    ('Anamika_Dutta',     'anamika.dutta@gmail.com',      'Siliguri',      'East',  '2023-09-12', 'Regular'),
    ('Krishanu_Pal',      'krishanu.pal@gmail.com',       'Kolkata',       'East',  '2023-10-28', 'Regular'),
    ('Sayani_Bose',       'sayani.bose@gmail.com',        'Asansol',       'East',  '2023-11-18', 'Regular'),
    ('Riju_Nath',         'riju.nath@gmail.com',          'Guwahati',      'East',  '2023-12-22', 'Regular'),
    ('Biplab_Mitra',      'biplab.mitra@gmail.com',       'Kolkata',       'East',  '2024-01-20', 'Regular'),
    ('Chandrani_Paul',    'chandrani.paul@gmail.com',     'Patna',         'East',  '2024-02-08', 'Regular'),
    ('Subhro_Saha',       'subhro.saha@gmail.com',        'Kolkata',       'East',  '2024-03-25', 'VIP'),
    ('Pampa_Roy',         'pampa.roy@gmail.com',          'Bhubaneswar',   'East',  '2024-04-15', 'Regular'),
    ('Niloy_Chakraborty', 'niloy.chakraborty@gmail.com',  'Kolkata',       'East',  '2024-05-08', 'Regular'),
    ('Supriya_Maity',     'supriya.maity@gmail.com',      'Siliguri',      'East',  '2024-06-18', 'Regular'),
    ('Arnab_Biswas',      'arnab.biswas@gmail.com',       'Kolkata',       'East',  '2024-07-28', 'Regular'),
    ('Debarati_Majhi',    'debarati.majhi@gmail.com',     'Ranchi',        'East',  '2024-08-12', 'Regular'),
    # Extra (ids 81-97) -- covers the orphan range 91-95 from v1
    ('Sahil_Khan',        'sahil.khan@gmail.com',         'Delhi',         'North', '2024-01-05', 'Regular'),
    ('Fatima_Shaikh',     'fatima.shaikh@gmail.com',      'Mumbai',        'West',  '2024-02-15', 'Regular'),
    ('Rajesh_Nair',       'rajesh.nair@gmail.com',        'Bangalore',     'South', '2024-03-08', 'Regular'),
    ('Asha_Ghosh',        'asha.ghosh@gmail.com',         'Kolkata',       'East',  '2024-04-22', 'Regular'),
    ('Mohan_Lal',         'mohan.lal@gmail.com',          'Delhi',         'North', '2024-05-30', 'Regular'),
    ('Sunita_Devi',       'sunita.devi@gmail.com',        'Patna',         'East',  '2024-06-05', 'Regular'),
    ('Vinod_Sharma',      'vinod.sharma@gmail.com',       'Jaipur',        'North', '2024-07-14', 'Regular'),
    ('Bhavna_Patel',      'bhavna.patel@gmail.com',       'Surat',         'West',  '2024-07-25', 'Regular'),
    ('Naveen_Gowda',      'naveen.gowda@gmail.com',       'Mysore',        'South', '2024-08-02', 'Regular'),
    ('Shalini_Khanna',    'shalini.khanna@gmail.com',     'Noida',         'North', '2024-08-18', 'Regular'),
    ('Ankit_Joshi',       'ankit.joshi@gmail.com',        'Pune',          'West',  '2024-09-01', 'Regular'),
    ('Deepika_Reddy',     'deepika.reddy@gmail.com',      'Hyderabad',     'South', '2024-09-10', 'Regular'),
    ('Sudhir_Das',        'sudhir.das@gmail.com',         'Kolkata',       'East',  '2024-09-15', 'Regular'),
    ('Prerna_Sharma',     'prerna.sharma@gmail.com',      'Delhi',         'North', '2024-10-01', 'Regular'),
    ('Kavitha_M',         'kavitha.m@gmail.com',          'Chennai',       'South', '2024-10-10', 'Regular'),
    ('Nilesh_Patil',      'nilesh.patil@gmail.com',       'Nagpur',        'West',  '2024-10-20', 'Regular'),
    ('Ritika_Bose',       'ritika.bose@gmail.com',        'Kolkata',       'East',  '2024-11-05', 'Regular'),
]

# seller_id 1-20; user_id references must exist in USERS
SELLERS_PROTO = [
    # (name, rating, established_date, user_id)
    ('TechZone Electronics',   4.8, '2020-05-15',  1),
    ('FashionFirst India',     4.6, '2019-08-20', 21),
    ('HomeDecor Plus',         4.5, '2021-02-10', 41),
    ('BooksWorld India',       4.9, '2018-11-01', 61),
    ('GadgetGuru Store',       4.7, '2020-03-25',  2),
    ('StyleHub Fashion',       4.4, '2021-06-18', 22),
    ('KitchenKing Supplies',   4.6, '2019-09-12', 42),
    ('ReadMore Books',         4.8, '2018-07-08', 62),
    ('SmartTech Solutions',    4.5, '2020-11-30',  3),
    ('TrendyWear Clothing',    4.3, '2022-01-15', 23),
    ('FurnitureMart Online',   4.7, '2019-04-22', 43),
    ('PageTurner Books',       4.6, '2018-03-18', 63),
    ('ElectroMart India',      4.9, '2017-12-05',  4),
    ('DesignerDen Fashion',    4.5, '2021-09-10', 24),
    ('HomeEssentials Store',   4.4, '2020-07-20', 44),
    ('AcademicBooks Hub',      4.7, '2017-05-28', 64),
    ('MobileZone India',       4.8, '2019-01-14',  5),
    ('EthnicWear Palace',      4.6, '2020-10-08', 25),
    ('ApplianceKing India',    4.5, '2021-03-22', 45),
    ('UrbanReads Books',       4.8, '2018-09-15', 65),
]

# product_id 1-50; (name, cat_id, seller_id, price, rating, stock, created_date)
PRODUCTS = [
    # cat 1 - Smartphones
    ('Samsung Galaxy S24 Ultra 256GB',      1,  1, 109999.00, 4.7,  45, '2024-02-01'),
    ('Apple iPhone 15 128GB',               1, 17,  79999.00, 4.8,  30, '2024-01-15'),
    ('OnePlus 12 256GB',                    1,  5,  64999.00, 4.6,  60, '2024-03-01'),
    ('Realme 12 Pro Plus 5G 256GB',         1, 13,  27999.00, 4.3,  80, '2024-04-01'),
    ('Redmi Note 13 Pro 5G 128GB',          1,  5,  19999.00, 4.4, 120, '2024-04-15'),
    # cat 2 - Laptops
    ('Apple MacBook Air M2 8GB',            2,  1, 114900.00, 4.9,  20, '2023-10-01'),
    ('Dell XPS 15 Core i7 16GB',            2,  9, 149990.00, 4.7,  15, '2023-11-01'),
    ('HP Pavilion 15 Core i5 8GB',          2, 13,  54999.00, 4.4,  35, '2024-01-10'),
    ('Lenovo IdeaPad Slim 5 Ryzen 5',       2,  9,  48999.00, 4.3,  40, '2024-02-15'),
    ('ASUS VivoBook 15 Core i3',            2,  5,  35990.00, 4.2,  50, '2024-03-10'),
    # cat 3 - Tablets
    ('Apple iPad Air 5th Gen 64GB',         3,  1,  59900.00, 4.8,  25, '2023-09-01'),
    ('Samsung Galaxy Tab S9 128GB',         3, 13,  74999.00, 4.6,  18, '2024-01-05'),
    ('Redmi Pad Pro WiFi 128GB',            3, 17,  22999.00, 4.3,  55, '2024-04-01'),
    # cat 4 - Accessories
    ('Sony WH-1000XM5 Headphones',          4,  1,  26990.00, 4.8,  70, '2023-08-01'),
    ('JBL Flip 6 Bluetooth Speaker',        4, 13,   9999.00, 4.5,  90, '2023-10-15'),
    ('Anker PowerBank 20000mAh',            4,  9,   2499.00, 4.4, 150, '2024-01-01'),
    ('boAt Rockerz 450 Headphones',         4, 17,   1299.00, 4.2, 200, '2024-02-01'),
    ('Logitech MX Master 3S Mouse',         4,  5,   9495.00, 4.7,  60, '2024-03-15'),
    # cat 5 - Men Clothing
    ('Raymond Slim Fit Formal Shirt',       5,  6,   1299.00, 4.4, 200, '2024-01-05'),
    ('Allen Solly Slim Fit Chinos',         5, 10,   2499.00, 4.3, 150, '2024-02-01'),
    ('Levis 511 Slim Fit Jeans',            5, 14,   3299.00, 4.5, 120, '2024-02-15'),
    ('Peter England Formal Suit',           5,  6,   6999.00, 4.4,  80, '2024-03-01'),
    ('US Polo Assn Polo T-Shirt',           5,  2,   1499.00, 4.3, 250, '2024-03-15'),
    # cat 6 - Women Clothing
    ('Biba Anarkali Kurta Set',             6, 18,   2499.00, 4.6, 100, '2024-01-10'),
    ('W for Woman Straight Kurta',          6,  2,   1799.00, 4.4, 150, '2024-02-05'),
    ('Banarasi Silk Saree with Blouse',     6, 18,   4999.00, 4.7,  60, '2024-02-20'),
    ('FabIndia Cotton Salwar Suit',         6,  6,   3499.00, 4.5,  90, '2024-03-05'),
    # cat 7 - Footwear
    ('Nike Air Max 270 Men Shoes',          7, 10,   8995.00, 4.6,  80, '2024-01-20'),
    ('Adidas Ultraboost 22 Men',            7, 14,  12995.00, 4.7,  55, '2024-02-10'),
    ('Metro Shoes Formal Derby Men',        7,  2,   2499.00, 4.3, 100, '2024-03-01'),
    ('Bata Ladies Block Heels',             7,  6,   1799.00, 4.2, 120, '2024-03-20'),
    # cat 8 - Kitchen Appliances
    ('Instant Pot Duo 7-in-1',             8,  3,   8999.00, 4.7,  40, '2024-01-08'),
    ('Prestige SS Pressure Cooker 5L',      8,  7,   2499.00, 4.5, 100, '2024-01-25'),
    ('Philips Air Fryer HD9200 2.75L',      8, 15,   6499.00, 4.6,  60, '2024-02-08'),
    ('IFB 30L Convection Microwave',        8, 19,  14999.00, 4.4,  30, '2024-02-25'),
    ('Lifelong Mixer Grinder 500W',         8,  7,   2799.00, 4.3,  80, '2024-03-12'),
    # cat 9 - Furniture
    ('IKEA LACK Coffee Table',             9, 11,   4999.00, 4.3,  20, '2024-01-12'),
    ('Solid Wood Study Desk',              9,  3,   8499.00, 4.5,  15, '2024-02-12'),
    ('Nilkamal Plastic Chair Set of 4',    9, 11,   3499.00, 4.2,  25, '2024-03-08'),
    ('Wakefit Memory Foam Mattress Queen', 9, 15,  14999.00, 4.7,  10, '2024-03-25'),
    # cat 10 - Home Decor
    ('Asian Paints Royale Atmos 20L',     10,  3,   5499.00, 4.4,  50, '2024-01-18'),
    ('Bombay Dyeing Cotton Bed Sheet',    10,  7,   1299.00, 4.3, 150, '2024-02-18'),
    ('WallMantra Motivational Wall Art',  10, 11,    799.00, 4.1, 200, '2024-03-18'),
    # cat 11 - Academic Books
    ('NCERT Mathematics Class 12',        11,  4,    399.00, 4.8, 300, '2024-01-02'),
    ('Data Structures Made Easy',         11,  8,    499.00, 4.7, 200, '2024-01-20'),
    ('CA Foundation Study Material',      11, 12,   1299.00, 4.6, 150, '2024-02-02'),
    ('GATE 2025 Computer Science',        11, 16,    699.00, 4.5, 180, '2024-02-20'),
    # cat 12 - Fiction Books
    ('The God of Small Things',           12, 20,    299.00, 4.8, 250, '2024-01-05'),
    ('Malgudi Days RK Narayan',           12,  4,    199.00, 4.7, 300, '2024-01-22'),
    ('The Palace of Illusions',           12,  8,    349.00, 4.6, 220, '2024-02-08'),
]

CATEGORIES = [
    ('Electronics', 'Smartphones'), ('Electronics', 'Laptops'),
    ('Electronics', 'Tablets'),     ('Electronics', 'Accessories'),
    ('Fashion', 'Men Clothing'),    ('Fashion', 'Women Clothing'),
    ('Fashion', 'Footwear'),        ('Home', 'Kitchen Appliances'),
    ('Home', 'Furniture'),          ('Home', 'Home Decor'),
    ('Books', 'Academic'),          ('Books', 'Fiction'),
]

# Pre-built lookup tables
PRODUCT_PRICE = {i+1: D(str(PRODUCTS[i][3])) for i in range(len(PRODUCTS))}
USER_INFO = {idx+1: (u[3], date.fromisoformat(u[4])) for idx, u in enumerate(USERS)}

# 60% COD, 20% UPI, 10% CC, 5% DC, 5% Wallet
PAYMENT_POOL = ['COD']*60 + ['UPI']*20 + ['Credit Card']*10 + ['Debit Card']*5 + ['Wallet']*5

FESTIVAL_MULT = {
    (2025, 10): 2.5, (2025, 11): 2.8, (2025, 12): 1.4,
    (2026,  1): 2.0, (2026,  2): 1.2, (2026,  3): 1.6,
    (2026,  4): 1.0, (2026,  5): 1.0, (2026,  6): 1.0,
    (2026,  7): 1.0, (2026,  8): 1.8, (2026,  9): 1.3,
}
BASE_PER_MONTH = 18

RETURN_REASONS = [
    'Product not as described', 'Defective product', 'Wrong item delivered',
    'Size not fitting', 'Better price available elsewhere', 'Changed mind',
    'Product damaged during delivery', 'Quality not as expected',
    'Duplicate order placed', 'Colour different from website',
    'Mobile overheating issue', 'Book pages torn', 'Wrong book edition delivered',
    'Saree colour faded after first wash', 'Furniture piece missing',
    'Table surface scratched in transit',
]
RETURN_STATUSES = ['Completed', 'Completed', 'Completed', 'Approved', 'Rejected']

REVIEW_TEXTS = [
    'Excellent quality! Worth every rupee.',
    'Great product, highly recommended.',
    'Good value for money.',
    'Average quality, expected better.',
    'Outstanding performance, very happy.',
    'Decent quality for the price.',
    'Brilliant product, exactly as described.',
    'Fast delivery, good packaging.',
    'Very comfortable and durable.',
    'Battery life is amazing!',
    'Display quality is superb.',
    'Build quality is solid.',
    'Perfect fit and finish.',
    'Exceeded my expectations!',
    'Works perfectly, no issues at all.',
    'Recommend to everyone.',
    'Good but slightly overpriced.',
    'Exactly what I needed for daily use.',
    'Solid performance throughout.',
    'Very happy with the purchase.',
]


# ---------------------------------------------------------------------------
# data generation functions
# ---------------------------------------------------------------------------

def generate_orders():
    """Generate orders and order_items deterministically (seed=42).
    Guarantees:
      - orders.region == user.region
      - orders.order_date > user.signup_date
      - orders.total_amount == SUM(order_items.quantity * order_items.unit_price)
      - order_items.unit_price == product.price
      - Each order has 1-4 items
    """
    orders, items = [], []
    oid = 1
    period = [
        (2025, 10), (2025, 11), (2025, 12),
        (2026,  1), (2026,  2), (2026,  3), (2026,  4),
        (2026,  5), (2026,  6), (2026,  7), (2026,  8), (2026,  9),
    ]
    all_pids = list(range(1, len(PRODUCTS) + 1))

    for yr, mo in period:
        n_orders = max(1, round(BASE_PER_MONTH * FESTIVAL_MULT.get((yr, mo), 1.0)))
        mstart = date(yr, mo, 1)
        mend = (date(yr, 12, 31) if mo == 12
                else date(yr if mo < 12 else yr+1, mo % 12 + 1, 1) - timedelta(days=1))

        for _ in range(n_orders):
            uid = random.randint(1, len(USERS))
            region, signup = USER_INFO[uid]
            earliest = max(mstart, signup + timedelta(days=1))
            if earliest > mend:
                earliest = mend
            odate = rand_date(earliest, mend)
            payment = random.choice(PAYMENT_POOL)

            r = random.random()
            if   r < 0.77: status = 'Delivered'
            elif r < 0.85: status = 'Cancelled'
            elif r < 0.92: status = 'Returned'
            elif r < 0.96: status = 'Shipped'
            elif r < 0.98: status = 'Confirmed'
            else:          status = 'Pending'

            n_items = random.randint(1, 4)
            chosen_pids = random.sample(all_pids, min(n_items, len(all_pids)))
            total = D('0')
            for pid in chosen_pids:
                qty = random.randint(1, 3)
                up = PRODUCT_PRICE[pid]
                total += up * qty
                items.append({'order_id': oid, 'product_id': pid,
                              'quantity': qty, 'unit_price': up})

            orders.append({'order_id': oid, 'user_id': uid, 'order_date': odate,
                           'total_amount': total, 'payment_method': payment,
                           'order_status': status, 'region': region})
            oid += 1

    return orders, items


def generate_returns(orders, items):
    """Guarantee:
      - Every 'Returned' order has at least one return row.
      - Returns only on Delivered or Returned orders.
      - Each return references an existing (order_id, product_id) pair.
    """
    items_by_order = defaultdict(list)
    for it in items:
        items_by_order[it['order_id']].append(it['product_id'])

    returned_oids = {o['order_id'] for o in orders if o['order_status'] == 'Returned'}
    delivered_oids = {o['order_id'] for o in orders if o['order_status'] == 'Delivered'}
    odate_map = {o['order_id']: o['order_date'] for o in orders}

    returns, used = [], set()

    def add_return(oid, pid):
        if (oid, pid) in used:
            return False
        rd = odate_map[oid] + timedelta(days=random.randint(3, 15))
        returns.append({'order_id': oid, 'product_id': pid,
                        'return_date': rd,
                        'reason': random.choice(RETURN_REASONS),
                        'status': random.choice(RETURN_STATUSES)})
        used.add((oid, pid))
        return True

    # Every Returned order must have a return row
    for oid in sorted(returned_oids):
        pids = items_by_order.get(oid, [])
        if pids:
            add_return(oid, pids[0])

    # ~15 extra returns from Delivered orders
    delivered_list = sorted(delivered_oids)
    random.shuffle(delivered_list)
    extras = 0
    for oid in delivered_list:
        if extras >= 15:
            break
        pids = items_by_order.get(oid, [])
        if pids and add_return(oid, random.choice(pids)):
            extras += 1

    return returns


def generate_reviews(orders, items):
    """Only users who have a Delivered order for a product may review it."""
    del_orders = {o['order_id']: (o['user_id'], o['order_date'])
                  for o in orders if o['order_status'] == 'Delivered'}

    eligible = {}  # (user_id, product_id) -> earliest delivered order_date
    for it in items:
        if it['order_id'] in del_orders:
            uid, odate = del_orders[it['order_id']]
            key = (uid, it['product_id'])
            if key not in eligible or odate < eligible[key]:
                eligible[key] = odate

    pairs = list(eligible.items())
    random.shuffle(pairs)
    reviews = []
    for (uid, pid), odate in pairs:
        rdate = odate + timedelta(days=random.randint(5, 30))
        rating = random.choices([3, 4, 4, 5, 5], k=1)[0]
        reviews.append({'product_id': pid, 'user_id': uid, 'rating': rating,
                        'review_text': random.choice(REVIEW_TEXTS),
                        'review_date': rdate})
        if len(reviews) >= 70:
            break
    return reviews


# ---------------------------------------------------------------------------
# SQL builders
# ---------------------------------------------------------------------------

SCHEMA_SQL = """\
-- =============================================================================
-- Flipkart Analytics Hub - Database Schema (v2)
-- =============================================================================
-- Engine : MySQL 8.0+
-- Tables : users, sellers, categories, products, orders,
--           order_items, reviews, returns
-- =============================================================================

DROP DATABASE IF EXISTS flipkart_analytics;
CREATE DATABASE flipkart_analytics
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE flipkart_analytics;

-- Table 1: users
CREATE TABLE users (
    user_id      INT             NOT NULL AUTO_INCREMENT,
    username     VARCHAR(80)     NOT NULL,
    email        VARCHAR(120)    NOT NULL UNIQUE,
    city         VARCHAR(60)     NOT NULL,
    region       ENUM('North','South','East','West') NOT NULL,
    signup_date  DATE            NOT NULL,
    user_type    ENUM('Regular','Premium','VIP') NOT NULL DEFAULT 'Regular',
    PRIMARY KEY (user_id)
);

-- Table 2: sellers
CREATE TABLE sellers (
    seller_id        INT          NOT NULL AUTO_INCREMENT,
    seller_name      VARCHAR(120) NOT NULL,
    rating           DECIMAL(3,2) NOT NULL DEFAULT 4.00,
    total_products   INT          NOT NULL DEFAULT 0,
    established_date DATE         NOT NULL,
    user_id          INT          NOT NULL,
    PRIMARY KEY (seller_id),
    CONSTRAINT fk_seller_user FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

-- Table 3: categories
CREATE TABLE categories (
    category_id   INT         NOT NULL AUTO_INCREMENT,
    category_name VARCHAR(80) NOT NULL,
    subcategory   VARCHAR(80) NOT NULL,
    PRIMARY KEY (category_id)
);

-- Table 4: products
CREATE TABLE products (
    product_id   INT           NOT NULL AUTO_INCREMENT,
    product_name VARCHAR(200)  NOT NULL,
    category_id  INT           NOT NULL,
    seller_id    INT           NOT NULL,
    price        DECIMAL(10,2) NOT NULL,
    rating       DECIMAL(3,2)  NOT NULL DEFAULT 0.00,
    stock        INT           NOT NULL DEFAULT 0,
    created_date DATE          NOT NULL,
    PRIMARY KEY (product_id),
    CONSTRAINT fk_product_category FOREIGN KEY (category_id)
        REFERENCES categories (category_id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_product_seller   FOREIGN KEY (seller_id)
        REFERENCES sellers   (seller_id)   ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Table 5: orders
CREATE TABLE orders (
    order_id       INT           NOT NULL AUTO_INCREMENT,
    user_id        INT           NOT NULL,
    order_date     DATE          NOT NULL,
    total_amount   DECIMAL(12,2) NOT NULL,
    payment_method ENUM('COD','UPI','Credit Card','Debit Card','Wallet') NOT NULL,
    order_status   ENUM('Pending','Confirmed','Shipped','Delivered','Cancelled','Returned')
                                 NOT NULL DEFAULT 'Pending',
    region         ENUM('North','South','East','West') NOT NULL,
    PRIMARY KEY (order_id),
    CONSTRAINT fk_order_user FOREIGN KEY (user_id)
        REFERENCES users (user_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Table 6: order_items
CREATE TABLE order_items (
    order_item_id INT           NOT NULL AUTO_INCREMENT,
    order_id      INT           NOT NULL,
    product_id    INT           NOT NULL,
    quantity      INT           NOT NULL DEFAULT 1,
    unit_price    DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (order_item_id),
    CONSTRAINT fk_item_order   FOREIGN KEY (order_id)
        REFERENCES orders   (order_id)   ON DELETE CASCADE  ON UPDATE CASCADE,
    CONSTRAINT fk_item_product FOREIGN KEY (product_id)
        REFERENCES products (product_id) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- Table 7: reviews
CREATE TABLE reviews (
    review_id   INT     NOT NULL AUTO_INCREMENT,
    product_id  INT     NOT NULL,
    user_id     INT     NOT NULL,
    rating      TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    review_date DATE    NOT NULL,
    PRIMARY KEY (review_id),
    CONSTRAINT fk_review_product FOREIGN KEY (product_id)
        REFERENCES products (product_id) ON DELETE CASCADE  ON UPDATE CASCADE,
    CONSTRAINT fk_review_user    FOREIGN KEY (user_id)
        REFERENCES users    (user_id)    ON DELETE CASCADE  ON UPDATE CASCADE
);

-- Table 8: returns
CREATE TABLE returns (
    return_id   INT          NOT NULL AUTO_INCREMENT,
    order_id    INT          NOT NULL,
    product_id  INT          NOT NULL,
    return_date DATE         NOT NULL,
    reason      VARCHAR(200) NOT NULL,
    status      ENUM('Requested','Approved','Rejected','Completed')
                             NOT NULL DEFAULT 'Requested',
    PRIMARY KEY (return_id),
    CONSTRAINT fk_return_order   FOREIGN KEY (order_id)
        REFERENCES orders   (order_id)   ON DELETE CASCADE  ON UPDATE CASCADE,
    CONSTRAINT fk_return_product FOREIGN KEY (product_id)
        REFERENCES products (product_id) ON DELETE RESTRICT ON UPDATE CASCADE
);
"""


def build_sample_data_sql(orders, items, returns, reviews):
    """Build the complete sample_data.sql content as a string."""
    L = []
    def ln(s=''): L.append(s)

    stat_c = defaultdict(int)
    for o in orders: stat_c[o['order_status']] += 1
    pay_c = defaultdict(int)
    for o in orders: pay_c[o['payment_method']] += 1
    n = len(orders)

    ln('-- =============================================================================')
    ln('-- Flipkart Analytics Hub - Sample Data  (v2, random seed = 42)')
    ln('-- NOTE: ALL DATA IS SYNTHETIC / SAMPLE, generated for portfolio purposes.')
    ln('-- Date range: Oct 2025 - Sep 2026')
    ln('-- Festival volume spikes: Oct/Nov 2025 (Big Billion Days/Diwali),')
    ln('--   Jan 2026 (Republic Day Sale), Mar 2026 (Holi Sale),')
    ln('--   Aug 2026 (Independence Day Sale).')
    ln('-- =============================================================================')
    ln('USE flipkart_analytics;')
    ln()

    # USERS
    ln(f'-- {len(USERS)} users, 4 regions: North (1-20), South (21-40), West (41-60), East (61-80), Extra (81-97)')
    ln('INSERT INTO users (username, email, city, region, signup_date, user_type) VALUES')
    rows = [f"('{esc(u[0])}','{esc(u[1])}','{esc(u[2])}','{u[3]}','{u[4]}','{u[5]}')"
            for u in USERS]
    ln(',\n'.join(rows) + ';')
    ln()

    # SELLERS - total_products computed from actual product list
    spc = defaultdict(int)
    for p in PRODUCTS: spc[p[2]] += 1
    ln(f'-- {len(SELLERS_PROTO)} sellers; total_products = actual count in products table')
    ln('INSERT INTO sellers (seller_name, rating, total_products, established_date, user_id) VALUES')
    rows = [f"('{esc(s[0])}',{s[1]},{spc.get(i+1,0)},'{s[2]}',{s[3]})"
            for i, s in enumerate(SELLERS_PROTO)]
    ln(',\n'.join(rows) + ';')
    ln()

    # CATEGORIES
    ln(f'-- {len(CATEGORIES)} categories across Electronics, Fashion, Home, Books')
    ln('INSERT INTO categories (category_name, subcategory) VALUES')
    ln(','.join(f"('{c[0]}','{c[1]}')" for c in CATEGORIES) + ';')
    ln()

    # PRODUCTS
    ln(f'-- {len(PRODUCTS)} products; realistic INR pricing (Rs 199 - Rs 149990)')
    ln('INSERT INTO products (product_name, category_id, seller_id, price, rating, stock, created_date) VALUES')
    rows = [f"('{esc(p[0])}',{p[1]},{p[2]},{p[3]},{p[4]},{p[5]},'{p[6]}')"
            for p in PRODUCTS]
    ln(',\n'.join(rows) + ';')
    ln()

    # ORDERS
    ln(f'-- {n} orders')
    ln(f'-- Status: Delivered={stat_c["Delivered"]} ({round(stat_c["Delivered"]*100/n,1)}%),'
       f' Cancelled={stat_c["Cancelled"]} ({round(stat_c["Cancelled"]*100/n,1)}%),'
       f' Returned={stat_c["Returned"]} ({round(stat_c["Returned"]*100/n,1)}%),'
       f' Shipped={stat_c["Shipped"]} ({round(stat_c["Shipped"]*100/n,1)}%),'
       f' Confirmed={stat_c["Confirmed"]} ({round(stat_c["Confirmed"]*100/n,1)}%),'
       f' Pending={stat_c["Pending"]} ({round(stat_c["Pending"]*100/n,1)}%)')
    ln(f'-- Payment: COD={pay_c["COD"]} ({round(pay_c["COD"]*100/n,1)}%),'
       f' UPI={pay_c["UPI"]} ({round(pay_c["UPI"]*100/n,1)}%),'
       f' Credit Card={pay_c["Credit Card"]}, Debit Card={pay_c["Debit Card"]},'
       f' Wallet={pay_c["Wallet"]}')
    ln('INSERT INTO orders (user_id, order_date, total_amount, payment_method, order_status, region) VALUES')
    rows = []
    for o in orders:
        ta = str(o['total_amount'].quantize(D('0.01'), rounding=ROUND_HALF_UP))
        rows.append(f"({o['user_id']},'{fmt_date(o['order_date'])}',{ta},"
                    f"'{o['payment_method']}','{o['order_status']}','{o['region']}')")
    ln(',\n'.join(rows) + ';')
    ln()

    # ORDER_ITEMS
    ln(f'-- {len(items)} order_items (1-4 per order)')
    ln('-- unit_price = product.price; orders.total_amount = SUM(quantity * unit_price)')
    ln('INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES')
    rows = []
    for it in items:
        up = str(it['unit_price'].quantize(D('0.01'), rounding=ROUND_HALF_UP))
        rows.append(f"({it['order_id']},{it['product_id']},{it['quantity']},{up})")
    ln(',\n'.join(rows) + ';')
    ln()

    # RETURNS
    ln(f'-- {len(returns)} returns')
    ln('-- Only Delivered or Returned orders; every Returned order has >= 1 return row')
    ln('INSERT INTO returns (order_id, product_id, return_date, reason, status) VALUES')
    rows = [f"({r['order_id']},{r['product_id']},'{fmt_date(r['return_date'])}',"
            f"'{esc(r['reason'])}','{r['status']}')" for r in returns]
    ln(',\n'.join(rows) + ';')
    ln()

    # REVIEWS
    ln(f'-- {len(reviews)} reviews; only verified Delivered buyers')
    ln('INSERT INTO reviews (product_id, user_id, rating, review_text, review_date) VALUES')
    rows = [f"({rv['product_id']},{rv['user_id']},{rv['rating']},"
            f"'{esc(rv['review_text'])}','{fmt_date(rv['review_date'])}')" for rv in reviews]
    ln(',\n'.join(rows) + ';')
    ln()

    return '\n'.join(L)


def build_readme(n_u, n_s, n_p, n_o, n_i, n_ret, n_rev,
                 cod_pct, upi_pct, card_pct, n_returned, ret_pct,
                 min_price, max_price):
    return f"""\
# Flipkart Analytics Hub - SQL Portfolio Project

[![SQL](https://img.shields.io/badge/SQL-MySQL%208.0-blue?style=flat-square&logo=mysql)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Queries](https://img.shields.io/badge/Analytical%20Queries-15-orange?style=flat-square)](queries.sql)

> **Synthetic / Sample Data** - All users, sellers, products, orders, and transactions are
> artificially generated (Python, random seed 42) for portfolio purposes only.
> 8-table schema | {n_o} orders | 15 advanced analytical queries | Oct 2025 - Sep 2026

---

## Project Overview

| Metric | Value |
|--------|-------|
| Users | {n_u} (North / South / East / West across 20+ cities) |
| Sellers | {n_s} (rated 4.3 - 4.9) |
| Products | {n_p} (Electronics, Fashion, Home, Books) |
| Orders | {n_o} (Oct 2025 - Sep 2026) |
| Order Items | {n_i} line-items (1-4 per order) |
| Payment | {cod_pct}% COD | {upi_pct}% UPI | {card_pct}% Cards+Wallet (measured) |
| Price Range | Rs {min_price:,} - Rs {max_price:,} |
| Returned Orders | {n_returned} (~{ret_pct}% of all orders) |
| Return Rows | {n_ret} |
| Reviews | {n_rev} (verified Delivered buyers only) |

---

## Setup

```bash
# Load schema and data:
mysql -u root -p < schema.sql
mysql -u root -p < sample_data.sql

# Validate data integrity (all bad_rows must = 0):
mysql -u root -p flipkart_analytics < validation.sql

# Run all 15 analytical queries:
mysql -u root -p flipkart_analytics < queries.sql
```

---

## Database Schema (8 Tables)

| Table | Key Foreign Keys | Notable Columns |
|-------|-----------------|-----------------|
| users | - | region ENUM, user_type ENUM |
| sellers | user_id -> users | rating DECIMAL, total_products INT |
| categories | - | category_name, subcategory |
| products | category_id, seller_id | price, stock, rating |
| orders | user_id | payment_method ENUM, order_status ENUM |
| order_items | order_id, product_id | quantity, unit_price |
| reviews | product_id, user_id | rating CHECK(1-5) |
| returns | order_id, product_id | reason, status ENUM |

---

## 15 Analytical Queries

| # | Query | SQL Concepts |
|---|-------|-------------|
| 1 | Top 10 Customers by Spending | GROUP BY, ORDER BY, aggregate functions |
| 2 | Best-Selling Products by Category | RANK() OVER PARTITION BY |
| 3 | Payment Method Preferences | SUM() OVER(), percentage |
| 4 | Regional Sales Performance | Window SUM OVER() |
| 5 | Top Sellers - Rating + Revenue | Composite normalised scoring |
| 6 | Product Return Analysis | CTE pre-aggregation, LEFT JOIN, NULLIF, GROUP_CONCAT |
| 7 | RFM Customer Segmentation | CTE + NTILE(5), fixed @as_of |
| 8 | Monthly Revenue Trends | LAG(), cumulative SUM OVER() |
| 9 | Churn Analysis (60-day) | DATEDIFF(), HAVING, @as_of |
| 10 | Category Performance | CTE pre-aggregation, multi-table JOINs |
| 11 | Festival Season Patterns | DATE_FORMAT(), CASE WHEN |
| 12 | Payment by Region | PARTITION BY region |
| 13 | Seller Reliability Score | CTE + weighted formula, NULLIF fix |
| 14 | Time-to-First-Purchase & CLV | Chained CTEs, one clean row per user |
| 15 | Inventory Health Check | FIELD() custom sort, subquery status filter |

---

## SQL Concepts Demonstrated

```
DDL             CREATE TABLE with ENUM, CHECK, FK constraints
DML             Bulk INSERT with realistic Indian e-commerce data
Window Funcs    RANK, NTILE, LAG, SUM OVER, PARTITION BY, ROWS UNBOUNDED PRECEDING
CTEs            WITH clauses for multi-step analytical logic
Joins           INNER JOIN, LEFT JOIN up to 5 tables
Aggregation     SUM, COUNT, AVG, MAX, MIN with GROUP BY / HAVING
Conditional     CASE WHEN, COALESCE, NULLIF, FIELD
Date Funcs      DATE_FORMAT, DATEDIFF, MONTHNAME, @as_of session variable
String Funcs    GROUP_CONCAT with ORDER BY and SEPARATOR
Business KPIs   RFM scoring, CLV, churn rate, reliability score, inventory velocity
Integrity       validation.sql: 13 automated data-quality checks
```

---

## Resume Line

> "Designed and queried an 8-table MySQL 8 database ({n_o} synthetic orders, Oct 2025-Sep 2026)
> for an Indian e-commerce platform. Implemented 15 BI queries covering RFM customer
> segmentation, churn detection, festival-season trend analysis, inventory health scoring,
> and regional revenue analytics using window functions, CTEs, and automated integrity
> validation (13 checks, all pass)."

---

## Project Structure

```
flipkart-analytics-hub/
|-- schema.sql          # 8-table schema (FK, ENUM, CHECK constraints)
|-- sample_data.sql     # Synthetic data (seed=42, Oct 2025-Sep 2026, {n_o} orders)
|-- queries.sql         # 15 analytical queries (v2 - all bugs fixed)
|-- validation.sql      # 13 integrity checks (all must return bad_rows = 0)
|-- README.md           # This file (stats computed from actual loaded data)
`-- generate_project.py # Python generator (run to regenerate all files)
```

MIT License - use freely for your portfolio.
"""


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main():
    random.seed(RANDOM_SEED)

    print('Generating data (seed=42) ...')
    orders, items = generate_orders()
    returns = generate_returns(orders, items)
    reviews = generate_reviews(orders, items)

    n_u = len(USERS)
    n_s = len(SELLERS_PROTO)
    n_p = len(PRODUCTS)
    n_o = len(orders)
    n_i = len(items)
    n_ret = len(returns)
    n_rev = len(reviews)

    pay = defaultdict(int)
    for o in orders: pay[o['payment_method']] += 1
    cod_pct  = round(pay['COD'] * 100 / n_o, 1)
    upi_pct  = round(pay['UPI'] * 100 / n_o, 1)
    card_pct = round((pay['Credit Card'] + pay['Debit Card'] + pay['Wallet']) * 100 / n_o, 1)

    n_returned = sum(1 for o in orders if o['order_status'] == 'Returned')
    ret_pct = round(n_returned * 100 / n_o, 1)
    min_p = int(min(p[3] for p in PRODUCTS))
    max_p = int(max(p[3] for p in PRODUCTS))

    print('\n=== Dataset Statistics ===')
    print(f'Users: {n_u}  |  Sellers: {n_s}  |  Products: {n_p}')
    print(f'Orders: {n_o}  |  Items: {n_i}  |  Returns: {n_ret}  |  Reviews: {n_rev}')
    print(f'Payment: COD={cod_pct}%  UPI={upi_pct}%  Cards+Wallet={card_pct}%')
    stat = defaultdict(int)
    for o in orders: stat[o['order_status']] += 1
    for s in ['Delivered', 'Cancelled', 'Returned', 'Shipped', 'Confirmed', 'Pending']:
        c = stat[s]
        print(f'  {s:<12}: {c:>4}  ({round(c*100/n_o, 1):.1f}%)')

    p = OUTPUT_DIR
    print(f'\nWriting files to: {p}')

    def write(fname, content):
        fpath = os.path.join(p, fname)
        with open(fpath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'  [OK] {fname}')

    write('schema.sql',      SCHEMA_SQL)
    write('sample_data.sql', build_sample_data_sql(orders, items, returns, reviews))

    # queries.sql and validation.sql are written directly (not overwritten if user edited them)
    # Uncomment the two lines below to also regenerate those files:
    # write('queries.sql',     QUERIES_SQL_CONTENT)
    # write('validation.sql',  VALIDATION_SQL_CONTENT)

    readme = build_readme(n_u, n_s, n_p, n_o, n_i, n_ret, n_rev,
                          cod_pct, upi_pct, card_pct, n_returned, ret_pct, min_p, max_p)
    write('README.md', readme)

    print('\nDone! Next steps:')
    print('  mysql -u root -p < schema.sql')
    print('  mysql -u root -p < sample_data.sql')
    print('  mysql -u root -p flipkart_analytics < validation.sql  (all bad_rows must = 0)')
    print('  mysql -u root -p flipkart_analytics < queries.sql')


if __name__ == '__main__':
    main()
