#!/usr/bin/bash -l

echo "$(date +'%Y-%m-%d %H:%M:%S') begins"
pid=$(python -c $'import yaml\nwith open("config.yaml", "r") as f:_config = yaml.safe_load(f)\nprint(_config["project_id"])')
vid=$(python -c $'import yaml\nwith open("config.yaml", "r") as f:_config = yaml.safe_load(f)\nprint(_config["version_id"])')
udb=$(python -c $'import yaml\nwith open("config.yaml", "r") as f:_config = yaml.safe_load(f)\nprint(_config["dbs"]["user"])')
echo "project_id=$pid, version_id=$vid, user_db=$udb"

if [ "$#" -eq 1 ]; then
    if [ "$1" = "--auto" ]; then
        end_date=$(date +"%Y%m%d")
    else
        end_date="$1"
    fi
else
    read -p "Please input the end date, format = [YYYYMMDD]:" end_date
fi
echo "end_date = $end_date"

rm_tqdb $udb --table "$pid"_tbl_optimize_"$vid"
rm_tqdb $udb --table "$pid"_tbl_sig_opt_"$vid"
cls_prv_cache
echo "$(date +'%Y-%m-%d %H:%M:%S') old data removed"

bgn_date_opt="20180102"
bgn_date="20180102"

python main.py optimize --bgn $bgn_date_opt --end $end_date
python main.py sig --bgn $bgn_date --end $end_date
python main.py sim --bgn $bgn_date --end $end_date
