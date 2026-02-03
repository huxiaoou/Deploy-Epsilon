import yaml
from qtools_sxzq.qdata import CDataDescriptor
from typedef import TName, TClsData
from typedef import CCfgDbs, CSectorClassification, TClassifications
from typedef import CCfg

with open("config.yaml", "r") as f:
    _config = yaml.safe_load(f)

d: TClassifications = {}
for cls_name, cls_data in _config["classification"].items():
    cls_name: TName
    cls_data: TClsData
    d[cls_name] = CSectorClassification(name=cls_name, data=cls_data)

cfg = CCfg(
    dbs=CCfgDbs(**_config["dbs"]),
    path_calendar=_config["path_calendar"],
    classifications=d,
)

"""
-------------------
--- public data ---
-------------------
"""

data_desc_pv = CDataDescriptor(codes=[], **_config["src_tables"]["pv"])
data_desc_pv1m = CDataDescriptor(codes=[], **_config["src_tables"]["pv1m"])

if __name__ == "__main__":
    print(cfg)
    print(data_desc_pv)
    print(data_desc_pv1m)
