## ======SPREAD GROUP mapping =======
class SpreadGroupMappers:
    member_spread_group_dict = {
        1: {'code': 'A', 'description': 'No additional spread', 'ranking': 7},
        2: {'code': 'B', 'description': 'Additional 2 points spread', 'ranking': 6},
        3: {'code': 'C', 'description': 'Additional 4 points spread', 'ranking': 5},
        4: {'code': 'D', 'description': 'Additional 6 points spread', 'ranking': 4},
        5: {'code': 'E', 'description': 'Additional 8 points spread', 'ranking': 3},
        6: {'code': 'F', 'description': 'Additional 10 points spread', 'ranking': 2},
        7: {'code': 'G', 'description': 'Additional 16 points spread', 'ranking': 1}
    }

    # using above ori dict, automatically build another lookup map for ranking to spreadID {ranking1: ID1,ranking2: ID2}
    _member_spread_group_ranking_to_id_map = {
        spread_data['ranking']: spread_id
        for spread_id, spread_data in member_spread_group_dict.items()
    }
    # helper functions for profileGroup
    @classmethod
    def get_ID_by_ranking(cls, ranking):
        # Extremely fast O(1) dictionary lookup
        return cls._member_spread_group_ranking_to_id_map.get(int(ranking), None)

    @classmethod
    def get_ranking_by_ID(cls,ID):
        ID = int(ID)
        return cls.member_spread_group_dict[ID]['ranking']
    @classmethod
    def get_name_by_ID(cls,ID):
        ID = int(ID)
        return cls.member_spread_group_dict[ID]['description']
    @classmethod
    def get_by_code(cls,code):
        for ID, data in cls.member_spread_group_dict.items():
            if data['code'] == code:
                return ID, data
        return None



##====MEMBER SETTING PROFILE mapping ## the bigger the number the less severe it is
class MemberProfileSettingMappers:
    member_profileSetting_dict = {
        1: {'name': 'GroupPercent100', 'description': '100% Group','percentage':100,'ranking': 26},
        2: {'name': 'GroupPercent75', 'description': '75% Group', 'percentage':75,'ranking': 18},
        3: {'name': 'GroupPercent50', 'description': '50% Group', 'percentage':50,'ranking': 13},
        4: {'name': 'GroupPercent25', 'description': '25% Group', 'percentage':25,'ranking': 8},
        5: {'name': 'GroupPercent10', 'description': '10% Group', 'percentage':10,'ranking': 5},
        6: {'name': 'GroupPercent5', 'description': '5% Group', 'percentage':5,'ranking': 4},
        7: {'name': 'GroupPercent250', 'description': '250% Group', 'percentage':250,'ranking': 28},
        8: {'name': 'GroupRMB50', 'description': 'RMB 50 Group', 'percentage':None,'ranking': 3},
        9: {'name': 'StdTics100Percentx2', 'description': '100% x 2 Std Tics', 'percentage':None,'ranking': 27},
        10: {'name': 'GroupPercent350', 'description': '350% Group', 'percentage':350,'ranking': 29},
        11: {'name': 'GroupRMB1', 'description': 'RMB 1 Group', 'percentage':None,'ranking': 2},
        12: {'name': 'GroupPercent800', 'description': '800% Group', 'percentage':800,'ranking': 33},
        13: {'name': 'GroupPercent500', 'description': '500% Group', 'percentage':500,'ranking': 30},
        14: {'name': 'GroupPercent600', 'description': '600% Group', 'percentage':600,'ranking': 31},
        15: {'name': 'GroupPercent700', 'description': '700% Group', 'percentage':700,'ranking': 32},
        16: {'name': 'GroupPercent15', 'description': '15% Group', 'percentage':15,'ranking': 6},
        17: {'name': 'GroupPercent20', 'description': '20% Group', 'percentage':20,'ranking': 7},
        18: {'name': 'GroupPercent30', 'description': '30% Group', 'percentage':30,'ranking': 9},
        19: {'name': 'GroupPercent35', 'description': '35% Group', 'percentage':35,'ranking': 10},
        20: {'name': 'GroupPercent40', 'description': '40% Group', 'percentage':40,'ranking': 11},
        21: {'name': 'GroupPercent45', 'description': '45% Group', 'percentage':45,'ranking': 12},
        22: {'name': 'GroupPercent55', 'description': '55% Group', 'percentage':55,'ranking': 14},
        23: {'name': 'GroupPercent60', 'description': '60% Group', 'percentage':60,'ranking': 15},
        24: {'name': 'GroupPercent65', 'description': '65% Group', 'percentage':65,'ranking': 16},
        25: {'name': 'GroupPercent70', 'description': '70% Group', 'percentage':70,'ranking': 17},
        26: {'name': 'GroupPercent80', 'description': '80% Group', 'percentage':80,'ranking': 22},
        27: {'name': 'GroupPercent85', 'description': '85% Group', 'percentage':85,'ranking': 23},
        28: {'name': 'GroupPercent90', 'description': '90% Group', 'percentage':90,'ranking': 24},
        29: {'name': 'GroupPercent95', 'description': '95% Group', 'percentage':95,'ranking': 25},
        30: {'name': 'MollyGroup', 'description': 'Molly Group', 'percentage':None,'ranking': 1}
    }

    # using above ori dict, automatically build another lookup map for ranking to spreadID {ranking1: ID1,ranking2: ID2}
    _member_profileSetting_ranking_to_id_map = {
        msp_data['ranking']: msp_id
        for msp_id, msp_data in member_profileSetting_dict.items()
    }
    _member_profileSetting_ranking_to_perc_map = {
        msp_data['ranking']: msp_data['percentage']
        for msp_id, msp_data in member_profileSetting_dict.items()
    }
    _member_profileSetting_perc_to_id_map = {
        msp_data['percentage']: msp_id
        for msp_id, msp_data in member_profileSetting_dict.items()
    }


    # helper functions for memberSettingProfile
    @classmethod
    def get_ID_by_ranking(cls, ranking):
        # Extremely fast O(1) dictionary lookup
        return cls._member_profileSetting_ranking_to_id_map.get(int(ranking), None)
    @classmethod
    def get_ranking_by_ID(cls,ID):
        ID = int(ID)
        return cls.member_profileSetting_dict[ID]['ranking']
    @classmethod
    def get_perc_by_ranking(cls, ranking):
        # Extremely fast O(1) dictionary lookup
        return cls._member_profileSetting_ranking_to_perc_map.get(int(ranking), None)
    @classmethod
    def get_perc_by_id(cls, ID):
        ID = int(ID)
        return cls.member_profileSetting_dict[ID]['percentage']
    @classmethod
    def get_id_by_percentage(cls, percentage):
        # Extremely fast O(1) dictionary lookup
        return cls._member_profileSetting_perc_to_id_map.get(int(percentage), None)
    @classmethod
    def get_name_by_value(cls,ID):
        ID = int(ID)
        return cls.member_profileSetting_dict[ID]['description']
    @classmethod
    def get_by_ranking(cls,ranking):
        for ID, data in cls.member_profileSetting_dict.items():
            if data['ranking'] == ranking:
                return ID, data
        return None
    @classmethod
    def get_by_name(cls,description):
        for ID, data in cls.member_profileSetting_dict.items():
            if data['description'] == description:
                return ID, data
        return None

