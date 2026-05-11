import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mtick
import os

os.makedirs('charts', exist_ok=True)

# Style
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10
BG = '#F8F9FA'
DARK = '#2E4057'
TEAL = '#048A81'
PURPLE = '#8B5CF6'
AMBER = '#F59E0B'
RED = '#EF4444'
BLUE = '#3B82F6'
GRAY = '#6B7280'
COLORS = [DARK, TEAL, PURPLE, AMBER, RED, BLUE]

def save_chart(fig, name):
    fig.savefig(f'charts/{name}.png', dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved charts/{name}.png")

# Load data
df = pd.read_csv('data/customer_churn_data.csv')
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0)
df['is_churned'] = df['Churn'] == 'Yes'

print("=" * 65)
print("SUBSCRIPTION CHURN ANALYSIS")
print(f"Dataset: {len(df):,} customers")
print("=" * 65)

# ============================================================
# OVERALL METRICS
# ============================================================
total_customers = len(df)
total_churned = df['is_churned'].sum()
total_active = total_customers - total_churned
churn_rate = total_churned / total_customers * 100
active_mrr = df[~df['is_churned']]['MonthlyCharges'].sum()
lost_mrr = df[df['is_churned']]['MonthlyCharges'].sum()
annual_revenue_at_risk = lost_mrr * 12

print(f"\n  Total customers: {total_customers:,}")
print(f"  Active: {total_active:,} | Churned: {total_churned:,}")
print(f"  Overall churn rate: {churn_rate:.1f}%")
print(f"  Active MRR: ${active_mrr:,.2f}")
print(f"  Monthly revenue lost to churn: ${lost_mrr:,.2f}")
print(f"  Annual revenue at risk: ${annual_revenue_at_risk:,.2f}")

# ============================================================
# 1. EXECUTIVE DASHBOARD (Multi-panel)
# ============================================================
print("\n1. EXECUTIVE DASHBOARD")
print("-" * 45)
print("  Building composite dashboard...")

fig = plt.figure(figsize=(20, 14), facecolor=BG)
fig.suptitle('Subscription Retention Dashboard', fontsize=24, fontweight='bold',
             color=DARK, y=0.98)
fig.text(0.5, 0.955, 'Where should we focus retention efforts to maximize revenue impact?',
         fontsize=13, color=GRAY, ha='center', style='italic')

gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.35, wspace=0.3,
                       top=0.92, bottom=0.06, left=0.06, right=0.97)

# --- ROW 1: KPI CARDS ---
kpi_data = [
    ('Total Customers', f'{total_customers:,}', DARK),
    ('Churn Rate', f'{churn_rate:.1f}%', RED),
    ('Active MRR', f'${active_mrr:,.0f}', TEAL),
    ('Annual Revenue at Risk', f'${annual_revenue_at_risk:,.0f}', AMBER),
]

for i, (label, value, color) in enumerate(kpi_data):
    ax = fig.add_subplot(gs[0, i])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_facecolor('white')
    for spine in ax.spines.values():
        spine.set_color('#E5E7EB')
        spine.set_linewidth(1.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.text(0.5, 0.62, value, fontsize=26, fontweight='bold', color=color,
            ha='center', va='center')
    ax.text(0.5, 0.28, label, fontsize=11, color=GRAY, ha='center', va='center')

# --- ROW 2, LEFT: Churn by Contract Type ---
ax1 = fig.add_subplot(gs[1, 0:2])
ax1.set_facecolor('white')
for spine in ax1.spines.values():
    spine.set_color('#E5E7EB')

contract = df.groupby('Contract').agg(
    total=('customerID', 'count'),
    churned=('is_churned', 'sum'),
    avg_tenure=('tenure', 'mean'),
    avg_monthly=('MonthlyCharges', 'mean')
).reset_index()
contract['churn_rate'] = (contract['churned'] / contract['total'] * 100).round(1)
contract['avg_tenure'] = contract['avg_tenure'].round(1)
contract['avg_monthly'] = contract['avg_monthly'].round(2)
contract = contract.sort_values('churn_rate', ascending=True)

bars1 = ax1.barh(contract['Contract'], contract['churn_rate'],
                 color=[TEAL, AMBER, RED], alpha=0.85, edgecolor='white', height=0.5)
ax1.set_xlabel('Churn Rate (%)', fontsize=10, color=GRAY)
ax1.set_title('Churn Rate by Contract Type', fontsize=13, fontweight='bold',
              color=DARK, pad=10)
for bar, val in zip(bars1, contract['churn_rate']):
    ax1.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height()/2,
             f'{val}%', va='center', fontsize=11, fontweight='bold', color=DARK)
