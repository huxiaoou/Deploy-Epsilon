import numpy as np
import pandas as pd
from transmatrix import SignalMatrix
from transmatrix.strategy import SignalStrategy
from transmatrix.data_api import create_factor_table
from qtools_sxzq.qdata import CDataDescriptor
from typedef import CSectorClassification

"""
------------------------------------
------- signals factor opt ---------
------------------------------------
"""


class CSignalsSecOpt(SignalStrategy):
    def __init__(
        self,
        data_desc_pv: CDataDescriptor,
        data_desc_optimize: CDataDescriptor,
        clsf: CSectorClassification,
    ):
        self.data_desc_pv: CDataDescriptor
        self.data_desc_optimize: CDataDescriptor
        super().__init__(data_desc_pv, data_desc_optimize, clsf)
        self.sec_df = (
            pd.DataFrame(self.clsf.instru_map).loc[self.data_desc_pv.codes, data_desc_optimize.codes].fillna(0)
        )

    def init(self):
        self.add_clock(milestones="15:00:00")
        self.subscribe_data("optimize", self.data_desc_optimize.to_args())
        self.subscribe_data("pv", self.data_desc_pv.to_args())
        self.create_factor_table(["wgt"])

    def on_clock(self):
        wgt_sec = pd.Series(self.optimize.get_dict("wgt"))
        amt_ins = pd.Series(self.pv.get_dict("turnover"))
        rel_wgt = np.sqrt(amt_ins.fillna(0))
        raw_wgt = self.sec_df.mul(rel_wgt, axis=0)
        wgt_sum = raw_wgt.sum(axis=0)
        nrm_wgt = (raw_wgt / wgt_sum).fillna(0)
        wgt = nrm_wgt @ wgt_sec
        self.update_factor("wgt", wgt[self.codes])


def main_process_signals_sec_opt(
    span: tuple[str, str],
    data_desc_pv: CDataDescriptor,
    data_desc_optimize: CDataDescriptor,
    clsf: CSectorClassification,
    dst_db: str,
    table_sig_opt: str,
):
    cfg = {
        "span": span,
        "codes": data_desc_pv.codes,
        "cache_data": False,
        "progress_bar": True,
    }

    # --- run
    mat = SignalMatrix(cfg)
    signals_fac_opt = CSignalsSecOpt(
        data_desc_pv=data_desc_pv,
        data_desc_optimize=data_desc_optimize,
        clsf=clsf,
    )
    signals_fac_opt.set_name("signals_fac_opt")
    mat.add_component(signals_fac_opt)
    mat.init()
    mat.run()

    # --- save
    dst_path = f"{dst_db}.{table_sig_opt}"
    create_factor_table(dst_path)
    signals_fac_opt.save_factors(dst_path)
    return 0
