
CREATE TABLE [dbo].[yng_ts_raw_last_data](
	[id] [varchar](255) PRIMARY KEY,
	[ts] [varchar](255) default '',
	[name] [nvarchar](255) default '',--运行状态,香型，配方，挤压机温度，切片产线速度
	[value] [nvarchar](MAX) default '',
    [create_time] [datetime2](0) default NULL,
    [update_time] [datetime2](0) default NULL
);


create TABLE [dbo].[yng_event_log](
	[id] [int] IDENTITY(1,1) PRIMARY KEY,
	[sku] [nvarchar](255) default NULL, -- sku
	[shift] [nvarchar](255) default NULL,  -- 班次
	[actual_weight] decimal(10, 2) default NULL, -- 当前真实重量
	[type] int default NULL,  --  1 人工修改推荐值  2 sku参数配置 3 OPC点位数据变化 4 运行状态 5 推荐值回写记录 6 用户数据修改
    [type_name] [nvarchar](255) default '',
	[event_time] [varchar](255) default '',
	[content] [nvarchar](MAX) default '', -- 内容
	[content_ext] [nvarchar](MAX) default '',  -- 扩展内容
	[create_by] [nvarchar](255) default '',
	[update_by] [nvarchar](255) default '',
    [create_time] [datetime2](0) default NULL,
    [update_time] [datetime2](0) default NULL
);

CREATE TABLE [dbo].[yng_alert_log](
	[id] [int] IDENTITY(1,1) PRIMARY KEY,
	[sku] [nvarchar](255) default NULL,  -- sku
	[shift] [nvarchar](255) default '',  -- 班次
	[actual_weight] decimal(10, 2) default NULL, -- 当前真实重量
	[alert_time] [varchar](255) default '',
	[content] [nvarchar](255) default '',
	[create_by] [nvarchar](255) default '',
	[update_by] [nvarchar](255) default '',
    [create_time] [datetime2](0) default NULL,
    [update_time] [datetime2](0) default NULL
);


CREATE TABLE [dbo].[yng_dict_item](
	[id] [int] IDENTITY(1,1) PRIMARY KEY,
	[code] [varchar](255) default '',  -- code
	[name] [nvarchar](255) default ''  -- 名称
);

CREATE TABLE [dbo].[yng_dict_item_detail](
	[id] [int] IDENTITY(1,1) PRIMARY KEY,
	[item_code] int default NULL,  -- 字典id
	[item_value] [nvarchar](255) default '',  -- 具体项的值
	[seq] int default NULL, -- 名称,
	[dict_item_id] int default NULL  -- 字典id
);



