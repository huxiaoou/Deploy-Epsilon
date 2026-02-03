import numpy as np
import pandas as pd
from transmatrix import SignalMatrix
from transmatrix.strategy import SignalStrategy
from transmatrix.data_api import create_factor_table
from qtools_sxzq.qdata import CDataDescriptor
from typedef import CCfgOptimizer


class COptimizerSecWgt(SignalStrategy):
    CONST_SAFE_RET_LENGTH = 10
    CONST_ANNUAL_FAC = 250

    def __init__(self, cfg_optimizer: CCfgOptimizer, data_desc_sector: CDataDescriptor):
        self.cfg_optimizer: CCfgOptimizer
        self.data_desc_sector: CDataDescriptor
        super().__init__(cfg_optimizer, data_desc_sector)
        p = len(self.data_desc_sector.codes)
        self.opt_val: pd.Series = pd.Series(np.ones(p) / p, index=self.data_desc_sector.codes)

    def init(self):
        self.add_scheduler(milestones="15:00:00", handler=self.on_day_end)
        self.subscribe_data("sec_data", self.data_desc_sector.to_args())
        self.create_factor_table(["wgt"])

    def on_day_end(self):
        self.optimize()
        self.update_factor("wgt", self.opt_val)

    def optimize(self):
        net_ret_data: pd.DataFrame = self.sec_data.get_window_df(
            field="ret",
            length=self.cfg_optimizer.window,
            codes=self.codes,
        )
        self.opt_val = net_ret_data.mean()


def main_process_optimize_sec_wgt(
    span: tuple[str, str],
    cfg_optimizer: CCfgOptimizer,
    data_desc_sector: CDataDescriptor,
    dst_db: str,
    table_optimize: str,
):
    """

    :param span:
    :param cfg_optimizer:
    :param data_desc_sector:
    :param dst_db: database to save optimized weights for factors
    :param table_optimize: table to save optimized weights for factors
    :return:
    """
    cfg = {
        "span": span,
        "codes": data_desc_sector.codes,
        "cache_data": False,
        "progress_bar": True,
    }

    # --- run
    mat = SignalMatrix(cfg)
    optimizer = COptimizerSecWgt(
        cfg_optimizer=cfg_optimizer,
        data_desc_sector=data_desc_sector,
    )
    optimizer.set_name("optimizer")
    mat.add_component(optimizer)
    mat.init()
    mat.run()

    # --- save
    dst_path = f"{dst_db}.{table_optimize}"
    create_factor_table(dst_path)
    optimizer.save_factors(dst_path)
    return 0