ax1.set_xlim(0, 55)

# --- ROW 2, RIGHT: Revenue Lost by Contract Type ---
ax2 = fig.add_subplot(gs[1, 2:4])
ax2.set_facecolor('white')
for spine in ax2.spines.values():
    spine.set_color('#E5E7EB')

contract_rev = df[df['is_churned']].groupby('Contract').agg(
    lost_mrr=('MonthlyCharges', 'sum'),
    churned=('customerID', 'count')
).reset_index()
contract_rev['lost_annual'] = contract_rev['lost_mrr'] * 12
contract_rev = contract_rev.sort_values('lost_annual', ascending=True)

bars2 = ax2.barh(contract_rev['Contract'], contract_rev['lost_annual'],
                 color=[TEAL, AMBER, RED], alpha=0.85, edgecolor='white', height=0.5)
ax2.set_xlabel('Annual Revenue Lost ($)', fontsize=10, color=GRAY)
ax2.set_title('Annual Revenue Lost to Churn by Contract Type', fontsize=13,
              fontweight='bold', color=DARK, pad=10)
for bar, val in zip(bars2, contract_rev['lost_annual']):
    ax2.text(bar.get_width() + 5000, bar.get_y() + bar.get_height()/2,
             f'${val:,.0f}', va='center', fontsize=11, fontweight='bold', color=DARK)
ax2.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# --- ROW 3, LEFT: Service Impact on Churn ---
ax3 = fig.add_subplot(gs[2, 0:2])
ax3.set_facecolor('white')
for spine in ax3.spines.values():
    spine.set_color('#E5E7EB')

services = ['OnlineSecurity', 'TechSupport', 'OnlineBackup', 'DeviceProtection']
svc_impact = []
for svc in services:
    with_svc = df[df[svc] == 'Yes']['is_churned'].mean() * 100
    without_svc = df[df[svc] != 'Yes']['is_churned'].mean() * 100
    svc_impact.append({
        'service': svc.replace('Online', 'Online ').replace('Tech', 'Tech ').replace('Device', 'Device '),
        'with': round(with_svc, 1),
        'without': round(without_svc, 1),
        'reduction': round(without_svc - with_svc, 1)
    })
svc_df = pd.DataFrame(svc_impact).sort_values('reduction', ascending=True)

y_pos = range(len(svc_df))
ax3.barh([y - 0.2 for y in y_pos], svc_df['without'], height=0.35,
         label='Without Service', color=RED, alpha=0.7, edgecolor='white')
ax3.barh([y + 0.2 for y in y_pos], svc_df['with'], height=0.35,
         label='With Service', color=TEAL, alpha=0.7, edgecolor='white')
ax3.set_yticks(list(y_pos))
ax3.set_yticklabels(svc_df['service'])
ax3.set_xlabel('Churn Rate (%)', fontsize=10, color=GRAY)
ax3.set_title('Service Adoption Impact on Churn', fontsize=13, fontweight='bold',
              color=DARK, pad=10)
ax3.legend(fontsize=9, loc='lower right')

# --- ROW 3, RIGHT: Churn by Tenure ---
ax4 = fig.add_subplot(gs[2, 2:4])
ax4.set_facecolor('white')
for spine in ax4.spines.values():
    spine.set_color('#E5E7EB')

df['tenure_cohort'] = pd.cut(df['tenure'],
    bins=[0, 6, 12, 24, 48, 72],
    labels=['0-6\nmonths', '7-12\nmonths', '13-24\nmonths', '25-48\nmonths', '49-72\nmonths'],
    include_lowest=True)

tenure = df.groupby('tenure_cohort', observed=True).agg(
    total=('customerID', 'count'),
    churned=('is_churned', 'sum')
).reset_index()
tenure['churn_rate'] = (tenure['churned'] / tenure['total'] * 100).round(1)

colors = [RED, AMBER, AMBER, TEAL, TEAL]
bars4 = ax4.bar(tenure['tenure_cohort'].astype(str), tenure['churn_rate'],
                color=colors, alpha=0.85, edgecolor='white', width=0.6)
ax4.set_xlabel('Customer Tenure', fontsize=10, color=GRAY)
ax4.set_ylabel('Churn Rate (%)', fontsize=10, color=GRAY)
ax4.set_title('Churn Rate by Customer Tenure', fontsize=13, fontweight='bold',
              color=DARK, pad=10)
