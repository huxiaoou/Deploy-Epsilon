import yaml
from qtools_sxzq.qdata import CDataDescriptor, CMarketDescriptor
from typedef import TName, TClsData
from typedef import CCfgDbs, CSectorClassification, TClassifications
from typedef import CTarget, CCfgOptimizer, CCfgBackTest
from typedef import CCfg

with open("config.yaml", "r") as f:
    _config = yaml.safe_load(f)

d: TClassifications = {}
for cls_name, cls_data in _config["classification"].items():
    cls_name: TName
    cls_data: TClsData
    d[cls_name] = CSectorClassification(name=cls_name, data=cls_data)


cfg = CCfg(
    pid=_config["project_id"],
    vid=_config["version_id"],
    dbs=CCfgDbs(**_config["dbs"]),
    path_calendar=_config["path_calendar"],
    target=CTarget(
        freq=_config["target"]["freq"],
        clsf=d[_config["target"]["name"]],
    ),
    optimizer=CCfgOptimizer(**_config["optimizer"]),
    backtest=CCfgBackTest(**_config["backtest"]),
    project_data_dir=_config["project_data_dir"],
)

"""
-------------------
--- public data ---
-------------------
"""

data_desc_pv = CDataDescriptor(codes=cfg.codes, **_config["src_tables"]["pv"])
data_desc_pv1m = CDataDescriptor(codes=cfg.codes, **_config["src_tables"]["pv1m"])

"""
-----------------
--- user data ---
-----------------
"""

data_desc_sector = cfg.target.get_data_desc(db_name=cfg.dbs.user)
data_desc_optimize = CDataDescriptor(
    db_name=cfg.dbs.user,
    table_name=cfg.table_optimize,
    codes=cfg.target.clsf.sectors,
    fields=["wgt"],
    lag=120,
    data_view_type="data3d",
)
data_desc_sig_opt = CDataDescriptor(
    db_name=cfg.dbs.user,
    table_name=cfg.table_sig_opt,
    codes=cfg.codes,
    fields=["wgt"],
    lag=120,
    data_view_type="data3d",
)

"""
-----------------
--- Back Test ---
-----------------
"""

mkt_desc_fut = CMarketDescriptor(
    matcher="daily",
    ini_cash=cfg.backtest.init_cash,
    fee_rate=cfg.backtest.cost_rate_pri,
    account="detail",
    data=(cfg.dbs.public, "future_bar_1day_aft"),
    settle_price_table=(cfg.dbs.public, "future_bar_1day_aft"),
    settle_price_field="close",
    open_field="open",
    close_field="close",
    multiplier_field="multiplier",
    limit_up_field="limit_up",
    limit_down_field="limit_down",
    dominant_contract_table=(cfg.dbs.public, "future_dominant"),
)


if __name__ == "__main__":
    print(cfg)
    print(data_desc_pv)
    print(data_desc_pv1m)
