from dataclasses import dataclass
from typing import Literal
from qtools_sxzq.qdata import CDataDescriptor


@dataclass(frozen=True)
class CCfgDbs:
    public: str
    user: str


TFreq = Literal["d", "m", None]
TName = str
TSector = str
TInstrument = str
TClsData = dict[TSector, list[TInstrument]]
TInstruMap = dict[TSector, dict[TInstrument, int]]


@dataclass(frozen=True)
class CSectorClassification:
    name: TName  # ["c0", "c1", ...]
    data: TClsData

    def comb_name(self, freq: TFreq) -> str:
        return f"{self.name}_{freq}"

    @property
    def instru_map(self) -> TInstruMap:
        res: TInstruMap = {}
        for sector, instruments in self.data.items():
            sector: TSector
            instruments: list[TInstrument]
            res[sector] = {ins: 1 for ins in instruments}
        return res

    @property
    def sectors(self) -> list[str]:
        return sorted(list(self.data))

    @property
    def codes(self) -> list[str]:
        res: set[str] = set()
        for instruments in self.data.values():
            res = res.union(set(instruments))
        return sorted(list(res))

    def get_save_data_desc(self, db_name: str, freq: TFreq) -> CDataDescriptor:
        return CDataDescriptor(
            db_name=db_name,
            table_name=f"sector_{self.comb_name(freq)}",
            codes=self.sectors,
            fields=["ret", "close"],
            lag=365,
            data_view_type="data3d",
        )


TClassifications = dict[TName, CSectorClassification]


@dataclass(frozen=True)
class CTarget:
    freq: TFreq
    clsf: CSectorClassification

    def get_data_desc(self, db_name: str) -> CDataDescriptor:
        return self.clsf.get_save_data_desc(db_name, self.freq)


@dataclass(frozen=True)
class CCfgOptimizer:
    window: int
    lbd: float


@dataclass(frozen=True)
class CCfg:
    pid: str
    vid: str
    dbs: CCfgDbs
    path_calendar: str
    target: CTarget
    optimizer: CCfgOptimizer

    @property
    def codes(self) -> list[str]:
        return self.target.clsf.codes

    @property
    def table_optimize(self) -> str:
        return f"{self.pid}_tbl_optimize_{self.vid}"

    @property
    def table_sig_opt(self) -> str:
        return f"{self.pid}_tbl_sig_opt_{self.vid}"
