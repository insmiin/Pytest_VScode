
import tests.memberAction_tests.helpers.memAction_sql_helpers as qhlp
import tests.memberAction_tests.helpers.memAction_api_helpers as ahlp
from tests.utils.comparison_utils import is_match, is_LT
import ast
import logging

logger = logging.getLogger(__name__)




def assert_new_hit_action(api_session, hitObject, companyName, mysql_connection,csv_filter,action_to_exclude):
    action_to_exclude_set = set(map(int, [x.strip() for x in action_to_exclude.split(',')]))
    # 7  >>>>>  GET DEFINED ACTIONS ASSOCIATED WITH NEW HIT FROM SP/PG UI  <<<<<
    # retrieve all defined Actions(in SP/PG UI) associated with newhit
    UI_defined_action = ahlp.get_action(api_session, hitObject, companyName, csv_filter['gbRuleScore'])

    # 8 >>>>> CHECK THAT TRIGGERRING IS SUCCESSFUL (BY ENSURING THAT ACTION HAS BEEN SAVED IN MYSQL & TALLY WITH DEFINED ACTION FROM SP/PG UI)    <<<<<
    member_new_hit = qhlp.call_mySQL_getHitHistory(mysql_connection, csv_filter, hitObject.mysql_filter_statement,
                                              action_to_exclude, 'NewHit')  # list of dict
    assert len(member_new_hit) == 1, f'NewHit issue: either new hit is not successful & not saved in DB ORR there is >1 similar ModulehitType'
    new_Hit_Action = member_new_hit[0]
    #print('===new_Hit_Action:===>', new_Hit_Action)
    logger.info(f"===new_Hit_Action:===> {new_Hit_Action}")
    assert is_match(new_Hit_Action['latest_ScoreType'],
                    UI_defined_action['UI_ScoretypeID']), f'Hit latest_ScoreType is different from UI setting'
    assert is_match(new_Hit_Action['latest_BetDelay'],
                    UI_defined_action['UI_BetDelayID']), f'Hit latest_BetDelay is different from UI setting'
    assert is_match(new_Hit_Action['latest_MemberProfile'],
                    UI_defined_action['UI_MemberSettingProfileID']), f'Hit latest_MemberProfile is different from UI setting'
    assert is_match(new_Hit_Action['latest_SpreadGroup'],
                    UI_defined_action['UI_SpreadGroupID']), f'Hit latest_SpreadGroup is different from UI setting'
    assert is_match(new_Hit_Action['latest_MemberCategory'],
                    UI_defined_action['UI_MemberCategoryID']), f'Hit latest_MemberCategory is different from UI setting'
    assert is_match(new_Hit_Action['latest_IsAdvised'],
                    UI_defined_action['UI_IsAdvisedID']), f'Hit latest_IsAdvised is different from UI setting'
    assert is_match(new_Hit_Action['latest_NotifyMerchant'],
                    UI_defined_action['UI_IsNotifyMerchantID']), f'Hit latest_NotifyMerchant is different from UI setting'
    assert is_match(ast.literal_eval(new_Hit_Action['latest_BDSportGroups']),
                    UI_defined_action['UI_BDSportGroupIDs']), f'Hit latest_BDSportGroups is different from UI setting'
    # Hits that is not (SP/PG not found, whitelist, featureoff, ActionCondNotMet) need save in la
    if new_Hit_Action['actionStatusID'] not in action_to_exclude_set and hitObject.hitGbRule:
        assert is_match(new_Hit_Action['latest_ScoreType'],
                        new_Hit_Action['lastWfActn_ScoreType']), f'latest_ScoreType is not being saved as la'
        assert is_match(new_Hit_Action['latest_BetDelay'],
                        new_Hit_Action['lastWfActn_BetDelay']), f'latest_BetDelay is not being saved as la'
        assert is_match(new_Hit_Action['latest_MemberProfile'],
                        new_Hit_Action['lastWfActn_MemberProfile']), f'latest_MemberProfile is not being saved as la'
        assert is_match(new_Hit_Action['latest_SpreadGroup'],
                        new_Hit_Action['lastWfActn_SpreadGroup']), f'latest_SpreadGroup is not being saved as la'
        assert is_match(new_Hit_Action['latest_MemberCategory'],
                        new_Hit_Action['lastWfActn_MemberCategory']), f'latest_MemberCategory is not being saved as la'
        assert is_match(new_Hit_Action['latest_IsAdvised'],
                        new_Hit_Action['lastWfActn_IsAdvised']), f'latest_IsAdvised is not being saved as la'
        assert is_match(new_Hit_Action['latest_NotifyMerchant'],
                        new_Hit_Action['lastWfActn_NotifyMerchant']), f'latest_NotifyMerchant is not being saved as la'
        assert is_match(new_Hit_Action['latest_BDSportGroups'],
                        new_Hit_Action['lastWfActn_BDSportGroups']), f'latest_BDSportGroups is not being saved as la'
    else:
        assert new_Hit_Action['lastWfActn_updatedAt'] != new_Hit_Action[
            'updatedAt'], f'hit without action has been saved as la'

    return member_new_hit