CREATE TABLE [dbo].[yng_recommend_weight_data](
	[id] [int] IDENTITY(1,1) PRIMARY KEY,
	[sku] [nvarchar](255) default '',  -- sku
	[formula] [varchar](255) default '',  --配方
	[extruder_temperature] decimal(10, 4) default NULL,-- 挤压机温度夹套嘴
	[extruder_exit_gum_temp] decimal(10, 4) default NULL,-- 挤压机出口胶温度
	[slice_product_line_speed] decimal(10, 2) default NULL, -- 切片产线速度
	[n1_roller_gap] decimal(10, 4) default NULL, -- 1号辊间隙
	[n2_roller_gap] decimal(10, 4) default NULL, -- 2号辊间隙
	[n3_roller_gap] decimal(10, 4) default NULL, -- 3号辊间隙
	[forming_roller_gap] decimal(10, 4) default NULL, -- 定型辊间隙
	[extruder_temperature_up] decimal(10, 4) default NULL,-- 挤压机温度夹套上口
	[cross_cutter_speed] decimal(10, 2) default NULL,-- 推荐横刀速度
	[target_weight] decimal(10, 2) default NULL, -- 目标重量
	[data_time] [datetime2](0) default NULL,  -- opc最新一条的时间
	[weight_ts] [datetime2](0) default NULL,  -- spc称重时间
	[shift] [nvarchar](255) default '',  -- spc班次
	[actual_weight] decimal(10, 2) default NULL, -- spc当前真实重量
	[recommend_1_roller_gap] decimal(10, 4) default NULL, -- 推荐1号辊间隙
	[recommend_2_roller_gap] decimal(10, 4) default NULL, -- 推荐2号辊间隙
	[recommend_3_roller_gap] decimal(10, 4) default NULL, -- 推荐3号辊间隙
	[recommend_forming_roller_gap] decimal(10, 4) default NULL, -- 推荐定型辊间隙
	[recommend_extruder_temperature_up] decimal(10, 4) default NULL,-- 推荐挤压机温度夹套上口
	[recommend_cross_cutter_speed] decimal(10, 2) default NULL,-- 推荐横刀速度
	[predicted_weight] decimal(10, 2) default NULL, -- 预测重量
	[operator_status] [int] default NULL,-- 0 未操作 1 接受 2 部分接受 3 拒绝
	[operator_reason] [nvarchar](255) default '', -- 原因(拒绝原因)
	[write_back_status] [int] default NULL,-- 回写状态 0 失败 1 成功
	[create_by] [nvarchar](255) default '',
	[update_by] [nvarchar](255) default '',
	[create_time] [datetime2](0) default NULL,
    [update_time] [datetime2](0) default NULL

);

CREATE TABLE [dbo].[yng_recommend_weight_data_log](
	[id] [int] IDENTITY(1,1) PRIMARY KEY,
	[is_change] int default NULL,  -- # 是否需要调整
	[sku] [nvarchar](255) default '',  -- sku
	[formula] [varchar](255) default '',  --配方
	[extruder_temperature] decimal(10, 4) default NULL,-- 挤压机温度夹套嘴
	[extruder_exit_gum_temp] decimal(10, 4) default NULL,-- 挤压机出口胶温度
	[slice_product_line_speed] decimal(10, 2) default NULL, -- 切片产线速度
	[n1_roller_gap] decimal(10, 4) default NULL, -- 1号辊间隙
	[n2_roller_gap] decimal(10, 4) default NULL, -- 2号辊间隙
	[n3_roller_gap] decimal(10, 4) default NULL, -- 3号辊间隙
	[forming_roller_gap] decimal(10, 4) default NULL, -- 定型辊间隙
	[extruder_temperature_up] decimal(10, 4) default NULL,-- 挤压机温度夹套上口
	[cross_cutter_speed] decimal(10, 2) default NULL,-- 推荐横刀速度
	[target_weight] decimal(10, 2) default NULL, -- 目标重量
	[data_time] [datetime2](0) default NULL,  -- opc最新一条的时间
	[weight_ts] [datetime2](0) default NULL,  -- spc称重时间
	[shift] [nvarchar](255) default '',  -- spc班次
	[actual_weight] decimal(10, 2) default NULL, -- spc当前真实重量
	[ai_res_actual_weight] decimal(10, 2) default NULL, -- ai返回当前真实重量
	[recommend_1_roller_gap] decimal(10, 4) default NULL, -- 1号辊间隙
	[recommend_2_roller_gap] decimal(10, 4) default NULL, -- 2号辊间隙
	[recommend_3_roller_gap] decimal(10, 4) default NULL, -- 3号辊间隙
	[recommend_forming_roller_gap] decimal(10, 4) default NULL, -- 定型辊间隙
	[recommend_extruder_temperature_up] decimal(10, 4) default NULL,-- 挤压机温度夹套上口
	[recommend_cross_cutter_speed] decimal(10, 2) default NULL,-- 横刀速度
	[predicted_weight_before_change] decimal(10, 2) default NULL, -- 按照现有参数重量预测 页面用这个值
	[predicted_weight_after_change] decimal(10, 2) default NULL, -- 安装推荐的参数重量预测
	[recommend_weight_data_id] int default NULL,  -- # 推荐重量表id
	[create_by] [nvarchar](255) default '',
	[update_by] [nvarchar](255) default '',
	[create_time] [datetime2](0) default NULL,
    [update_time] [datetime2](0) default NULL
);


