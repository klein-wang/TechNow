

class RedisKey:
    YNG_CONSUMER_TIME_DATA_LOCK = "yng_consumer_time_data_lock"

    YNG_CONSUMER_ETL_MSG_LOCK = "yng_consumer_etl_msg_lock"

    YNG_SKU_VIEW_VALUE_LOCK = "yng_sku_view_value_lock"

    YNG_UPDATE_STATUS_LOCK = "yng_update_status_lock"

    YNG_UPDATE_SYSTEM_STATUS_LOCK = "yng_update_system_status_lock"

    SYSTEM_STATUS_KEY = 'yng_system_status'

    # 只会保留最新的一条状态  1 人工开始 2 人工结束  3 系统开始 4 系统结束
    SYSTEM_STATUS_KEY_LOG = 'yng_system_status_log'

    YNG_SCHEDULER_LOCK = "yng_scheduler_lock"


# 未用到点位
# 挤压机夹套温度上（设定值）
# WRITE_TAG_EXTRUDER_TEMPERATURE_UP = "SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_SP"
# 挤压机夹套温度下（设定值）
# WRITE_TAG_EXTRUDER_TEMPERATURE_LW = "SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_SP"
# 挤压机夹套温度嘴（设定值） SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_PH_Temp_SP
class WriteBackTagKey:
    # 1号辊间隙_ToPLC
    WRITE_TAG_1_ROLLER = "CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap1stSizing.rFormulaSP_inches"
    # 2号辊间隙_ToPLC
    WRITE_TAG_2_ROLLER = "CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap2ndSizing.rFormulaSP_inches"
    # 3号辊间隙_ToPLC
    WRITE_TAG_3_ROLLER = "CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rFormulaSP_inches"
    # 定型辊间隙_ToPLC
    WRITE_TAG_FORMING_ROLLER = "CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rFormulaSP_inches"
    # 横刀速度_ToPLC (横刀速度(设定值))
    WRITE_TAG_CROSS_CUTTER_SPEED = "CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rSetpoint_Ratio"
    # 挤压机PLC_Enabler(挤压机上下温度回写需要回写这个开关点位)
    WRITE_TAG_WRITE_TO_PLC_ENABLE = "SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.Write_To_PLC_Enable"
    # 挤压机夹套温度下_ToPLC
    WRITE_TAG_EXT_LB_TEMP_SP_TO_PLC = "SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_SP_ToPLC"
    # 挤压机夹套温度上_ToPLC
    WRITE_TAG_EXT_UB_TEMP_SP_TO_PLC = "SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_SP_ToPLC"

    # tag名字对应的中文描述
    TAG_MAP_ZN_NAME = {
        WRITE_TAG_1_ROLLER: "1号辊",
        WRITE_TAG_2_ROLLER: "2号辊",
        WRITE_TAG_3_ROLLER: "3号辊",
        WRITE_TAG_FORMING_ROLLER: "定型辊",
        WRITE_TAG_CROSS_CUTTER_SPEED: "横刀速度",
        WRITE_TAG_WRITE_TO_PLC_ENABLE: "挤压机夹套温度回写开关",
        WRITE_TAG_EXT_LB_TEMP_SP_TO_PLC: "挤压机夹套温度下",
        WRITE_TAG_EXT_UB_TEMP_SP_TO_PLC: "挤压机夹套温度上"
    }


# 回写之前查看这个点位有没有故障
class CheckWriteBackBefore:
    TAG_N1_ROLLER_UPDATE_CHECK = "n1_roller_update_check"
    TAG_N2_ROLLER_UPDATE_CHECK = "n2_roller_update_check"
    TAG_N3_ROLLER_UPDATE_CHECK = "n3_roller_update_check"
    TAG_FORMING_ROLLER_UPDATE_CHECK = "forming_roller_update_check"

    TAG_EVENT_MSG = {
        TAG_N1_ROLLER_UPDATE_CHECK: "1号辊间隙点位故障,无法回写",
        TAG_N2_ROLLER_UPDATE_CHECK: "2号辊间隙点位故障,无法回写",
        TAG_N3_ROLLER_UPDATE_CHECK: "3号辊间隙点位故障,无法回写",
        TAG_FORMING_ROLLER_UPDATE_CHECK: "定型辊间隙点位故障,无法回写"
    }


# 接受的点位数据限制
TAG_RUNNING_STATUS = "running_status"
TAG_SKU = "sku"
TAG_FORMULA = "formula"
# 挤压机温度夹套嘴
TAG_EXTRUDER_TEMPERATURE = "extruder_temperature"
TAG_SLICE_PRODUCT_LINE_SPEED = "slice_product_line_speed"
TAG_BIG_ROLLER_GAP = "big_roller_gap"
TAG_N1_ROLLER_GAP = "n1_roller_gap"
TAG_N2_ROLLER_GAP = "n2_roller_gap"
TAG_N3_ROLLER_GAP = "n3_roller_gap"
TAG_FORMING_ROLLER_GAP = "forming_roller_gap"
#  挤压机温度夹套上口 实际值
TAG_EXTRUDER_TEMPERATURE_UP = "extruder_temperature_up"
# 横刀速度  实际值
TAG_CROSS_CUTTER_SPEED = "cross_cutter_speed"

#  挤压机温度夹套上口 设定值
TAG_EXTRUDER_TEMPERATURE_UP_SV = "extruder_temperature_up_sv"
# 横刀速度 设定值
TAG_CROSS_CUTTER_SPEED_SV = "cross_cutter_speed_sv"

# 1号冷辊入口温度
TAG_DRUM1_INLET_TEMP = "drum1_inlet_temp"
# 2号冷辊入口温度
TAG_DRUM2_INLET_TEMP = "drum2_inlet_temp"
# 冷辊设定温度
TAG_CHILLER_SET_POINT = "chiller_set_point"

# 挤压机出口胶温
TAG_EXTRUDER_EXIT_GUM_TEMP = "extruder_exit_gum_temp"
# 冷辊入口胶温
TAG_GUM_ENTRANCE_TEMPERATURE = "gum_entrance_temperature"

# 系统操作的用户名,用于库里记录操作人使用
SYSTEM_OPERATOR_NAME = "SYSTEM"
MANUAL_OPERATOR_NAME = "MANUAL"

TARGET_WEIGHT = "2.71"
JOB_ID = "recommended_value_job"