#############MAPPING FOR BET DELAY SPORT GROUP
class SportGroupMapper:
    _mapping = {1001:[1],1002:[2],1003:[54,55],1000:['to populate dynamically']}

    @classmethod
    def get_all(cls):
        return cls._mapping
#############MAPPING FOR GBRULE & GBFEATURE

class ModuleMapper:
    _mapping = {
        "GbRule": 1,
        "GbFeature": 2
    }

    @classmethod
    def get(cls, code):
        return cls._mapping.get(code, None)

class GbRuleMapper:
    _mapping = {
        "Arber - Real BB": {            #module_code or name get it from simulator dropdown list
            "id": 2,                    #module_ID id associated with this module
            "UpdBy_Name":"GB_ArberRule_BB",      #updatedby_module, Module name to store in updatedBy field
            "action_featureOnOffFlag_id":281,
            "sportdict": [
                {"sportID": 2, "sportTypeID": 1}
            ],
            "sport": [
                (2, 1)
            ]
        },
        "Arber - Real Soccer": {
            "id": 1,
            "UpdBy_Name": "GB_ArberRule_SC",
            "action_featureOnOffFlag_id": 278,
            "sportdict": [
                {"sportID": 1, "sportTypeID": 1}
            ],
            "sport": [
                (1, 1)
            ]
        },
        "FAMember - Exceed API Count": {
            "id": 4,
            "UpdBy_Name": "GB_FAMem_ExceedAPICount",
            "action_featureOnOffFlag_id": 501,
            "sportdict": [
                {"sportID": 1, "sportTypeID": 1},
                {"sportID": 1, "sportTypeID": 2},
                {"sportID": 2, "sportTypeID": 1},
                {"sportID": 2, "sportTypeID": 2},
                {"sportID": 54, "sportTypeID": 2},
                {"sportID": 55, "sportTypeID": 2}
            ],
            "sport": [
                (1, 1),(1,2),(2,1),(2,2),(54,2),(55,2)
            ]
        },
        "LateBet - Real Basketball": {
            "id": 10,
            "UpdBy_Name": "GB_LateBetRule",
            "action_featureOnOffFlag_id": 657,
            "sportdict": [
                {"sportID": 2, "sportTypeID": 1}
            ],
            "sport": [
                (2, 1)
            ]
        },
        "MBR - Real Basketball": {
            "id": 6,
            "UpdBy_Name": "GB_MBRRule_BB",
            "action_featureOnOffFlag_id": 557,
            "sportdict": [
                {"sportID": 2, "sportTypeID": 1}
            ],
            "sport": [
                (2, 1)
            ]
        },
        "MBR - Real Soccer": {
            "id": 5,
            "UpdBy_Name": "GB_MBRRule_SC",
            "action_featureOnOffFlag_id": 556,
            "sportdict": [
                {"sportID": 1, "sportTypeID": 1}
            ],
            "sport": [
                (1, 1)
            ]
        },
        "ML UI Level - Robot": {
            "id": 7,
            "UpdBy_Name": "GB_MLTagging_UIRobot",
            "action_featureOnOffFlag_id": 608,
            "sportdict": [
                {"sportID": 1, "sportTypeID": 1},
                {"sportID": 1, "sportTypeID": 2},
                {"sportID": 2, "sportTypeID": 1},
                {"sportID": 2, "sportTypeID": 2},
                {"sportID": 3, "sportTypeID": 1},
                {"sportID": 3, "sportTypeID": 2},
                {"sportID": 4, "sportTypeID": 1},
                {"sportID": 4, "sportTypeID": 2},
                {"sportID": 5, "sportTypeID": 1},
                {"sportID": 5, "sportTypeID": 2},
                {"sportID": 6, "sportTypeID": 1},
                {"sportID": 6, "sportTypeID": 2},
                {"sportID": 7, "sportTypeID": 1},
                {"sportID": 7, "sportTypeID": 2},
                {"sportID": 8, "sportTypeID": 1},
                {"sportID": 8, "sportTypeID": 2},
                {"sportID": 9, "sportTypeID": 1},
                {"sportID": 9, "sportTypeID": 2},
                {"sportID": 10, "sportTypeID": 1},
                {"sportID": 10, "sportTypeID": 2},
                {"sportID": 11, "sportTypeID": 1},
                {"sportID": 11, "sportTypeID": 2},
                {"sportID": 12, "sportTypeID": 1},
                {"sportID": 12, "sportTypeID": 2},
                {"sportID": 13, "sportTypeID": 1},
                {"sportID": 13, "sportTypeID": 2},
                {"sportID": 14, "sportTypeID": 1},
                {"sportID": 14, "sportTypeID": 2},
                {"sportID": 15, "sportTypeID": 1},
                {"sportID": 15, "sportTypeID": 2},
                {"sportID": 16, "sportTypeID": 1},
                {"sportID": 16, "sportTypeID": 2},
                {"sportID": 17, "sportTypeID": 1},
                {"sportID": 17, "sportTypeID": 2},
                {"sportID": 18, "sportTypeID": 1},
                {"sportID": 18, "sportTypeID": 2},
                {"sportID": 19, "sportTypeID": 1},
                {"sportID": 19, "sportTypeID": 2},
                {"sportID": 20, "sportTypeID": 1},
                {"sportID": 20, "sportTypeID": 2},
                {"sportID": 21, "sportTypeID": 1},
                {"sportID": 21, "sportTypeID": 2},
                {"sportID": 22, "sportTypeID": 1},
                {"sportID": 22, "sportTypeID": 2},
                {"sportID": 23, "sportTypeID": 1},
                {"sportID": 23, "sportTypeID": 2},
                {"sportID": 24, "sportTypeID": 1},
                {"sportID": 24, "sportTypeID": 2},
                {"sportID": 25, "sportTypeID": 1},
                {"sportID": 25, "sportTypeID": 2},
                {"sportID": 26, "sportTypeID": 1},
                {"sportID": 26, "sportTypeID": 2},
                {"sportID": 27, "sportTypeID": 1},
                {"sportID": 27, "sportTypeID": 2},
                {"sportID": 28, "sportTypeID": 1},
                {"sportID": 28, "sportTypeID": 2},
                {"sportID": 29, "sportTypeID": 1},
                {"sportID": 29, "sportTypeID": 2},
                {"sportID": 30, "sportTypeID": 1},
                {"sportID": 30, "sportTypeID": 2},
                {"sportID": 31, "sportTypeID": 1},
                {"sportID": 31, "sportTypeID": 2},
                {"sportID": 32, "sportTypeID": 1},
                {"sportID": 32, "sportTypeID": 2},
                {"sportID": 33, "sportTypeID": 1},
                {"sportID": 33, "sportTypeID": 2},
                {"sportID": 34, "sportTypeID": 1},
                {"sportID": 34, "sportTypeID": 2},
                {"sportID": 35, "sportTypeID": 1},
                {"sportID": 35, "sportTypeID": 2},
                {"sportID": 36, "sportTypeID": 1},
                {"sportID": 36, "sportTypeID": 2},
                {"sportID": 37, "sportTypeID": 1},
                {"sportID": 37, "sportTypeID": 2},
                {"sportID": 38, "sportTypeID": 1},
                {"sportID": 38, "sportTypeID": 2},
                {"sportID": 39, "sportTypeID": 1},
                {"sportID": 39, "sportTypeID": 2},
                {"sportID": 40, "sportTypeID": 1},
                {"sportID": 40, "sportTypeID": 2},
                {"sportID": 41, "sportTypeID": 1},
                {"sportID": 41, "sportTypeID": 2},
                {"sportID": 42, "sportTypeID": 1},
                {"sportID": 42, "sportTypeID": 2},
                {"sportID": 43, "sportTypeID": 1},
                {"sportID": 43, "sportTypeID": 2},
                {"sportID": 44, "sportTypeID": 1},
                {"sportID": 44, "sportTypeID": 2},
                {"sportID": 45, "sportTypeID": 1},
                {"sportID": 45, "sportTypeID": 2},
                {"sportID": 46, "sportTypeID": 1},
                {"sportID": 46, "sportTypeID": 2},
                {"sportID": 47, "sportTypeID": 1},
                {"sportID": 47, "sportTypeID": 2},
                {"sportID": 48, "sportTypeID": 1},
                {"sportID": 48, "sportTypeID": 2},
                {"sportID": 49, "sportTypeID": 1},
                {"sportID": 49, "sportTypeID": 2},
                {"sportID": 50, "sportTypeID": 1},
                {"sportID": 50, "sportTypeID": 2},
                {"sportID": 51, "sportTypeID": 1},
                {"sportID": 51, "sportTypeID": 2},
                {"sportID": 52, "sportTypeID": 1},
                {"sportID": 52, "sportTypeID": 2},
                {"sportID": 53, "sportTypeID": 1},
                {"sportID": 53, "sportTypeID": 2},
                {"sportID": 54, "sportTypeID": 1},
                {"sportID": 54, "sportTypeID": 2},
                {"sportID": 55, "sportTypeID": 1},
                {"sportID": 55, "sportTypeID": 2},
                {"sportID": 56, "sportTypeID": 1},
                {"sportID": 56, "sportTypeID": 2},
                {"sportID": 57, "sportTypeID": 1},
                {"sportID": 57, "sportTypeID": 2},
                {"sportID": 58, "sportTypeID": 1},
                {"sportID": 58, "sportTypeID": 2},
                {"sportID": 59, "sportTypeID": 1},
                {"sportID": 59, "sportTypeID": 2},
                {"sportID": 60, "sportTypeID": 1},
                {"sportID": 60, "sportTypeID": 2},
                {"sportID": 61, "sportTypeID": 1},
                {"sportID": 61, "sportTypeID": 2},
                {"sportID": 62, "sportTypeID": 1},
                {"sportID": 62, "sportTypeID": 2},
                {"sportID": 63, "sportTypeID": 1},
                {"sportID": 63, "sportTypeID": 2},
                {"sportID": 64, "sportTypeID": 1},
                {"sportID": 64, "sportTypeID": 2},
                {"sportID": 65, "sportTypeID": 1},
                {"sportID": 65, "sportTypeID": 2},
                {"sportID": 66, "sportTypeID": 1},
                {"sportID": 66, "sportTypeID": 2},
                {"sportID": 67, "sportTypeID": 1},
                {"sportID": 67, "sportTypeID": 2}
            ],
            "sport": [
                (1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (3, 2), (4, 1), (4, 2), (5, 1), (5, 2), (6, 1), (6, 2), (7, 1), (7, 2), (8, 1), (8, 2), (9, 1),
                (9, 2), (10, 1), (10, 2), (11, 1), (11, 2), (12, 1), (12, 2), (13, 1), (13, 2), (14, 1), (14, 2), (15, 1), (15, 2), (16, 1), (16, 2),
                (17, 1), (17, 2), (18, 1), (18, 2), (19, 1), (19, 2), (20, 1), (20, 2), (21, 1), (21, 2), (22, 1), (22, 2), (23, 1), (23, 2), (24, 1), (24, 2),
                (25, 1), (25, 2), (26, 1), (26, 2), (27, 1), (27, 2), (28, 1), (28, 2), (29, 1), (29, 2), (30, 1), (30, 2), (31, 1), (31, 2), (32, 1), (32, 2),
                (33, 1), (33, 2), (34, 1), (34, 2), (35, 1), (35, 2), (36, 1), (36, 2), (37, 1), (37, 2), (38, 1), (38, 2), (39, 1), (39, 2), (40, 1), (40, 2),
                (41, 1), (41, 2), (42, 1), (42, 2), (43, 1), (43, 2), (44, 1), (44, 2), (45, 1), (45, 2), (46, 1), (46, 2), (47, 1), (47, 2), (48, 1), (48, 2),
                (49, 1), (49, 2), (50, 1), (50, 2), (51, 1), (51, 2), (52, 1), (52, 2), (53, 1), (53, 2), (54, 1), (54, 2), (55, 1), (55, 2), (56, 1), (56, 2),
                (57, 1), (57, 2), (58, 1), (58, 2), (59, 1), (59, 2), (60, 1), (60, 2), (61, 1), (61, 2), (62, 1), (62, 2), (63, 1), (63, 2), (64, 1), (64, 2),
                (65, 1), (65, 2), (66, 1), (66, 2), (67, 1), (67, 2)

            ]
        },
        "ML Wager Level": {
            "id": 3,
            "UpdBy_Name": "GB_NewMLTag_Wager",
            "action_featureOnOffFlag_id": 610,
            "sportdict": [
                {"sportID": 1, "sportTypeID": 1},
                {"sportID": 2, "sportTypeID": 1}
            ],
            "sport": [
                (1, 1),(2,1)
            ]
        },
        "TWM - Real Basketball": {
            "id": 9,
            "UpdBy_Name": "GB_TWMRule_BB",
            "action_featureOnOffFlag_id": 654,
            "sportdict": [
                {"sportID": 2, "sportTypeID": 1}
            ],
            "sport": [
                (2, 1)
            ]
        },
        "TWM - Real Soccer": {
            "id": 8,
            "UpdBy_Name": "GB_TWMRule_SC",
            "action_featureOnOffFlag_id": 613,
            "sportdict": [
                {"sportID": 1, "sportTypeID": 1}
            ],
            "sport": [
                (1, 1)
            ]
        },
        "EGON": {
            "id": 11,
            "UpdBy_Name": "GB_EGON",
            "action_featureOnOffFlag_id": 730,
            "sportdict": [
                {"sportID": 1, "sportTypeID": 1},
                {"sportID": 1, "sportTypeID": 2},
                {"sportID": 2, "sportTypeID": 1},
                {"sportID": 2, "sportTypeID": 2},
                {"sportID": 3, "sportTypeID": 1},
                {"sportID": 3, "sportTypeID": 2},
                {"sportID": 4, "sportTypeID": 1},
                {"sportID": 4, "sportTypeID": 2},
                {"sportID": 5, "sportTypeID": 1},
                {"sportID": 5, "sportTypeID": 2},
                {"sportID": 6, "sportTypeID": 1},
                {"sportID": 6, "sportTypeID": 2},
                {"sportID": 7, "sportTypeID": 1},
                {"sportID": 7, "sportTypeID": 2},
                {"sportID": 8, "sportTypeID": 1},
                {"sportID": 8, "sportTypeID": 2},
                {"sportID": 9, "sportTypeID": 1},
                {"sportID": 9, "sportTypeID": 2},
                {"sportID": 10, "sportTypeID": 1},
                {"sportID": 10, "sportTypeID": 2},
                {"sportID": 11, "sportTypeID": 1},
                {"sportID": 11, "sportTypeID": 2},
                {"sportID": 12, "sportTypeID": 1},
                {"sportID": 12, "sportTypeID": 2},
                {"sportID": 13, "sportTypeID": 1},
                {"sportID": 13, "sportTypeID": 2},
                {"sportID": 14, "sportTypeID": 1},
                {"sportID": 14, "sportTypeID": 2},
                {"sportID": 15, "sportTypeID": 1},
                {"sportID": 15, "sportTypeID": 2},
                {"sportID": 16, "sportTypeID": 1},
                {"sportID": 16, "sportTypeID": 2},
                {"sportID": 17, "sportTypeID": 1},
                {"sportID": 17, "sportTypeID": 2},
                {"sportID": 18, "sportTypeID": 1},
                {"sportID": 18, "sportTypeID": 2},
                {"sportID": 19, "sportTypeID": 1},
                {"sportID": 19, "sportTypeID": 2},
                {"sportID": 20, "sportTypeID": 1},
                {"sportID": 20, "sportTypeID": 2},
                {"sportID": 21, "sportTypeID": 1},
                {"sportID": 21, "sportTypeID": 2},
                {"sportID": 22, "sportTypeID": 1},
                {"sportID": 22, "sportTypeID": 2},
                {"sportID": 23, "sportTypeID": 1},
                {"sportID": 23, "sportTypeID": 2},
                {"sportID": 24, "sportTypeID": 1},
                {"sportID": 24, "sportTypeID": 2},
                {"sportID": 25, "sportTypeID": 1},
                {"sportID": 25, "sportTypeID": 2},
                {"sportID": 26, "sportTypeID": 1},
                {"sportID": 26, "sportTypeID": 2},
                {"sportID": 27, "sportTypeID": 1},
                {"sportID": 27, "sportTypeID": 2},
                {"sportID": 28, "sportTypeID": 1},
                {"sportID": 28, "sportTypeID": 2},
                {"sportID": 29, "sportTypeID": 1},
                {"sportID": 29, "sportTypeID": 2},
                {"sportID": 30, "sportTypeID": 1},
                {"sportID": 30, "sportTypeID": 2},
                {"sportID": 31, "sportTypeID": 1},
                {"sportID": 31, "sportTypeID": 2},
                {"sportID": 32, "sportTypeID": 1},
                {"sportID": 32, "sportTypeID": 2},
                {"sportID": 33, "sportTypeID": 1},
                {"sportID": 33, "sportTypeID": 2},
                {"sportID": 34, "sportTypeID": 1},
                {"sportID": 34, "sportTypeID": 2},
                {"sportID": 35, "sportTypeID": 1},
                {"sportID": 35, "sportTypeID": 2},
                {"sportID": 36, "sportTypeID": 1},
                {"sportID": 36, "sportTypeID": 2},
                {"sportID": 37, "sportTypeID": 1},
                {"sportID": 37, "sportTypeID": 2},
                {"sportID": 38, "sportTypeID": 1},
                {"sportID": 38, "sportTypeID": 2},
                {"sportID": 39, "sportTypeID": 1},
                {"sportID": 39, "sportTypeID": 2},
                {"sportID": 40, "sportTypeID": 1},
                {"sportID": 40, "sportTypeID": 2},
                {"sportID": 41, "sportTypeID": 1},
                {"sportID": 41, "sportTypeID": 2},
                {"sportID": 42, "sportTypeID": 1},
                {"sportID": 42, "sportTypeID": 2},
                {"sportID": 43, "sportTypeID": 1},
                {"sportID": 43, "sportTypeID": 2},
                {"sportID": 44, "sportTypeID": 1},
                {"sportID": 44, "sportTypeID": 2},
                {"sportID": 45, "sportTypeID": 1},
                {"sportID": 45, "sportTypeID": 2},
                {"sportID": 46, "sportTypeID": 1},
                {"sportID": 46, "sportTypeID": 2},
                {"sportID": 47, "sportTypeID": 1},
                {"sportID": 47, "sportTypeID": 2},
                {"sportID": 48, "sportTypeID": 1},
                {"sportID": 48, "sportTypeID": 2},
                {"sportID": 49, "sportTypeID": 1},
                {"sportID": 49, "sportTypeID": 2},
                {"sportID": 50, "sportTypeID": 1},
                {"sportID": 50, "sportTypeID": 2},
                {"sportID": 51, "sportTypeID": 1},
                {"sportID": 51, "sportTypeID": 2},
                {"sportID": 52, "sportTypeID": 1},
                {"sportID": 52, "sportTypeID": 2},
                {"sportID": 53, "sportTypeID": 1},
                {"sportID": 53, "sportTypeID": 2},
                {"sportID": 54, "sportTypeID": 1},
                {"sportID": 54, "sportTypeID": 2},
                {"sportID": 55, "sportTypeID": 1},
                {"sportID": 55, "sportTypeID": 2},
                {"sportID": 56, "sportTypeID": 1},
                {"sportID": 56, "sportTypeID": 2},
                {"sportID": 57, "sportTypeID": 1},
                {"sportID": 57, "sportTypeID": 2},
                {"sportID": 58, "sportTypeID": 1},
                {"sportID": 58, "sportTypeID": 2},
                {"sportID": 59, "sportTypeID": 1},
                {"sportID": 59, "sportTypeID": 2},
                {"sportID": 60, "sportTypeID": 1},
                {"sportID": 60, "sportTypeID": 2},
                {"sportID": 61, "sportTypeID": 1},
                {"sportID": 61, "sportTypeID": 2},
                {"sportID": 62, "sportTypeID": 1},
                {"sportID": 62, "sportTypeID": 2},
                {"sportID": 63, "sportTypeID": 1},
                {"sportID": 63, "sportTypeID": 2},
                {"sportID": 64, "sportTypeID": 1},
                {"sportID": 64, "sportTypeID": 2},
                {"sportID": 65, "sportTypeID": 1},
                {"sportID": 65, "sportTypeID": 2},
                {"sportID": 66, "sportTypeID": 1},
                {"sportID": 66, "sportTypeID": 2},
                {"sportID": 67, "sportTypeID": 1},
                {"sportID": 67, "sportTypeID": 2}
            ],
            "sport": [
                (1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (3, 2), (4, 1), (4, 2), (5, 1), (5, 2), (6, 1), (6, 2), (7, 1),
                (7, 2), (8, 1), (8, 2), (9, 1),
                (9, 2), (10, 1), (10, 2), (11, 1), (11, 2), (12, 1), (12, 2), (13, 1), (13, 2), (14, 1), (14, 2),
                (15, 1), (15, 2), (16, 1), (16, 2),
                (17, 1), (17, 2), (18, 1), (18, 2), (19, 1), (19, 2), (20, 1), (20, 2), (21, 1), (21, 2), (22, 1),
                (22, 2), (23, 1), (23, 2), (24, 1), (24, 2),
                (25, 1), (25, 2), (26, 1), (26, 2), (27, 1), (27, 2), (28, 1), (28, 2), (29, 1), (29, 2), (30, 1),
                (30, 2), (31, 1), (31, 2), (32, 1), (32, 2),
                (33, 1), (33, 2), (34, 1), (34, 2), (35, 1), (35, 2), (36, 1), (36, 2), (37, 1), (37, 2), (38, 1),
                (38, 2), (39, 1), (39, 2), (40, 1), (40, 2),
                (41, 1), (41, 2), (42, 1), (42, 2), (43, 1), (43, 2), (44, 1), (44, 2), (45, 1), (45, 2), (46, 1),
                (46, 2), (47, 1), (47, 2), (48, 1), (48, 2),
                (49, 1), (49, 2), (50, 1), (50, 2), (51, 1), (51, 2), (52, 1), (52, 2), (53, 1), (53, 2), (54, 1),
                (54, 2), (55, 1), (55, 2), (56, 1), (56, 2),
                (57, 1), (57, 2), (58, 1), (58, 2), (59, 1), (59, 2), (60, 1), (60, 2), (61, 1), (61, 2), (62, 1),
                (62, 2), (63, 1), (63, 2), (64, 1), (64, 2),
                (65, 1), (65, 2), (66, 1), (66, 2), (67, 1), (67, 2)

            ]
        },
        "1H ART - Real Soccer": {
            "id": 16,
            "UpdBy_Name": "GB_ART_SC1H",
            "action_featureOnOffFlag_id": 724,
            "sportdict": [
                {"sportID": 1, "sportTypeID": 1}
            ],
            "sport": [
                (1, 1)
            ]
        },
        "FT ART - Real Soccer": {
            "id": 17,
            "UpdBy_Name": "GB_ART_SCFT",
            "action_featureOnOffFlag_id": 727,
            "sportdict": [
                {"sportID": 1, "sportTypeID": 1}
            ],
            "sport": [
                (1, 1)
            ]
        }
    }

    # using above ori dict, automatically build another lookup map for updByName to id {'GB_ART_SCFT': 17,'GB_ART_SC1H': 16,...}
    _mapping_updByName_to_id = {
        Gbrule_data['UpdBy_Name']: Gbrule_data['id']
        for Gbrule_code, Gbrule_data in _mapping.items()
    }

    @classmethod
    def get_id_by_updByName(cls, updByName):
        # Extremely fast O(1) dictionary lookup
        return cls._mapping_updByName_to_id.get(updByName, None)
    @classmethod
    def get_id_byCode(cls, code):  #to get id associated with each name/code
        return cls._mapping.get(code, {}).get('id')
    @classmethod
    def get_updByName_byCode(cls, code):  #to get UpdatedBy_SysName associated with each name/code
        return cls._mapping.get(code, {}).get('UpdBy_Name')
    @classmethod
    def get_sports_byCode(cls, code):
        return cls._mapping.get(code, {}).get('sport')
    @classmethod
    def get_sports_byID(cls, id):
        return cls._mapping.get(id, {}).get('sport')
    @classmethod
    def get_action_featureOnOffFlag_id_byCode(cls, code):
        return cls._mapping.get(code, {}).get('action_featureOnOffFlag_id')

class GbFeatureMapper:
    _mapping = {
        "Member Listing": {
            "id": 14,
            "UpdBy_Name": "GB_MemberList",
            "sportdict": [
                {"sportID": 9, "sportTypeID": 9},
                {"sportID": 9, "sportTypeID": 9},
                {"sportID": 9, "sportTypeID": 9}
            ],
            "sport": [
                (9,9),(9,9),(9,9)
            ]
        },
        "Late Bet": {
            "id": 19,
            "UpdBy_Name": "GB_LateBet",
            "action_featureOnOffFlag_id": 657,
            "sportdict": [
                {"sportID": 1, "sportTypeID": 1}
            ],
            "sport": [
                (1,1)
            ]
        },
        "FAMember - Invalid Key": {
            "id": 74,
            "UpdBy_Name": "GB_FAMemFeatures_InvKey",
            "action_featureOnOffFlag_id": 504,
            "sportdict": [
                {"sportID": 1, "sportTypeID": 1},
                {"sportID": 1, "sportTypeID": 2},
                {"sportID": 2, "sportTypeID": 1},
                {"sportID": 2, "sportTypeID": 2},
                {"sportID": 54, "sportTypeID": 2},
                {"sportID": 55, "sportTypeID": 2}
            ],
            "sport": [
                (1,1),(1,2),(2,1),(2,2),(54,2),(55,2)
            ]
        },
        "ISBBR - Real Basketball": {      #name get it from simulator dropdown list
            "id": 126,
            "UpdBy_Name": "GB_ISBBR_RealBB",
            "action_featureOnOffFlag_id": 743,
            "sportdict": [
                {"sportID": 2, "sportTypeID": 1}
            ],
            "sport": [
                (2, 1)
            ]
        },
        "MLTag UI Arber": {
            "id": 84,
            "UpdBy_Name": "GB_MLTagging_UIArber",
            "action_featureOnOffFlag_id": 610,
            "sportdict": [
                {"sportID": 1, "sportTypeID": 1},
                {"sportID": 1, "sportTypeID": 2},
                {"sportID": 2, "sportTypeID": 1},
                {"sportID": 2, "sportTypeID": 2},
                {"sportID": 3, "sportTypeID": 1},
                {"sportID": 3, "sportTypeID": 2},
                {"sportID": 4, "sportTypeID": 1},
                {"sportID": 4, "sportTypeID": 2},
                {"sportID": 5, "sportTypeID": 1},
                {"sportID": 5, "sportTypeID": 2},
                {"sportID": 6, "sportTypeID": 1},
                {"sportID": 6, "sportTypeID": 2},
                {"sportID": 7, "sportTypeID": 1},
                {"sportID": 7, "sportTypeID": 2},
                {"sportID": 8, "sportTypeID": 1},
                {"sportID": 8, "sportTypeID": 2},
                {"sportID": 9, "sportTypeID": 1},
                {"sportID": 9, "sportTypeID": 2},
                {"sportID": 10, "sportTypeID": 1},
                {"sportID": 10, "sportTypeID": 2},
                {"sportID": 11, "sportTypeID": 1},
                {"sportID": 11, "sportTypeID": 2},
                {"sportID": 12, "sportTypeID": 1},
                {"sportID": 12, "sportTypeID": 2},
                {"sportID": 13, "sportTypeID": 1},
                {"sportID": 13, "sportTypeID": 2},
                {"sportID": 14, "sportTypeID": 1},
                {"sportID": 14, "sportTypeID": 2},
                {"sportID": 15, "sportTypeID": 1},
                {"sportID": 15, "sportTypeID": 2},
                {"sportID": 16, "sportTypeID": 1},
                {"sportID": 16, "sportTypeID": 2},
                {"sportID": 17, "sportTypeID": 1},
                {"sportID": 17, "sportTypeID": 2},
                {"sportID": 18, "sportTypeID": 1},
                {"sportID": 18, "sportTypeID": 2},
                {"sportID": 19, "sportTypeID": 1},
                {"sportID": 19, "sportTypeID": 2},
                {"sportID": 20, "sportTypeID": 1},
                {"sportID": 20, "sportTypeID": 2},
                {"sportID": 21, "sportTypeID": 1},
                {"sportID": 21, "sportTypeID": 2},
                {"sportID": 22, "sportTypeID": 1},
                {"sportID": 22, "sportTypeID": 2},
                {"sportID": 23, "sportTypeID": 1},
                {"sportID": 23, "sportTypeID": 2},
                {"sportID": 24, "sportTypeID": 1},
                {"sportID": 24, "sportTypeID": 2},
                {"sportID": 25, "sportTypeID": 1},
                {"sportID": 25, "sportTypeID": 2},
                {"sportID": 26, "sportTypeID": 1},
                {"sportID": 26, "sportTypeID": 2},
                {"sportID": 27, "sportTypeID": 1},
                {"sportID": 27, "sportTypeID": 2},
                {"sportID": 28, "sportTypeID": 1},
                {"sportID": 28, "sportTypeID": 2},
                {"sportID": 29, "sportTypeID": 1},
                {"sportID": 29, "sportTypeID": 2},
                {"sportID": 30, "sportTypeID": 1},
                {"sportID": 30, "sportTypeID": 2},
                {"sportID": 31, "sportTypeID": 1},
                {"sportID": 31, "sportTypeID": 2},
                {"sportID": 32, "sportTypeID": 1},
                {"sportID": 32, "sportTypeID": 2},
                {"sportID": 33, "sportTypeID": 1},
                {"sportID": 33, "sportTypeID": 2},
                {"sportID": 34, "sportTypeID": 1},
                {"sportID": 34, "sportTypeID": 2},
                {"sportID": 35, "sportTypeID": 1},
                {"sportID": 35, "sportTypeID": 2},
                {"sportID": 36, "sportTypeID": 1},
                {"sportID": 36, "sportTypeID": 2},
                {"sportID": 37, "sportTypeID": 1},
                {"sportID": 37, "sportTypeID": 2},
                {"sportID": 38, "sportTypeID": 1},
                {"sportID": 38, "sportTypeID": 2},
                {"sportID": 39, "sportTypeID": 1},
                {"sportID": 39, "sportTypeID": 2},
                {"sportID": 40, "sportTypeID": 1},
                {"sportID": 40, "sportTypeID": 2},
                {"sportID": 41, "sportTypeID": 1},
                {"sportID": 41, "sportTypeID": 2},
                {"sportID": 42, "sportTypeID": 1},
                {"sportID": 42, "sportTypeID": 2},
                {"sportID": 43, "sportTypeID": 1},
                {"sportID": 43, "sportTypeID": 2},
                {"sportID": 44, "sportTypeID": 1},
                {"sportID": 44, "sportTypeID": 2},
                {"sportID": 45, "sportTypeID": 1},
                {"sportID": 45, "sportTypeID": 2},
                {"sportID": 46, "sportTypeID": 1},
                {"sportID": 46, "sportTypeID": 2},
                {"sportID": 47, "sportTypeID": 1},
                {"sportID": 47, "sportTypeID": 2},
                {"sportID": 48, "sportTypeID": 1},
                {"sportID": 48, "sportTypeID": 2},
                {"sportID": 49, "sportTypeID": 1},
                {"sportID": 49, "sportTypeID": 2},
                {"sportID": 50, "sportTypeID": 1},
                {"sportID": 50, "sportTypeID": 2},
                {"sportID": 51, "sportTypeID": 1},
                {"sportID": 51, "sportTypeID": 2},
                {"sportID": 52, "sportTypeID": 1},
                {"sportID": 52, "sportTypeID": 2},
                {"sportID": 53, "sportTypeID": 1},
                {"sportID": 53, "sportTypeID": 2},
                {"sportID": 54, "sportTypeID": 1},
                {"sportID": 54, "sportTypeID": 2},
                {"sportID": 55, "sportTypeID": 1},
                {"sportID": 55, "sportTypeID": 2},
                {"sportID": 56, "sportTypeID": 1},
                {"sportID": 56, "sportTypeID": 2},
                {"sportID": 57, "sportTypeID": 1},
                {"sportID": 57, "sportTypeID": 2},
                {"sportID": 58, "sportTypeID": 1},
                {"sportID": 58, "sportTypeID": 2},
                {"sportID": 59, "sportTypeID": 1},
                {"sportID": 59, "sportTypeID": 2},
                {"sportID": 60, "sportTypeID": 1},
                {"sportID": 60, "sportTypeID": 2},
                {"sportID": 61, "sportTypeID": 1},
                {"sportID": 61, "sportTypeID": 2},
                {"sportID": 62, "sportTypeID": 1},
                {"sportID": 62, "sportTypeID": 2},
                {"sportID": 63, "sportTypeID": 1},
                {"sportID": 63, "sportTypeID": 2},
                {"sportID": 64, "sportTypeID": 1},
                {"sportID": 64, "sportTypeID": 2},
                {"sportID": 65, "sportTypeID": 1},
                {"sportID": 65, "sportTypeID": 2},
                {"sportID": 66, "sportTypeID": 1},
                {"sportID": 66, "sportTypeID": 2},
                {"sportID": 67, "sportTypeID": 1},
                {"sportID": 67, "sportTypeID": 2}
            ],
            "sport": [
                (1, 1), (1, 2), (2, 1), (2, 2), (3, 1), (3, 2), (4, 1), (4, 2), (5, 1), (5, 2), (6, 1), (6, 2), (7, 1),
                (7, 2), (8, 1), (8, 2), (9, 1),
                (9, 2), (10, 1), (10, 2), (11, 1), (11, 2), (12, 1), (12, 2), (13, 1), (13, 2), (14, 1), (14, 2),
                (15, 1), (15, 2), (16, 1), (16, 2),
                (17, 1), (17, 2), (18, 1), (18, 2), (19, 1), (19, 2), (20, 1), (20, 2), (21, 1), (21, 2), (22, 1),
                (22, 2), (23, 1), (23, 2), (24, 1), (24, 2),
                (25, 1), (25, 2), (26, 1), (26, 2), (27, 1), (27, 2), (28, 1), (28, 2), (29, 1), (29, 2), (30, 1),
                (30, 2), (31, 1), (31, 2), (32, 1), (32, 2),
                (33, 1), (33, 2), (34, 1), (34, 2), (35, 1), (35, 2), (36, 1), (36, 2), (37, 1), (37, 2), (38, 1),
                (38, 2), (39, 1), (39, 2), (40, 1), (40, 2),
                (41, 1), (41, 2), (42, 1), (42, 2), (43, 1), (43, 2), (44, 1), (44, 2), (45, 1), (45, 2), (46, 1),
                (46, 2), (47, 1), (47, 2), (48, 1), (48, 2),
                (49, 1), (49, 2), (50, 1), (50, 2), (51, 1), (51, 2), (52, 1), (52, 2), (53, 1), (53, 2), (54, 1),
                (54, 2), (55, 1), (55, 2), (56, 1), (56, 2),
                (57, 1), (57, 2), (58, 1), (58, 2), (59, 1), (59, 2), (60, 1), (60, 2), (61, 1), (61, 2), (62, 1),
                (62, 2), (63, 1), (63, 2), (64, 1), (64, 2),
                (65, 1), (65, 2), (66, 1), (66, 2), (67, 1), (67, 2)

            ]
        }
    }

    # using above ori dict, automatically build another lookup map for updByName to id {'GB_ART_SCFT': 17,...}
    _mapping_updByName_to_id = {
        Gbrule_data['UpdBy_Name']: Gbrule_data['id']
        for Gbrule_code, Gbrule_data in _mapping.items()
    }

    @classmethod
    def get_id_by_updByName(cls, updByName):
        # Extremely fast O(1) dictionary lookup
        return cls._mapping_updByName_to_id.get(updByName, None)
    @classmethod
    def get_id_byCode(cls, code):  #to get id associated with each name/code
        return cls._mapping.get(code, {}).get('id')
    @classmethod
    def get_updByName_byCode(cls, code):  #to get UpdatedBy_SysName associated with each name/code
        return cls._mapping.get(code, {}).get('UpdBy_Name')
    @classmethod
    def get_sports_byCode(cls, code):
        return cls._mapping.get(code, {}).get('sport')
    @classmethod
    def get_sports_byID(cls, id):
        return cls._mapping.get(id, {}).get('sport')
    @classmethod
    def get_action_featureOnOffFlag_id_byCode(cls, code):
        return cls._mapping.get(code, {}).get('action_featureOnOffFlag_id')
