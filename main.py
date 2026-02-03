import argparse
from qtools_sxzq.qcalendar import CCalendar


def parse_args():
    arg_parser = argparse.ArgumentParser(description="This project is designed to try sector allocation")
    arg_parser.add_argument("command", type=str, choices=("optimize", "sig"))
    arg_parser.add_argument("--bgn", type=str, required=True, help="begin date, format = 'YYYYMMDD'")
    arg_parser.add_argument("--end", type=str, default=None, help="end date, format = 'YYYYMMDD'")
    return arg_parser.parse_args()


def validate_args(bgn_date: str, end_date: str, calendar: CCalendar) -> bool:
    if not calendar.is_trade_date(bgn_date) or not calendar.is_trade_date(end_date):
        print(f"[ERR] {bgn_date=:} or {end_date=:} is not in trade calendar, please check again.")
        return False
    return True


if __name__ == "__main__":
    import sys
    from logbook import Logger, StreamHandler, set_datetime_format
    from qtools_sxzq.qwidgets import SFG
    from config import cfg
    from config import data_desc_pv, data_desc_sector, data_desc_optimize, data_desc_sig_opt

    StreamHandler(sys.stdout).push_application()
    set_datetime_format("local")
    logger = Logger(f"{SFG('SZST')}")

    calendar = CCalendar(calendar_path=cfg.path_calendar)

    args = parse_args()
    bgn, end = args.bgn, args.end or args.bgn
    if not validate_args(bgn, end, calendar=calendar):
        sys.exit(-1)
    span: tuple[str, str] = bgn, end

    if args.command == "optimize":
        from solutions.optimize import main_process_optimize_sec_wgt

        main_process_optimize_sec_wgt(
            span=span,
            cfg_optimizer=cfg.optimizer,
            data_desc_sector=data_desc_sector,
            dst_db=data_desc_optimize.db_name,
            table_optimize=data_desc_optimize.table_name,
        )
    elif args.command == "sig":
        from solutions.signals import main_process_signals_sec_opt

        main_process_signals_sec_opt(
            span=span,
            codes=cfg.codes,
            data_desc_pv=data_desc_pv,
            data_desc_optimize=data_desc_optimize,
            clsf=cfg.target.clsf,
            dst_db=data_desc_sig_opt.db_name,
            table_sig_opt=data_desc_sig_opt.table_name,
        )