for bar, val in zip(bars4, tenure['churn_rate']):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
             f'{val}%', ha='center', fontsize=10, fontweight='bold', color=DARK)

plt.savefig('charts/00_executive_dashboard.png', dpi=150, bbox_inches='tight',
            facecolor=BG)
plt.close(fig)
print("  Saved charts/00_executive_dashboard.png")

# ============================================================
# 2. CHURN RISK HEATMAP (Contract x Internet Type)
# ============================================================
print("\n2. CHURN RISK HEATMAP")
print("-" * 45)

pivot = df.groupby(['Contract', 'InternetService']).agg(
    churn_rate=('is_churned', 'mean')
).reset_index()
pivot['churn_rate'] = (pivot['churn_rate'] * 100).round(1)
heatmap_data = pivot.pivot(index='Contract', columns='InternetService', values='churn_rate')
heatmap_data = heatmap_data.reindex(['Month-to-month', 'One year', 'Two year'])
heatmap_data = heatmap_data[['Fiber optic', 'DSL', 'No']]

print("  Churn Rate by Contract x Internet Type:")
print(f"  {'':20} {'Fiber optic':>12} {'DSL':>8} {'No':>8}")
for idx in heatmap_data.index:
    vals = heatmap_data.loc[idx]
    print(f"  {idx:20} {vals['Fiber optic']:>11.1f}% {vals['DSL']:>7.1f}% {vals['No']:>7.1f}%")

fig, ax = plt.subplots(figsize=(10, 5))
im = ax.imshow(heatmap_data.values, cmap='RdYlGn_r', aspect='auto', vmin=0, vmax=60)
ax.set_xticks(range(len(heatmap_data.columns)))
ax.set_xticklabels(heatmap_data.columns, fontsize=12)
ax.set_yticks(range(len(heatmap_data.index)))
ax.set_yticklabels(heatmap_data.index, fontsize=12)
ax.set_title('Churn Rate Heatmap: Contract Type x Internet Service', fontsize=14,
             fontweight='bold', color=DARK, pad=15)

for i in range(len(heatmap_data.index)):
    for j in range(len(heatmap_data.columns)):
        val = heatmap_data.values[i, j]
        color = 'white' if val > 30 else DARK
        ax.text(j, i, f'{val:.1f}%', ha='center', va='center',
                fontsize=14, fontweight='bold', color=color)

plt.colorbar(im, ax=ax, label='Churn Rate (%)', shrink=0.8)
plt.tight_layout()
save_chart(fig, '01_churn_heatmap')

# ============================================================
# 3. CUSTOMER VALUE SEGMENTS
# ============================================================
print("\n3. CUSTOMER VALUE SEGMENTS")
print("-" * 45)

active_df = df[~df['is_churned']]
churned_df = df[df['is_churned']]

avg_churned_value = churned_df['MonthlyCharges'].mean()
avg_active_value = active_df['MonthlyCharges'].mean()
avg_churned_tenure = churned_df['tenure'].mean()
avg_active_tenure = active_df['tenure'].mean()

print(f"  Active customers: avg ${avg_active_value:.2f}/mo, avg {avg_active_tenure:.0f} months tenure")
print(f"  Churned customers: avg ${avg_churned_value:.2f}/mo, avg {avg_churned_tenure:.0f} months tenure")
print(f"  Insight: Churned customers paid more on average, suggesting price sensitivity")

fig, ax = plt.subplots(figsize=(10, 6))
ax.scatter(active_df['tenure'], active_df['MonthlyCharges'], alpha=0.15, s=10,
           color=TEAL, label=f'Active ({len(active_df):,})')
ax.scatter(churned_df['tenure'], churned_df['MonthlyCharges'], alpha=0.15, s=10,
           color=RED, label=f'Churned ({len(churned_df):,})')
ax.set_xlabel('Tenure (months)', fontsize=12)
ax.set_ylabel('Monthly Charges ($)', fontsize=12)
ax.set_title('Customer Distribution: Tenure vs Monthly Charges', fontsize=14,
             fontweight='bold', color=DARK, pad=15)
ax.legend(fontsize=11, markerscale=5)
plt.tight_layout()
save_chart(fig, '02_customer_scatter')

# ============================================================
# 4. SERVICE ADOPTION DEEP DIVE (all 6 services)
# ============================================================
print("\n4. SERVICE ADOPTION DEEP DIVE")
print("-" * 45)