CREATE TABLE [dbo].[yng_dim_sku_data](
	[id] [int] IDENTITY(1,1) PRIMARY KEY,
	[sku_name] [nvarchar](255) default '',
	[fz_std] decimal(10, 2) default NULL,
	[fz_top_limit] decimal(10, 2) default NULL,
	[fz_bottom_limit] decimal(10, 2) default NULL,
	[fh_std] decimal(10, 2) default NULL,
	[fh_top_limit] decimal(10, 2) default NULL,
	[fh_bottom_limit] decimal(10, 2) default NULL,
	[fs_std] decimal(10, 2) default NULL,
	[fs_top_limit] decimal(10, 2) default NULL,
	[fs_bottom_limit] decimal(10, 2) default NULL,
	[fc_std] decimal(10, 2) default NULL,
	[fc_top_limit] decimal(10, 2) default NULL,
	[fc_bottom_limit] decimal(10, 2) default NULL,
	[fk_std] decimal(10, 2) default NULL,
	[fk_top_limit] decimal(10, 2) default NULL,
	[fk_bottom_limit] decimal(10, 2) default NULL,
	[n1_roller_std] decimal(10, 4) default NULL,
	[n1_roller_top_limit] decimal(10, 4) default NULL,
	[n1_roller_bottom_limit] decimal(10, 4) default NULL,
	[n2_roller_std] decimal(10, 4) default NULL,
	[n2_roller_top_limit] decimal(10, 4) default NULL,
	[n2_roller_bottom_limit] decimal(10, 4) default NULL,
	[n3_roller_std] decimal(10, 4) default NULL,
	[n3_roller_top_limit] decimal(10, 4) default NULL,
	[n3_roller_bottom_limit] decimal(10, 4) default NULL,
	[forming_roller_std] decimal(10, 4) default NULL,
	[forming_roller_top_limit] decimal(10, 4) default NULL,
	[forming_roller_bottom_limit] decimal(10, 4) default NULL,
	[cross_cutter_speed_std] decimal(10, 2) default NULL,
	[cross_cutter_speed_top_limit] decimal(10, 2) default NULL,
	[cross_cutter_speed_bottom_limit] decimal(10, 2) default NULL,
	[extruder_temperature_std] decimal(10, 4) default NULL,
	[extruder_temperature_top_limit] decimal(10, 4) default NULL,
	[extruder_temperature_bottom_limit] decimal(10, 4) default NULL,
	[create_by] [nvarchar](255) default '',
	[update_by] [nvarchar](255) default '',
	[create_time] [datetime2](0) default NULL,
	[update_time] [datetime2](0) default NULL
);

