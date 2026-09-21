"""Historical trends with clearly marked demonstration thresholds."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def trend_plot(records, sensor, rule):
    ordered = records.sort_values("timestamp")
    fig, ax = plt.subplots(figsize=(11, 3.8), constrained_layout=True)
    ax.plot(ordered.timestamp, ordered[sensor], color="#087e8b", linewidth=1.7, label="Recorded reading")
    ax.axhline(rule.healthy_max, color="#ca8a04", linestyle="--", label="Healthy upper bound")
    ax.axhline(rule.warning_max, color="#c34b4b", linestyle="--", label="Warning upper bound")
    if rule.healthy_min != rule.valid_min:
        ax.axhline(rule.healthy_min, color="#ca8a04", linestyle=":", label="Healthy lower bound")
        ax.axhline(rule.warning_min, color="#c34b4b", linestyle=":", label="Warning lower bound")
    ax.set(xlabel="Timestamp (UTC)", ylabel=rule.unit, title=sensor.replace("_", " ").title())
    ax.grid(alpha=.15)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(fontsize=8, ncol=2)
    return fig