all_services = ['OnlineSecurity', 'OnlineBackup', 'DeviceProtection',
                'TechSupport', 'StreamingTV', 'StreamingMovies']
all_svc_data = []
for svc in all_services:
    with_svc = df[df[svc] == 'Yes']
    without_svc = df[df[svc] != 'Yes']
    churn_with = with_svc['is_churned'].mean() * 100
    churn_without = without_svc['is_churned'].mean() * 100
    all_svc_data.append({
        'service': svc,
        'users_with': len(with_svc),
        'churn_with': round(churn_with, 1),
        'users_without': len(without_svc),
        'churn_without': round(churn_without, 1),
        'churn_reduction': round(churn_without - churn_with, 1)
    })

all_svc_df = pd.DataFrame(all_svc_data).sort_values('churn_reduction', ascending=False)
print(all_svc_df.to_string(index=False))

fig, ax = plt.subplots(figsize=(12, 6))
x = range(len(all_svc_df))
width = 0.35
ax.bar([i - width/2 for i in x], all_svc_df['churn_with'], width,
       label='With Service', color=TEAL, alpha=0.85)
ax.bar([i + width/2 for i in x], all_svc_df['churn_without'], width,
       label='Without Service', color=RED, alpha=0.85)
ax.set_xticks(x)
ax.set_xticklabels(all_svc_df['service'], rotation=30, ha='right')
ax.set_ylabel('Churn Rate (%)', fontsize=12)
ax.set_title('Churn Rate: With vs Without Each Service', fontsize=14,
             fontweight='bold', pad=15)
ax.legend(fontsize=11)
plt.tight_layout()
save_chart(fig, '03_service_adoption')

# ============================================================
# 5. PAYMENT METHOD ANALYSIS
# ============================================================
print("\n5. PAYMENT METHOD ANALYSIS")
print("-" * 45)

payment = df.groupby('PaymentMethod').agg(
    total=('customerID', 'count'),
    churned=('is_churned', 'sum'),
    avg_monthly=('MonthlyCharges', 'mean')
).reset_index()
payment['churn_rate'] = (payment['churned'] / payment['total'] * 100).round(1)
payment = payment.sort_values('churn_rate', ascending=False)
print(payment.to_string(index=False))

payment_risk = df[df['is_churned']].groupby('PaymentMethod').agg(
    churned=('customerID', 'count'),
    lost_mrr=('MonthlyCharges', 'sum')
).reset_index()
payment_risk['lost_annual'] = payment_risk['lost_mrr'] * 12
payment_risk = payment_risk.sort_values('lost_annual', ascending=False)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Churn rate by payment method
bars1 = ax1.barh(payment['PaymentMethod'], payment['churn_rate'],
                 color=[RED, AMBER, BLUE, TEAL], alpha=0.85, edgecolor='white')
ax1.set_xlabel('Churn Rate (%)', fontsize=12)
ax1.set_title('Churn Rate by Payment Method', fontsize=14, fontweight='bold', pad=15)
for bar, val in zip(bars1, payment['churn_rate']):
    ax1.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
             f'{val}%', va='center', fontsize=11, fontweight='bold')

# Revenue at risk by payment method
bars2 = ax2.bar(range(len(payment_risk)), payment_risk['lost_annual'],
                color=[RED, AMBER, BLUE, TEAL], alpha=0.85, edgecolor='white')
ax2.set_xticks(range(len(payment_risk)))
ax2.set_xticklabels(payment_risk['PaymentMethod'], rotation=15, ha='right', fontsize=9)
ax2.set_ylabel('Annual Revenue Lost ($)', fontsize=12)
ax2.set_title('Annual Revenue Lost by Payment Method', fontsize=14,
              fontweight='bold', pad=15)
ax2.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, p: f'${x:,.0f}'))
for bar, val in zip(bars2, payment_risk['lost_annual']):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5000,
             f'${val:,.0f}', ha='center', fontsize=10, fontweight='bold', color=DARK)
plt.tight_layout()
save_chart(fig, '04_payment_analysis')

# ============================================================
# 6. INTERNET SERVICE TYPE vs CHURN
# ============================================================
print("\n6. INTERNET SERVICE TYPE vs CHURN")
print("-" * 45)

