"""
VoltYield Post-Windfall Projection Engine (v2026.1.13)
Revenue Annuity & Grid-Sellback Modeling
"""

def display_annuity_projections():
    projections = {
        "V2G GRID SELLBACK": 142000000.00,
        "DATA LICENSING (SaaS)": 88500000.00,
        "SECONDARY ASSET PREMIUM": 65000000.00
    }
    
    print(f"\n{'='*64}")
    print(f"{'2027-2030 RECURRING YIELD PROJECTIONS':^64}")
    print(f"{'='*64}")
    
    total = 0
    for key, value in projections.items():
        total += value
        print(f" {key:<30} | \033[1;32m${value:>15,.2f} /yr\033[0m")
    
    print(f"{'-'*64}")
    print(f" TOTAL POST-WINDFALL ANNUITY: \033[1;32m${total:>15,.2f} / YEAR\033[0m")
    print(f"{'='*64}")

if __name__ == "__main__":
    display_annuity_projections()
