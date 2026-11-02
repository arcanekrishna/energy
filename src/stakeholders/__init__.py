"""
stakeholders — Stakeholder-oriented translation layers for Indian electricity risk intelligence:
- MarketRiskView: Tail-risk VaR/ES, spike regimes, trading desks.
- GridRiskView: Supply-demand pressure index, net demand ramp alerts, system reliability.
- ProcurementRiskView: Discom/C&I DAM-RTM spread arbitrage, hedging strategies, exposure calculation.
"""

try:
    from .market_view import MarketRiskView
    from .grid_view import GridRiskView
    from .procurement_view import ProcurementRiskView
except ImportError:
    from src.stakeholders.market_view import MarketRiskView
    from src.stakeholders.grid_view import GridRiskView
    from src.stakeholders.procurement_view import ProcurementRiskView

__all__ = [
    "MarketRiskView",
    "GridRiskView",
    "ProcurementRiskView",
]