internet = df.groupby('InternetService').agg(
    total=('customerID', 'count'),
    churned=('is_churned', 'sum'),
    avg_monthly=('MonthlyCharges', 'mean'),
    avg_tenure=('tenure', 'mean')
).reset_index()
internet['churn_rate'] = (internet['churned'] / internet['total'] * 100).round(1)
internet['avg_monthly'] = internet['avg_monthly'].round(2)
internet['avg_tenure'] = internet['avg_tenure'].round(1)
internet = internet.sort_values('churn_rate', ascending=False)
print(internet.to_string(index=False))

fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.bar(internet['InternetService'], internet['churn_rate'],
              color=[RED, AMBER, TEAL], alpha=0.85, edgecolor='white')
ax.set_ylabel('Churn Rate (%)', fontsize=12)
ax.set_title('Churn Rate by Internet Service Type', fontsize=14, fontweight='bold', pad=15)
for bar, val in zip(bars, internet['churn_rate']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8,
            f'{val}%', ha='center', fontsize=11, fontweight='bold')
plt.tight_layout()
save_chart(fig, '05_internet_type')

# ============================================================
# 7. REVENUE IMPACT SUMMARY
# ============================================================
print("\n7. REVENUE IMPACT")
print("-" * 45)

print(f"  Active MRR: ${active_mrr:,.2f}")
print(f"  Lost MRR (churn): ${lost_mrr:,.2f}")
print(f"  Annual revenue at risk: ${annual_revenue_at_risk:,.2f}")
print(f"  Avg monthly charge (active): ${avg_active_value:.2f}")
print(f"  Avg monthly charge (churned): ${avg_churned_value:.2f}")

fig, ax = plt.subplots(figsize=(8, 6))
labels = ['Active MRR', 'Lost to Churn']
values = [active_mrr, lost_mrr]
bars = ax.bar(labels, values, color=[TEAL, RED], alpha=0.85, edgecolor='white', width=0.5)
ax.set_ylabel('Monthly Revenue ($)', fontsize=12)
ax.set_title('Monthly Revenue: Active vs Lost to Churn', fontsize=14,
             fontweight='bold', pad=15)
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 500,
            f'${val:,.0f}', ha='center', fontsize=12, fontweight='bold')
plt.tight_layout()
save_chart(fig, '06_revenue_impact')

# ============================================================
# FINDINGS AND RECOMMENDATIONS
# ============================================================
print("\n" + "=" * 65)
print("FINDINGS AND RECOMMENDATIONS")
print("=" * 65)

best_contract = contract.loc[contract['churn_rate'].idxmin()]
worst_contract = contract.loc[contract['churn_rate'].idxmax()]
best_service = all_svc_df.iloc[0]
worst_payment = payment.iloc[0]

print(f"\nKey Findings:")
print(f"  1. Contract type is the strongest churn predictor:")
print(f"     {worst_contract['Contract']}: {worst_contract['churn_rate']}% churn")
print(f"     vs {best_contract['Contract']}: {best_contract['churn_rate']}% churn")
print(f"  2. Month-to-month fiber optic is the highest-risk segment")
print(f"     ({heatmap_data.loc['Month-to-month', 'Fiber optic']:.1f}% churn)")
print(f"  3. {best_service['service']} has the largest churn reduction")
print(f"     ({best_service['churn_reduction']}% lower with service)")
print(f"  4. First 6 months: highest churn rate ({tenure.iloc[0]['churn_rate']}%)")
print(f"  5. {worst_payment['PaymentMethod']}: highest churn among")
print(f"     payment methods ({worst_payment['churn_rate']}%)")
print(f"  6. Churned customers paid more on average")
print(f"     (${avg_churned_value:.2f} vs ${avg_active_value:.2f})")

print(f"\nRecommendations (Priority Order):")
print(f"  1. CONVERT month-to-month to annual contracts")
print(f"     Largest churn gap ({worst_contract['churn_rate']}% vs")
print(f"     {best_contract['churn_rate']}%), largest revenue impact")
print(f"  2. BUNDLE Online Security and Tech Support into base plans")
print(f"     15-17 percentage point churn reduction when adopted")
print(f"  3. INVEST in first-6-month onboarding")
print(f"     {tenure.iloc[0]['churn_rate']}% of new customers churn in this window")
print(f"  4. MIGRATE electronic check users to auto-pay")
print(f"     Highest churn rate among payment methods")
print(f"  5. REVIEW fiber optic pricing")
print(f"     Premium customers churning at premium rates")

print(f"\n{'=' * 65}")
print(f"Analysis complete. 7 charts saved to /charts directory.")
print(f"{'=' * 65}")