CREATE TABLE [dbo].[yng_dim_sku_data_log](
	[id] [int] IDENTITY(1,1) PRIMARY KEY,
	[sourceId] [int] default NULL,
	[sku_name] [nvarchar](255) default '',
	[fz_std] decimal(10, 2) default NULL,
	[fz_top_limit] decimal(10, 2) default NULL,
	[fz_bottom_limit] decimal(10, 2) default NULL,
	[fh_std] decimal(10, 2) default NULL,
	[fh_top_limit] decimal(10, 2) default NULL,
	[fh_bottom_limit] decimal(10, 2) default NULL,
	[fs_std] decimal(10, 2) default NULL,
	[fs_top_limit] decimal(10, 2) default NULL,
	[fs_bottom_limit] decimal(10, 2) default NULL,
	[fc_std] decimal(10, 2) default NULL,
	[fc_top_limit] decimal(10, 2) default NULL,
	[fc_bottom_limit] decimal(10, 2) default NULL,
	[fk_std] decimal(10, 2) default NULL,
	[fk_top_limit] decimal(10, 2) default NULL,
	[fk_bottom_limit] decimal(10, 2) default NULL,
	[n1_roller_std] decimal(10, 4) default NULL,
	[n1_roller_top_limit] decimal(10, 4) default NULL,
	[n1_roller_bottom_limit] decimal(10, 4) default NULL,
	[n2_roller_std] decimal(10, 4) default NULL,
	[n2_roller_top_limit] decimal(10, 4) default NULL,
	[n2_roller_bottom_limit] decimal(10, 4) default NULL,
	[n3_roller_std] decimal(10, 4) default NULL,
	[n3_roller_top_limit] decimal(10, 4) default NULL,
	[n3_roller_bottom_limit] decimal(10, 4) default NULL,
	[forming_roller_std] decimal(10, 4) default NULL,
	[forming_roller_top_limit] decimal(10, 4) default NULL,
	[forming_roller_bottom_limit] decimal(10, 4) default NULL,
	[cross_cutter_speed_std] decimal(10, 2) default NULL,
	[cross_cutter_speed_top_limit] decimal(10, 2) default NULL,
	[cross_cutter_speed_bottom_limit] decimal(10, 2) default NULL,
	[extruder_temperature_std] decimal(10, 4) default NULL,
	[extruder_temperature_top_limit] decimal(10, 4) default NULL,
	[extruder_temperature_bottom_limit] decimal(10, 4) default NULL,
	[create_by] [nvarchar](255) default '',
	[update_by] [nvarchar](255) default '',
	[create_time] [datetime2](0) default NULL,
	[update_time] [datetime2](0) default NULL,
	[operator] [nvarchar](255) default '',
	[operatorTime] [datetime2](0) default NULL
);


CREATE TABLE [dbo].[yng_ts_opc_data_log] (
    [id] [int] IDENTITY(1,1) PRIMARY KEY,
	[IOTDeviceID] [varchar](255) default '',
	[SiteId] [varchar](255) default '',
	[LineId] [varchar](255) default '',
    [SensorId] [varchar](255) default '',
	[MachineId] [varchar](255) default '',
	[Tag] [varchar](255) default '',
	[Value] [varchar](255) default '',
	[TS] [datetime] default NULL,
	[uuid][varchar](255) default '',
	[TS2] [datetime] default NULL,
    [CreationDate] [datetime] default GETDATE()
);


-- opc时序数据的动作表
CREATE TABLE [dbo].[yng_ts_raw_data_action_config](
	[id] [int] IDENTITY(1,1) PRIMARY KEY,
	[cn_name] [nvarchar](255) default '',
	[en_name] [nvarchar](255) default '',
	[map_tb_field_name] [nvarchar](255) default '',
	[action_code] int default NULL,  -- 1 OPC点位值变化，暂时就这一种动作，可扩展
    [create_time] [datetime2](0) default NULL,
    [update_time] [datetime2](0) default NULL
);

GO
SET IDENTITY_INSERT [dbo].[yng_ts_raw_data_action_config] ON

INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (1, N'运行状态', N'SFBMix.plcSFBMix.dbAdditionalParameter.StateFromSheeting.bMachineRunning', N'running_status', NULL, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (2, N'(SKU)香型', N'CG_Sheeting.CG_Sheeting.sCurrentFormula', N'sku', NULL, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (3, N'配方', N'SFBMix.plcSFBMix.dbRecipes_Current.Current[1].sName', N'formula', NULL, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (4, N'博士挤压机温度', N'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_PH_Temp_RealValue', N'extruder_temperature', NULL, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (5, N'切片产线速度', N'CG_Sheeting.CG_Sheeting.dbHMI.Variables.rSheetsPerMinuteActual', N'slice_product_line_speed', NULL, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (6, N'大辊间隙', N'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapBullRoll.rActualPosition_inches', N'big_roller_gap', NULL, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (7, N'1号辊', N'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap1stSizing.rActualPosition_inches', N'n1_roller_gap', NULL, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (8, N'2号辊', N'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap2ndSizing.rActualPosition_inches', N'n2_roller_gap', NULL, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (9, N'3号辊', N'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_Gap3rdSizing.rActualPosition_inches', N'n3_roller_gap', NULL, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (10, N'定型辊', N'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_GapFinalSizing.rActualPosition_inches', N'forming_roller_gap', NULL, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (11, N'系统速度（设定值）', N'CG_Sheeting.CG_Sheeting.dbHMI.Proform.Variables.rBaseline_Speed', NULL, 1, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (12, N'大辊速度（设定值）', N'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_BullRoll.rSetpoint_Ratio', NULL, 1, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (13, N'1号辊轮速度（设定值）', N'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_1stSizing.rSetpoint_Ratio', NULL, 1, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (14, N'2号辊轮速度（设定值）', N'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_2ndSizing.rSetpoint_Ratio', NULL, 1, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (15, N'3号辊轮速度（设定值）', N'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_3rdSizing.rSetpoint_Ratio', NULL, 1, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (16, N'定型辊速度（设定值）', N'CG_Sheeting.CG_Sheeting.dbHMI.Sheeting.SRV_FinalSizing.rSetpoint_Ratio', NULL, 1, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (17, N'圆刀速度（设定值', N'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CircularScore.rSetpoint_Ratio', NULL, 1, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (18, N'横刀速度（设定值）', N'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rSetpoint_Ratio', NULL, 1, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (19, N'挤压机夹套温度上（设定值）', N'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_SP', NULL, 1, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (20, N'挤压机夹套温度下（设定值）', N'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_LB_Temp_SP', NULL, 1, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (21, N'挤压机夹套温度嘴（设定值）', N'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_PH_Temp_SP', NULL, 1, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (22, N'挤压机喂胶轮速度（设定值）', N'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.Drum_Speed_SP', NULL, 1, CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2), CAST(N'2024-08-16T18:27:11.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (23, N'挤压机夹套温度上', N'SFBMix.PLC_BOSCH EXTRUDER.DB_Data_Exchange.EXT_UB_Temp_RealValue', N'extruder_temperature_up', NULL, CAST(N'2024-09-24T14:50:00.0000000' AS DateTime2), CAST(N'2024-09-24T14:50:00.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (24, N'横刀速度', N'CG_Sheeting.CG_Sheeting.dbHMI.Scoring.SRV_CrossScore.rActualVelocityRPM', N'cross_cutter_speed', NULL, CAST(N'2024-09-24T14:50:00.0000000' AS DateTime2), CAST(N'2024-09-24T14:50:00.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (25, N'1号冷辊入口温度', N'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum1InletTemp', N'drum1_inlet_temp', NULL, CAST(N'2024-10-09T18:00:00.0000000' AS DateTime2), CAST(N'2024-10-09T18:00:00.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (26, N'2号冷辊入口温度', N'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rDrum2InletTemp', N'drum2_inlet_temp', NULL, CAST(N'2024-10-09T18:00:00.0000000' AS DateTime2), CAST(N'2024-10-09T18:00:00.0000000' AS DateTime2))
INSERT [dbo].[yng_ts_raw_data_action_config] ([id], [cn_name], [en_name], [map_tb_field_name], [action_code], [create_time], [update_time]) VALUES (27, N'冷辊设定温度', N'CG_Sheeting.CG_Sheeting.dbHMI.Cooling.Variables.rChillerSetpoint', N'chiller_set_point', NULL, CAST(N'2024-10-09T18:00:00.0000000' AS DateTime2), CAST(N'2024-10-09T18:00:00.0000000' AS DateTime2))
SET IDENTITY_INSERT [dbo].[yng_ts_raw_data_action_config] OFF
GO

